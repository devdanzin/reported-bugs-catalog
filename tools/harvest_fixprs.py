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
    # ALL same-repo /pull/ cross-refs from our harvested ISSUES = the complete
    # candidate fix/backport set (independent of what is already on disk).
    all_fix = collections.defaultdict(set)   # repo -> {pr numbers}
    for f in glob.glob(os.path.join(RAW, "*", "*.json")):
        d = json.load(open(f))
        if d["type"] != "issue":
            continue
        repo = d["repo"]
        for t in d.get("timeline_refs") or []:
            m = re.search(rf"/{re.escape(repo)}/pull/(\d+)", t.get("source") or "")
            if m:
                all_fix[repo].add(int(m.group(1)))

    # Fetch only the ones missing from raw/ (idempotent).
    missing = [(repo, n) for repo in sorted(all_fix)
               for n in sorted(all_fix[repo]) if n not in in_raw]
    total = sum(len(v) for v in all_fix.values())
    print(f"{total} fix-PR cross-refs; fetching {len(missing)} missing from raw/...")
    ok = err = 0
    for repo, n in missing:
        r = h.fetch_artifact(repo, n, refresh=False)
        if r.startswith("err"):
            err += 1
            print(f"  ERR {repo}#{n}: {r[:80]}")
            continue
        ok += 1

    # backfill = the COMPLETE set of fix/backport PRs authored by the FIXER (not
    # devdanzin). Recording EVERY cross-ref fix-PR (not just this run's fetches) is
    # what makes the set idempotent: the old "only newly-fetched" logic dropped a
    # fix-PR from the set once it was already on disk, so on a re-run group.py
    # stopped absorbing it and the OOM fix-PRs/backports resurfaced as standalone,
    # double-counted bugs. Excluding devdanzin-authored PRs keeps our own fix-PRs
    # as real artifacts rather than absorbing them.
    backfill = []
    for repo in sorted(all_fix):
        for n in sorted(all_fix[repo]):
            p = h.raw_path(repo, n, True)
            if not os.path.exists(p):
                continue  # fetch failed / not a PR — skip
            if (json.load(open(p)) or {}).get("author") != "devdanzin":
                backfill.append(f"{repo}#{n}")
    json.dump(sorted(backfill), open(os.path.join(SRC, "backfill_prs.json"), "w"), indent=1)
    print(f"fetched ok={ok} err={err}; wrote sources/backfill_prs.json "
          f"({len(backfill)} total — idempotent, fixer-authored only)")
    print(f"raw total now: {len(glob.glob(os.path.join(RAW, '*', '*.json')))}")


if __name__ == "__main__":
    main()
