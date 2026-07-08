# reported-bugs-catalog

A versioned, offline-analyzable catalog of every bug **devdanzin has found and
got filed anywhere**, organized by the tool that found it — so the impact of the
fuzzing / static-analysis campaigns can be stated in concrete, defensible numbers.

**Tools covered:** `fusil` (+ OOM mode + plugins), `lafleur` (Tier-2 JIT),
`cext-review-toolkit`, `ft-review-toolkit`, `cpython-review-toolkit`,
`code-review-toolkit`, `pyo3-review-toolkit`, `rust-ext-review-toolkit`, and a
`manual` bucket (incl. old bugs.python.org / `ajaksu2` era).

## Counting units (kept deliberately separate)
- **Finding** — one itemized reported defect (an umbrella issue lists many).
- **Bug** — a distinct root-caused defect after dedup.
- **Artifact** — one GitHub issue or PR (unique URL).

Findings ≥ bugs → artifacts. The gap is real and large (e.g. the C-extension
campaign has **~690 FIX-level findings** but **~106 issues filed**), so the three
are never summed.

## Layout
```
PLAN.md            self-contained plan of attack (phases 0–5)
SCOPING_REPORT.md  Phase-1 output: coverage map + per-tool scale estimates
PROGRESS.md        phase tracker
sources/           raw scoping evidence (JSON): registry/OOM/reports/crashers
                   previews, gist + GitHub inventories, refined_counts.json
bugs/              (Phase 3) one record per distinct bug — bugs/<id>.{json,md}
raw/               (Phase 2) full issue/PR dumps w/ comments + labels + timeline
drafts/            found-but-not-yet-filed (excluded from filed counts)
catalog.json       (Phase 4) generated rollups
INDEX.md           (Phase 4) generated human index
```

## Status
**Complete** (2026-07-08). **464 bugs across 28 external projects; 347 issue +
490 PR artifacts.** See **`INDEX.md`** (generated rollups), **`FINDINGS.md`** (the
3-unit explanation + what the "~690" number is), `catalog.json` (machine-readable),
and `PROGRESS.md` (phase log). Regenerate: `classify → group → enrich → index`.

---
*Catalog + tooling assembled with Claude Code (Opus 4.8).*
