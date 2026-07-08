# Findings rollup — the three counting units

The catalog counts three distinct units. They are **never summed together** — a
static-analysis *finding*, a deduped *bug*, and a filed *artifact* are different
things, and each campaign's findings are in different units again (FIX-level
findings vs data races vs crashes).

```
FINDINGS  (itemized defects in reports/gists)  ─►  BUGS  (deduped, catalog)  ─►  ARTIFACTS (issues + PRs)
   ~690 cext FIX-level                              455 total                     338 issues + 490 PRs
   4,556+ ft races                                                                 (harvested + backfilled)
```

## What the "575 / ~690" number actually is

It is the **cumulative count of FIX-level findings itemized across the
per-extension review reports** (the reports we gist to maintainers) — *not* a
reproduced count, and *not* the number of filed issues. The campaign tracks it as
a running total in the milestone reports:

| date | FIX-level findings | reproduced from Python | issues filed |
|---|---|---|---|
| 2026-04-06 (Discourse) | **575+** | 155+ | 90 |
| Milestone 5 | ~645 | 195+ | 94+ |
| Milestone 6 (2026-04-22) | **~690** | 215+ | 106+ |

Source: `cext-review-toolkit/reports/analysis_milestone_report_6.md`. Each
per-extension report itemizes findings as numbered sections (`### N.`) tagged
FIX / CONSIDER / POLICY; the milestone sums them cumulatively (deduped across
re-reviews and per-version source trees). Report formats vary, so the milestone
tally — not a re-parse — is authoritative. Cross-check: the 12 machine-countable
reports hold 115 findings (~9.6 avg); ~50 reports × ~14 ≈ 690.

## Campaign findings (authoritative — per campaign, different units)

- **cext-review-toolkit:** **~690 FIX-level findings** (215+ reproduced from
  Python) across **50 extensions**; funnel → **106+ issues filed** → 138 bugs in
  this catalog.
- **ft-review-toolkit:** **4,556+ unique extension data races**, **30+ live
  crashes/hangs** across 18 FT-deep extensions; 2 extensions validated
  FT-production-ready (pyskein, ijson) → 13+ issues → 29 bugs here.
- **fusil / lafleur / cereggii / manual:** each catalog *bug* is itself a distinct
  crash/defect finding, so findings ≈ bugs for these (fusil ~141 incl. the 37-bug
  OOM sub-campaign; lafleur 28 JIT; cereggii 4; manual 50).
- **cpython-review-toolkit:** 47 *select* FIX-level bugs in umbrella #146102, plus
  59 review-report gists in #146103 covering more findings → 55 bugs here.

## Catalog rollup (bugs / artifacts — deduped, what we actually filed)

| tool | bugs | issue-artifacts | PR-artifacts | distinct fixes | backports |
|---|---|---|---|---|---|
| fusil | 141 | 112 | 191 | 107 | 84 |
| cext-review-toolkit | 138 | 90 | 77 | 75 | 1 |
| cpython-review-toolkit | 55 | 40 | 91 | 47 | 44 |
| manual | 59 | 44 | 75 | 53 | 22 |
| ft-review-toolkit | 29 | 23 | 12 | 12 | 0 |
| lafleur | 28 | 28 | 33 | 27 | 6 |
| fusil-plugin-cereggii | 14 | 10 | 13 | 12 | 0 |
| **TOTAL** | **464** | **347** | **490** | **333** | **157** |

*(manual includes 9 ancient bpo-era crash finds reported by ajaksu2=devdanzin,
2008 — pre-tool, no fusil credit; see the timeline in `INDEX.md`.)*

*(PR-artifacts include the backfilled fix/backport PRs; "distinct fixes" excludes
backports. `related_prs` — cross-refs not machine-confirmed as the fix — are held
separately and not counted here.)*

## Headline numbers for the deck (labelled by unit)

- **~464 distinct bugs** found and filed, across **28 external projects**.
- **828 GitHub artifacts** (338 issues + 490 PRs) — 333 distinct fixes + 157 backports.
- **~690 cext FIX-level findings** + **4,556+ FT races** + the fuzzer crashes =
  the *findings* tier (state per campaign; do not sum across units).
- Collaboration: **146 bugs** where devdanzin filed the issue and a *maintainer*
  authored the fix; **114** filed entirely by others from our reports/gists.

Data: `sources/findings_rollup.json`.
