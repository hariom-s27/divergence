"""
check_llm.py  --  run this BEFORE you burn any credits.

Answers four questions in about ten seconds:
    1. Is a key set, and which provider will the pipeline use?
    2. Does that key actually authenticate?
    3. Does each of the three model slots exist on your plan?
    4. Will each one return parseable JSON?

Costs a few hundred tokens total. Nothing is written to disk.

    python check_llm.py
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import llm_call


def main():
    try:
        prov = llm_call.provider_name()
    except llm_call.LLMError as e:
        print("FAIL  " + str(e))
        return 1

    print("provider : %s" % prov)
    print("base_url : %s" % (llm_call.PROVIDERS[prov]["base_url"] or "(anthropic default)"))
    print("key env  : %s  [set]" % llm_call.PROVIDERS[prov]["env"])
    print()

    ok = True
    families = {}
    for key in ("small", "large", "adversarial"):
        model = llm_call.model_id(key, prov)
        families[key] = model.split("/")[0].lower()
        sys.stdout.write("  %-12s %-48s " % (key, model))
        sys.stdout.flush()
        try:
            obj = llm_call.call_json(
                system="You reply with JSON only.",
                user_content='Reply with exactly: {"ok": true}',
                model_key=key,
                max_tokens=64,
                node_name="check:" + key,
            )
            if obj.get("ok") is True:
                print("OK")
            else:
                print("REACHED, but returned %r" % (obj,))
        except Exception as e:
            ok = False
            print("FAIL")
            print("        %s" % str(e).splitlines()[0])

    print()
    # D41: the adversary must not be the same family as the resolvers
    if families["adversarial"] and families["adversarial"] == families["large"]:
        print("WARNING  node 5 (adversarial) is the same model family as the "
              "resolvers (%s)." % families["large"])
        print("         D41 exists so the check is independent. Point "
              "DIVERGENCE_MODEL_ADVERSARIAL at another family.")
    else:
        print("D41 OK   resolvers=%s  adversary=%s  (different families)"
              % (families["large"], families["adversarial"]))

    print()
    p = llm_call.provenance()
    print("smoke-test spend: %d calls, %d in / %d out tokens"
          % (p["total_calls"], p["total_in_tokens"], p["total_out_tokens"]))

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
