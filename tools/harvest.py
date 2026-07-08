#!/usr/bin/env python3
"""Phase-2 raw harvester for the reported-bugs catalog.

Idempotent + resumable. For every target (repo, number) it fetches the full
issue/PR — core fields + labels + comments + timeline (the timeline carries the
issue<->fix-PR cross-references we need in Phase 3) — and writes
    raw/<owner>__<repo>/(issue|pull)-<n>.json

Targets come from two places:
  1. ENUMERATE: `author:devdanzin` issues+PRs in each in-scope external repo
     (worklist below). Beats the 1000-cap by querying per-repo.
  2. INGEST: the 139 cext issue/PR JSON exports already on disk (these include
     *maintainer-authored* artifacts that the author-search misses).

Everything dedups by (repo, number). Re-run to resume; pass --refresh to refetch
existing files, --only-enumerate / --only-ingest to limit, --repo R to restrict.

Uses `gh api` (inherits auth). REST budget ~3 calls/artifact, well under 5000/hr.
"""
# gh() returns dynamic JSON (dict|list); Pyright can't narrow the .get() calls.
# pyright: reportAttributeAccessIssue=false
import json, os, subprocess, sys, glob, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw")
SRC = os.path.join(ROOT, "sources")
PROGRESS = os.path.join(ROOT, "sources", "harvest_progress.json")
CEXT_COMMS = "/home/danzin/projects/cext-review-toolkit/comms"

# In-scope external bug-target repos to enumerate (author:devdanzin). Own repos
# and OTHER_OSS (wily/mu/radon/Tuxemon/icalendar/…) are intentionally excluded
# per the scoping decisions. Derived from sources/refined_counts.json + the cext
# registry + the author TARGET histogram.
ENUM_REPOS = [
    "python/cpython", "pypy/pypy", "dpdani/cereggii",
    # cext / ft review-toolkit targets:
    "h5py/h5py", "pydata/bottleneck", "python-pillow/Pillow", "numpy/numpy",
    "indygreg/python-zstandard", "nucleic/atom", "nucleic/kiwi", "nucleic/enaml",
    "simplejson/simplejson", "aio-libs/multidict", "python-lz4/python-lz4",
    "bloomberg/memray", "scipy/scipy", "ilanschnell/bitarray", "cython/cython",
    "zhuyifei1999/guppy3", "matplotlib/matplotlib", "duckdb/duckdb-python",
    "enthought/traits", "pycurl/pycurl", "giampaolo/psutil",
    "protocolbuffers/protobuf", "zopefoundation/zope.interface",
    "GrahamDumpleton/wrapt", "python-greenlet/greenlet", "igraph/python-igraph",
    "rogerbinns/apsw", "pygame-community/pygame-ce", "aio-libs/aiohttp",
]


def gh(path, paginate=False):
    """Return parsed JSON from `gh api PATH`. Flattens --paginate --slurp pages."""
    cmd = ["gh", "api", path]
    if paginate:
        cmd += ["--paginate", "--slurp"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"gh api {path} failed: {r.stderr.strip()[:300]}")
    data = json.loads(r.stdout or ("[]" if paginate else "{}"))
    if paginate:  # slurp gives [page, page, ...]; each page is a list
        flat = []
        for page in data:
            flat.extend(page if isinstance(page, list) else [page])
        return flat
    return data


def search_numbers(repo, typ):
    """All issue OR pr numbers by author:devdanzin in repo (uncapped, paginated)."""
    q = f"repo:{repo} author:devdanzin type:{typ}"
    out, page = [], 1
    while True:
        import urllib.parse
        qs = urllib.parse.quote(q)
        res = gh(f"search/issues?q={qs}&per_page=100&page={page}")
        items = res.get("items", [])
        out += [it["number"] for it in items]
        if len(items) < 100 or page >= 10:
            break
        page += 1
        time.sleep(2)  # search API: 30/min
    return out


def raw_path(repo, number, is_pr):
    owner, name = repo.split("/", 1)
    d = os.path.join(RAW, f"{owner}__{name}")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"{'pull' if is_pr else 'issue'}-{number}.json")


def fetch_artifact(repo, number, refresh=False):
    """Fetch one artifact fully; write raw JSON. Returns 'skip'|'ok'|'err:...'."""
    # We don't yet know issue vs pr; the issues endpoint serves both.
    try:
        core = gh(f"repos/{repo}/issues/{number}")
    except RuntimeError as e:
        return f"err:{e}"
    is_pr = "pull_request" in core
    p = raw_path(repo, number, is_pr)
    if os.path.exists(p) and not refresh:
        return "skip"
    # comments/timeline are enrichment — a transient failure on either must NOT
    # drop the whole artifact. Retry once, then degrade to empty + record it.
    fetch_errors = []

    def _safe(path):
        for attempt in (1, 2):
            try:
                return gh(path, paginate=True)
            except RuntimeError as e:
                if attempt == 2:
                    fetch_errors.append(f"{path}: {str(e)[:120]}")
                    return []
                time.sleep(2)
        return []

    comments = _safe(f"repos/{repo}/issues/{number}/comments?per_page=100")
    timeline = _safe(f"repos/{repo}/issues/{number}/timeline?per_page=100")
    rec = {
        "repo": repo, "number": number, "type": "pull" if is_pr else "issue",
        "url": core.get("html_url"), "title": core.get("title"),
        "state": core.get("state"),
        "state_reason": core.get("state_reason"),
        "author": (core.get("user") or {}).get("login"),
        "author_association": core.get("author_association"),
        "labels": [l["name"] for l in core.get("labels", [])],
        "created_at": core.get("created_at"), "closed_at": core.get("closed_at"),
        "body": core.get("body"),
        "comments": [
            {"author": (c.get("user") or {}).get("login"),
             "created_at": c.get("created_at"), "body": c.get("body")}
            for c in comments
        ],
        # keep only cross-reference / connection events (issue<->PR links) + closes
        "timeline_refs": [
            {"event": e.get("event"),
             "source": (((e.get("source") or {}).get("issue") or {}).get("html_url")),
             "commit": e.get("commit_id"),
             "actor": (e.get("actor") or {}).get("login")}
            for e in timeline
            if e.get("event") in ("cross-referenced", "connected", "closed",
                                  "merged", "referenced")
        ],
        "fetch_errors": fetch_errors or None,
    }
    with open(p, "w") as f:
        json.dump(rec, f, indent=1)
    return "ok"


def ingest_cext_targets():
    """Return (repo, number) pairs from the 139 cext issue/PR JSON exports."""
    targets = set()
    for fn in glob.glob(os.path.join(CEXT_COMMS, "*", "issues_prs", "*.json")):
        try:
            d = json.load(open(fn))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue  # skip the 9 search-result / commit dumps (lists)
        url = d.get("url", "")
        # url like https://github.com/<owner>/<repo>/(issues|pull)/<n>
        parts = url.rstrip("/").split("/")
        if len(parts) >= 5 and parts[2] == "github.com":
            repo = f"{parts[3]}/{parts[4]}"
            try:
                targets.add((repo, int(parts[-1])))
            except ValueError:
                pass
    return targets


def load_progress():
    if os.path.exists(PROGRESS):
        return json.load(open(PROGRESS))
    return {"done_repos": [], "counts": {}}


def save_progress(pr):
    with open(PROGRESS, "w") as f:
        json.dump(pr, f, indent=1)


def main():
    args = sys.argv[1:]
    refresh = "--refresh" in args
    only_enum = "--only-enumerate" in args
    only_ingest = "--only-ingest" in args
    repo_filter = None
    if "--repo" in args:
        repo_filter = args[args.index("--repo") + 1]

    os.makedirs(RAW, exist_ok=True)
    prog = load_progress()

    # 1. Build the (repo -> set of (number, )) target map.
    targets = {}  # repo -> set(number)
    if not only_ingest:
        repos = [repo_filter] if repo_filter else ENUM_REPOS
        for repo in repos:
            nums = set()
            for typ in ("issue", "pr"):
                try:
                    nums.update(search_numbers(repo, typ))
                except RuntimeError as e:
                    print(f"  ! enumerate {repo} {typ}: {e}", flush=True)
                time.sleep(1)
            targets.setdefault(repo, set()).update(nums)
            print(f"  enum {repo}: {len(nums)} authored", flush=True)
    if not only_enum:
        for repo, n in ingest_cext_targets():
            if repo_filter and repo != repo_filter:
                continue
            targets.setdefault(repo, set()).add(n)

    # 2. Harvest each target artifact.
    grand = {"ok": 0, "skip": 0, "err": 0}
    for repo in sorted(targets):
        nums = sorted(targets[repo])
        c = {"ok": 0, "skip": 0, "err": 0}
        for n in nums:
            res = fetch_artifact(repo, n, refresh=refresh)
            key = "err" if res.startswith("err") else res
            c[key] += 1
            grand[key] += 1
            if res.startswith("err"):
                print(f"    ERR {repo}#{n}: {res[4:][:160]}", flush=True)
        prog["counts"][repo] = c
        if repo not in prog["done_repos"]:
            prog["done_repos"].append(repo)
        save_progress(prog)
        print(f"[{repo}] ok={c['ok']} skip={c['skip']} err={c['err']} "
              f"(total {len(nums)})", flush=True)

    print(f"\nDONE. ok={grand['ok']} skip={grand['skip']} err={grand['err']}. "
          f"raw/ files: {len(glob.glob(os.path.join(RAW, '*', '*.json')))}", flush=True)


if __name__ == "__main__":
    main()
