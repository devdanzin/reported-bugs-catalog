#!/usr/bin/env python3
"""Phase-3d: backfill the fix/backport PRs that closed our issues.

Our issues were harvested, but the PRs that FIXED them are usually authored by the
fixer (not devdanzin) and don't cite a gist, so `harvest.py` never fetched them.
Their numbers ARE in each issue's timeline cross-references. This tool collects
those same-repo /pull/ numbers, harvests the missing ones, and records the set in
sources/backfill_prs.json so group.py can (a) merge them into the issue's bug
(backports included) and (b) drop any that don't actually link back to one of our
issues.

Run once after harvest.py; then re-run classify.py -> group.py -> enrich.py.
"""
# pyright: reportMissingImports=false, reportOptionalMemberAccess=false
import json, glob, os, re, collections
import tools.harvest as h  # noqa: E402  (run from repo root: python -m tools.harvest_fixprs)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw")
SRC = os.path.join(ROOT, "sources")


def main():
    in_raw = {int(re.search(r"-(\d+)\.json", f).group(1))
              for f in glob.glob(os.path.join(RAW, "*", "*.json"))}
    # candidate fix-PRs = same-repo /pull/ cross-refs from our harvested ISSUES
    cand = collections.defaultdict(set)   # repo -> {pr numbers}
    for f in glob.glob(os.path.join(RAW, "*", "*.json")):
        d = json.load(open(f))
        if d["type"] != "issue":
            continue
        repo = d["repo"]
        for t in d.get("timeline_refs") or []:
            m = re.search(rf"/{re.escape(repo)}/pull/(\d+)", t.get("source") or "")
            if m:
                n = int(m.group(1))
                if n not in in_raw:
                    cand[repo].add(n)

    total = sum(len(v) for v in cand.values())
    print(f"backfilling {total} candidate fix/backport PRs...")
    backfill = []
    ok = err = 0
    for repo in sorted(cand):
        for n in sorted(cand[repo]):
            r = h.fetch_artifact(repo, n, refresh=False)
            if r.startswith("err"):
                err += 1
                print(f"  ERR {repo}#{n}: {r[:80]}")
                continue
            ok += 1
            backfill.append(f"{repo}#{n}")
    json.dump(sorted(backfill), open(os.path.join(SRC, "backfill_prs.json"), "w"), indent=1)
    print(f"harvested ok={ok} err={err}; wrote sources/backfill_prs.json ({len(backfill)})")
    print(f"raw total now: {len(glob.glob(os.path.join(RAW, '*', '*.json')))}")


if __name__ == "__main__":
    main()
