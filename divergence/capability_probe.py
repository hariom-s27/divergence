"""
capability_probe.py -- S8: is response_format a silent no-op?

Every resolver call in this pipeline sets response_format={"type":
"json_object"} (llm_call.py's _raw_call). If the provider hard-rejects
that field, _raw_call already catches it and retries without it -- a
loud, already-handled failure. The question this file exists to answer
is quieter: what if Featherless's OpenAI-compatible layer accepts the
field without complaint, but the actual open-weight model behind it
(routed through whatever inference backend Featherless runs that day)
never implemented grammar-constrained JSON decoding at all, and just
ignores it? No exception. No signal. The pipeline would look identical
either way, because its own reliability today already comes mostly from
the prompt asking for JSON, not from the flag.

THE TEST: fire the same prompt twice, asking for a one-sentence PLAIN
PROSE answer ("do NOT use JSON") --
    A. with response_format set
    B. without it (the control)
If the flag is doing real work, it should win the fight against an
explicit contrary instruction: A comes back as JSON, B (no flag, same
contrary instruction) comes back as prose. If A comes back as prose too
-- same as the unflagged control -- the flag demonstrably changed
nothing observable for that model.

Deliberately NOT a system-prompt "reply in JSON only" instruction, and
deliberately NOT reusing this project's own resolver prompts: either
would let voluntary instruction-following manufacture a false ENFORCED
verdict. The point is to isolate the flag's effect from the model's own
willingness to comply when asked nicely.

NOT a CI gate for the live probe itself -- CI has no API key (D63's
whole reason for existing). The classifier logic (classify(), pure, no
network calls) IS self-tested and IS safe to run in CI; only main()
needs a key.

    python capability_probe.py             # live, needs FEATHERLESS_API_KEY
    python capability_probe.py --self-test  # offline, classifier logic only
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import llm_call  # noqa: E402

PROBE_SYSTEM = "You are a helpful assistant."
PROBE_USER = (
    "Answer in one short sentence: why does the sky look blue? "
    "Important: answer in plain prose. Do NOT use JSON, do NOT use "
    "markdown formatting -- one plain sentence of text, nothing else."
)


def _is_response_format_error(e):
    # Mirrors _raw_call's own detection in llm_call.py exactly, on
    # purpose -- if this string check misses something _raw_call's
    # matching check also misses, that's the same failure mode either
    # way, not a new one introduced here.
    text = str(e)
    return "response_format" in text or "json" in text.lower()


def classify(text_a, err_a, text_b, err_b):
    """Pure classifier, no network calls -- fully covered by --self-test.

    text_a/err_a: result of the flagged call (response_format set).
    text_b/err_b: result of the control call (same prompt, no flag)."""
    if err_a is not None and _is_response_format_error(err_a):
        return "REJECTED", (
            "provider raised an error naming response_format/json -- already "
            "handled by _raw_call's own fallback in real pipeline use, so this "
            "never reaches a resolver as a silent problem: %s"
            % str(err_a).splitlines()[0]
        )
    if err_a is not None:
        return "ERROR", "flagged call failed for an unrelated reason: %s" % str(err_a).splitlines()[0]
    if err_b is not None:
        return "ERROR", (
            "control call (no flag) failed for an unrelated reason -- can't "
            "compare: %s" % str(err_b).splitlines()[0]
        )

    a_is_json = llm_call.try_parse_json(text_a) is not None
    b_is_json = llm_call.try_parse_json(text_b) is not None

    if b_is_json:
        return "INCONCLUSIVE", (
            "the model produced JSON even in the control call, despite being "
            "asked for plain prose -- can't attribute the flagged call's "
            "behaviour to response_format either way"
        )
    if a_is_json:
        return "ENFORCED", (
            "the flag overrode an explicit 'answer in plain prose' instruction "
            "that the unflagged control call obeyed -- response_format is doing "
            "real work on this model/provider pair"
        )
    return "APPARENT NO-OP", (
        "response_format was set, but the model answered in prose anyway, "
        "exactly like the unflagged control -- the flag produced no observable "
        "effect on this model/provider pair"
    )


def _fire(model_key, prov, json_mode):
    """One raw, unrepaired call. Deliberately bypasses call_json's
    retry-and-repair loop -- that loop's own 'that was not valid JSON,
    try again' follow-up would coerce a JSON object out of the model on
    a second attempt regardless of whether the flag itself did
    anything, which would mask exactly the signal this probe needs."""
    model = llm_call.model_id(model_key, prov)
    c = llm_call.client(prov)
    kwargs = dict(
        model=model,
        messages=[
            {"role": "system", "content": PROBE_SYSTEM},
            {"role": "user", "content": PROBE_USER},
        ],
        max_tokens=200,
    )
    _t = llm_call.temperature()
    if _t is not None:
        kwargs["temperature"] = _t
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    try:
        r = c.chat.completions.create(**kwargs)
        return r.choices[0].message.content, None
    except Exception as e:
        return None, e


def probe_model(model_key, prov):
    text_a, err_a = _fire(model_key, prov, json_mode=True)
    text_b, err_b = _fire(model_key, prov, json_mode=False)
    verdict, detail = classify(text_a, err_a, text_b, err_b)
    return verdict, detail, text_a, text_b


def _self_test():
    cases = [
        (
            "REJECTED",
            None, Exception("Error code: 400 - {'message': 'response_format not supported'}"),
            None, None,
        ),
        (
            "ENFORCED",
            '{"note": "Rayleigh scattering"}', None,
            "The sky looks blue because of Rayleigh scattering.", None,
        ),
        (
            "APPARENT NO-OP",
            "The sky looks blue because of Rayleigh scattering.", None,
            "The sky looks blue because of Rayleigh scattering.", None,
        ),
        (
            "INCONCLUSIVE",
            '{"note": "Rayleigh scattering"}', None,
            '{"note": "Rayleigh scattering, apparently"}', None,
        ),
        (
            "ERROR",
            None, Exception("connection timeout"),
            None, None,
        ),
    ]
    ok = True
    for expected, text_a, err_a, text_b, err_b in cases:
        got, detail = classify(text_a, err_a, text_b, err_b)
        mark = "OK" if got == expected else "FAIL"
        if got != expected:
            ok = False
        print("  %-16s expected=%-16s got=%-16s" % (mark, expected, got))
    print()
    print("SELF-TEST " + ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return _self_test()

    try:
        prov = llm_call.provider_name()
    except llm_call.LLMError as e:
        print("FAIL  " + str(e))
        return 1

    if llm_call.PROVIDERS[prov]["kind"] != "openai":
        print(
            "provider %r is not an OpenAI-compatible endpoint -- response_format "
            "is a json_object-mode parameter specific to that API shape. Nothing "
            "to probe here; this question does not apply to Anthropic's Messages "
            "API." % prov
        )
        return 0

    print("provider : %s" % prov)
    print("costs ~a few hundred tokens per model slot (two short calls each)\n")

    exit_code = 0
    for key in ("small", "large", "adversarial"):
        model = llm_call.model_id(key, prov)
        print("  %-12s %s" % (key, model))
        try:
            verdict, detail, text_a, text_b = probe_model(key, prov)
        except Exception as e:
            print("    ERROR   %s" % str(e).splitlines()[0])
            exit_code = 1
            continue
        print("    verdict : %s" % verdict)
        print("    why     : %s" % detail)
        if verdict in ("ENFORCED", "APPARENT NO-OP", "INCONCLUSIVE"):
            print("    A (flagged) : %r" % ((text_a or "")[:120]))
            print("    B (control) : %r" % ((text_b or "")[:120]))
        print()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
