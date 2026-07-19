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
# user-confirmed review-queue decisions (2026-07-08): devdanzin found these while
# USING the tools but not WITH them, or while minimizing other repros — all manual
# except #130999 (fusil). #126018 was the bug that inspired reviving fusil.
_REVIEW_MANUAL = [122353, 122398, 122461, 125732, 126018, 131878, 131936, 132470,
                  132565, 141805, 142029, 130163, 137218, 139193, 142629, 143751,
                  145064, 121016, 122145, 122170, 122533, 122692, 125852, 126032,
                  145887, 30135]
for _n in _REVIEW_MANUAL:
    OVERRIDES[("python/cpython", _n)] = ("manual", "", "high", "user-review")
OVERRIDES[("python/cpython", 130999)] = ("fusil", "general", "high", "user-review")

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
TITLE_GH = re.compile(r"gh-(\d{3,7})", re.I)   # CPython fix-PR title: "gh-<issue>: ..."


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
    # title + body: "fixes #N" / "gh-N" / "#N". Title matters for CPython fix-PRs
    # which are titled "gh-<issue>: ..." and backports "[3.x] gh-<issue>: ...".
    text = (d.get("title") or "") + "\n" + (d.get("body") or "")
    for rx in (FIX_RE, GH_RE, HASH_RE):
        for m in rx.finditer(text):
            n = int(m.group(1))
            if n != d["number"]:
                links.add(n)
    return sorted(links)


def extract_fix_links(d):
    """The issue(s) a PR actually FIXES (for merging) — precise, unlike `links`
    which includes every name-dropped #N. A CPython fix-PR is titled
    'gh-<issue>: ...'; a backport '[3.x] gh-<issue>: ... (GH-<mainpr>)'. We take the
    FIRST gh-<n> in the title (the fixed issue, before the parenthetical PR ref)
    plus any body 'fixes/closes/resolves #N'. Only PRs fix things."""
    if d["type"] != "pull":
        return []
    fixes = set()
    m = TITLE_GH.search(d.get("title") or "")   # first = the issue, not the (GH-pr)
    if m and int(m.group(1)) != d["number"]:
        fixes.add(int(m.group(1)))
    for mm in FIX_RE.finditer(d.get("body") or ""):
        if int(mm.group(1)) != d["number"]:
            fixes.add(int(mm.group(1)))
    return sorted(fixes)


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


def load_tsan_overrides():
    """The filed fusil --tsan (ThreadSanitizer) findings -> fusil/tsan. Covers the
    umbrella #153852, the 3 picked-up sub-issues, and the 4 standalone crash issues.
    Several are community-authored (johng/brijkapadia/deadlovelll), so keyword/author
    heuristics would mislabel them; the TSan catalog is authoritative."""
    try:
        tsan = json.load(open(os.path.join(os.path.dirname(OUT), "tsan_findings_preview.json")))
    except FileNotFoundError:
        return
    umb = tsan.get("umbrella")
    if umb:
        repo, n = umb.split("#")
        OVERRIDES[(repo, int(n))] = ("fusil", "tsan", "high", "tsan-umbrella:153852")
    for b in tsan["bugs"]:
        ui = b.get("upstream_issue")
        if ui:
            repo, n = ui.split("#")
            OVERRIDES[(repo, int(n))] = ("fusil", "tsan", "high", f"tsan-catalog:{b['bug_id']}")


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


BPO_SELF = set()   # (repo, number) of ajaksu2/devdanzin-created bpo bugs -> filed_by self


def load_bpo_overrides():
    """Ancient bpo issues CREATED by ajaksu2 (=devdanzin). GitHub shows the
    migration-bot as author, so author-based filed_by is wrong -> force 'self'.
    Real crash/hang bugs -> manual (bpo-era, pre-tool); features/docs/junk ->
    non-bug (excluded from counts, like the OTHER_OSS decision)."""
    try:
        rows = json.load(open(os.path.join(os.path.dirname(OUT), "bpo_ajaksu2.json")))
    except FileNotFoundError:
        return
    for r in rows:
        key = ("python/cpython", r["number"])
        BPO_SELF.add(key)
        if r["category"] == "bug":
            tool = r.get("tool", "manual")   # 5 user-confirmed early-fusil finds
            reason = "bpo-ajaksu2-fusil" if tool == "fusil" else "bpo-ajaksu2"
            OVERRIDES[key] = (tool, "general" if tool == "fusil" else "", "high", reason)
        else:
            OVERRIDES[key] = ("non-bug", "", "high", "bpo-ajaksu2-nonbug")


def main():
    load_oom_overrides()
    load_tsan_overrides()
    load_crtk_overrides()
    load_bpo_overrides()
    rows = []
    for f in sorted(glob.glob(os.path.join(RAW, "*", "*.json"))):
        d = json.load(open(f))
        tool, mode, conf, reason = classify_tool(d)
        gists = sorted(set(GIST_RE.findall(d.get("body") or "")))
        rows.append({
            "repo": d["repo"], "number": d["number"], "type": d["type"],
            "url": d["url"], "title": (d.get("title") or "")[:120],
            "state": d["state"], "author": d["author"],
            "filed_by": ("self" if d["author"] == "devdanzin"
                         or (d["repo"], d["number"]) in BPO_SELF else "maintainer"),
            "labels": d["labels"],
            "tool": tool, "mode": mode, "confidence": conf, "reason": reason,
            "needs_review": "REVIEW" in reason,
            "gists": gists,
            "is_umbrella": None,   # set in group.py
            "reproduced": None,    # set later (gist-comb for repro count)
            "links": extract_links(d),
            "fix_links": extract_fix_links(d),
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
