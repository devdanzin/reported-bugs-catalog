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

Pipeline: **classify.py → group.py → enrich.py** (enrich adds synthetic records
for catalog bugs with no GitHub artifact). Re-run all three after any edit.

**Bug counts (excl. 20 umbrella containers) = 442 total:** **fusil 152** · cext-review
135 · **cpython-review 55** · lafleur 34 · ft-review 26 · manual 26 · cereggii 14.
(fusil 131 artifact + 22 OOM synthetic; crtk 44 artifact + 13 synthetic.)
filed_by: self 297 · other 114 · self+maintainer 16.

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

**Remaining Phase 3:**
- [ ] **Review queue: 27 bugs** (`sources/review_queue.md`) — untagged CPython
      artifacts needing user tool sign-off (12 fusil-guess / 6 lafleur-guess /
      9 manual-guess; mostly PyREPL work vs fusil crashes vs JIT).
- [ ] Findings rollup (umbrella bodies + OOM 37 + cext 690) → the *findings* number;
      **gist-comb for the reproduced-count** (per user — 575 may = reproduced).
- [ ] Then Phase 4 index (catalog.json + INDEX.md).

## Open decisions (block Phase 3, not Phase 2) — SCOPING_REPORT §5 + §10
- Own-repo (1471) EXCLUDE? OTHER_OSS (120) EXCLUDE? pypy/simplejson → `manual`?
- `ajaksu2` long-tail method (not `author:`-searchable). Unit framing for deck.
- Separate "unfiled findings" headline?
