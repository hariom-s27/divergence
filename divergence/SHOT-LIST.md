# SHOT LIST — DIVERGENCE, M9 demo video (~3:00)

Companion to [`VIDEO-SCRIPT.md`](VIDEO-SCRIPT.md). Every window, tab, and
scroll position named below, so recording is mechanical: open exactly
what's listed, scroll to exactly the line named, record the section, move
to the next row. Line numbers are as of this file's own commit — if a
source file is edited afterward, re-check the line number before
recording, don't trust it blind.

**Supersedes the earlier shot list**, which was built around a different
six-block structure. This one follows `VIDEO-SCRIPT.md`'s real five-part
structure (introduction → problem → components → demo → close).

## Windows to have open before recording starts

1. **Browser** — one tab: `divergence/output-interface.html`, opened
   directly from disk (`file://.../divergence/output-interface.html`) or
   via `https://hariom-s27.github.io/divergence/output-interface.html`.
   Zoom set so section 02's dimension line and fieldset are both visible
   without mid-shot scrolling (test this before recording).
2. **Image viewer or a maximized editor tab** — `divergence/flowchart.png`,
   pre-opened, zoomed to fit the frame with no UI chrome visible if
   possible (full-screen image viewer beats an editor's image preview
   pane for this one shot).
3. **Editor** (VS Code or equivalent), tabs open in this order:
   - `citation_matcher.py`, pre-scrolled so `verify()` and the `Verdict`
     dataclass (lines ~165–216) are both in frame without scrolling.
   - `runs/21aug/D1_final_seed2.json`
   - `runs/21aug/D1_final_seed2_attack.json`
   - `results.md`
   - `README.md`
4. **Backup only, never recorded unless a judge asks live:** a terminal
   in `divergence/`, ready to run
   `python run_pipeline.py --record-id LIVE-DEMO --tax-year "FY 2026-27" --text cases/D1/input.md --node5`
   with a real `FEATHERLESS_API_KEY` set. This is insurance, not a shot —
   don't open it on camera as part of the scripted recording.

Screen-record a fixed window region covering the browser/viewer/editor;
switch between them with a visible Alt-Tab or dock click, not an
off-screen cut that would be jarring without a transition.

---

## 1. INTRODUCTION — ~0:00–0:15

- **Shot 1 (0:00–0:02):** A plain title card, "DIVERGENCE," text only —
  build this once as a static image or a title slide in the editing
  tool, not a live window.
- **Shot 2 (0:02–0:15):** Browser, `output-interface.html`, scrolled to
  the very top — the `<h1>` "Payment received 28 June 2026, 03:14 IST"
  and the sub-line "5,000 USDC · Invoice 2026-114..." both in frame.

## 2. PROBLEM — ~0:15–0:50

- **Window:** Browser, same tab.
- **Scroll position:** Section **02 — What it was worth in rupees**,
  scrolled so the two `.amt` figures and the red dimension-line label are
  centered in frame (roughly 400–700px down at 1080p — adjust and note
  the real pixel offset once tested).
- **Action:** Static shot, no interaction, for the full 35 seconds. Let
  `₹469,750`, `₹517,619`, and `₹47,869 · 10.19%` sit on screen.

## 3. COMPONENTS — ~0:50–1:20

- **Shot 1 (0:50–1:05), ~15s:** Image viewer or full-screen preview,
  `flowchart.png`. Static, full frame. If your tool supports a very slow
  zoom (ease in, no faster than a few percent over the full 15s) toward
  the five 🤖 nodes, that reads better than a hard static frame — but a
  static frame is entirely acceptable if a slow zoom isn't easy to
  produce. **No fast pan, no scroll.**
- **Shot 2 (1:05–1:20), ~15s:** Cut to the editor, `citation_matcher.py`,
  pre-scrolled to lines **165–216** (`Verdict` dataclass through the
  start of `verify()`'s tax-year gate). Static, syntax-highlighted, no
  scrolling and no live typing during the shot — this is the "~10 seconds
  of purposeful code" the script calls for; don't stretch it into a tour
  of the file.

## 4. DEMO — ~1:20–2:40

### 4a. Lattice and uncertainty budget (~1:20–1:45)

- **Window:** Browser, `output-interface.html`, section 02 (same scroll
  position as section 2 above, or ~100px further down to bring the
  `<details>` element into frame).
- **Action:** Click the `<summary>` "Where the spread actually comes
  from — decomposed by source" at roughly 1:22. It expands. Hold the
  four budget rows (domestic premium, which price within the day, the
  proxy, which official date) on screen for the rest of the beat.

### 4b. Election toggle (~1:45–2:05)

- **Window:** Browser, scrolled to the `<fieldset>` at the bottom of
  section 02. Both radio options and the `#election-status` line must be
  in frame together.
- **Action, timed to the SAY lines:**
  - ~1:47 — click radio `ea` (₹469,750). Status line updates to
    *"Recorded in this browser: SBI TTBR 2026-06-29..."*
  - ~1:55 — click radio `eb` (₹517,619). Status line updates again.
  - ~2:02 — click **Clear this record** so the recording ends this beat
    on a clean, unticked state (this click can run slightly into the
    next section's audio — it's a visual beat, not narrated).

### 4c. Evidence — the ablation miss (~2:05–2:40)

- **Window:** Editor, `results.md`.
- **Scroll position:** The heading `### The ablation — 4 planted
  defects, D1's real conclusions as the base` at the top of frame, so
  the four-row table is fully visible below it.
- **Action:** Highlight (a real text selection or a callout box, not
  just a cursor hover) the **D1-b | ... | NOT CAUGHT** row, with the
  other three **CAUGHT** rows visible above/below for contrast — the
  miss should read as no smaller or less prominent than the three
  catches.

## 5. CLOSE — ~2:40–3:00

- **Shot 1 (2:40–2:45), ~5s:** Editor, `README.md`, scrolled to the
  `## Cost` table — highlight the `₹0 metered — plan-tier access` row.
- **Shot 2 (2:45–2:52), ~7s:** Cut to `runs/21aug/D1_final_seed2.json`,
  scrolled to **line 345** (`regimes[0].outcome`). Highlight *"No
  deduction obligation arises under s.393(1)... the payer is outside
  India."*
- **Shot 3 (2:52–3:00), final ~8s:** Cut to
  `runs/21aug/D1_final_seed2_attack.json`, **lines 12–17**
  (`attacked[1]`). Highlight `"survived": false` (line 15) and the
  `"attack"` text (line 14). **Hold this frame, unmoving, for the last 3
  seconds.** Fade to black from here — no logo card, no summary slide.
  The attacked claim is the last thing visible.

---

## Pre-flight checklist, run once before the real take

- [ ] `output-interface.html` renders correctly (fonts loaded, no
      console errors) in the exact browser/zoom used for recording.
- [ ] Both radio clicks in section 4b actually update
      `#election-status` — test once, then click **Clear this record**
      so the real take starts from a clean state.
- [ ] `flowchart.png` opens and reads clearly at the resolution you're
      recording at — check the five 🤖/five ⚙ labels are legible, not
      just present.
- [ ] `citation_matcher.py` lines 165–216 fit on screen at your editor's
      font size without scrolling. Increase font size if not — legible
      code beats more code visible at once.
- [ ] The editor tabs are pre-scrolled to their starting positions
      before recording begins, so no shot opens on a visible scroll- or
      tab-switch-into-place.
- [ ] Line numbers above still match the current state of `results.md`,
      `README.md`, `citation_matcher.py`, and the two `runs/21aug/`
      files — re-grep if any were edited after this shot list was
      written.
- [ ] **Voice-over is recorded separately from the screen capture**,
      to the script above, then synced in editing — not narrated live
      over a live screen recording.

## Publishing checklist

- [ ] **If uploading to YouTube, the video is marked "Not for Kids."**
      COPPA restrictions otherwise block judges from accessing it —
      check this before the link goes into the submission form, not
      after.
- [ ] The live pipeline terminal from the "Windows to have open" section
      was never part of the recorded video — confirm by watching the
      final export once end to end before uploading.
