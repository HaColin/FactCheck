"""Parser robustness sweep with an independent grep cross-check.

Invariant: every `run:` key in a workflow file should surface as exactly one
extracted run block, and every `image:` under a services: block should surface
as a service. If the counts drift, the parser silently lost something.
"""
import os, re, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import collect, extract

RUN_KEY = re.compile(r"^(\s*)(?:-\s+)?run:")

def grep_run_lines(path):
    """Line numbers of real step `run:` keys.

    Excludes two lookalikes that are not step scripts: `defaults: run:` (a
    shell-config mapping) and `run:` passed as a `with:` input to an action.
    """
    lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
    out = []
    for i, line in enumerate(lines):
        m = RUN_KEY.match(line)
        if not m:
            continue
        ind = len(m.group(1))
        parent = ""
        for j in range(i - 1, -1, -1):
            prev = lines[j]
            if not prev.strip() or prev.strip().startswith("#"):
                continue
            pind = len(prev) - len(prev.lstrip(" "))
            if pind < ind:
                parent = prev.strip()
                break
        if parent in ("defaults:", "with:"):
            continue
        out.append(i + 1)
    return out

def grep_run_count(path):
    return len(grep_run_lines(path))

def grep_service_count(path):
    """Service names: the direct child keys of every `services:` block."""
    lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
    total = 0
    for i, line in enumerate(lines):
        m = re.match(r"^(\s*)services:\s*$", line)
        if not m:
            continue
        base, child = len(m.group(1)), None
        for nxt in lines[i + 1:]:
            if not nxt.strip() or nxt.strip().startswith("#"):
                continue
            ind = len(nxt) - len(nxt.lstrip(" "))
            if ind <= base:
                break
            if child is None:
                child = ind
            if ind == child and re.match(r"^\s*[\w.-]+:", nxt):
                total += 1
    return total

def main(repos):
    print("%-34s %6s %5s %5s %5s %5s %6s %6s %6s  %s" % (
        "repo", "clone", "wfs", "jobs", "runs", "svcs", "grep", "dRun", "dSvc", "errors"))
    for r in repos:
        owner, name, url = collect.parse_repo_url(r)
        dest = os.path.expanduser("~/.cache/factcheck/%s__%s" % (owner, name))
        t0 = time.time()
        try:
            collect.clone(url, dest)
        except subprocess.CalledProcessError as e:
            print("%-34s CLONE FAIL %s" % (r, e.stderr.strip()[:60])); continue
        except subprocess.TimeoutExpired:
            print("%-34s CLONE TIMEOUT" % r); continue
        ct = time.time() - t0
        paths = extract.workflow_paths(dest)
        jobs = runs = svcs = 0
        errs = []
        grep = gsvc = 0
        for p in paths:
            grep += grep_run_count(os.path.join(dest, p))
            gsvc += grep_service_count(os.path.join(dest, p))
            wf = extract.extract_workflow(dest, p)
            if wf["error"]:
                errs.append("%s: %s" % (os.path.basename(p), wf["error"][:40]))
                continue
            jobs += len(wf["jobs"])
            for j in wf["jobs"]:
                runs += len(j["blocks"])
                svcs += len(j["services"])
        print("%-34s %5.1fs %5d %5d %5d %5d %6d %+6d %+6d  %s" % (
            "%s/%s" % (owner, name), ct, len(paths), jobs, runs, svcs, grep,
            runs - grep, svcs - gsvc, "; ".join(errs)[:60]))

if __name__ == "__main__":
    main(sys.argv[1:])
