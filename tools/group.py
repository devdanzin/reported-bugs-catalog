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
# pyright: reportAttributeAccessIssue=false
import json, os, re, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources")
BUGS = os.path.join(ROOT, "bugs")

KNOWN_UMBRELLAS = {
    ("python/cpython", 151763),   # OOM umbrella
    ("python/cpython", 146102),   # cpython-review-toolkit umbrella
    ("dpdani/cereggii", 149),     # cereggii 4-bug umbrella
}
UMBRELLA_TITLE = re.compile(
    r"\b(umbrella|tracking issue|analysis report|c extension analysis|"
    r"(four|five|six|seven|eight|nine|ten|\d+)\s+bugs?\b|multiple (bugs|issues|crashes))",
    re.I)


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

    for r in rows:
        r["_umbrella"] = is_umbrella(r)

    # union-find over issue<->PR edges only, skipping umbrellas
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
        key = (r["repo"], r["number"])
        find(key)
        if r["_umbrella"]:
            continue
        for n in r.get("links", []):
            other = idx.get((r["repo"], n))
            if not other or other["_umbrella"]:
                continue
            # only merge an issue with a PR (one of each), same repo
            if {r["type"], other["type"]} == {"issue", "pull"}:
                union(key, (r["repo"], n))

    # gather clusters
    clusters = collections.defaultdict(list)
    for r in rows:
        clusters[find((r["repo"], r["number"]))].append(r)

    bugs = []
    for members in clusters.values():
        repo = members[0]["repo"]
        issues = sorted([m for m in members if m["type"] == "issue"], key=lambda m: m["number"])
        prs = sorted([m for m in members if m["type"] == "pull"], key=lambda m: m["number"])
        umbrella = any(m["_umbrella"] for m in members)
        # tool: highest-confidence non-'?' among members
        rank = {"high": 3, "medium": 2, "low": 1}
        cand = [m for m in members if m["tool"] not in ("?",)]
        tool = "?"
        mode = ""
        if cand:
            best = max(cand, key=lambda m: (rank.get(m["confidence"], 0),
                                            m["tool"] != "manual"))
            tool, mode = best["tool"], best["mode"]
        # primary artifact = lowest-numbered issue else lowest PR
        primary = (issues or prs)[0]
        key = (repo, primary["number"])
        # bug_id
        if key in oom:
            bug_id = oom[key]
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
            "gists": sorted(set(g for m in members for g in m["gists"])),
            "labels": sorted(set(l for m in members for l in m["labels"])),
            "filed_by": filed_by,
            "filers": filers,
            "status": status,
            "confidence": min((m["confidence"] for m in members),
                              key=lambda c: rank.get(c, 0)),
            "needs_review": any(m.get("needs_review") for m in members),
            "review_reason": next((m["reason"] for m in members
                                   if m.get("needs_review")), None),
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
    print(f"{len(rows)} artifacts -> {len(bugs)} bug clusters "
          f"(merged {len(rows) - len(bugs)} PRs into their issues)")
    print(f"umbrellas: {len(umb)}   needs-review bugs: {len(review)}")
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
