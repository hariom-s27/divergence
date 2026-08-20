"""
llm_call.py  --  the single place DIVERGENCE talks to a model.

Two providers. One interface. The key is NEVER in this file.

    Featherless (open models)  ->  set  FEATHERLESS_API_KEY
    Anthropic   (Claude)       ->  set  ANTHROPIC_API_KEY

Which one is used is decided at runtime, and RECORDED, so results.md can
state honestly which models produced which arm.

Design note (D35): the eval runs on Featherless open models. The Claude
cost figure stays in the write-up as the *metered deployment estimate*,
not as the measured run. Do not blur those two.

Design note (D41): node 5 (adversarial) must run on a DIFFERENT model
family from the resolvers, or "an independent check" is just the same
model agreeing with itself. Under Featherless that is Qwen for the
resolvers and Llama for the adversary. If you override the model names,
KEEP THEM IN DIFFERENT FAMILIES or you have silently deleted the control.
"""

import json
import os
import re
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


class LLMError(RuntimeError):
    pass


# ----------------------------------------------------------------------
# Providers
# ----------------------------------------------------------------------
# Model ids can be overridden WITHOUT editing this file, via env vars:
#     DIVERGENCE_MODEL_SMALL / _LARGE / _ADVERSARIAL
# Useful when a Featherless plan tier does not serve a given size.

PROVIDERS = {
    "featherless": {
        "env": "FEATHERLESS_API_KEY",
        "base_url": "https://api.featherless.ai/v1",
        "models": {
            "small":       "Qwen/Qwen2.5-7B-Instruct",
            "large":       "Qwen/Qwen2.5-72B-Instruct",
            # every meta-llama/* model on this account 403s: "model_gated_needs_oauth"
            # (needs a HuggingFace account connected to Featherless, out-of-band, per
            # model family). Mistral is still a different family from Qwen (D41) and
            # is NOT gated on this account -- verified live, see DECISION-D42.md addendum.
            "adversarial": "mistralai/Mistral-Large-Instruct-2411",
        },
        "kind": "openai",
    },
    "anthropic": {
        "env": "ANTHROPIC_API_KEY",
        "base_url": None,
        "models": {
            "small":       "claude-haiku-4-5-20251001",
            "large":       "claude-sonnet-5",
            "adversarial": "claude-opus-5",
        },
        "kind": "anthropic",
    },
}

_ENV_OVERRIDE = {
    "small":       "DIVERGENCE_MODEL_SMALL",
    "large":       "DIVERGENCE_MODEL_LARGE",
    "adversarial": "DIVERGENCE_MODEL_ADVERSARIAL",
}


def provider_name():
    """Which provider this run uses. Explicit wins; otherwise whichever key is set."""
    forced = os.environ.get("DIVERGENCE_PROVIDER", "").strip().lower()
    if forced:
        if forced not in PROVIDERS:
            raise LLMError(
                "DIVERGENCE_PROVIDER=%r is not a provider. Use one of: %s"
                % (forced, ", ".join(sorted(PROVIDERS)))
            )
        if not os.environ.get(PROVIDERS[forced]["env"]):
            raise LLMError(
                "DIVERGENCE_PROVIDER=%s but %s is not set in this shell."
                % (forced, PROVIDERS[forced]["env"])
            )
        return forced

    for name in ("featherless", "anthropic"):     # Featherless first: D35
        if os.environ.get(PROVIDERS[name]["env"]):
            return name

    raise LLMError(
        "No model API key found in this shell.\n"
        "  Featherless (what the eval runs on):  set FEATHERLESS_API_KEY\n"
        "  Anthropic   (cost estimate only)   :  set ANTHROPIC_API_KEY\n"
        "Set it as an environment variable. Do not put a key in any file "
        "in this repo."
    )


def model_id(model_key, prov=None):
    prov = prov or provider_name()
    override = os.environ.get(_ENV_OVERRIDE.get(model_key, ""), "").strip()
    if override:
        return override
    try:
        return PROVIDERS[prov]["models"][model_key]
    except KeyError:
        raise LLMError(
            "Unknown model_key %r. Known: %s"
            % (model_key, ", ".join(sorted(PROVIDERS[prov]["models"])))
        )


# ----------------------------------------------------------------------
# Clients (built once, lazily)
# ----------------------------------------------------------------------

_CLIENT = {}


def client(prov=None):
    prov = prov or provider_name()
    if prov in _CLIENT:
        return _CLIENT[prov]

    key = os.environ.get(PROVIDERS[prov]["env"])
    if not key:
        raise LLMError("%s is not set." % PROVIDERS[prov]["env"])

    if PROVIDERS[prov]["kind"] == "openai":
        try:
            from openai import OpenAI
        except ImportError:
            raise LLMError(
                "The 'openai' package is required for provider %s.\n"
                "  pip install openai" % prov
            )
        c = OpenAI(api_key=key, base_url=PROVIDERS[prov]["base_url"])
    else:
        try:
            import anthropic
        except ImportError:
            raise LLMError(
                "The 'anthropic' package is required for provider %s.\n"
                "  pip install anthropic" % prov
            )
        c = anthropic.Anthropic(api_key=key)

    _CLIENT[prov] = c
    return c


# ----------------------------------------------------------------------
# Provenance  --  every call is recorded, so results.md cannot guess
# ----------------------------------------------------------------------

_CALLS = []


def provenance():
    """What actually ran. Fold this into every node's _meta block."""
    by_node = {}
    for c in _CALLS:
        row = by_node.setdefault(c["node"], {"model": c["model"], "calls": 0,
                                             "in_tokens": 0, "out_tokens": 0,
                                             "retries": 0})
        row["calls"] += 1
        row["in_tokens"] += c["in_tokens"]
        row["out_tokens"] += c["out_tokens"]
        row["retries"] += c["retries"]
    return {
        "provider": provider_name(),
        "models": {k: model_id(k) for k in ("small", "large", "adversarial")},
        "by_node": by_node,
        "total_calls": len(_CALLS),
        "total_in_tokens": sum(c["in_tokens"] for c in _CALLS),
        "total_out_tokens": sum(c["out_tokens"] for c in _CALLS),
        "note": ("Figures above are the MEASURED run on this provider. "
                 "Any Claude rupee-per-record figure quoted elsewhere is a "
                 "metered deployment estimate, not this run."),
    }


def reset_provenance():
    _CALLS.clear()


# ----------------------------------------------------------------------
# JSON extraction  --  open models fence, preamble, and trail
# ----------------------------------------------------------------------

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def _extract_json(text):
    """Return a parsed object, or raise ValueError. Tolerant of fences and chatter."""
    if text is None:
        raise ValueError("empty response")
    t = text.strip()

    try:
        return json.loads(t)
    except Exception:
        pass

    m = _FENCE.search(t)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except Exception:
            t = m.group(1).strip()

    # first balanced { ... } or [ ... ], respecting strings
    for opener, closer in (("{", "}"), ("[", "]")):
        start = t.find(opener)
        if start == -1:
            continue
        depth, in_str, esc = 0, False, False
        for i in range(start, len(t)):
            ch = t[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(t[start:i + 1])
                    except Exception:
                        break
    raise ValueError("no parseable JSON object in response")


# ----------------------------------------------------------------------
# The one call
# ----------------------------------------------------------------------

MAX_ATTEMPTS = 3
BACKOFF = 2.0


def _raw_call(prov, model, system, messages, max_tokens, json_mode):
    """Returns (text, in_tokens, out_tokens)."""
    c = client(prov)

    if PROVIDERS[prov]["kind"] == "openai":
        kwargs = dict(
            model=model,
            messages=[{"role": "system", "content": system}] + messages,
            max_tokens=max_tokens,
            temperature=0,
        )
        seed = os.environ.get("DIVERGENCE_SEED")
        if seed:
            kwargs["seed"] = int(seed)
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        try:
            r = c.chat.completions.create(**kwargs)
        except Exception as e:
            # not every open model serves JSON mode; degrade rather than die
            if json_mode and ("response_format" in str(e) or "json" in str(e).lower()):
                kwargs.pop("response_format", None)
                r = c.chat.completions.create(**kwargs)
            else:
                raise
        text = r.choices[0].message.content
        u = getattr(r, "usage", None)
        return text, getattr(u, "prompt_tokens", 0) or 0, getattr(u, "completion_tokens", 0) or 0

    r = c.messages.create(
        model=model,
        system=system,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0,
    )
    text = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
    return text, r.usage.input_tokens, r.usage.output_tokens


def call_json(system, user_content, model_key, max_tokens=4096, node_name="node"):
    """
    Ask for JSON. Get JSON, or raise LLMError.

    Same signature the nodes already use -- node1_extract.py and
    node2_gaps.py do not change.
    """
    prov = provider_name()
    model = model_id(model_key, prov)
    messages = [{"role": "user", "content": user_content}]
    retries = 0
    last_text = None
    last_err = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            text, tin, tout = _raw_call(prov, model, system, messages,
                                        max_tokens, json_mode=True)
        except Exception as e:
            last_err = e
            if attempt == MAX_ATTEMPTS:
                raise LLMError("[%s] %s/%s transport failure after %d attempts: %s"
                               % (node_name, prov, model, attempt, e))
            retries += 1
            time.sleep(BACKOFF * attempt)
            continue

        last_text = text
        try:
            obj = _extract_json(text)
        except ValueError as e:
            last_err = e
            if attempt == MAX_ATTEMPTS:
                break
            retries += 1
            # show the model its own bad output; open models fix this reliably
            messages = [
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": (text or "")[:2000]},
                {"role": "user", "content":
                    "That was not valid JSON. Reply with the JSON object only. "
                    "No prose before it, no prose after it, no markdown fence."},
            ]
            continue

        _CALLS.append({"node": node_name, "model": model, "provider": prov,
                       "in_tokens": tin, "out_tokens": tout, "retries": retries})
        return obj

    raise LLMError(
        "[%s] %s/%s returned unparseable JSON after %d attempts (%s).\n"
        "--- last 500 chars of response ---\n%s"
        % (node_name, prov, model, MAX_ATTEMPTS, last_err, (last_text or "")[-500:])
    )


if __name__ == "__main__":
    print("provider :", provider_name())
    for k in ("small", "large", "adversarial"):
        print("  %-12s %s" % (k, model_id(k)))
