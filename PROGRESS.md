# PROGRESS

Tracking file for the reported-bugs catalog. One block per phase (see `PLAN.md`).

## Phase 0 — Bootstrap
- [x] Directory + `PLAN.md` present.
- [x] `sources/` populated (scoping raw data).
- [x] `SCOPING_REPORT.md` + `PROGRESS.md` written.
- [x] Local `git init` + initial commit (versioning the scoping pass).
- [ ] **Create PUBLIC GitHub repo `devdanzin/reported-bugs-catalog` + push** —
      DEFERRED (outward-facing; awaiting explicit user go-ahead).
- [ ] `README.md`, `sources.yaml`, `tools/` stubs — deferred to Phase 2 kickoff.

## Phase 1 — Scoping pass  ✅ DONE (2026-07-08)
Deliverable: **`SCOPING_REPORT.md`**. Raw data in `sources/`.

Completed:
- [x] Ingest-preview cext/ft registry + 148 JSON → `cext_registry_preview.json`
      (139 real artifacts / 138 unique, 24 repos, 79 ours / 60 maintainer).
- [x] Ingest-preview cpython-oom-findings 43 meta.json → `oom_findings_preview.json`
      (37 unique bugs, 15 filed, umbrella #151763).
- [x] Local inventory — reports/ trees → `local_inventory_reports.json`
      (milestone_6: ~690 FIX / 106+ filed; ft: 13+ filed; pyo3/rust 0-filed;
      8-item unfiled backlog).
- [x] Local inventory — crashers + memory → `local_inventory_crashers.json`
      (fusil/lafleur/cereggii filed refs; 6 drafts; ~30 no-ref crash dirs).
- [x] Gist inventory → `gist_list.json` + `gist_reportish.json` (285 total,
      161 pub / 124 sec; 35 OOM report-gists; ~201 report-ish).
- [x] GitHub inventory → `gh_author_issues.json` (1078 true), `gh_author_prs.json`
      (907), `gh_mentions.json` (715), consolidated `github_inventory.json`
      (1907 → 316 TARGET / 120 OTHER_OSS / 1471 OWN).
- [x] Cross-reference / coverage map (SCOPING_REPORT §6) + own-vs-external split.
- [x] WebFetch 3 discuss threads (SCOPING_REPORT §9).
- [x] **Refined counts pass (2026-07-08, user-guided)** → `refined_counts.json`.
      `total_count` searches (uncapped) + `-owner:devdanzin` + per-tool keyword.
      CPython = 157i+18p (not 129); fusil 113i / lafleur 27i / cext-rt 63i+16p /
      ft-rt 7i+3p / crtk 17i. In-scope ≈ 430 filed artifacts. pypy→fusil,
      simplejson→review-toolkit (both corrected from "manual"). 75 upstream
      issues cite a devdanzin gist (Phase-2 vector). §1/§2/§5/§6/§7 updated.

## Phase 2 — Raw harvest / import  ✅ DONE (2026-07-08)
`tools/harvest.py` (idempotent, resumable). **452 artifacts in `raw/`** across
**34 repos** — full core + labels + comments + issue↔PR timeline refs. 338
issues / 114 PRs; 332 closed / 120 open; **344 self + 108 maintainer-authored**;
0 fetch errors. Coverage in `sources/harvest_coverage.json`. Enumeration matched
refined counts (cpython 175, pypy 31, …); cext-JSON ingest added maintainer
artifacts (Pillow 0→24, zope 0→9, h5py 16→25). Labels: type-crash 133,
fusil-fuzzer 8, topic-JIT 34.

Sub-passes:
- [x] **Gist-cite sub-pass** — 89 artifacts cite a `gist.github.com/devdanzin`
      gist; 48 were new → harvested. **Grew maintainer-filed 60→108**: +26
      cpython fix-PRs/issues citing OOM gists, **+wrapt 15 (all GrahamDumpleton)**,
      +pyerfa 1, +pola-rs/polars 1, +greenlet/multidict/numpy extras.
- [x] **Communicated-only extensions** resolved: **10 confirmed 0-filed**
      (astropy, cffi, cvxopt, isal, ml_dtypes, msgspec, nanobind, pybind11,
      pymongo, awkward). 3 were NOT 0-filed → harvested: **wrapt 15** (maintainer),
      **pyerfa 1** (maintainer), **mypyc = python/mypy#20585** (devdanzin, mypyc
      assertion crash).
- [x] **Crashers reconciled** — 59 dirs, only 8 have a report/finding; 51 are
      bare historical repros (expected unfiled, per user). Of the 8: 4 cereggii +
      wsgiref + fleet8 already filed & captured; **h5py_get_name + hdf5_property
      _list = the only genuine unfiled drafts.**
- [x] **Drafts staged** → `drafts/` (12 stubs + INDEX; found-but-not-filed,
      excluded from counts): h5py/HDF5/astropy/coveragepy/numpy + review-toolkit
      backlog (couchbase/frozendict/uvloop/ijson/_decimal/igraph) + itertools draft.

**Deferred to Phase 3 (classify-adjacent):**
- [ ] Verify #146443 vs #146124 (cpython-review PR).
- [ ] Old bpo / ajaksu2 long-tail.

## Phase 3 — Classify / dedup / reconcile  🟡 IN PROGRESS (2026-07-08)
`tools/classify.py` (per-artifact tool/mode/filed_by/links + evidence OVERRIDES +
OOM-catalog overrides) → `sources/classification.json`; `tools/group.py`
(union-find on issue↔PR links, umbrella-protected, tool propagation) →
**`bugs/<id>.json` (410 bug clusters)** from 461 artifacts (51 PRs merged).

Pipeline: **harvest.py → harvest_fixprs.py → classify.py → group.py → enrich.py**
(fixprs backfills fix/backport PRs; enrich adds synthetic records for catalog bugs
with no GitHub artifact). Re-run classify→group→enrich after any edit.

**FIX-PR BACKFILL (user-flagged gap):** the PRs that closed our issues were
authored by the fixer (not devdanzin) + cite no gist, so they weren't harvested.
Backfilled **425 fix/backport PRs** (raw 479→904) from issue-timeline cross-refs.
Merging rewritten to use precise **fix_links** (PR title `gh-<issue>` + body
`fixes #N`), NOT bare `#N` mentions — this fixed bad merges (PR #142529, cited by
16 sibling issues, had chain-merged them; #137728/#137762 lafleur wrongly merged).
**0 multi-issue non-umbrella clusters now.** All 32 #146102 sub-issues have their
fix-PRs. **491 PRs in clusters = 334 distinct fixes + 157 backports** (backports =
same bug, flagged `n_backports`).

**REVIEW QUEUE RESOLVED (user, 2026-07-08):** 26 of 27 → manual, only #130999 → fusil
(locked as overrides). User note: found many bugs *while using* the tools, not *with*
them, or while minimizing other repros. needs-review now 0.

**DROPPED-PRs → RECOVERED (user-flagged):** the 55 unmerged backfill PRs weren't
dropped — now attached to their origin bug. A batch-fix PR (fixes ≥2 of our issues,
e.g. cereggii#80→#78+#79) is recorded in each bug's `shared_fix_prs`; a cross-ref
whose fix couldn't be machine-confirmed (mostly non-CPython repos that don't use the
`gh-<issue>`/`fixes #N` convention — multidict#1317, scipy#24752, numpy#29368,
protobuf#27570) goes in `related_prs`. **Accounting: 425 backfilled = 370 merged fixes
+ 55 shared/related + 0 unaccounted (nothing lost).**

**Bug counts (filed-artifact + synthetic), USER-VALIDATED:** cext-review 149 · **fusil
142** (120+22 OOM) · **cpython-review 57** (44+13) · **manual 50** · ft-review 34 ·
lafleur 28 · cereggii 15. filed_by (clusters): **self 180 · self+maintainer 146 ·
maintainer 114**. PRs: 490 in-cluster (333 fixes + 157 backports) + 4 shared + 83 related.

**#146102 clump captured (user-flagged):** the cpython-review umbrella lists **47
select bugs**; harvested its 18 missing sub-issues/PRs (again mostly
contributor-authored: aisk 9, lpyu001 5, A0su 4, **vstinner 2**…), wired
`sources/crtk_umbrella.json` as an authoritative override → **crtk 17 → 55 bugs**.
#146103 (companion "reports" umbrella) adds no new issues — 59 review-report gists
(findings source) + points back to #146102.

**Mid-phase fixes:** (a) harvested 9 missing OOM issues by number — **12 of 15 filed
OOM issues were authored by CONTRIBUTORS** (sobolevn ×3, prakashsellathurai…) from
umbrella #151763, not devdanzin; added OOM-catalog overrides so they tag fusil/oom.
(b) dropped the `>=4 links` umbrella heuristic (46 false positives) → 20 real umbrellas.
**Contributor/maintainer impact: 113 bugs have a non-devdanzin filer** (radarhere 16,
neutrinoceros 16, GrahamDumpleton 15, sobolevn 6, hugovk 5…).

**Phase 3 sub-tasks:**
- [x] Review queue resolved (user): 26/27 manual, #130999 fusil.
- [x] **Findings rollup DONE → `FINDINGS.md` + `sources/findings_rollup.json`.**
      Settled what "575/690" is: **cumulative FIX-level findings itemized across
      the per-extension review reports (gisted)** — NOT reproduced (=215+) nor
      filed issues (=106+). Tracked in milestone_report_6 (575 Apr6 → 645 M5 →
      690 M6). Reconstruction cross-check: 115 findings in 12 machine-countable
      reports (~9.6 avg × ~50 ≈ 690). Reports use `### N.` numbered findings;
      formats vary so milestone tally is authoritative. **3-unit totals: 455 bugs
      / 338 issues + 490 PRs (333 fixes + 157 backports) / campaign findings ~690
      cext FIX-level + 4,556+ ft races (per-campaign, never summed).**
- [x] **Ancient bpo (ajaksu2-era) bugs added** — user surfaced 5; found 19
      ajaksu2-*created* cpython issues (vs 589 nosy), 9 real crashes → manual
      (2008, pre-tool), 10 features/junk excluded. `creator = 'ajaksu2'` in body
      is the reporter signal; `sources/bpo_ajaksu2.json` override.

## Phase 4 — Index & numbers  ✅ DONE (2026-07-08)
`tools/index.py` → **`catalog.json` (machine) + `INDEX.md` (human)**. Pipeline is
now `harvest → harvest_fixprs → classify → group → enrich → index`.
**FINAL TOTALS: 464 bugs / 28 external repos / 347 issue-artifacts + 490
PR-artifacts (333 fixes + 157 backports).** By tool: fusil 141, cext-review 138,
manual 59, cpython-review 55, ft-review 29, lafleur 28, cereggii 14. filed_by:
self 180 / self+maintainer 146 / maintainer 114 / none 22 / self+commit 2.
Labels: type-crash 146, interpreter-core 109, topic-JIT 35, topic-free-threading
32, fusil-fuzzer 8. Timeline: 2008=9 (bpo), 2024=83, 2025=84, 2026=250. Top
collaborators (bots excluded): vstinner 28, sobolevn/neutrinoceros/radarhere 16,
GrahamDumpleton 15. Hand-verified sample (OOM-0036, #146080, cereggii-78, #47903)
vs GitHub — correct.

**CATALOG COMPLETE.** Optional follow-ups: Phase 5 refresh (re-run for state
drift), pyo3/rust-ext confirm-0, deck rendering.

## Open decisions (block Phase 3, not Phase 2) — SCOPING_REPORT §5 + §10
- Own-repo (1471) EXCLUDE? OTHER_OSS (120) EXCLUDE? pypy/simplejson → `manual`?
- `ajaksu2` long-tail method (not `author:`-searchable). Unit framing for deck.
- Separate "unfiled findings" headline?
