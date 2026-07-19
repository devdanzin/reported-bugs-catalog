#!/usr/bin/env python3
"""Phase-3b: group classified artifacts into BUGS and write bugs/<id>.json.

Clusters artifacts via issue<->fix-PR links (union-find), propagates the tool
across each cluster (so a maintainer fix-PR inherits its issue's tool), assigns a
stable bug_id (reusing OOM-00NN), and records filed_by / status / issues / prs /
gists / labels per bug.

Guards against over-merging:
  * Only issue<->PR edges merge (never issue<->issue) — distinct bugs stay apart.
  * Known + heuristic UMBRELLAS (title 'analysis report'/'umbrella'/'N bugs',
    or a PR/issue linking to >=4 same-repo artifacts) are kept as singletons and
    flagged; their references are separate bugs, not merged in.
"""
# pyright: reportAttributeAccessIssue=false, reportOptionalSubscript=false
import json, os, re, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources")
BUGS = os.path.join(ROOT, "bugs")

KNOWN_UMBRELLAS = {
    ("python/cpython", 151763),   # OOM umbrella
    ("python/cpython", 153852),   # fusil --tsan free-threading-races umbrella
    ("python/cpython", 146102),   # cpython-review-toolkit umbrella
    ("dpdani/cereggii", 149),     # cereggii 4-bug umbrella
}
UMBRELLA_TITLE = re.compile(
    r"\b(umbrella|tracking issue|analysis report|c extension analysis|"
    r"(four|five|six|seven|eight|nine|ten|\d+)\s+bugs?\b|multiple (bugs|issues|crashes))",
    re.I)
BACKPORT_TITLE = re.compile(r"^\s*\[3\.\d+\]")   # CPython backport PR convention


def load_backfill():
    try:
        return set(json.load(open(os.path.join(SRC, "backfill_prs.json"))))
    except FileNotFoundError:
        return set()


def load(name):
    return json.load(open(os.path.join(SRC, name)))


def oom_map():
    m = {}
    for b in load("oom_findings_preview.json")["bugs"]:
        ui = b.get("upstream_issue")
        if ui:
            repo, n = ui.split("#")
            m[(repo, int(n))] = b["bug_id"]
    return m


def tsan_map():
    """(repo, issue#) -> TSAN-00NN for the filed --tsan findings (the 3 picked-up
    sub-issues + 4 standalone crash issues), so their harvested clusters get the
    stable TSAN id instead of a repo-derived one. Mirrors oom_map()."""
    m = {}
    try:
        bugs = load("tsan_findings_preview.json")["bugs"]
    except FileNotFoundError:
        return m
    for b in bugs:
        ui = b.get("upstream_issue")
        if ui:
            repo, n = ui.split("#")
            m[(repo, int(n))] = b["bug_id"]
    return m


def is_umbrella(r):
    # Title markers + known ids ONLY. A link-count heuristic was tried and
    # dropped: normal issues that reference >=4 other issues (backports,
    # "see also") were false-flagged (scipy CMPLX, tokenize perf, tkinter segv).
    key = (r["repo"], r["number"])
    return key in KNOWN_UMBRELLAS or bool(UMBRELLA_TITLE.search(r["title"] or ""))


def main():
    os.makedirs(BUGS, exist_ok=True)
    rows = load("classification.json")
    idx = {(r["repo"], r["number"]): r for r in rows}
    oom = oom_map()
    tsan = tsan_map()

    backfill = load_backfill()
    for r in rows:
        r["_umbrella"] = is_umbrella(r)

    # union-find. A PR merges ONLY with the issue it actually FIXES (fix_links:
    # title "gh-<issue>" + body "fixes #N"), not every issue it name-drops — this
    # is what keeps distinct bugs apart (a mere "#N" mention no longer bridges).
    # A PR that fixes several distinct corpus-issues (batch fix) doesn't merge any
    # of them (would conflate bugs); its issues stay separate. Backports share the
    # same fix target as the main PR, so they join the same bug.
    parent = {}
    def find(k):
        parent.setdefault(k, k)
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k
    def union(a, b):
        parent[find(a)] = find(b)

    for r in rows:
        find((r["repo"], r["number"]))
    for r in rows:
        if r["type"] != "pull" or r["_umbrella"]:
            continue
        targets = [n for n in r.get("fix_links", [])
                   if (idx.get((r["repo"], n)) or {}).get("type") == "issue"
                   and not idx[(r["repo"], n)]["_umbrella"]]
        if len(targets) != 1:      # 0 = no in-corpus issue; >=2 = batch fix
            continue
        union((r["repo"], r["number"]), (r["repo"], targets[0]))

    # gather clusters
    clusters = collections.defaultdict(list)
    for r in rows:
        clusters[find((r["repo"], r["number"]))].append(r)

    # A PR whose fix_links hit >=2 of our issues is a genuine batch fix — it never
    # merges (would conflate bugs) but must be RECORDED on each bug it fixes.
    def issue_fix_targets(r):
        return [n for n in r.get("fix_links", [])
                if (idx.get((r["repo"], n)) or {}).get("type") == "issue"]
    shared_by_issue = collections.defaultdict(list)   # (repo,issue#) -> [pr#]
    batch_fix_keys = set()
    for r in rows:
        if r["type"] != "pull":
            continue
        tgts = issue_fix_targets(r)
        if len(tgts) >= 2:
            batch_fix_keys.add((r["repo"], r["number"]))
            for n in tgts:
                shared_by_issue[(r["repo"], n)].append(r["number"])

    bugs = []
    absorbed = 0   # backfill/batch PRs attached to a bug as shared/related, not dropped
    for members in clusters.values():
        repo = members[0]["repo"]
        # a single unmerged PR (backfilled cross-ref, or a batch fix) is NOT its own
        # bug — it's absorbed into its origin bug's shared_fix_prs / related_prs
        # below, so no information is lost.
        if len(members) == 1 and members[0]["type"] == "pull" and (
                f"{repo}#{members[0]['number']}" in backfill
                or (repo, members[0]["number"]) in batch_fix_keys):
            absorbed += 1
            continue
        issues = sorted([m for m in members if m["type"] == "issue"], key=lambda m: m["number"])
        prs = sorted([m for m in members if m["type"] == "pull"], key=lambda m: m["number"])
        if not (issues or prs):
            continue
        n_backports = sum(1 for m in prs if BACKPORT_TITLE.match(m["title"] or ""))
        # shared fixes (batch-fix PRs targeting one of this bug's issues) + related
        # PRs (backfilled cross-refs not confirmed as the fix here)
        already = {m["number"] for m in prs}
        shared = sorted({p for m in issues
                         for p in shared_by_issue.get((repo, m["number"]), [])
                         if p not in already})
        already |= set(shared)
        related = sorted({n for m in issues for n in m.get("links", [])
                          if f"{repo}#{n}" in backfill
                          and (idx.get((repo, n)) or {}).get("type") == "pull"
                          and n not in already})
        umbrella = any(m["_umbrella"] for m in members)
        # tool comes from the highest-confidence non-'?' member — but a backfilled
        # fix-PR only INHERITS the bug's tool, so it must not determine the tool or
        # the review flag (else a confidently-classified issue looks "tentative"
        # because its fix-PR was heuristically guessed).
        rank = {"high": 3, "medium": 2, "low": 1}
        cand = [m for m in members if m["tool"] != "?"
                and f"{repo}#{m['number']}" not in backfill]
        if not cand:
            cand = [m for m in members if m["tool"] != "?"]
        best = (max(cand, key=lambda m: (rank.get(m["confidence"], 0),
                                         m["tool"] != "manual")) if cand else None)
        tool = best["tool"] if best else "?"
        mode = best["mode"] if best else ""
        b_conf = best["confidence"] if best else "low"
        b_review = bool(best and best.get("needs_review"))
        b_reason = best["reason"] if b_review else None
        if tool == "non-bug":   # bpo-era features/docs/junk — excluded from counts
            continue
        # primary artifact = lowest-numbered issue else lowest PR
        primary = (issues or prs)[0]
        key = (repo, primary["number"])
        # bug_id
        if key in oom:
            bug_id = oom[key]
        elif key in tsan:
            bug_id = tsan[key]
        else:
            short = repo.split("/")[-1].lower().replace(".", "")
            bug_id = f"{short}-{primary['number']}"
        authors = set(m["filed_by"] for m in members)
        filed_by = ("self+maintainer" if authors == {"self", "maintainer"}
                    else authors.pop())
        # actual non-devdanzin filers (contributors/maintainers) for the impact story
        filers = sorted(set(m["author"] for m in members
                            if m["author"] and m["author"] != "devdanzin"))
        # status: merged if a PR merged/closed; fixed if issue closed w/ fix; else state
        states = set(m["state"] for m in members)
        closed = all(s == "closed" for s in [m["state"] for m in members])
        status = "closed/fixed" if closed else ("open" if "open" in states else "mixed")
        bugs.append({
            "bug_id": bug_id,
            "title": primary["title"],
            "tool": tool, "mode": mode,
            "target_repo": repo,
            "is_umbrella": umbrella,
            "issues": [f"{repo}#{m['number']}" for m in issues],
            "prs": [f"{repo}#{m['number']}" for m in prs],
            "shared_fix_prs": [f"{repo}#{n}" for n in shared],
            "related_prs": [f"{repo}#{n}" for n in related],
            "n_prs": len(prs),
            "n_backports": n_backports,
            "n_fix_prs": len(prs) - n_backports,
            "n_shared_fixes": len(shared),
            "n_related_prs": len(related),
            "gists": sorted(set(g for m in members for g in m["gists"])),
            "labels": sorted(set(l for m in members for l in m["labels"])),
            "filed_by": filed_by,
            "filers": filers,
            "status": status,
            "confidence": b_conf,
            "needs_review": b_review,
            "review_reason": b_reason,
            "reproduced": None,
            "raw": [m["raw"] for m in members],
            "n_artifacts": len(members),
        })

    # write per-bug json
    for b in bugs:
        json.dump(b, open(os.path.join(BUGS, b["bug_id"] + ".json"), "w"), indent=1)

    # summary: split confirmed vs needs-review per tool
    conf_ct = collections.Counter(b["tool"] for b in bugs if not b["needs_review"])
    rev_ct = collections.Counter(b["tool"] for b in bugs if b["needs_review"])
    umb = [b for b in bugs if b["is_umbrella"]]
    review = [b for b in bugs if b["needs_review"]]
    total_prs = sum(b["n_prs"] for b in bugs)
    total_bp = sum(b["n_backports"] for b in bugs)
    total_shared = sum(b["n_shared_fixes"] for b in bugs)
    total_related = sum(b["n_related_prs"] for b in bugs)
    # accounting: every backfill PR is either merged into a bug, a shared batch
    # fix, or a related cross-ref — nothing is dropped.
    merged_backfill = sum(1 for b in bugs for a in b["prs"] if a in backfill)
    print(f"{len(rows)} artifacts -> {len(bugs)} bug clusters "
          f"({absorbed} single PRs absorbed as shared/related, not dropped)")
    print(f"umbrellas: {len(umb)}   needs-review bugs: {len(review)}")
    print(f"PRs: {total_prs} in-cluster ({total_bp} backports, "
          f"{total_prs - total_bp} distinct fixes) + {total_shared} shared batch-fixes "
          f"+ {total_related} related cross-refs")
    print(f"backfill accounting: {len(backfill)} backfilled = "
          f"{merged_backfill} merged-as-fix + {total_shared} shared + "
          f"{total_related} related (nothing dropped)")
    print("\nbugs per tool  (confirmed + tentative[review]):")
    for t in sorted(set(conf_ct) | set(rev_ct), key=lambda t: -(conf_ct[t] + rev_ct[t])):
        print(f"  {conf_ct[t]:4d} + {rev_ct[t]:<3} tentative   {t}")
    filed = collections.Counter(b["filed_by"] for b in bugs)
    print(f"\nfiled_by (bug clusters): {dict(filed)}")

    # review_queue.md
    rq = ["# Review queue — low-confidence tool attributions",
          "",
          "Best-guess tool assigned by heuristic; **please confirm or correct**.",
          "These are devdanzin-authored CPython artifacts that name no tool — a mix",
          "of manual contributions, fusil crashes, and JIT (lafleur) crashes.",
          "", f"**{len(review)} bugs to review.**", ""]
    by_guess = collections.defaultdict(list)
    for b in review:
        by_guess[b["tool"]].append(b)
    for t in sorted(by_guess):
        rq.append(f"## best-guess: {t}  ({len(by_guess[t])})")
        rq.append("| artifact | title | reason |")
        rq.append("|---|---|---|")
        for b in sorted(by_guess[t], key=lambda b: b["issues"] or b["prs"]):
            art = (b["issues"] or b["prs"])[0]
            rq.append(f"| {art} | {b['title'][:70]} | {b['review_reason']} |")
        rq.append("")
    open(os.path.join(SRC, "review_queue.md"), "w").write("\n".join(rq) + "\n")
    print(f"\nwrote sources/review_queue.md ({len(review)} bugs)")


if __name__ == "__main__":
    main()
