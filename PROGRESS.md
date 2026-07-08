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

## Phase 2 — Raw harvest / import  🟡 IN PROGRESS (core harvest DONE 2026-07-08)
`tools/harvest.py` (idempotent, resumable). **403 artifacts in `raw/`** — full
core + labels + comments + issue↔PR timeline refs. 300 issues / 103 PRs; 296
closed / 107 open; **343 self + 60 maintainer-authored**; 0 fetch errors (2
cpython timeline hiccups retried clean after making sub-fetches non-fatal).
Coverage in `sources/harvest_coverage.json`. Enumeration matched refined counts
(cpython 175, pypy 31, …); cext-JSON ingest added the maintainer-authored ones
(Pillow 0→24, zope 0→9, h5py 16→25, bottleneck 15→24). Labels: type-crash 133,
fusil-fuzzer 8, topic-JIT 34.

**Still to do in Phase 2 (long-tail + enrichment):**
- [ ] **Gist-cite sub-pass:** the 75 upstream issues citing a `gist.github.com/
      devdanzin` gist → harvest any not already in `raw/` (maintainer-filed +
      untagged finds). Enumerate the 285 gists → per-id issue search.
- [ ] **cext communicated-only extensions** (astropy, cffi, cvxopt, isal,
      ml-dtypes, msgspec, mypyc, nanobind, pybind, pyerfa, pymongo, wrapt,
      awkward-cpp): confirm 0 filed (enum returned 0) or catch late filings.
- [ ] **Reconcile the ~30 no-ref crash dirs** + drafts staging.
- [ ] **Verify #146443 vs #146124** (cpython-review PR) during classify.
- [ ] Old bpo / ajaksu2 long-tail (Phase-3-adjacent).

## Open decisions (block Phase 3, not Phase 2) — SCOPING_REPORT §5 + §10
- Own-repo (1471) EXCLUDE? OTHER_OSS (120) EXCLUDE? pypy/simplejson → `manual`?
- `ajaksu2` long-tail method (not `author:`-searchable). Unit framing for deck.
- Separate "unfiled findings" headline?
