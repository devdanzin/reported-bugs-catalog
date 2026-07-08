#!/usr/bin/env python3
"""Phase-3a per-artifact classifier for the reported-bugs catalog.

Reads raw/*/*.json, assigns each artifact a TOOL + mode + filed_by + confidence
and extracts issue<->PR LINKS (from timeline cross-references + body "fixes #N").
Writes sources/classification.json (one row per artifact) + prints a tool x repo
summary. Grouping into bugs is Phase-3b (group.py); this is signal assignment.

Classification signal priority (PLAN §5, first hit wins):
  1. repo-anchored campaign (cereggii=fusil-plugin; cext repos=cext/ft; simplejson
     =review-toolkit; pypy=fusil-if-tagged)  -> high
  2. explicit tool keyword in title/body (fusil / lafleur / cpython-review-toolkit) -> high
  3. OOM signal (allocation-failure / set_nomemory / OOM gist) on cpython -> fusil/oom
  4. otherwise '?' (untagged) -> resolved later by link-propagation in group.py
"""
# pyright: reportAttributeAccessIssue=false
import json, glob, os, re, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw")
OUT = os.path.join(ROOT, "sources", "classification.json")

CEXT_REPOS = {
    "h5py/h5py", "pydata/bottleneck", "python-pillow/Pillow", "numpy/numpy",
    "indygreg/python-zstandard", "nucleic/atom", "nucleic/kiwi", "nucleic/enaml",
    "aio-libs/multidict", "python-lz4/python-lz4", "bloomberg/memray",
    "scipy/scipy", "ilanschnell/bitarray", "cython/cython", "zhuyifei1999/guppy3",
    "matplotlib/matplotlib", "duckdb/duckdb-python", "enthought/traits",
    "pycurl/pycurl", "giampaolo/psutil", "protocolbuffers/protobuf",
    "zopefoundation/zope.interface", "GrahamDumpleton/wrapt",
    "python-greenlet/greenlet", "igraph/python-igraph", "rogerbinns/apsw",
    "pygame-community/pygame-ce", "liberfa/pyerfa", "pola-rs/polars",
}
OOM_KW = ("allocation-failure", "allocation failure", "set_nomemory",
          "remove_mem_hooks", "--oom", "oom-fuzz", "out of memory",
          "out-of-memory", "no memory left", "allocation-failure fuzzer")
FT_KW = ("free-threading", "free threading", "data race", "tsan", "atomic",
         "thread sanitizer", "thread-sanitizer", "race condition")
FT_LABELS = ("free-threading", "free threading", "topic-free-threading", "race",
             "atomic", "concurrency")
# evidence-based overrides (from the crashers/reports scans) — win over heuristics
OVERRIDES = {
    ("python/cpython", 148181): ("cpython-review-toolkit", "static-analysis", "high", "scan:zip_longest"),
    ("python/cpython", 149142): ("ft-review-toolkit", "static-analysis", "high", "scan:_decimal dec_addstatus"),
    ("python/cpython", 148180): ("ft-review-toolkit", "static-analysis", "medium", "lru_cache FT critical-section"),
    ("python/cpython", 148589): ("ft-review-toolkit", "static-analysis", "medium", "GetFrame FT thread-safety"),
    ("python/cpython", 145197): ("lafleur", "jit", "high", "scan:lafleur"),
    ("python/cpython", 136996): ("lafleur", "jit", "high", "discourse:lafleur"),
    ("python/cpython", 137007): ("lafleur", "jit", "high", "discourse:lafleur"),
    ("python/cpython", 137728): ("lafleur", "jit", "high", "discourse:lafleur"),
    ("python/cpython", 137762): ("lafleur", "jit", "high", "discourse:lafleur"),
    ("python/cpython", 132461): ("fusil", "general", "high", "scan:OrderedDict.setdefault"),
    ("python/cpython", 153354): ("fusil", "general", "high", "scan:wsgiref __annotate__"),
}
FEATURE_KW = ("speed up", "support ", "teach ", "typo", "docstring", "not tested",
              "not currently tested", "missing from", "performance regression",
              "add support", "improve", "faster", "deprecat", "quadratic",
              "history in", "help-env", "command history")
CRASH_KW = ("segfault", "segmentation fault", "abort", "assertion", "crash",
            "fatal", "buffer overflow", "null", "use-after-free", "double free")
GIST_RE = re.compile(r"gist\.github\.com/devdanzin/([0-9a-f]+)")
# link patterns in bodies/comments: "fixes #123", "gh-123", bare "#12345"
FIX_RE = re.compile(r"\b(?:fix(?:es|ed)?|close[sd]?|resolve[sd]?)\s*:?\s*#?(?:gh-)?(\d+)", re.I)
GH_RE = re.compile(r"\bgh-(\d{3,7})\b", re.I)
HASH_RE = re.compile(r"(?<![\w/])#(\d{3,7})\b")


def full_text(d):
    parts = [d.get("title") or "", d.get("body") or ""]
    return " ".join(parts).lower()


def has_oom(txt):
    if any(k in txt for k in OOM_KW):
        return True
    return "memoryerror" in txt and ("fusil" in txt or "set_nomemory" in txt)


def is_ft(d, txt):
    labels = [l.lower() for l in d["labels"]]
    return any(l in FT_LABELS for l in labels) or any(k in txt for k in FT_KW)


def classify_tool(d):
    """Return (tool, mode, confidence, reason)."""
    repo = d["repo"]
    txt = full_text(d)
    # 0. evidence-based overrides
    if (repo, d["number"]) in OVERRIDES:
        return OVERRIDES[(repo, d["number"])]
    # 1. repo-anchored campaigns
    if repo == "dpdani/cereggii":
        return ("fusil-plugin-cereggii", "general", "high", "repo:cereggii")
    if repo == "pypy/pypy":
        if "fusil" in txt:
            return ("fusil", "general", "high", "pypy+fusil-kw")
        return ("manual", "", "low", "pypy-untagged")
    if repo == "simplejson/simplejson":
        tool = "ft-review-toolkit" if is_ft(d, txt) else "cext-review-toolkit"
        return (tool, "static-analysis", "medium", "repo:simplejson(review-toolkit)")
    if repo == "python/mypy":
        return ("cext-review-toolkit", "static-analysis", "low", "mypyc(review)")
    if repo in CEXT_REPOS:
        # h5py OOM-fuzzing (fusil plugin) vs static review
        if repo == "h5py/h5py" and has_oom(txt) and "fusil" in txt:
            return ("fusil-plugin-h5py", "oom", "medium", "h5py+oom+fusil")
        if is_ft(d, txt):
            return ("ft-review-toolkit", "static-analysis", "high", "cext-repo+ft")
        return ("cext-review-toolkit", "static-analysis", "high", "cext-repo")
    # 2/3. cpython: keyword then OOM
    if repo == "python/cpython":
        if "lafleur" in txt:
            return ("lafleur", "jit", "high", "kw:lafleur")
        if "cpython-review-toolkit" in txt:
            return ("cpython-review-toolkit", "static-analysis", "high", "kw:crtk")
        oom = has_oom(txt) or bool(GIST_RE.search(d.get("body") or ""))
        if "fusil" in txt:
            return ("fusil", "oom" if oom else "general", "high", "kw:fusil")
        if oom:
            return ("fusil", "oom", "medium", "cpython+oom/gist")
        # secondary heuristics for untagged cpython artifacts
        labels = [l.lower() for l in d["labels"]]
        jit = "topic-jit" in labels or re.search(r"\bjit\b", txt)
        if jit and any(k in txt for k in CRASH_KW):
            return ("lafleur", "jit", "low", "cpython-jit-crash(REVIEW)")
        if any(k in txt for k in FEATURE_KW):
            return ("manual", "", "medium", "cpython-feature/docs")
        if any(k in txt for k in CRASH_KW):
            return ("fusil", "general", "low", "cpython-crash-untagged(REVIEW:fusil-vs-manual)")
        return ("manual", "", "low", "cpython-untagged(REVIEW)")
    return ("manual", "", "low", "unanchored")


def extract_links(d):
    """Same-repo issue/PR numbers this artifact references (for issue<->PR grouping)."""
    repo = d["repo"]
    links = set()
    # timeline cross-references / connections carry the linked artifact url
    for t in d.get("timeline_refs") or []:
        src = t.get("source")
        if src and f"/{repo}/" in src:
            m = re.search(r"/(?:issues|pull)/(\d+)", src)
            if m:
                links.add(int(m.group(1)))
    # body "fixes #N" / "gh-N" / "#N"
    body = d.get("body") or ""
    for rx in (FIX_RE, GH_RE, HASH_RE):
        for m in rx.finditer(body):
            n = int(m.group(1))
            if n != d["number"]:
                links.add(n)
    return sorted(links)


def load_oom_overrides():
    """The 15 filed OOM issues -> fusil/oom (many are contributor-authored, so
    keyword/author heuristics would miss them; the OOM catalog is authoritative)."""
    try:
        oom = json.load(open(os.path.join(os.path.dirname(OUT), "oom_findings_preview.json")))
    except FileNotFoundError:
        return
    for b in oom["bugs"]:
        ui = b.get("upstream_issue")
        if ui:
            repo, n = ui.split("#")
            OVERRIDES[(repo, int(n))] = ("fusil", "oom", "high", f"oom-catalog:{b['bug_id']}")


def load_crtk_overrides():
    """The cpython-review-toolkit umbrella #146102 authoritatively maps 47 bugs to
    their issue/PR. Those sub-issues rarely name the toolkit, so override them."""
    try:
        rows = json.load(open(os.path.join(os.path.dirname(OUT), "crtk_umbrella.json")))
    except FileNotFoundError:
        return
    for r in rows:
        if r.get("false_alarm"):
            continue
        for n in r.get("issues", []) + r.get("prs", []):
            OVERRIDES[("python/cpython", n)] = (
                "cpython-review-toolkit", "static-analysis", "high",
                f"crtk-umbrella:{r['section']}")


def main():
    load_oom_overrides()
    load_crtk_overrides()
    rows = []
    for f in sorted(glob.glob(os.path.join(RAW, "*", "*.json"))):
        d = json.load(open(f))
        tool, mode, conf, reason = classify_tool(d)
        gists = sorted(set(GIST_RE.findall(d.get("body") or "")))
        rows.append({
            "repo": d["repo"], "number": d["number"], "type": d["type"],
            "url": d["url"], "title": (d.get("title") or "")[:120],
            "state": d["state"], "author": d["author"],
            "filed_by": "self" if d["author"] == "devdanzin" else "maintainer",
            "labels": d["labels"],
            "tool": tool, "mode": mode, "confidence": conf, "reason": reason,
            "needs_review": "REVIEW" in reason,
            "gists": gists,
            "is_umbrella": None,   # set in group.py
            "reproduced": None,    # set later (gist-comb for repro count)
            "links": extract_links(d),
            "raw": os.path.relpath(f, ROOT),
        })
    json.dump(rows, open(OUT, "w"), indent=1)

    # summary
    by_tool = collections.Counter(r["tool"] for r in rows)
    by_tool_type = collections.defaultdict(lambda: collections.Counter())
    conf = collections.Counter(r["confidence"] for r in rows)
    filed = collections.Counter(r["filed_by"] for r in rows)
    for r in rows:
        by_tool_type[r["tool"]][r["type"]] += 1
    print(f"classified {len(rows)} artifacts -> {OUT}")
    print(f"confidence: {dict(conf)}   filed_by: {dict(filed)}")
    print("\ntool  (issue/pr):")
    for t, n in by_tool.most_common():
        c = by_tool_type[t]
        print(f"  {n:4d}  {t:26s} issue={c['issue']:<4} pr={c['pull']}")
    unt = [r for r in rows if r["tool"] == "?"]
    linked = [r for r in unt if r["links"]]
    print(f"\nuntagged '?': {len(unt)} (of which {len(linked)} have links "
          f"-> resolvable by propagation in group.py)")


if __name__ == "__main__":
    main()
