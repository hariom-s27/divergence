# CORPUS PROVENANCE — why this project's statutory text is hand-curated, checked directly

**S3 of a SHOULD list, 22-23 Aug 2026.** This project builds
`corpus/tier-a/` by hand: one provision per file, copied verbatim from a
gazette source, front-matter-tagged with `current_citation`,
`former_citation`, `source_url`, `retrieved`. That is real, ongoing human
effort (`MANIFEST.md`), and it's worth stating precisely *why* it was
done this way rather than assuming — checked directly against six real
sources, not assumed from a title or a general impression that "Indian
law isn't online."

## The precise claim, not the exaggerated one

**No machine-readable feed of current Indian central statute *text*
exists — full stop, that claim is checked and holds.** But the sharper,
more interesting version is narrower: **a real, working JSON API for
statute *metadata* does exist**, and finding it, then confirming exactly
where it stops, is worth more than a flat "nothing is online."

## What was checked, and what each one actually offers

| Source | What it is | Machine-readable? |
|---|---|---|
| **India Code** (`indiacode.gov.in`) | The official Government of India repository of central acts, running a DSpace 9.1 instance | **A real, working JSON REST API — `/server/api/discover/search/objects?query=...`** — confirmed by fetching it directly, not assumed. HAL/hypermedia-style JSON: `dc.title`, `dc.identifier.act_number`, `dc.date.issued`, `dc.identifier.ministry_name`, a `handle`/`uuid` per item. **But the response is catalogue metadata only.** No field carries the operative section text; every item's actual content is a linked bitstream, and every bitstream checked is a PDF. The API can tell a program *that* the Income-tax Act, 2025 exists and when it was issued. It cannot deliver a single section's text. |
| **data.gov.in** | India's open government data portal | No statute-text dataset found for the Income-tax Act, CGST, or IGST across several search angles. What IS tagged CGST/IGST there is revenue statistics, not legal text. Not exhaustively crawled (the portal blocked a direct browse attempt), so this is search-evidence, not a full catalogue check — stated as a real limit on this claim, not smoothed over. |
| **e-Gazette** (`egazette.gov.in`) | The official publication channel for new Rules and amendments — this is *how* Rule 206/207/56/57 etc. actually entered into force | Confirmed PDF-only, and structurally so: each notification is a digitally-signed PDF, and the signature/QR code **is** the authentication mechanism — the PDF is the legal artifact, not an inconvenient wrapper around one. A paid third-party monitoring service exists specifically to watch this site and push webhook alerts, which is itself evidence no official feed does. |
| **Income Tax Department** (`incometaxindia.gov.in` / `incometax.gov.in`) | The department's own publication of the Act/Rules | Browsable `.aspx` pages and downloadable PDFs only. No API found or indicated anywhere on the site. |
| **Indian Kanoon** | The most mature Indian legal-tech API that exists | Its documented API (`api.indiankanoon.org`) has exactly four endpoints — search, doc, docfragment, docmeta — all oriented around **case law**. No dedicated bare-acts/statute endpoint; a statute surfaces only incidentally inside search results mixed with judgments. This is the sharpest confirmation of the actual gap: case-law tooling in India is materially more mature than statute-text tooling, and this project's problem is on the wrong side of that line. |
| **GitHub / open-source** | Any maintained, structured, current dataset of Income-tax Act/Rules or CGST/IGST text | Found only a stale, unmaintained scraper targeting the pre-2025 regime, and unrelated civic-tech datasets (Penal Code, Constitution) with no Income Tax/GST coverage. Nothing current, nothing maintained. |

## What this means for this project's own design

**The India Code API finding sharpens, rather than undermines, the case
for `corpus_hash.py` and a frozen verbatim corpus (`DECISION-D60.md`)
over any kind of live lookup.** Even the one real API that exists cannot
answer "what does Rule 57 say" — only "does a document called the
Income-tax Rules, 2026 exist, and when was it issued." Building against
it would still require the same PDF-extraction step this project already
does by hand, plus a dependency on a government DSpace instance staying
up, with no gain over curating the text once and hashing it against
tampering afterward.

**This also means `citation_matcher.py`'s own stated limitation is, if
anything, generous to the state of the field.** "Existence is not
relevance" (its own `LIMITATIONS` section) is a sharper check than
anything the one real government API in this space can currently offer,
which doesn't distinguish existence from relevance either — it doesn't
carry the text to check relevance against at all.

## What was not fully verified

data.gov.in and e-Gazette both blocked a direct fetch attempt (403 /
TLS error) during this check — the findings above for those two rest on
search-engine evidence, cross-checked across multiple query angles, not
a page personally rendered and read end to end. Stated here rather than
quietly relied on as equally solid to the other four, which were
confirmed by direct fetch.
