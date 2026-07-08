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

## Phase 2 — Raw harvest / import  ← NEXT
Worklist in SCOPING_REPORT §7. Highlights: import 139 cext JSON + refresh
labels/state; per-repo harvest (beat the 1000-cap); OOM 15 issues + umbrella +
gists; maintainer-filed + gist-id sub-pass; verify **#146443 vs #146124**;
reconcile the ~30 no-ref crash dirs vs GitHub live.

## Open decisions (block Phase 3, not Phase 2) — SCOPING_REPORT §5 + §10
- Own-repo (1471) EXCLUDE? OTHER_OSS (120) EXCLUDE? pypy/simplejson → `manual`?
- `ajaksu2` long-tail method (not `author:`-searchable). Unit framing for deck.
- Separate "unfiled findings" headline?
