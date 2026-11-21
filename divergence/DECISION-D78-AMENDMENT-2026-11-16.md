# D78 amendment: dates, projection and exact lookup v2

Date: 16 November 2026. Owner-approved P09 C4 design and addendum.
This amends the implementation contract in DECISION-D78.md; the original decision is retained.

## Changes and reasons

- D1: date intervals are half-open [in_force_from, in_force_to); null end is open and null start never covers.
  Reason: VERSION-DATES already stores exclusive ends; adjacent versions must not overlap at a boundary.
- D2: project one record per table key, with numeric version_id and the same unit's v(n-1) supersedes link,
  including gaps and never-operative versions. Reason: the version chain must preserve every known state.
- D3: 1961 rows ending at REPEAL_DAY (2026-04-01), except rows starting that day, become repealed_saved;
  repeal-day rows stay in_force with exclusive end 2026-04-02. Empty state becomes unprinted, with null body,
  body hash and character count; never_operative has null dates, hashed empty body, and an original_note.
  Reason: absence of printed text and zero-length originals are distinct states, not reconstructed text.
- D4/D5: enacted_on is the maximum assent of cumulative same-unit effects with wef <= the raw table start;
  absent effects use the registered Act 30/2025 assent for 2025, null for 1961. Retro moves in_force_from and
  the predecessor end to enacted_on, retaining the raw start as retrospective_from.
  Reason: effective time and what was knowable at enactment are different clocks.
- D6: copy basis_category, strictly parse the basis exception tail, and retain only repeal_day_unsettled and
  corrigendum_open as lookup_flags. Unknown exception IDs/categories are errors.
  Reason: owner applicability choices and unresolved legal issues must remain explicit.
- D7/addendum: amended_by is cumulative (127 items; 53 empty URLs on these tables). kind is the registered
  instrument type (finance_act for all five contributing instruments); optional operation is substitute, insert,
  omit or renumber. URLs are literal registered URLs or empty, never constructed. owner_target changes only the
  clause path and never target_section. Reason: provenance describes the full state and preserves missing evidence.
- D7/addendum: project(vd, effects, sources, mapping, knowledge, fetch_log=None) is pure. Knowledge dates and
  FETCH-LOG are caller arguments; CI supplies synthetic/None knowledge and fetch_log=None, never the local corpus.
  Printed text_current_as_of uses its edition; unprinted uses the latest checked edition; never_operative uses its
  successor's enacted_on. C4-C computes knowledge in process and cross-checks the C2 sheet before writing.
  Reason: local provenance must not become an implicit CI dependency.
- D7: counterpart is present only on 1961 records, using operative_2025; source_url is empty. 194S to 393 is
  CBDT_official with note "official Act PDF, owner eye check"; 115BBH to 194 is SECONDARY, "unverified";
  all other mappings are SECONDARY. ITD editions have gazette_published=no; label-gap sources retain
  source_label_gap notes; storage_mode is local_only and outstanding_effects is empty.
  Reason: source authority, label limitations and publication status must not be overstated.
- D8: CORPUS_CHECKED_THROUGH = 2026-11-15. Evidence: SOURCES.json registry plus MANUAL-SOURCES save dates;
  the owner's web check found only Income-tax Rules amendments after TOLA 2026, outside corpus scope.
  An official eGazette check is pending before the D80 freeze.
  Reason: exact lookup cannot claim coverage beyond the last corpus check.
- D10: REASON_CLASS and reason_class(code) classify every emitted reason; unknown codes raise an error.
  Reason: legal uncertainty, query granularity, corpus limitations and absence of law require different handling.
- D11: V05 requires from < to; V07 allows repealed_saved ends through REPEAL_DAY and applicability through
  2025-26; unprinted requires a dated start (end may be open), null body metadata and no body file. Only
  unprinted allows null body fields. V09's immediate-predecessor rule stays unchanged.
  Reason: validation must enforce the new interval and text-availability contract.
- Guard addendum: statute_guard --code hashes the sorted code-column CSV; --body uses the historical sorted
  body-hash-pair representation and build(write=False). Default/write=True build outputs retain their bytes.
  Reason: code changes must preserve both approved table proposals and extracted bodies. First real body run is C4-C.

## D9 lookup order

1. Select the same source_kind, act and unit. S is as_of or tax-year 1 April; FYb is next 1 April.
2. 1961 tax years starting on/after repeal return after_repeal. 1961 as_of on/after repeal returns the same,
   except exactly repeal day when this unit has a record starting that day. 2025 S before commencement returns
   before_commencement. These edges precede the horizon.
3. S beyond CORPUS_CHECKED_THROUGH returns AMBIGUOUS with beyond_corpus_horizon.
4. At knowledge date K hide enactments after K, retain/mark null enactments, and hide never_operative rows if
   their successor was enacted after K. Preserve hidden rows for the missing-known-text fallback.
5. Nonempty all-never-operative candidates return never_operative; otherwise drop those rows. Prospective
   rows with no commencement retain the existing prospective rule.
6. As-of coverage is effective_start <= S < end, using retrospective_from or in_force_from; tax-year coverage
   uses inclusive owner applicability years, null upper year open.
7. Apply explicit supersession only when the newer covering record's effective start <= S; mark surviving
   unknown enactments when K is supplied.
8. In tax-year mode add midyear_effect for S < effective_start < FYb or S < end < FYb, except charging_ay_rule.
9. Retain outstanding-effects behavior, add unprinted_intermediate for covering unprinted rows, and add flags.
10. If none cover, first try tax-year fallback W=[S,FYb+1 day): an intersecting unprinted row, then an intersecting
    unclear-basis row, each AMBIGUOUS with its reason. Otherwise hidden coverage gives known_text_not_in_corpus;
    S before the unit's earliest dated effective start gives before_coverage; otherwise no_version_covers_point.
11. Multiple candidates give AMBIGUOUS with overlap plus reasons; any reason gives AMBIGUOUS; otherwise FOUND.

## Reason classes

- LEGAL: repeal_day_unsettled, corrigendum_open, overlap, applicability_unclear_row.
- QUERY: midyear_effect.
- CORPUS: unprinted_intermediate, outstanding_effect, unknown_enactment_date, beyond_corpus_horizon,
  before_coverage, known_text_not_in_corpus.
- NO_LAW: never_operative, prospective, before_commencement, after_repeal, no_version_covers_point.

## What this does not do; where it fails

No real records or law bodies are generated in C4-B; no public release, freeze, source-table change, or body
reconstruction is authorized here. Original D78 is retained. Knowledge/provenance can be incomplete in a test-only
projection and must be supplied/validated before persistence in C4-C.

The corpus horizon limits date coverage. Section granularity cannot resolve clause-specific applicability.
Label gaps remain source defects. ITD and Gazette differences exist; consolidated editions are not presumed to
be Gazette text. Missing instrument URLs and unprinted states remain visible limitations.
