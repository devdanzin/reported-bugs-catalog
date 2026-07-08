# CPython bugs found & filed by devdanzin's tools

A CPython-only slice of the catalog (full catalog: `INDEX.md`). Counts are
**bugs** (deduped) and **artifacts** (issues/PRs); the C-extension review campaign's
*findings* are a separate, larger unit not counted here (see `FINDINGS.md`).

## Overview

- **220 filed CPython bugs** (each has a GitHub issue and/or PR), across the
  interpreter core, stdlib, C extension modules, JIT, and free-threading.
  **182 fixed/closed, 38 still open.**
- **204 issues + 381 PR-artifacts** (225 distinct fixes + 156 backports).
- **+ 35 more** reported-but-not-individually-filed (OOM bugs tracked under
  umbrella #151763 via gists; cpython-review-toolkit findings fixed directly in a
  commit or still on gists) — bringing the CPython total to **255**.
- **Collaboration:** **114 bugs** were filed by devdanzin and fixed by a
  *maintainer's* PR; **51** were filed entirely by others from the reports/gists;
  55 filed and (often) fixed by devdanzin.
- Spans **2008 → 2026**: the first 9 are early-`fusil` crashes on bugs.python.org
  (2008); the campaign resumed at scale in 2024 (52), 2025 (62), 2026 (96).

## By tool (filed CPython bugs)

| tool | bugs | issues | fix-PRs | backports |
|---|---|---|---|---|
| **fusil** (crash/OOM fuzzer) | 104 | 97 | 106 | 84 |
| **manual** (found by hand, incl. 2008 early-fusil era) | 43 | 36 | 44 | 22 |
| **cpython-review-toolkit** (static C analysis) | 42 | 40 | 47 | 44 |
| **lafleur** (Tier-2 JIT fuzzer) | 28 | 28 | 27 | 6 |
| **ft-review-toolkit** (free-threading review) | 3 | 3 | 1 | 0 |
| **TOTAL (filed)** | **220** | **204** | **225** | **156** |

*(+35 gisted/commit-only bugs not in this table: fusil-OOM ~22 under #151763,
cpython-review ~13.)*

## fusil sub-campaigns (within the 104+ fusil CPython bugs)

- **General crash fuzzing** — segfaults, aborts, assertion failures from hostile
  arguments/objects (the bulk; e.g. the 2024–25 campaign, 52 issues per the
  original Discourse writeup).
- **OOM / allocation-failure injection** — 37 unique bugs driving error paths
  under simulated `MemoryError`; 15 filed as individual issues, the rest tracked
  under umbrella **python/cpython#151763**.
- **Early fusil (2008)** — the original bugs.python.org crashes (#47903, #47912,
  #47914, #47916, #47944).

## Labels (sliceable)

`type-crash` **146** · `interpreter-core` 109 · `extension-modules` 64 ·
`topic-JIT` 35 · `topic-free-threading` 32 · `type-bug` 48 · `topic-subinterpreters`
13 · `topic-repl` 9 · `3.14` 56 · `3.13` 50 · `3.15` 15.

## Timeline (CPython bugs by year)

| year | bugs | note |
|---|---|---|
| 2008 | 9 | early fusil on bugs.python.org |
| 2021–2023 | 3 | occasional manual |
| 2024 | 52 | fusil campaign resumes |
| 2025 | 62 | fusil + lafleur (JIT) |
| 2026 | 96 | OOM injection + cpython-review-toolkit + FT |

## Top CPython collaborators (maintainers/contributors who filed or fixed)

vstinner (28), sobolevn (16), Fidget-Spinner (14), aisk (11), ZeroIntensity (11),
picnixz (9), lpyu001 (8), Wulian233 (6), serhiy-storchaka (5), sergey-miryanov (5),
kumaraditya303 (4), brijkapadia (4). *(auto-backport bot miss-islington excluded.)*

---
*Generated from the catalog at github.com/devdanzin/reported-bugs-catalog
(`sources/cpython_slice.json`). Bugs = deduped defects; a bug may span one issue +
several fix/backport PRs.*
