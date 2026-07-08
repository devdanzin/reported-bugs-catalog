# Reported-bugs catalog — plan of attack

Goal: a versioned, offline-analyzable catalog of every bug **devdanzin has found
and got filed anywhere**, organized by the tool that found it (fusil, lafleur,
cpython-review-toolkit, cext-review-toolkit, ft-review-toolkit,
pyo3-review-toolkit, rust-ext-review-toolkit, code-review-toolkit, plus a
`manual` bucket), with the issues and fix-PRs each produced — so we can put
concrete numbers on impact (per-tool counts; umbrella-issue → sub-issues →
merged PRs; sliceable by issue label e.g. "crash").

Primary consumer: a presentation. We need defensible totals for **bugs**,
**issues/PRs**, and **findings**, sliceable by tool and by label.

Status: PLANNED. Start at **Phase 1 (scoping pass)**. This doc is self-contained;
a fresh context can execute from it.

**Big realization from source review:** the C-extension campaign
(cext/ft-review-toolkit) is already heavily structured — a registry, per-extension
counts, and **148 issue/PR JSON exports (with comments) already on disk**. For
that half this is mostly **ingest + reconcile + refresh**, not discovery. The
fuzzers (fusil OOM, lafleur, general) and the long tail need real discovery.

**Freshness caveat (important):** the `issues_and_prs_registry.md` and the "575
confirmed" Discourse number are **STALE** — treat them as a *starting inventory*,
not ground truth. **Source-of-truth hierarchy:** (1) **GitHub live** = current
artifact state/labels (always refresh); (2) **reports/ + gists** = up-to-date
attribution + findings; (3) **latest milestone reports** (in
`cext-review-toolkit/reports/`, not `history/`) = best campaign-level counts, but
still dated ~April 2026 (the June–July fusil/OOM/cereggii/h5py/wsgiref work is
NOT in them); (4) registry / 575-post = stale seeds to verify, never to cite.

---

## 0. Decisions locked in

- **"Reported" = found-and-filed-anywhere** (by us OR a maintainer we handed it
  to). **Drafts / not-yet-filed EXCLUDED** from counts (kept in `drafts/`): e.g.
  the h5py/HDF-Group OOM reports, and `~/projects/coveragepy/ctracer_review_*.md`
  (sent to the coveragepy maintainer, never filed).
- **Scope = ALL tools + a `manual` bucket.** Pre-tool **triage** activity
  (commented/nosy but NOT the report author) is EXCLUDED.
- **Old bpo bugs: use the `manual` bucket BUT still attempt tool attribution** —
  some old ones used **fusil** (Victor-Stinner era), and that's worth capturing.
- **Identities:** GitHub **`devdanzin`**; bugs.python.org **`ajaksu2`** (migrated
  to GitHub — old issues may show a bot author + `ajaksu2` in the body).
- **Capture issue LABELS** (GitHub) — they classify e.g. crash/type-crash on
  CPython; index must be sliceable by label. (Labels are rich on CPython, sparse
  on most C-ext repos.)
- **Review-toolkit finds were filed a MIX of ways** (some by us, some by
  maintainers) → the registry already records `filed_by`; for the rest use
  `author:` + `involves:`/`mentions:` + gist-reference search + local notes.
- **CPython tool tag = free text in title/body** (not a GitHub label).
- **Gists are markers:** we **always create a gist for a report sent to a
  maintainer**. 285 gists total (mostly secret, many NOT reports). The reported
  ones are markers → enumerate gists, and **search GitHub for gist URLs/ids** to
  find issues/PRs that cite our gist without mentioning us.
- **Home = new git repo, PUBLIC**, pushed to GitHub `devdanzin/reported-bugs-catalog`.
- **Layout = raw store + per-bug files + generated index** (§3).

---

## 1. Units & counting definitions

- **Artifact** = one GitHub issue or PR (unique URL). This is what we harvest/store.
- **Finding** = one itemized reported defect. Single-bug issue ⇒ 1. An **umbrella**
  (issue body lists K items) or a gist/report-file with K bugs ⇒ K. The
  C-extension campaign's "**575 confirmed**" (per the Discourse post) is a
  *findings* count, far exceeding the number of filed issues.
- **Bug** = a distinct root-caused defect after **dedup** (an umbrella's K
  findings may collapse to <K; OOM umbrella #151763: 35 findings → 31 bugs).
- Relationships: `finding` → in an `artifact` (or gist/report) → rolls up to a
  `bug` → has report `issues` + fix `prs`. Umbrella = 1 artifact, N findings.

Headline numbers, per tool / label / overall: `# bugs`, `# findings`, `# issues`,
`# fix-PRs`, `# fixed/merged`, `# open`; per umbrella: findings → bugs → merged.

---

## 2. Sources (registry → `sources.yaml`)

### 2a. Already-structured (INGEST, don't re-discover)
- **`~/projects/cext-review-toolkit/comms/`** — the cext + ft campaign registry:
  - `issues_and_prs_registry.md` — per-extension table (issues ours/maintainer,
    PRs ours/maintainer, open, closed/merged, status, channel, contact) + a
    per-extension **Detailed Registry** with umbrella + issue/PR links. Records
    `filed_by` directly. (tool = cext-review-toolkit or ft-review-toolkit.)
    **LIKELY STALE** — use for the artifact/extension inventory + `filed_by`, but
    **re-verify state (open/merged) and counts against GitHub live**; do not
    trust its open/closed numbers.
  - `<ext>/issues_prs/<ext>_(issue|pr)_<n>.json` — **148 files already harvested
    with comments** (keys: author, body, closedAt, comments, createdAt, number,
    state, title, url). ⇒ import into `raw/`; **augment with `labels` +
    `repository`** (missing from these dumps) via a light `gh api` refresh.
  - `<ext>/communications.md`, `<ext>/mastodon_thread.json`, `follow_up_summary.json`,
    `search_results_summary.json` — provenance + channel.
- **`~/projects/cpython-oom-findings/`** — fusil OOM campaign; per-bug `meta.json`
  (`upstream_issue`, `status`, gist), umbrella #151763. (tool=fusil,
  mode=oom/oom-foreign/oom-seq.)

### 2b. Reports & campaign records (findings source + attribution + timeline)
- `~/projects/cext-review-toolkit/reports/` — **the LIVE location**: per-extension
  `<ext>_report.md` (findings) + the newest milestones (`analysis_milestone_report`
  through **_6**, `ft_review_toolkit_milestone_report`, **_2**, **_3**). Use the
  latest of these for current campaign counts + the **"not yet filed" backlog**
  (the milestones explicitly track unfiled items, e.g. the CPython `_decimal`
  `dec_addstatus` race) → those go in `drafts/` and feed the *unfiled-findings*
  number (NOT the stale 575).
- `~/projects/cpython-review-toolkit/reports/` — `bug*-issue-draft.md`, deep
  reviews/audits (`sentinelobject-deep-review.md`, reinit/git-history), `reproducers/`.
  (tool=cpython-review-toolkit; umbrella #146102, PR #146443.)
- `~/projects/pyo3-review-toolkit/reports/`, `~/projects/rust-ext-review-toolkit/reports/`
  — **nothing reported yet** (confirm empty; likely 0 filed).
- `~/projects/history/` — an **archived snapshot** (copied for a "history of the
  review toolkit" project) — its milestones stop at _5 and it lacks the ft _2/_3;
  prefer `cext-review-toolkit/reports/` for anything current. Still useful for
  `extension_catalog.md` (reviewed-extensions checklist: 623 indexed, 233 C/C++
  targets, 43 analyzed + FT-status), `communication_record.md` (164 KB comms log),
  `development-*.md`, `discuss_python_org_post_draft.md`.
- `~/crashers/*/REPORT.md` + `FINDING.md` + `INDEX.md` + `cereggii_prs/INDEX.md`
  — fusil plugin finds (cereggii #145–149, h5py/HDF5 OOM [some DRAFT], wsgiref
  __annotate__ #153354).
- Memory `~/.claude/projects/-home-danzin-projects-fusil/memory/*.md` + `MEMORY.md`
  — grep for issue/PR/gist refs to cross-check + recover attribution.

### 2c. Gists (markers — 285 total)
- `gh gist list -L 400 --json` → titles encode findings (OOM-00NN, `[SUPERSEDED
  — duplicate of ...]`, extension names). Public OOM-00NN gists ↔
  cpython-oom-findings bugs. **For each gist: `gh search issues "<gist-id>"` and
  `"gist.github.com/devdanzin/<id>"`** to find citing issues/PRs.

### 2d. Announcements (context only — numbers here are STALE)
- discuss.python.org/t/.../106875 ("575 confirmed" — **stale, do not cite**;
  the current confirmed/unfiled counts come from the latest `reports/` milestones
  reconciled against GitHub, not this post)
- discuss.python.org/t/.../103452 (lafleur JIT fuzzer intro)
- discuss.python.org/t/.../91737 (fusil CPython campaign feedback)

### 2e. GitHub discovery (state + labels + long tail)
- `gh search issues --author devdanzin -L 1000` / `gh search prs --author devdanzin -L 1000` (global).
- `gh search issues --involves devdanzin` / `--mentions devdanzin` (maintainer-filed, pings).
- Old bpo: search `ajaksu2` (author bot + body match) across python/cpython.
- Per-tool free-text in python/cpython: `fusil`, `lafleur`, `cpython-review-toolkit`.
- Gist-reference searches (2c).

---

## 2.5 Discovery vectors → which bucket
| Vector | Catches | Bucket |
|---|---|---|
| cext registry + 148 JSON | cext/ft filed issues+PRs (ours & maintainer) | ingest |
| cpython-oom-findings meta | fusil OOM upstream issues | ingest |
| `author:devdanzin` | anything we filed anywhere | discover |
| `involves/mentions:devdanzin` | maintainer-filed crediting us, pings | discover |
| gist-id / gist-URL search | issues/PRs citing our gist w/o naming us | long-tail |
| `ajaksu2` on cpython | old bpo-migrated (fusil-era + manual) | long-tail |
| local notes naming an issue no search caught | no-mention finds | long-tail |
| reports/ + milestone + discuss counts | findings totals (incl. unfiled) | cross-check |

---

## 3. Repo layout

```
reported-bugs-catalog/
  PLAN.md  README.md  sources.yaml  PROGRESS.md
  tools/  harvest.py  classify.py  index.py  ingest_cext_registry.py  lib.py
  raw/<owner>__<repo>/(issue|pull)-<n>.json     # full dump w/ comments+labels+timeline
  bugs/<bug-id>.{json,md}                        # one record per distinct bug (§4)
  findings/<umbrella-or-report>.json             # umbrella/report -> finding -> bug maps
  drafts/<slug>.md                               # found-but-not-filed (excluded from counts)
  catalog.json   INDEX.md                        # generated
```
`ingest_cext_registry.py` = one-off importer for `comms/` (registry table +
detailed section + the 148 JSON) → seeds `bugs/` + `raw/` with `filed_by` from
the registry. `harvest.py`/`index.py` incremental & idempotent.

---

## 4. Per-bug record schema (`bugs/<id>.json`)

```json
{
  "bug_id": "cpython-annotate-compareop-boolcast",
  "title": "...",
  "tool": "fusil",                     // ...|cext-review-toolkit|ft-review-toolkit|manual
  "mode": "general",                   // oom|oom-foreign|oom-seq|jit|static-analysis|null
  "target_repo": "python/cpython",
  "umbrella": null,
  "findings": [{"id":"f1","source":"issue:python/cpython#153354"}],
  "issues": ["python/cpython#153354"],
  "prs": [],
  "gists": ["8c86ca...."],
  "labels": ["type-crash","3.14"],     // from GitHub (esp. CPython)
  "filed_by": "self",                  // self|maintainer|self+maintainer
  "status": "open",                    // open|fixed|merged|closed-wontfix|duplicate|closed-other
  "created_at": "...","closed_at": null,
  "channel": null,                     // registry: email|Mastodon|Discord|Discourse|Slack|GitHub
  "raw": ["raw/python__cpython/issue-153354.json"],
  "confidence": "high",
  "notes": "..."
}
```

---

## 5. Classification rules (tool)
First hit wins; record `confidence`:
1. **Registry/local artifact says so** (cext comms ⇒ cext/ft; cpython-oom-findings
   ⇒ fusil/oom; a toolkit report naming the issue ⇒ that toolkit) → high.
2. **Title/body names the tool** (free text) → high.
3. **Gist link** → the gist's campaign (OOM gist ⇒ fusil/oom; ext gist ⇒
   cext/ft) → high.
4. **Repo + shape heuristic** (cext/pyo3 repo + review-style multi-finding ⇒ that
   review toolkit; cpython crash repro ⇒ fusil, JIT-flavoured ⇒ lafleur) → medium.
5. Else `manual`, low → review queue. Old bpo: try fusil (Victor-era) vs manual.

---

## 6. Phases

### Phase 0 — Bootstrap
`git init`; layout; `README.md`; seed `sources.yaml` (§2); empty `PROGRESS.md`;
stub tools. Create **public** GitHub repo `devdanzin/reported-bugs-catalog`, push.

### Phase 1 — SCOPING PASS  ⟵ START HERE
Light discovery + coverage map + scale (metadata only). Steps:
1. **Ingest-preview** the structured sources: parse the cext registry table
   (per-ext counts, filed_by) + count the 148 JSON; parse cpython-oom-findings
   `meta.json`. → rough cext/ft + OOM totals for free.
2. **Local inventory**: scan §2b reports/notes/crashers; extract issue/PR/gist
   refs (`#\d+`, `gh-\d+`, `(python/cpython|owner/repo)#\d+`, `/(issues|pull)/\d+`,
   `gist.github.com/\w+/\w+`) + tool guess → `sources/local_inventory.json`.
3. **Gist inventory**: `gh gist list -L 400 --json` → classify report-gists by
   title; note which are markers.
4. **GitHub inventory**: author/involves/mentions + `ajaksu2` + per-tool text
   (§2e), metadata only → `sources/github_inventory.json` (repo, number, type,
   title, state, author, labels, createdAt, url), dedup by URL.
5. **Cross-reference & coverage map**: join local ↔ registry ↔ GitHub; bucket
   matched / GitHub-only / local-only(draft or non-GitHub) / bpo-migrated.
6. **WebFetch the 3 discuss threads** for headline counts (575 etc.) as cross-check.
7. **Deliverable: `SCOPING_REPORT.md`** — per-tool + per-repo + per-state rough
   counts, the ambiguity list, the coverage gaps (local bug w/ no artifact =
   draft or maintainer-filed-elsewhere to chase in the long-tail pass), and the
   Phase-2 worklist. Update `PROGRESS.md`.

### Phase 2 — Raw harvest / import (mechanical, incremental)
- **Import** the 148 cext JSON into `raw/`; **refresh** them for `labels` +
  current `state` (light `gh api`).
- **Harvest** the remaining worklist (fuzzer issues, cpython-review, long-tail)
  full incl. comments + timeline + labels → `raw/`. One link-expansion round
  (report-issue ↔ fix-PR). Respect rate limits; resumable from PROGRESS.md;
  background-able. → complete `raw/`.

### Phase 3 — Classify, dedup, reconcile (reasoning; batch per tool/repo)
`classify.py`/`ingest_cext_registry.py` → per-bug records; expand umbrellas into
findings; dedup findings→bugs (reuse OOM-00NN ids); link fix-PRs↔issues.
**Long-tail sub-pass**: gist-URL search hits, `ajaksu2`, no-mention-but-in-notes,
pings → resolve to bugs; low-confidence → `review_queue.md` for sign-off.

### Phase 4 — Index & numbers
`index.py` → `catalog.json` + `INDEX.md` (per-tool + per-label rollups; umbrella
impact chains; timeline; totals). Hand-verify a sample vs GitHub + the registry
and the 575 cross-check.

### Phase 5 — Refresh (re-run harvest+index for state drift; add new bugs).

---

## 7. Hard-case playbook
- **Maintainer-filed**: registry `filed_by` or `involves`/`mentions` + a local
  artifact naming the issue.
- **Gist-only citation**: found by gist-URL search; attribute via the gist's campaign.
- **bpo-migrated (ajaksu2)**: real author in body; authored vs triaged (nosy/
  comment-only = triaged = EXCLUDE); try fusil-vs-manual on old ones.
- **Umbrellas**: parse body → findings → dedup → bugs; 1 artifact, N findings.
- **Non-GitHub / draft** (HDF Group, coveragepy ctracer): `drafts/`, excluded.
- **Dedup**: signature key; reuse cpython-oom-findings ids; record duplicates.

---

## 8. Context-budget & resumability
Every phase persists to disk + resumes from `PLAN.md` + `PROGRESS.md` + on-disk
artifacts. Cost order: Phase 3 > 1 > 2 > 4 — spend interactive context on 1 & 3,
script/background 2 & 4; batch Phase 3 per tool/repo. Optional parallel fan-out
(only if you opt into a workflow) for scoping/harvest across sources; default is
sequential + incremental. Commit + update PROGRESS.md after each phase.

---

## 9. Scale estimate (rough — all numbers to be recomputed from live sources)
- cext/ft: **148 filed artifacts on disk** = a *starting inventory* (re-verify
  state vs GitHub); ~25 extensions with filed activity per the (stale) registry.
- fusil OOM: ~36–43 bugs, ~14 filed upstream, umbrella #151763.
- fusil general/plugins: cereggii (5 artifacts) + wsgiref #153354 + more.
- lafleur (JIT) + cpython-review-toolkit (#146102/#146443 + drafts): TBD.
- Old bpo (ajaksu2, fusil-era + manual): TBD long tail.
- **Filed catalog** = artifacts/bugs from the above, all reconciled against
  GitHub live. **Unfiled-findings** number (a nice separate headline) = derived
  from the **latest `reports/` milestones + gists + backlog**, NOT the stale 575.
  Three-unit counting (finding/bug/artifact) keeps "confirmed findings vs filed
  issues" legible.

---

## 10. Open items (confirm at kickoff, non-blocking)
- Confirm pyo3/rust-ext review-toolkit reports are truly 0-filed.
- Spot-confirm the `manual` + triage-exclusion policy on a couple of old bpo/ajaksu2 examples.
- Whether to include the "confirmed-but-unfiled" findings count as a separate
  headline (from reports/milestones/Discourse) alongside the filed catalog.
