"""
llm_call.py  --  the single place DIVERGENCE talks to a model.

FEATHERLESS ONLY.  Anthropic is reachable but never by accident (D44).

    set FEATHERLESS_API_KEY in your shell.  Never in a file in this repo.

Why "only": D35 says the eval runs on open weights and the Claude rupee
figure is a metered deployment estimate. An automatic fallback to Anthropic
would mean a shell missing one env var silently produces a Claude-generated
row in a results table labelled "open models". Nothing would crash. Nothing
would look wrong. That is a Class 3 failure inside our own harness, in the
exact shape the project exists to catch — so the fallback is gone. Running on
Claude now requires typing DIVERGENCE_PROVIDER=anthropic on purpose.

Design note (D41): node 5 (adversarial) must run on a DIFFERENT model family
from the resolvers, or "an independent check" is a model agreeing with
itself. Resolvers are Qwen; the adversary is Mistral. If you override the
model ids, KEEP THEM IN DIFFERENT FAMILIES — check_llm.py warns if you don't.

Design note (D43): every meta-llama/* id 403s on this account
(model_gated_needs_oauth — a HuggingFace licence gate Featherless passes
through). available_on_current_plan is TRUE for those models; the gate is one
layer further out and the catalogue does not signal it. Only a real call
finds it. Hence Mistral in the adversarial slot.
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


class GatedModelError(LLMError):
    """The model exists and is on your plan, but a licence gate blocks it."""


# ----------------------------------------------------------------------
# Providers
# ----------------------------------------------------------------------
# Override any slot WITHOUT editing this file:
#     DIVERGENCE_MODEL_SMALL / _LARGE / _ADVERSARIAL

PROVIDERS = {
    "featherless": {
        "env": "FEATHERLESS_API_KEY",
        "base_url": "https://api.featherless.ai/v1",
        "models": {
            "small":       "Qwen/Qwen2.5-7B-Instruct",
            "large":       "Qwen/Qwen2.5-72B-Instruct",
            # D43: NOT meta-llama/* — every one of them 403s on this account.
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

DEFAULT_PROVIDER = "featherless"


def temperature():
    """evaluation-design.md: 'Temperature | default, not zero — that is how a
    real user runs it.' Five runs at temperature 0 measure one point five
    times. The scored eval must never run at temperature 0.

    D52: this used to default to 0.0 unless DIVERGENCE_TEMPERATURE was set
    explicitly -- a setting that must be actively remembered every session
    is a setting that gets forgotten, and it was: every run across Blocks
    A through E1 the same night this was already fixed once (D45) ran at
    temperature 0 again, silently, because nobody typed the env var that
    session. The default is now inverted: the model's own default
    temperature is what you get for free. DEV/self-test work that
    actually wants reproducibility must opt IN with DIVERGENCE_DEV=1,
    not opt out of a bug that recurs by default. Explicit, per-run, and
    recorded in provenance()."""
    if os.environ.get("DIVERGENCE_DEV", "").strip() == "1":
        return 0.0          # explicit opt-in only: reproducible dev/self-test runs
    t = os.environ.get("DIVERGENCE_TEMPERATURE", "").strip()
    if t == "":
        return None          # send no temperature -- the model's own default
    if t.lower() in ("default", "none", "model"):
        return None
    return float(t)

# Model ids known to accept image_url blocks. Used by node1_extract.py to
# refuse a photographed invoice rather than send an image to a text-only
# model, which either errors or — worse — ignores it and invents the facts.
VISION_MODELS = {
    "Qwen/Qwen2.5-VL-3B-Instruct",
    "Qwen/Qwen2.5-VL-7B-Instruct",
    "Qwen/Qwen2.5-VL-32B-Instruct",
    "Qwen/Qwen2.5-VL-72B-Instruct",
    "Qwen/Qwen3-VL-30B-A3B-Instruct",
    "Qwen/Qwen3-VL-235B-A22B-Thinking",
}

_ENV_OVERRIDE = {
    "small":       "DIVERGENCE_MODEL_SMALL",
    "large":       "DIVERGENCE_MODEL_LARGE",
    "adversarial": "DIVERGENCE_MODEL_ADVERSARIAL",
}


def provider_name():
    """Featherless, unless you deliberately asked for something else.

    There is no fallback. A missing FEATHERLESS_API_KEY is an error, not a
    reason to quietly use Claude."""
    forced = os.environ.get("DIVERGENCE_PROVIDER", "").strip().lower()
    prov = forced or DEFAULT_PROVIDER

    if prov not in PROVIDERS:
        raise LLMError(
            "DIVERGENCE_PROVIDER=%r is not a provider. Use one of: %s"
            % (forced, ", ".join(sorted(PROVIDERS)))
        )

    if not os.environ.get(PROVIDERS[prov]["env"]):
        if prov == DEFAULT_PROVIDER:
            raise LLMError(
                "FEATHERLESS_API_KEY is not set in this shell.\n"
                "  PowerShell : $env:FEATHERLESS_API_KEY = \"rc_...\"\n"
                "  bash/zsh   : export FEATHERLESS_API_KEY=\"rc_...\"\n"
                "The key belongs in the shell, never in a file in this repo.\n"
                "\n"
                "This does NOT fall back to Anthropic on purpose (D44): a run\n"
                "that silently switched provider would put a Claude-generated\n"
                "row in a results table labelled 'open models'."
            )
        raise LLMError(
            "DIVERGENCE_PROVIDER=%s but %s is not set in this shell."
            % (prov, PROVIDERS[prov]["env"])
        )

    return prov


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


def is_vision_model(model_key_or_id):
    """True if this slot resolves to a model that can read an image."""
    mid = model_key_or_id
    if mid in _ENV_OVERRIDE:
        mid = model_id(mid)
    if mid in VISION_MODELS:
        return True
    return bool(re.search(r"(?i)(-VL-|vision)", mid))


# ----------------------------------------------------------------------
# Clients
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
            raise LLMError("pip install openai")
        c = OpenAI(api_key=key, base_url=PROVIDERS[prov]["base_url"])
    else:
        try:
            import anthropic
        except ImportError:
            raise LLMError("pip install anthropic")
        c = anthropic.Anthropic(api_key=key)

    _CLIENT[prov] = c
    return c


# ----------------------------------------------------------------------
# Provenance  --  what actually ran, folded into every record's _meta.llm
# ----------------------------------------------------------------------

_CALLS = []


def provenance():
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
        "temperature": ("0 (DIVERGENCE_DEV=1)" if os.environ.get("DIVERGENCE_DEV", "").strip() == "1"
                         else (os.environ.get("DIVERGENCE_TEMPERATURE", "").strip() or "default (model's own)")),
        "note": ("Figures above are the MEASURED run on this provider. Any "
                 "Claude rupee-per-record figure quoted elsewhere is a metered "
                 "deployment estimate, not this run."),
    }


def reset_provenance():
    _CALLS.clear()


# ----------------------------------------------------------------------
# JSON extraction  --  open models fence, preamble, and trail
# ----------------------------------------------------------------------

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def _extract_json(text):
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
# Retry policy  --  retry what can succeed, fail fast on what cannot
# ----------------------------------------------------------------------
# Retrying a 403 three times is three wasted calls and a slower, more
# confusing error. Only transient statuses get another attempt.

RETRYABLE = {408, 409, 425, 429, 500, 502, 503, 504}
MAX_ATTEMPTS = 3
BACKOFF = 2.0


def _status_of(e):
    s = getattr(e, "status_code", None)
    if s is None:
        s = getattr(getattr(e, "response", None), "status_code", None)
    if s is None:
        m = re.search(r"\b(4\d\d|5\d\d)\b", str(e))
        s = int(m.group(1)) if m else None
    return s


def _classify(e, model):
    """Return (retryable: bool, wrapped_error_or_None)."""
    text = str(e)
    if "model_gated_needs_oauth" in text or "This model is gated" in text:
        return False, GatedModelError(
            "%s is licence-gated on this Featherless account (403).\n"
            "  Every meta-llama/* id behaves this way — see DECISION-D43.md.\n"
            "  Fix it on featherless.ai (connect a HuggingFace account that has\n"
            "  accepted the licence), or point the slot at an ungated model:\n"
            "    $env:DIVERGENCE_MODEL_ADVERSARIAL = \"mistralai/Mistral-Large-Instruct-2411\""
            % model
        )
    status = _status_of(e)
    if status in RETRYABLE:
        return True, None
    if status is not None:
        return False, None
    return True, None          # unknown/transport -> worth one more go


def _raw_call(prov, model, system, messages, max_tokens, json_mode):
    c = client(prov)

    if PROVIDERS[prov]["kind"] == "openai":
        kwargs = dict(
            model=model,
            messages=[{"role": "system", "content": system}] + messages,
            max_tokens=max_tokens,
        )
        _t = temperature()
        if _t is not None:
            kwargs["temperature"] = _t
        seed = os.environ.get("DIVERGENCE_SEED")
        if seed:
            kwargs["seed"] = int(seed)
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        try:
            r = c.chat.completions.create(**kwargs)
        except Exception as e:
            if json_mode and ("response_format" in str(e) or "json" in str(e).lower()):
                kwargs.pop("response_format", None)
                r = c.chat.completions.create(**kwargs)
            else:
                raise
        text = r.choices[0].message.content
        u = getattr(r, "usage", None)
        return text, getattr(u, "prompt_tokens", 0) or 0, getattr(u, "completion_tokens", 0) or 0

    anthropic_kwargs = dict(model=model, system=system, messages=messages, max_tokens=max_tokens)
    _t = temperature()
    if _t is not None:
        anthropic_kwargs["temperature"] = _t
    r = c.messages.create(**anthropic_kwargs)
    text = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
    return text, r.usage.input_tokens, r.usage.output_tokens


def call_json(system, user_content, model_key, max_tokens=4096, node_name="node"):
    """Ask for JSON. Get JSON, or raise LLMError.

    Signature unchanged — node1_extract.py and node2_gaps.py do not change."""
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
            retryable, wrapped = _classify(e, model)
            if wrapped is not None:
                raise wrapped
            last_err = e
            if not retryable:
                raise LLMError("[%s] %s/%s: %s" % (node_name, prov, model, e))
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
        "--- last 500 chars ---\n%s"
        % (node_name, prov, model, MAX_ATTEMPTS, last_err, (last_text or "")[-500:])
    )


if __name__ == "__main__":
    print("provider :", provider_name())
    for k in ("small", "large", "adversarial"):
        mid = model_id(k)
        print("  %-12s %-42s %s" % (k, mid, "[vision]" if is_vision_model(mid) else ""))
