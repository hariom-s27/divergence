# The actual law text

Three folders, same provisions, different purposes:

- **`tier-a/`** — the full, citable corpus. One provision per file, each
  carrying its current citation, former citation, tax year, gazette page,
  and any open `known_limitation`. This is what `citation_matcher.py`
  checks every citation against.
- **`verbatim/`** — the same files, cut down to statutory text only,
  between `<!-- VERBATIM-START/END -->` markers. **This is the only text
  ever sent to a model** — no commentary, no analysis, nothing this
  project wrote itself (decision D31 — see `ITERATION-STORY.md` item 1 for
  why that distinction exists and what happened the one time it wasn't
  followed: ~40% of an earlier corpus turned out to be this project's own
  analysis, not statutory text).
- **`tier-b/`** — background context only (a rate-methodology document, a
  general commentary). Never citable as authority, never sent to a model
  as if it were law.

**Start with [`MANIFEST.md`](MANIFEST.md)** — it states the scope boundary
this corpus was built against, what was deliberately not checked, and the
current status of every file. A claim anywhere in this project that "no
rule prescribes X" means specifically *"no rule among the provisions in
this manifest prescribes X,"* not a claim about all of Indian law — the
manifest is what makes that boundary checkable rather than assumed.
