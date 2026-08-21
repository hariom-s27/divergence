# FLOWCHART — DIVERGENCE, end to end
### Step 34 deliverable · written 21 August 2026
### Five model calls, four deterministic steps (three checks, one composer). Shapes below are load-bearing, not decoration.

---

## Why shape, not just colour

A judge's first question is usually *"why so many nodes?"* The honest
answer is not a number, it is a distinction: **some of these boxes can be
wrong, and some of them cannot, because they are not models.** Round boxes
below (🤖) are a model call — they read text and predict tokens, so they can
hallucinate. Square boxes (⚙) are ordinary Python — an `if` statement, a
string match, arithmetic — so they cannot invent anything, only enforce or
compute what was already there.

**One correction made while building this diagram:** `architecture.md`
(Step 19) says every failure below traces to a numbered entry in
`failure-catalogue.md`. That file does not exist as a separate document —
the F-numbers and their "what fails without this node" text live directly
inside `architecture.md` itself, under each node's own heading. The
references below point there, not to a file that was never actually split
out. Checked before writing this, not assumed from the older file's own
cross-reference.

---

## The diagram

**This is the exact shape rendered in [`flowchart.png`](flowchart.png)** —
the PNG the track's submission rules actually require, with the same three
classes: where human input is necessary, which model answers each call, and
what each action does. This Mermaid version exists so the diagram also
renders directly on GitHub, without needing to open the image file.

```mermaid
flowchart TD
    IN["🧑 HUMAN INPUT — REQUIRED<br/>invoice + payment record<br/>PDF, photo, or typed text<br/>the pipeline cannot start without this"]

    N1(("🤖 1 EXTRACT<br/>Qwen2.5-7B-Instruct<br/>facts + confidence + source_span"))
    N2(("🤖 2 GAP DETECTOR<br/>Qwen2.5-7B-Instruct<br/>missing[] — runs BEFORE reasoning"))
    A["⚙ A GAP CONSTRAINT ENFORCER<br/>no model<br/>forces certainty to insufficient_evidence"]
    B["⚙ B VALUATION LATTICE<br/>no model, no API<br/>every defensible figure, arithmetic only"]
    N3(("🤖 3 INCOME TAX RESOLVER<br/>Qwen2.5-72B-Instruct<br/>scoped corpus only"))
    N4(("🤖 4 GST RESOLVER<br/>Qwen2.5-72B-Instruct<br/>scoped corpus only"))
    C["⚙ C CITATION MATCHER<br/>no model<br/>accept=False → conclusion DROPPED"]
    N5(("🤖 5 ADVERSARIAL CHECKER<br/>Mistral-Large-Instruct-2411, deliberately different family<br/>attacks every conclusion above, publishes it either way"))
    D["⚙ D DISCLOSURE COMPOSER<br/>no model<br/>deterministic HTML template"]
    OUT["📋 disclosure record<br/>output-interface.html"]
    ELECT["🧑 HUMAN INPUT — OPTIONAL, NEVER REQUIRED<br/>taxpayer may tick which figure they file<br/>no option is pre-selected"]

    IN --> N1 --> N2 --> A
    A --> N3
    A --> N4
    B --> N3
    B --> N4
    N3 --> C
    N4 --> C
    C --> N5 --> D --> OUT --> ELECT

    classDef model fill:#fde3cf,stroke:#c2571a,stroke-width:2px,color:#5c2a00;
    classDef code fill:#d6f5e3,stroke:#1a7a4c,stroke-width:2px,color:#0a3d24;
    classDef human fill:#e8d9f5,stroke:#6a3fa0,stroke-width:2px,color:#3a1f5c;
    classDef io fill:#e8e8f0,stroke:#4a4a6a,stroke-width:1.5px,color:#222;

    class N1,N2,N3,N4,N5 model;
    class A,B,C,D code;
    class IN,ELECT human;
    class OUT io;
```

**Legend:** 🧑 purple = a human input point (marked required or optional).
🤖 round orange = a model call, names the real model, can be wrong. ⚙ square
green = ordinary code, cannot invent.

---

## Node by node — what breaks without it, traced to `architecture.md`

| Node | One line | Fails without it (F-number, `architecture.md`) |
|---|---|---|
| 🤖 1 Extract | Pulls structured facts out of messy input, each one tagged with where it came from | F8 numeric/decimal confusion, F9 date normalisation, F10 entity confusion |
| 🤖 2 Gap detector | Establishes what is **absent** before anything reasons about what is present | F2 silent completeness — *predicted ~90%, the single highest-occurrence failure in the whole catalogue* |
| ⚙ A Gap enforcer | Forces `insufficient_evidence` on any conclusion that admits it depends on a missing fact — in code, not by asking nicely | Without it, F2 becomes a suggestion a fluent model can talk past |
| ⚙ B Valuation lattice | Enumerates all 12 defensible rupee figures by arithmetic, never picks one | F1 silent rate selection (highest RPN in the risk register, 125) · F11 weekend invention |
| 🤖 3 Income tax resolver | Resolves classification, recognition date, valuation method, TDS, penalty — scoped corpus, cross-regime citation structurally impossible | F6 regime collapse, F7 single-event tax, F4 inference stated as settled |
| 🤖 4 GST resolver | Resolves export-of-services status against IGST/CGST text only | Same regime-collapse family as 🤖 3, from the GST side |
| ⚙ C Citation matcher | String-matches every citation against real corpus text and the stated tax year; a miss drops the whole conclusion, not just a flag | F5 fabricated citation · F3 stale/year-less citation — caught 5 of this project's own historical errors automatically |
| 🤖 5 Adversarial checker | A **different model family** attacks every conclusion above, publishes the attack whether it lands or not | F4 false settledness — the only node built specifically to catch a real, current, correctly-quoted provision applied outside its own scope. Caught 3 real instances on unplanted data this project's own resolvers produced (D50, D54, D55) |
| ⚙ D Disclosure composer | Deterministic template — absence first, range second, single answer never | *"A document whose purpose is to be trustworthy cannot be produced by something that can hallucinate."* (`architecture.md`) |

---

## One thing this diagram cannot show, said here instead

`architecture.md`'s own warning box under 🤖 5 originally read *"this node
has never run"* — true 19 August, false by the time this flowchart was
first built. Fixed directly in `architecture.md` itself as of this
revision, not just noted here. Node 5 has since run repeatedly, caught real,
previously-undisclosed scope-reach errors in this project's own output
unprompted, and also produced real failure modes of its own (attacking
almost everything it sees; emitting incoherent output on one run) —
disclosed in `results.md`'s "Where we lose," not hidden because the node
also has real wins. This diagram shows the pipeline's shape, which has been
stable since 19 August; `results.md` and `START-HERE.md` are where the
current numbers and the full decision history actually live.
