#!/usr/bin/env python3
"""
NODE 1 — EXTRACT  ·  DIVERGENCE
Model: "small" — see llm_call.py PROVIDERS for which model that resolves to
on the active provider. Corpus: none.

Pulls structured facts out of an invoice + payment record. Every field
carries {value, confidence, source_span} — never a bare value
(schema.json $defs.extracted_field). source_span is what makes the
extraction auditable rather than trusted (architecture.md, node 1).

    python node1_extract.py --text cases/D1/case.txt
    python node1_extract.py --file invoice.png --file payment.png
    python node1_extract.py --text cases/D1/case.txt --out cases/D1/facts.json

IMAGES vs PDFs. The OpenAI-compatible chat API (what Featherless speaks) has
no native PDF block the way Anthropic's does — a PDF has to become either an
image or text before a model can read it. --file sends images (png/jpg) as
inline image_url blocks. A PDF is text-extracted first (via pypdf) and sent
as typed text; if it has no extractable text layer (a scan with no OCR),
this hard-fails and tells you to convert it to an image instead — silently
sending nothing would be worse (architecture.md ERROR HANDLING).

Typed input is fine for at least two cases — say so openly rather than
hiding it (STEP21-README) — that is what --text is for.

Reads   the SYSTEM block of step22drop/prompts/01-extract.md
Writes  facts.json: {"facts": {...}, "extraction_notes": [...], "_meta": {...}}
        — an intermediate artifact. run_pipeline.py folds "facts" into the
        schema.json-conforming record; extraction_notes is not a schema field.

WHAT FAILS WITHOUT source_span/confidence: F8 (currency confusion), F9 (date
normalisation), F10 (entity confusion) — see architecture.md, node 1.
"""

import os, sys, json, argparse, base64, mimetypes
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import llm_call  # noqa: E402
from llm_call import LLMError  # noqa: E402

PROMPT_FILE = os.path.join(HERE, "step22drop", "prompts", "01-extract.md")
NODE_NAME = "node1_extract"


def die(msg):
    print(f"\n  ERROR: {msg}\n")
    sys.exit(1)


def load_system_prompt():
    if not os.path.exists(PROMPT_FILE):
        die(f"{PROMPT_FILE} not found")
    text = open(PROMPT_FILE, encoding="utf-8").read()
    marker = "## SYSTEM"
    if marker not in text:
        die(f"{PROMPT_FILE} has no '## SYSTEM' section")
    fenced = text.split(marker, 1)[1].split("```", 2)
    if len(fenced) < 3:
        die(f"{PROMPT_FILE}'s SYSTEM section is not fenced with ```")
    return fenced[1].strip()


def _pdf_to_text(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        die(
            f"--file {path} is a PDF, and 'pypdf' is not installed.\n"
            "  Run: python -m pip install pypdf\n"
            "  Or convert it to a PNG/JPG page and pass that to --file instead."
        )
    reader = PdfReader(path)
    text = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
    if not text:
        die(
            f"--file {path}: no extractable text layer (likely a scanned image with no OCR).\n"
            "  Convert the page to a PNG/JPG and pass that to --file instead — "
            "sending nothing silently would be the wrong kind of failure."
        )
    return text


def build_content(text_paths, file_paths):
    blocks = []
    for p in text_paths:
        if not os.path.exists(p):
            die(f"--text file not found: {p}")
        blocks.append({
            "type": "text",
            "text": f"--- {os.path.basename(p)} (typed input) ---\n" + open(p, encoding="utf-8").read(),
        })
    for p in file_paths:
        if not os.path.exists(p):
            die(f"--file not found: {p}")
        mime, _ = mimetypes.guess_type(p)
        if mime == "application/pdf":
            blocks.append({
                "type": "text",
                "text": f"--- {os.path.basename(p)} (PDF, text-extracted) ---\n" + _pdf_to_text(p),
            })
        elif mime and mime.startswith("image/"):
            data = base64.standard_b64encode(open(p, "rb").read()).decode()
            blocks.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{data}"},
            })
            blocks.append({"type": "text", "text": f"[the image above is {os.path.basename(p)}]"})
        else:
            die(f"--file {p}: unrecognised type {mime!r} (expected a PDF or an image)")
    if not blocks:
        die("give at least one --text or --file input")
    return blocks


def extract(text_paths, file_paths, model="small"):
    """The reusable entry point — run_pipeline.py calls this directly rather
    than shelling out and re-parsing stdout. Returns (facts, extraction_notes,
    meta) — meta is this node's row from llm_call.provenance() after the call."""
    system = load_system_prompt()
    content = build_content(text_paths, file_paths)
    parsed = llm_call.call_json(system, content, model, node_name=NODE_NAME)
    if "facts" not in parsed or not isinstance(parsed["facts"], dict):
        raise LLMError(f"{NODE_NAME}: model output has no top-level 'facts' object\n{parsed}")
    meta = llm_call.provenance()["by_node"].get(NODE_NAME, {})
    return parsed["facts"], parsed.get("extraction_notes", []), meta


def main():
    ap = argparse.ArgumentParser(description="Node 1 — EXTRACT")
    ap.add_argument("--text", action="append", default=[],
                     help="typed/plaintext input file")
    ap.add_argument("--file", action="append", default=[],
                     help="invoice/payment image (png/jpg) or PDF (text-extracted)")
    ap.add_argument("--out", default=None,
                     help="where to write facts.json (default: alongside the first input)")
    ap.add_argument("--model", default="small")
    a = ap.parse_args()

    if not a.text and not a.file:
        die("give at least one --text or --file input")

    print(f"  [{NODE_NAME}] provider={llm_call.provider_name()} model={llm_call.model_id(a.model)}")
    try:
        facts, notes, meta = extract(a.text, a.file, model=a.model)
    except LLMError as e:
        die(str(e))

    out = {
        "facts": facts,
        "extraction_notes": notes,
        "_meta": {
            "node": "1_extract",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "inputs": a.text + a.file,
            **meta,
        },
    }

    first_input = (a.text + a.file)[0]
    out_path = a.out or os.path.join(os.path.dirname(os.path.abspath(first_input)), "facts.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    try:
        shown_path = os.path.relpath(out_path, HERE)
    except ValueError:
        shown_path = out_path  # different drive than HERE on Windows -- relpath can't express it
    print(f"\n  {len(facts)} field(s) extracted -> {shown_path}\n")
    for k, v in facts.items():
        print(f"    {k:<32} {str(v.get('value')):<26} [{v.get('confidence')}]")
    if notes:
        print("\n  extraction_notes:")
        for n in notes:
            print(f"    - {n}")
    print()


if __name__ == "__main__":
    main()
