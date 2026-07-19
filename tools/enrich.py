#!/usr/bin/env python3
"""Phase-3c: add SYNTHETIC bug records for catalog-known bugs that have no
harvested GitHub artifact — so the *bug* count reflects findings->bugs, not just
filed artifacts. Two sources:

  * OOM catalog (oom_findings_preview.json): 22 gisted/drafted OOM bugs beyond
    the 15 filed; 6 folded = duplicates (recorded, not counted).
  * cpython-review-toolkit umbrella (#146102 -> crtk_umbrella.json): rows that
    were fixed-in-commit or are still unfiled ('—') have no issue/PR artifact.

Synthetic records carry "is_synthetic": true and no "raw", so Phase-4 can count
bugs (incl. synthetic) separately from filed artifacts (harvested only).
Run AFTER group.py; idempotent (overwrites its own synthetic files).
"""
import json, os, glob, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources")
BUGS = os.path.join(ROOT, "bugs")


def existing_bug_ids():
    return {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(BUGS, "*.json"))}


def artifact_index():
    """set of 'python/cpython#N' already represented by a harvested bug record."""
    have = set()
    for f in glob.glob(os.path.join(BUGS, "*.json")):
        b = json.load(open(f))
        for a in b.get("issues", []) + b.get("prs", []):
            have.add(a)
    return have


def main():
    have_ids = existing_bug_ids()
    have_art = artifact_index()
    added = collections.Counter()
    folds = []

    # ---- OOM synthetics ----
    oom = json.load(open(os.path.join(SRC, "oom_findings_preview.json")))
    for b in oom["bugs"]:
        if b.get("status") == "folded":
            folds.append({"bug_id": b["bug_id"], "folded_into": b.get("folded_into")})
            continue
        if b["bug_id"] in have_ids:
            continue  # already a harvested record (the 15 filed)
        rec = {
            "bug_id": b["bug_id"], "title": b.get("title"),
            "tool": "fusil", "mode": b.get("mode") or "oom",
            "target_repo": "python/cpython", "is_umbrella": False,
            "issues": [], "prs": [], "shared_fix_prs": [], "related_prs": [],
            "n_prs": 0, "n_backports": 0, "n_fix_prs": 0,
            "n_shared_fixes": 0, "n_related_prs": 0,
            "gists": [b["gist_id"]] if b.get("gist_id") else [],
            "labels": [], "filed_by": "none", "filers": [],
            "status": b.get("status"),   # gisted | drafted
            "confidence": "high", "needs_review": False, "review_reason": None,
            "reproduced": None, "raw": [], "n_artifacts": 0,
            "is_synthetic": True, "source": "oom-catalog",
        }
        json.dump(rec, open(os.path.join(BUGS, b["bug_id"] + ".json"), "w"), indent=1)
        added["oom"] += 1

    # ---- TSan synthetics (umbrella findings with no individual issue) ----
    # The 12 findings filed collectively in the umbrella #153852 but not split into
    # their own sub-issue have no harvested artifact. Unlike OOM gisted synthetics,
    # these ARE filed (via the umbrella) -> filed_by="self", status="reported".
    try:
        tsan = json.load(open(os.path.join(SRC, "tsan_findings_preview.json")))
    except FileNotFoundError:
        tsan = {"bugs": []}
    for b in tsan["bugs"]:
        if b.get("status") == "folded":
            folds.append({"bug_id": b["bug_id"], "folded_into": b.get("folded_into")})
            continue
        if b["bug_id"] in have_ids:
            continue  # already a harvested record (3 sub-issues + 4 standalone)
        rec = {
            "bug_id": b["bug_id"], "title": b.get("title"),
            "tool": "fusil", "mode": b.get("mode") or "tsan",
            "target_repo": "python/cpython", "is_umbrella": False,
            "umbrella_issue": b.get("umbrella_issue"),
            "issues": [], "prs": [], "shared_fix_prs": [], "related_prs": [],
            "n_prs": 0, "n_backports": 0, "n_fix_prs": 0,
            "n_shared_fixes": 0, "n_related_prs": 0,
            "gists": [b["gist_id"]] if b.get("gist_id") else [],
            "labels": [], "filed_by": "self", "filers": [],
            "status": b.get("status") or "reported",
            "confidence": "high", "needs_review": False, "review_reason": None,
            "reproduced": None, "raw": [], "n_artifacts": 0,
            "is_synthetic": True, "source": "tsan-catalog",
        }
        json.dump(rec, open(os.path.join(BUGS, b["bug_id"] + ".json"), "w"), indent=1)
        added["tsan"] += 1

    # ---- crtk umbrella synthetics (rows with no harvested issue/PR) ----
    crtk = json.load(open(os.path.join(SRC, "crtk_umbrella.json")))
    for r in crtk:
        if r.get("false_alarm"):
            continue
        arts = [f"python/cpython#{n}" for n in r.get("issues", []) + r.get("prs", [])]
        if any(a in have_art for a in arts):
            continue  # already represented by a harvested artifact
        if arts:
            # referenced an issue/PR we somehow didn't harvest — skip (shouldn't happen)
            continue
        status = "fixed-in-commit" if r.get("has_commit") else "unfiled"
        bug_id = f"crtk-{r['gist'][:8]}"
        rec = {
            "bug_id": bug_id, "title": r.get("desc"),
            "tool": "cpython-review-toolkit", "mode": "static-analysis",
            "target_repo": "python/cpython", "is_umbrella": False,
            "issues": [], "prs": [], "shared_fix_prs": [], "related_prs": [],
            "n_prs": 0, "n_backports": 0, "n_fix_prs": 0,
            "n_shared_fixes": 0, "n_related_prs": 0,
            "gists": [r["gist"]], "labels": [],
            "filed_by": "self" if status == "unfiled" else "self+commit",
            "filers": [], "status": status,
            "confidence": "high", "needs_review": False, "review_reason": None,
            "reproduced": None, "raw": [], "n_artifacts": 0,
            "is_synthetic": True, "source": "crtk-umbrella",
        }
        json.dump(rec, open(os.path.join(BUGS, bug_id + ".json"), "w"), indent=1)
        added["crtk"] += 1

    # save fold record
    json.dump(folds, open(os.path.join(SRC, "oom_folds.json"), "w"), indent=1)

    # re-summarize all bugs
    allbugs = [json.load(open(f)) for f in glob.glob(os.path.join(BUGS, "*.json"))]
    synth = [b for b in allbugs if b.get("is_synthetic")]
    by_tool_all = collections.Counter(b["tool"] for b in allbugs)
    by_tool_filed = collections.Counter(b["tool"] for b in allbugs if not b.get("is_synthetic"))
    print(f"added synthetics: {dict(added)}  (folded OOM dups recorded: {len(folds)})")
    print(f"total bug records: {len(allbugs)}  ({len(synth)} synthetic, "
          f"{len(allbugs) - len(synth)} from harvested artifacts)")
    print("\nbugs per tool  (filed-artifact + synthetic = total):")
    for t in sorted(by_tool_all, key=lambda t: -by_tool_all[t]):
        f = by_tool_filed[t]
        s = by_tool_all[t] - f
        print(f"  {by_tool_all[t]:4d}  {t:26s} ({f} artifact + {s} synthetic)")


if __name__ == "__main__":
    main()
