# Scoping Report — reported-bugs catalog (Phase 1)

*Generated during the Phase 1 scoping pass. Metadata-only discovery + coverage
map + scale. All numbers here are **rough scoping estimates** to be recomputed
precisely in Phases 2–4. Sources of each number are cited so nothing is taken on
faith. Freshness hierarchy (per PLAN §Freshness caveat): **GitHub live > reports/
+ gists > April-2026 milestones/Discourse > registry/575 post**.*

Raw data written to `sources/`:
`cext_registry_preview.json`, `oom_findings_preview.json`,
`local_inventory_reports.json`, `local_inventory_crashers.json`,
`gist_list.json` + `gist_reportish.json`, `gh_author_issues.json`,
`gh_author_prs.json`, `gh_mentions.json`, `github_inventory.json`.

---

## 0. Headline (the presentation-relevant shape)

**Three counting units keep this legible** (PLAN §1): *findings* (itemized
defects) ≥ *bugs* (deduped) → *artifacts* (issues/PRs). The gap is large and
real — e.g. the cext campaign has **~690 FIX-level findings** (milestone_6,
2026-04-22) but only **106+ issues filed**; the OOM campaign has **37 unique
bugs** but only **15 filed**. *(Discourse's "575" is an older April-6 snapshot —
§8 milestones supersede it.)*

**Scale of externally-filed artifacts** (refined via `total_count` searches, not
the capped list — see §2). Using `-owner:devdanzin` to strip own repos:
**authored external = 352 issues + 154 PRs**. Dropping OTHER_OSS contributions
(~35 issues + ~103 PRs, per the exclude decision) leaves **~317 in-scope
authored issues + ~51 in-scope authored PRs ≈ ~368 authored artifacts**, plus
**~60 maintainer-authored cext artifacts** (not in the author set) ⇒ **~430
in-scope filed artifacts** across **~25 external projects**. (Up from the first
estimate because CPython was undercounted by the 1000-cap: it is **157 issues +
18 PRs = 175**, not 129.) Dwarfed by the **1907 raw authored artifacts** — 77%
own-repo internal tracking (§2).

---

## 1. Per-tool counts (the money table)

**Table A — authored artifacts, from live `total_count` searches**
(`author:devdanzin <tool> …`; uncapped). Keyword counts are a **lower bound** —
a bug issue that describes the crash and links a gist without naming the tool
won't match, so the campaign totals (Table B) sit above these.

| Tool | Issues (authored+kw) | PRs | Where | Notes |
|---|---|---|---|---|
| **fusil** (all) | **113** | 6 | 77i+2p CPython, 36i+4p non-CPython | biggest tool; incl. OOM + pypy 20 |
| ├ fusil → CPython | 77 | 2 | python/cpython | supersedes Discourse "52"; incl. ~15 OOM |
| └ fusil → non-CPython | 36 | 4 | pypy 20, h5py/numpy/cereggii/… 16 | |
| **lafleur** (JIT) | **27** | 0 | python/cpython only | #136996/007/728/762 (2025) + #145197 |
| **cext-review-toolkit** | **63** | 16 | ~24 C-ext repos | kw lower bound (campaign 106+) |
| **ft-review-toolkit** | **7** | 3 | C-ext repos | kw lower bound (campaign 13+) |
| **cpython-review-toolkit** | **17** | 0 | python/cpython | umbrella #146102; #146092→PR #146124; #148181 |
| **code-review-toolkit** | 0 | 0 | — | pure-Python tool, none filed |
| **pyo3 / rust-ext-review-toolkit** | **0** | 0 | — | CONFIRMED 0 filed (5+2 unfiled runs) |
| **manual / untagged** | ~36 CPython + ~3 pypy + tail | ? | python/cpython, pypy | issues naming no tool; Phase-3 classify |

*Cross-checks:* CPython authored = **157 issues + 18 PRs**; fusil 77 + lafleur 27
+ crtk 17 = **121 tag-attributed**, leaving ~36 untagged (some OOM without the
word "fusil", some manual). fusil-cpython **77 ≈ 52 (2025) + 15 OOM + wsgiref +
OrderedDict + tail** — reconciles. **Keyword negation needs `NOT`, not `-`**:
`NOT fusil` = 3 correct, `-fusil` = 20 (minus silently ignored for keywords;
`-` works only for `owner:`/`repo:`).

**Table B — campaign findings** (milestones/Discourse; *findings*, the larger
unit — never sum with Table A):

| Campaign | Findings | Bugs | Issues | PRs | Merged | Source |
|---|---|---|---|---|---|---|
| fusil OOM | 43 dirs | **37 unique** | 15 | 1 (#151931) | 4+ fixed | oom meta.json; umbrella #151763 |
| fusil plugins (cereggii) | 4 | 4 | #149 | #145–148 | open 2026-07-07 | crashers; h5py = drafts |
| cext-review-toolkit | **~690 FIX** (215+ reproduced) | TBD | **106+** | **64+** | 14 ext landed | milestone_6 (2026-04-22) |
| ft-review-toolkit | 4,556+ races, 30+ crashes | TBD | **13+** | ujson #689+ | 2 ext validated | ft milestone_3 (2026-04-30) |

**Unit caveat for the deck:** never sum *findings* and *artifacts*. Defensible
combined headline: **"~430 issues/PRs filed across ~25 projects; 700+ confirmed
findings; 116 CPython artifacts labelled `type-crash`."**

---

## 2. Own-vs-external split (why the raw author count is misleading)

Raw `author:devdanzin` = **1078 issues + 907 PRs** (true `total_count`; listable
results cap at 1000, so the earlier capped repo-histogram undercounted — use
`total_count`, not the list). **Clean split via `-owner:devdanzin`** (the right
filter — excludes only devdanzin-owned repos; note it does **NOT** exclude
python/cpython, owned by `python`):

| Class | Issues | PRs | Disposition |
|---|---|---|---|
| **OWN** (`owner:devdanzin`: lafleur, labeille, fusil, *-review-toolkit, plugins, forks) | ~726 | ~753 | **EXCLUDE** (decided) — internal tool-dev tracking |
| **External, all** (`-owner:devdanzin`, incl. CPython) | **352** | **154** | mixed — see below |
| ├ CPython | 157 | 18 | IN SCOPE |
| ├ non-CPython tool-target | ~160 | ~33 | IN SCOPE |
| └ OTHER_OSS (wily 33p, mu 18p, coveragepy 11p, radon, Tuxemon…) | ~35 | ~103 | **EXCLUDE** (decided) — features/docs, not tool bugs |

**In-scope authored ≈ 317 issues + 51 PRs ≈ 368**, + ~60 maintainer-authored cext
⇒ **~430 filed artifacts**.

**Per-repo (authored, live) with tool attribution** — note the outreach split
(issues-only ⇒ maintainer fixed; PRs-only ⇒ we fixed directly):

| Repo | Issues | PRs | Tool (corrected) |
|---|---|---|---|
| python/cpython | 157 | 18 | fusil 77 / lafleur 27 / crtk 17 / manual ~36 |
| pypy/pypy | 23 | 8 | **fusil** (20 of 23; ~3 manual) — *was mis-bucketed manual* |
| h5py/h5py | 16 | 0 | cext-review-toolkit |
| bottleneck | 15 | 0 | cext-review-toolkit |
| python-zstandard | 12 | 0 | cext-review-toolkit (#291–#302) |
| cereggii | 11 | 4 | fusil-plugin (#149 + #145–148) |
| numpy | 10 | 0 | cext-review-toolkit |
| atom / kiwi / enaml | 9 / 9 / 8 | 0 | cext-review-toolkit (nucleic) |
| simplejson | 8 | 9 | **review-toolkit** (2 umbrellas; 1 ft, rest cext) — *was mis-bucketed manual* |
| lz4 | 0 | 6 | cext-review-toolkit (direct PRs) |
| multidict | 4 | 0 | cext-review-toolkit |
| memray | 0 | 2 | cext-review-toolkit (direct PRs) |

**python/cpython labels** (147 artifacts, presentation-sliceable):
`type-crash` **116**, interpreter-core 72, extension-modules 47, 3.14 36,
topic-JIT 33, 3.13 30, topic-free-threading 26, 3.15 14, type-bug 11, stdlib 10.
→ **116 crash-labelled CPython artifacts** is a strong standalone headline.

---

## 3. Source reconciliation (the three structured ingest sources)

### 3a. cext/ft registry + 148 JSON  →  `cext_registry_preview.json`
- **148 JSON files on disk = 139 real artifact records (138 unique URLs)**;
  9 are search-result/commit dumps (excluded). traits #1881 duplicated.
- Per-type: **issue 77 / pr 62**. Per-state: **OPEN 74 / MERGED 45 / CLOSED 20**.
- **24 repos**; top: h5py 25, bottleneck 24, Pillow 24, atom 9, kiwi 9,
  zope.interface 9, enaml 8, lz4 6, cython 4, scipy 3.
- **Ours vs maintainer on disk: 79 / 60.** (Registry *claims* 84/54 — stale.)
- **All filed on the extension's own repo** — 0 cross-filed to python/cpython.
- **Staleness confirmed:** Pillow has 24 PR JSONs on disk vs 13 in the registry
  (11 undocumented: #9504/9505/9510/9517/9519/9520/9525/9526/9535/9536/9540);
  bitarray registry cites #270 but disk has #250 (typo). ⇒ **trust disk + GitHub
  live over the registry table.**
- Discourse #106875 says **90 issues filed** vs 77 on disk — ~13 issues filed
  after the JSON snapshot, or in the ~14 "communicated-only" extensions
  (astropy, cffi, cvxopt, isal, ml-dtypes, msgspec, mypyc, nanobind, pybind,
  pyerfa, pymongo, wrapt, awkward-cpp) that have no `issues_prs/` dir. **Phase 2
  must re-harvest all 24+ repos from GitHub live.**

### 3b. fusil OOM  →  `oom_findings_preview.json`
- **43 dirs → 37 unique bugs (6 folded dups).** Status: gisted 18, reported 11,
  folded 6, drafted 4, fixed 4.
- **15 filed upstream:** #151673, #151773, #151798, #151815, #151818, #151842,
  #151931, #151968, #151902, #152034, #152058, #152083, #152107, #152130,
  #152851. Umbrella **#151763** (tracks OOM-0001..0035 via gists).
- **~22 unique bugs gisted/drafted but NOT filed** → feed the *unfiled-findings*
  number. Two deliberate filing-holds (OOM-0020, OOM-0038: FT-subinterp, per
  policy #143232). Folds: 0005/0029/0033/0041→0036, 0011→0008, 0042→0040.
- Modes: default `oom`; `oom-seq` (0036/0038/0039/0040/0042); `oom-foreign`
  (0043 = #152851, first foreign-malloc find).

### 3c. Gists (285)  →  `gist_reportish.json`
- **285 total: 161 public / 124 secret.** ~201 look report-ish (109 pub / 92
  sec); **35 are OOM-00NN report gists** (public, 1:1 with OOM bugs incl.
  SUPERSEDED markers). Rest span cext/ft extension reviews + cereggii + code
  reviews.
- **Gists are markers** (PLAN §2c): Phase-2/3 long-tail = `gh search issues
  "<gist-id>"` per public report gist to find issues/PRs citing our gist without
  naming us. Known: `10536845…`→cereggii #149; OOM gists→cpython-oom-findings.

---

## 4. Local-artifact inventory (crashers + memory)  →  `local_inventory_crashers.json`
~55 distinct references; the actionable filed set:
- **CPython:** OOM issues (see 3b); fusil non-OOM #153354 (wsgiref `__annotate__`),
  #132461 + fix #132462 (OrderedDict.setdefault, 2025); lafleur #145197;
  cpython-review #146102 + #146092→**#146124** + #148181 (⚠️ crashers-scan
  "#146443" NOT found — verify; likely a mis-record for #146124).
- **cereggii:** #149 umbrella issue + #145/#146/#147/#148 fix PRs (2026-07-07).
- **Contributor-filed (credit us):** Abhi210 filing an FT `set_keys` managed-dict
  OOM assert we root-caused (under #151763). ⟵ a *maintainer-filed* case for §7 playbook.
- **DRAFTS (unfiled → `drafts/`, excluded from counts):** h5py `get_name` OOM
  null-deref, HDF5 property-list/skip-list OOM family, h5py `@with_phil`
  `Py_INCREF(NULL)`, astropy cext review (gist `fd3ffd45…` sent), coveragepy
  ctracer review, numpy OOM contract (optional).
- **Caveats:** (1) ~30 `report_trigger_*`/`report_crash_*` dirs describe real
  fusil finds with **no embedded issue number** — filed-status must be
  reconciled vs GitHub live. (2) naive `#NNNN` regex caught CSS hex colors in
  lafleur transcripts (noise — exclude).

---

## 5. Decisions — resolved + remaining

**RESOLVED (2026-07-08, user):**
1. **OWN-repo (`owner:devdanzin`, ~726i+753p) — EXCLUDE.** Internal tool-dev
   tracking, no pointer.
2. **OTHER_OSS (~35i+103p: wily, mu, coveragepy-features, radon, Tuxemon…) —
   EXCLUDE.** General contributions, not tool-found bugs. (A quick eyeball of
   coveragepy/mypy/cinder/pytest can promote any real bug report backed by a
   report/gist; default exclude.)
3. **pypy → `fusil`** (20 of 23 issues; ~3 manual) — *corrected from "manual".*
4. **simplejson → review-toolkit** (cext, + 1 ft umbrella) — *corrected from
   "manual".* ⇒ the "manual" bucket is now much smaller than first thought.

**REMAINING (gate Phase 3, not Phase 2):**
5. **`ajaksu2` old-bpo.** Account **not `author:`-searchable** (migrated); 589
   body-mentions in cpython are triage-heavy. Real authored-by-ajaksu2 bugs = a
   hand-filtered long-tail sub-pass (try fusil-era vs manual).
6. **~36 untagged CPython issues** (157 − fusil/lafleur/crtk 121): classify
   per-issue in Phase 3 (OOM-without-keyword, manual, or non-bug).
7. **Deck unit framing** — headline *artifacts filed* (~430) and *confirmed
   findings* (700+) as **separate** numbers, never summed. (Recommended; confirm.)

---

## 6. Coverage map (buckets for Phase 2 harvest)

| Bucket | What | Rough size | Phase-2 action |
|---|---|---|---|
| **INGEST** | cext 139 JSON + OOM 37 bugs | ~176 | import to `raw/`, refresh labels+state vs GitHub |
| **AUTHOR-EXTERNAL** | in-scope authored artifacts | **~317 issue + ~51 pr** | harvest full (comments/labels/timeline), **per-repo** to beat the 1000 cap |
| **MAINTAINER-FILED** | cext maintainer-authored (~60) + Abhi210 + gist-citations | ~60+ | gist-URL/id search (**75 upstream issues cite a devdanzin gist**) + `involves` diff, verify each |
| **LOCAL-ONLY (draft)** | h5py×3, HDF5, astropy, coveragepy, numpy | ~6 | → `drafts/`, excluded from counts |
| **LOCAL-ONLY (no ref)** | ~30 crash dirs w/o issue number | ~30 | reconcile vs GitHub; likely unfiled or dup |
| **BPO long-tail** | ajaksu2-era manual/fusil | TBD | hand-filtered sub-pass |
| **OTHER_OSS** | general contributions | ~35i + ~103p | **EXCLUDE** (decided) |

---

## 7. Phase-2 worklist (ordered)
1. **Import** the 139 cext JSON into `raw/`; **refresh** each for `labels` +
   current `state` via `gh api` (they lack both). Re-harvest the 24 cext repos +
   the ~14 communicated-only extensions from GitHub live (registry is stale).
2. **Harvest per-repo** (avoids the 1000-cap — confirmed: capped list said
   cpython 129, truth is 157): iterate `-owner:devdanzin` external repos, full
   (comments + timeline + labels). Start python/cpython (157i+18p), then the
   ~24 external target repos.
3. **OOM:** ingest the 15 filed issues + link the umbrella #151763 → 35 gists →
   bugs. Reuse OOM-00NN ids as bug ids.
4. **Maintainer-filed sub-pass:** gist-URL search (**75 upstream issues cite a
   `gist.github.com/devdanzin` gist** — a strong vector) + per-gist-id search;
   `involves:devdanzin -author:devdanzin` diff vs the author set to isolate the
   ~60 cext-maintainer + Abhi210 (filter the huge 621 involves-count by hand —
   it's mostly mention-noise).
5. **cpython-review-toolkit + code-review-toolkit + lafleur:** harvest the named
   issues/PRs + drafts (§8). **Verify #146443 vs #146124.**
6. **Drafts:** stage the 6 unfiled finds into `drafts/` (excluded from counts).

### Phase-2 search recipes (validated this pass)
- **Own-repo exclusion:** `-owner:devdanzin` (clean). ⚠️ keeps python/cpython
  (owned by `python`) — add `-repo:python/cpython` to isolate non-CPython.
- **Per-tool attribution (lower bound):** `author:devdanzin <tool> repo:<R>
  type:issue|pr` — validated fusil 77 / lafleur 27 / crtk 17 (CPython); cext 63
  / ft 7 (external). Under-counts bug issues that only link a gist → combine with
  the gist-URL vector + registry `filed_by` for the true per-tool total.
- **True counts:** always `gh api search/issues -f q=… --jq .total_count`
  (uncapped); the listable `gh search` caps at 1000 and undercounts.
- **Keyword negation = `NOT`, not `-`.** `NOT fusil` = 3 (correct); `-fusil` = 20
  (minus silently ignored for keywords). `-` works only for `owner:`/`repo:`
  qualifiers (e.g. `-owner:devdanzin`, `-repo:python/cpython`).
- **`ajaksu2`** is not `author:`-searchable — use body-text + local notes.

---

## 8. Review-toolkit reports inventory  →  `local_inventory_reports.json`
258 reference rows / 909 report files classified. **These April-2026 milestones
are NEWER than the Discourse post (§9) and supersede the "575" number.**

**Latest authoritative milestone counts:**
- **cext correctness — `analysis_milestone_report_6.md` (2026-04-22):** **50
  extensions analyzed, ~690 FIX-level bugs, 215+ reproduced from Python, 106+
  GitHub issues filed, 64+ PRs, 14 extensions landed**, 29 reproducer techniques,
  toolkit v0.3.0. *(⇒ up from Discourse's 575/90 — use these.)*
- **ft — `ft_review_toolkit_milestone_report_3.md` (2026-04-30):** 18 extensions
  FT-analyzed, **4,556+ unique races, 30+ live crashes, 13+ issues filed
  upstream**, pyskein + ijson validated FT-ready, ujson PR #689 validated.

**"Not yet filed" backlog (→ `drafts/`, feeds the unfiled-findings headline):**
CPython **`_decimal` `dec_addstatus` race** (`_decimal.c:605`, M3→M4 backlog);
couchbase-python-client (31 FIX, ready); frozendict (13 C FIX + 14 parity + 35
porting); uvloop (41 items, paused); ijson (76 items incl. 50 C bugs); ujson PR
#689 amendments; igraph 48-site double-free; time-machine/tprof/icu4py (contact
Adam Johnson).

**References:** 150 distinct issue/PR refs across 34 repos + 40 gists (39
`devdanzin/*`). Confirmed-filed set incl. **indygreg/python-zstandard #291–#302
(12 filed)**. *Caveat:* many python/cpython `gh-` refs in these reports are agent
**citations** of existing upstream issues, not our filings; bare `#NNN` is
dominated by finding **ordinals** — **use the milestone counts for "filed", not
a raw ref grep.**

**cpython-review-toolkit — filed artifacts (corrected):** the toolkit's own
`reports/` produced **no filed issue file** — only ANALYSIS (git-history,
reinit-audit, sentinel deep-review) + **1 DRAFT** (`bug1-issue-draft.md`,
itertools `_grouper` UAF, unfiled). Campaign-attributable CPython filings (cited
in the cext reports):
- **python/cpython#148181** — zip_longest (filed by us)
- **python/cpython#146092** — `_PyFrame_GetLocals` OOM (reported via toolkit) →
  **fixed by PR #146124**
- umbrella **python/cpython#146102**
- a drafted lru_cache bug filed by the user
- ⚠️ **#146443 (from the crashers scan / prior memory) was NOT found** anywhere
  in the reports tree — likely a mis-recorded number; the real fix PR is
  **#146124**. **Verify both in Phase 2 before citing.**

**code-review-toolkit:** no filed artifacts surfaced in the reports scan
(pure-Python analysis tool); treat as **0 filed pending Phase-2 GitHub check**.

**pyo3 / rust-ext-review-toolkit: CONFIRMED 0 filed** — pyo3 = 5 unfiled audit
runs (v1/v2/main_v1/v2/v3), rust-ext = 2 (cryptography-rust_v1, polars_v1); their
PyO3/pola-rs/serde refs are agents citing existing upstream issues.

**History snapshot** (`history/extension_catalog.md`, older): 623 indexed / 316
cloned / 272 native / **233 C-C++/Cython targets / 43 analyzed** / 39 Rust-only.

---

## 9. Discourse cross-check (context only — April-2026/2025 snapshots, some stale)
- **#106875** (cext, Apr 6–16 2026): 575+ confirmed (~10–15% FP), ~560 FIX-level
  across **43 extensions** (~950K LOC), 155+ reproduced, **90 issues filed**, 62
  PRs, 49 PRs + ~22 commits merged, 14 extensions landed. *("575" = findings, do
  NOT cite as filed count.)*
- **#103452** (lafleur, Aug 31 2025): 4 JIT crashes → #136996/#137007/#137728/#137762.
- **#91737** (fusil, May 12 2025): **52 CPython issues** filed in 6 months (23
  segfault + 22 abort + 2 SystemError + 2 Fatal + 3 other), 98 PRs, 18 devs,
  Victor fixed 14. Fusil = Victor Stinner's tool (~20 yrs old), revived.

---

## 10. Open items for kickoff (non-blocking)
- Confirm §5 ambiguity dispositions (own-exclude, other-OSS-exclude,
  pypy/simplejson→manual, ajaksu2 long-tail method, unit framing).
- Confirm pyo3/rust-ext truly 0-filed (§8, pending reports scan).
- Decide whether "confirmed-but-unfiled findings" (cext ~575−90; OOM ~22) is a
  separate deck headline. Recommended: **yes**, labeled as *findings not yet
  filed*, sourced from milestones + OOM meta, reconciled vs GitHub — never 575 raw.
