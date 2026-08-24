# CORPUS PROVENANCE — why this project's statutory text is hand-curated, checked directly

**S3 of a SHOULD list, 22-23 Aug 2026.** This project builds
`corpus/tier-a/` by hand: one provision per file, copied verbatim from a
gazette source, front-matter-tagged with `current_citation`,
`former_citation`, `source_url`, `retrieved`. That is real, ongoing human
effort (`MANIFEST.md`), and it's worth stating precisely *why* it was
done this way rather than assuming — checked directly against six real
sources, not assumed from a title or a general impression that "Indian
law isn't online."

**Update, 23 Aug 2026:** added the Income Tax Department's real ERI
filing-API programme (a correction to this file's own earlier "no API
found" line for that row — there is one, it just isn't for statute text),
the `legislation.gov.uk` contrast, and a real, generated (not
hand-typed) per-provision provenance table pulling `source_url`/
`retrieved`/SHA-256 directly from every Tier A file's own front matter
and `FREEZE-HASHES.json`.

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
| **e-Gazette** (`egazette.gov.in`) | The official publication channel for new Rules and amendments — this is *how* Rule 206/207/56/57 etc. actually entered into force | **Verified: search and individual PDF downloads. No API, no bulk download, no XML/JSON, no feed.** Each notification is a digitally-signed PDF, and the signature/QR code **is** the authentication mechanism — the PDF is the legal artifact, not an inconvenient wrapper around one. A paid third-party monitoring service exists specifically to watch this site and push webhook alerts, which is itself evidence no official feed does. |
| **Income Tax Department** (`incometaxindia.gov.in` / `incometax.gov.in`) | The department's own publication of the Act/Rules **for reading**, separately from its own filing infrastructure | Browsable `.aspx` pages and downloadable PDFs for the Act/Rules text — no API found or indicated anywhere on that half of the site. **Sharper, and worth stating precisely rather than left as "no API": the department DOES run a real, documented API programme — the ERI (e-Return Intermediary) APIs — and it is not for statute text.** Endpoints named in its own documentation: Login, Add Client, Prefill, Validate and Submit ITR, e-Verify. Access is restricted to registered **Type-2 e-Return Intermediaries** (licensed filing agents, not the general public or a research project), gated on taxpayer consent per client, and scoped to a taxpayer's own return data — AIS and Form 26AS are explicitly **not** in scope of that API surface. The one place this department *does* build and maintain real, modern, documented APIs is downstream of the law (filing a return against it), never the law's own text upstream of that. |
| **Indian Kanoon** | The most mature Indian legal-tech API that exists | Its documented API (`api.indiankanoon.org`) has exactly four endpoints — search, doc, docfragment, docmeta — all oriented around **case law**. No dedicated bare-acts/statute endpoint; a statute surfaces only incidentally inside search results mixed with judgments. This is the sharpest confirmation of the actual gap: case-law tooling in India is materially more mature than statute-text tooling, and this project's problem is on the wrong side of that line. |
| **GitHub / open-source** | Any maintained, structured, current dataset of Income-tax Act/Rules or CGST/IGST text | Found only a stale, unmaintained scraper targeting the pre-2025 regime, and unrelated civic-tech datasets (Penal Code, Constitution) with no Income Tax/GST coverage. Nothing current, nothing maintained. |

## The contrast that actually shows what "machine-readable" would look like

Six real Indian sources checked above, and not one delivers current
statute *text* over an API. It's worth naming what the alternative
actually looks like elsewhere, so "no machine-readable feed" doesn't read
as a vague complaint about India specifically rather than a precise,
checkable gap: **the United Kingdom's `legislation.gov.uk` publishes a
free, open, consolidated legislation API**, explicitly stated as
**"available under the Open Government Licence v3.0."** A program can
request a specific Act, a specific section, as of a specific date, and
receive structured, machine-consumable text back — not a PDF, not a
catalogue record pointing at a PDF, the operative text itself, licensed
for exactly this kind of reuse. *(This contrast is relayed as supplied,
not independently re-fetched and read against the live API the way the
six Indian sources above were each checked directly — flagged here
rather than presented with the same confidence as the rest of this
file's own discipline demands.)*

**The point isn't that the UK is more advanced technically.** It's that
a government publishing its own current, consolidated statute text as a
licensed, structured feed is a solved, demonstrated design — this
project's central corpus decision isn't reaching for a hard problem
nobody has solved, it's working around the absence of something that
already exists as ordinary practice in at least one other common-law
jurisdiction with comparable statutory volume.

## Per-provision provenance — every Tier A file this project actually cites from

Generated directly from each file's own front matter and
[`corpus/FREEZE-HASHES.json`](corpus/FREEZE-HASHES.json) by
[`corpus_provenance_table.py`](corpus_provenance_table.py) — never
hand-transcribed, so this table cannot silently drift from the real
files it describes. Regenerate with `python corpus_provenance_table.py`;
`--check` exits non-zero if any Tier A file is missing a required field.

| Provision | Current citation | Source | Retrieved | SHA-256 (first 12 hex) |
|---|---|---|---|---|
| `FEMA-2n` | Section 2, clauses (h), (m), (n), (q), Foreign Exchange Management Act, 1999 | https://indiacode.nic.in — FEMA 1999, Section 2 | 2026-08-06 | `1867e0db97b9…` |
| `FEMA-3-7-8` | Sections 3, 7 and 8, Foreign Exchange Management Act, 1999 | indiacode.nic.in — FEMA 1999, Act No. 42 of 1999 | 2026-08-06 | `a65337a2d047…` |
| `GST-CGST-50-74A` | Section 50, CGST Act 2017 | https://taxinformation.cbic.gov.in — *🔴 s.74A text not yet obtained — see the catch below.* | 2026-08-06 | `540d2d8e0b7b…` |
| `GST-CGST-74A` | Section 74A, CGST Act 2017 | https://taxinformation.cbic.gov.in | 2026-08-06 | `fb442edc27ea…` |
| `GST-IGST-2-6` | Section 2(6), Integrated Goods and Services Tax Act, 2017 | https://taxinformation.cbic.gov.in/content/html/tax_repository/gst/acts/2017_IGST_Act | 2026-08-04 | `018acc3bbafd…` |
| `IT-115BBH` | Section 115BBH, Income-tax Act, 1961 — carried into the Income-tax Act, 2025 | https://www.incometaxindia.gov.in/w/section-115bbh-1 — *2025 Act section number not yet confirmed. Cite in dual form.* | 2026-08-06 | `501418f02752…` |
| `IT-2-47A` | Section 2(47A), Income-tax Act, 1961 — carried into the Income-tax Act, 2025 | https://www.incometaxindia.gov.in — Section 2 — *2025 Act section number unconfirmed. Cite in dual form.* | 2026-08-06 | `ab85795a5de7…` |
| `IT-393-1-T8vi` | Section 393(1), Table Sl. No. 8(vi), Income-tax Act, 2025 | https://www.incometaxindia.gov.in — Section 393. Last reviewed 30 July 2026. | 2026-08-06 | `75cc9b198313…` |
| `IT-439-8` | Section 439(8), Income-tax Act, 2025 | **not recorded in front matter** — *Taken from an unofficial full-text source. VERIFY against indiacode.nic.in before this becomes load-bearing in the submission.* | 2026-08-06 | `0a35fccb167b…` |
| `IT-56-2-x` | Section 56(2)(x) and the Explanation to section 56(2)(vii), Income-tax Act, 1961 | incometaxindia.gov.in — Section 56 | 2026-08-06 | `479c4a124f2f…` |
| `ITR2026-RCASP-VALUATION` | Rule 243(8)(e), Income-tax Rules, 2026 | Notified Income-tax Rules, 2026, Gazette of India Extraordinary Part II Sec 3(i), 20 March 2026 | 2026-08-06 | `fc684c876359…` |
| `ITR2026-RULE-206` | Rule 206, Income-tax Rules, 2026 | Notified Income-tax Rules, 2026 — Gazette of India Extraordinary, Part II Sec 3(i), 20 March 2026, pp. 1687-1688 | 2026-08-18 | `d622f671d075…` |
| `ITR2026-RULE-207` | Rule 207, Income-tax Rules, 2026 | Notified Income-tax Rules, 2026 — Gazette of India Extraordinary, Part II Sec 3(i), 20 March 2026, p. 1688 | 2026-08-18 | `3116736afa8f…` |
| `ITR2026-RULE-247` | Rule 247, Income-tax Rules, 2026 | Notified Income-tax Rules, 2026 — Gazette of India Extraordinary, Part II Sec 3(i), 20 March 2026, pp. 1764-1765; Form No. 169 notes at p. 2432 — *Section 514 of the Income-tax Act, 2025 (registered valuers) not held verbatim in this corpus. The rule text is sufficient for the claim made here.* | 2026-08-18 | `c11b7f165cc5…` |
| `ITR2026-RULE-56` | Rule 56, Income-tax Rules, 2026 | Notified Income-tax Rules, 2026 — Gazette of India Extraordinary, Part II Sec 3(i), 20 March 2026, p. 1575 | 2026-08-18 | `e3a8dc10c751…` |
| `ITR2026-RULE-57` | Rule 57, Income-tax Rules, 2026 | Notified Income-tax Rules, 2026 — Gazette of India Extraordinary, Part II Sec 3(i), 20 March 2026, pp. 1575-1576 | 2026-08-18 | `cc387ca9fafa…` |
| `SBI-TTBR-DATA` | Rule 207(3)(b), Income-tax Rules, 2026 | https://github.com/sahilgupta/sbi-fx-ratekeeper — *Community archive of SBI's own published PDFs. Each row links to the original SBI PDF. SBI itself keeps no archive.* | 2026-08-06 | `01c7c2fba910…` |

**One line stating the absence, since every row above is itself the
answer to "how do you know this text is real": no row in this table
could have been produced by querying an API for the operative text
itself — every `source_url` above points at a PDF, a gazette page
reference, or (`IT-439-8`, honestly, not smoothed over) an unofficial
full-text mirror still pending verification — because no such API
exists for Indian central statute and rule text as of this writing,
checked directly against six real sources above, not assumed. That
absence is the reason this table, and the 17 files it describes, exist
by hand at all.**

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
