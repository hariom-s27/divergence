# D78 — versioned statute records: schema, validator and exact version lookup

Date: 13 November 2026 (Part A); implementation details filled {{date}}

Status: adopted for the benchmark corpus. The frozen hackathon corpus (corpus/, D41–D77) is unchanged.

## Why

The benchmark asks which law applied at a point in time. The Income-tax Act, 2025 replaced the Income-tax Act, 1961 from 1 April 2026. The 1961 Act still governs earlier tax years through the savings in s.536. Both Acts keep being amended, sometimes backwards in time. A record that stores only "the text" with one date cannot answer "which version applies?". This decision fixes the record shape before any law text is ingested, so version accuracy can be measured by code.

## What a record is

One section (or rule, notification or circular) of one Act, in one version. Metadata is a JSON file in statutes/records/<act>/; the body is a UTF-8, LF-only .txt file. Record IDs are built by code: source_kind:act:unit:vN (for example act:1961:s194S:v1). File names replace : with __. Offsets into a body are Unicode code points, half-open [start, end), on the text exactly as stored, with no normalisation.

## Three clocks, kept apart

1. In force (in_force_from, in_force_to): when the text was legally in force.
2. Applicability (applies_from_tax_year, applies_to_tax_year, "YYYY-YY"): which tax years it governs. For the 1961 Act after repeal, the text is no longer in force but still applies to tax years up to 2025-26 (status repealed_saved).
3. Knowledge (enacted_on, amended_by[].enacted_on, retrospective_from): when the law giving this text was made. A retrospective amendment changes what an earlier year's text is now taken to be. The lookup can ask for the law "as known on" a date.

This separation follows the legal-informatics distinction between a norm's time in force, efficacy and application (Palmirani et al., Akoma Ntoso / LegalRuleML literature; SECONDARY). It also follows the "prospective" and "outstanding effects" notions used by legislation.gov.uk. INFERENCE: the mapping of our fields onto those terms is ours.

## States

in_force, repealed_saved, never_operative (enacted but never operative, e.g. s.536 as originally enacted, per DR-1), prospective (enacted, commencement not reached or not notified), omitted. A retrospective amendment is a new version with retrospective_from earlier than enacted_on and a non-empty amended_by. Circulars and notifications that change how a section works without changing its text are separate records, linked by modified_by. Known amendments not yet applied to the stored text are listed in outstanding_effects, with text_current_as_of.

## Exact lookup

lookup(act, unit, as_of=date | tax_year="YYYY-YY", as_known_on=None) returns FOUND (one record), NO_APPLICABLE_VERSION or AMBIGUOUS, with reasons (midyear_effect, overlap, outstanding_effect, unknown_enactment_date, never_operative, prospective, no_version_covers_point). It never returns the nearest version. A later version replaces an earlier one only through an explicit supersedes link, never by date guessing. A change that takes effect inside a tax year (not on 1 April) makes a tax-year lookup AMBIGUOUS. That is the known limit of tax-year granularity: the code refuses instead of guessing. These outcomes feed the benchmark's abstention reasons later; they are not tax advice.

## Validator

python -m divergence.statute_validate checks 16 rules (V01–V16): schema and enums; ID and file name built from the fields; unique IDs; date and tax-year order; 2025-Act applicability from 2026-27 (an in-force date before 1 April 2026 is only a warning, because s.1(3) begins "Save as otherwise provided in this Act"); state consistency; retrospective rules; links resolve; body hash, length, encoding and line endings; source acknowledgement present; counterpart source labelled; local-only bodies not tracked by git; an original note on public verbatim Act records; test fixtures never inside the real folder. --freeze / --verify keep a hash manifest of the folder once real records exist.

## Storage and copyright (decided: S3)

The schema supports local_only (the body stays in the git-ignored statutes/_local_text/; the public repo holds metadata, offsets and hashes) and public_verbatim. While building, bodies stay local. The public form is decided at release, after a legal check.

The Copyright Act, 1957, s.52(1)(q) (India Code, https://www.indiacode.nic.in/bitstream/123456789/1367/1/a195714.pdf, accessed 12 Nov 2026; LEGAL-PRIMARY, via R02) says that the following do not infringe copyright:

> (i) any matter which has been published in any Official Gazette except an Act of a Legislature;
>
> (ii) any Act of a Legislature subject to the condition that such Act is reproduced or published together with any commentary thereon or any other original matter;

No judgment found defines "commentary thereon or any other original matter". Whether structured metadata counts is untested (R02). The validator therefore requires an original_note on public verbatim Act records. This is a safeguard, not a claim that it satisfies (q)(ii).

The Income Tax Department's Copyright Policy (https://www.incometaxindia.gov.in/copyright-policy, accessed 12 Nov 2026) says material "may be reproduced free of charge in any format or media without specific permission", provided it is reproduced accurately and "the source must be prominently acknowledged". Every record carries source_acknowledgement. The Department's Disclaimer says commercial use of web contents needs its written permission.

Open questions before any public release (for a lawyer): does metadata or a short note count as "original matter"; is the consolidated "as amended" text on incometaxindia.gov.in "an Act of a Legislature"; which Rules and notifications were Gazette-published; how the Copyright Policy and the Disclaimer interact for public, possibly commercial, re-use.

## Alternatives considered

- One validity interval: rejected; it cannot express a repealed Act that still applies to past years.
- Storing a mid-year flag: rejected; code computes it from the dates, so it cannot contradict them.
- Nearest-version lookup: rejected; a wrong version presented as right is the failure this project measures.
- Putting the new records inside the frozen corpus/: rejected; that would change a frozen item.
- Full bitemporal history of every consolidation: too heavy now; enacted_on + as_known_on cover retrospective amendments.

## Evidence

- Implementation (filled in Part C): commit {{commit}}; tests {{n_new}} new, {{n_total}} total passing; files divergence/statute_schema.py, statute_validate.py, statute_lookup.py, statutes/schema/statute_record.schema.json.
- Fixtures are invented (FAKE FIXTURE - NOT LAW), {{n_fixtures}} records in tests/fixtures/statutes/.

## Where it fails / what is not done

- No real law text is ingested yet (next step, P09). The schema has only been exercised on invented records.
- Tax-year granularity cannot express a mid-year change. Such lookups return AMBIGUOUS by design.
- as_known_on is only as good as the enacted_on dates recorded at ingest.
- The counterpart mapping (1961 ↔ 2025) needs the official CBDT table; until then a counterpart marked SECONDARY is a lead, not a fact.
- The public release form waits for the legal check above.
