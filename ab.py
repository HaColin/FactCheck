"""Phases A+B driver: clone, inventory, parse CI, print what was found.

    python3 ab.py https://github.com/OWNER/NAME [--cache-dir DIR] [--all-runs]

Zero GitHub API calls.
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import collect
import extract

B = "\033[1m"; D = "\033[2m"; G = "\033[32m"; Y = "\033[33m"; C = "\033[36m"; R = "\033[0m"
if not sys.stdout.isatty():
    B = D = G = Y = C = R = ""


def hdr(text):
    print("\n%s%s%s" % (B, text, R))
    print(D + "-" * len(text) + R)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--cache-dir", default=os.path.expanduser("~/.cache/factcheck"))
    ap.add_argument("--all-runs", action="store_true",
                    help="print every run command, not just the first 12 per job")
    args = ap.parse_args()

    owner, name, url = collect.parse_repo_url(args.repo)
    dest = os.path.join(args.cache_dir, "%s__%s" % (owner, name))
    os.makedirs(args.cache_dir, exist_ok=True)

    t0 = time.time()
    fresh = not os.path.isdir(os.path.join(dest, ".git"))
    collect.clone(url, dest)
    clone_s = time.time() - t0

    print("%s%s/%s%s  @ %s %s(%s, clone %s %.1fs)%s" % (
        B, owner, name, R, collect.default_branch(dest),
        D, collect.head_sha(dest), "fresh" if fresh else "cached", clone_s, R))

    # ---- phase A -----------------------------------------------------
    hdr("A. Collected  (0 API calls)")
    inv = collect.inventory(dest)
    for cat, _ in collect.CATEGORIES:
        hits = inv[cat]
        if not hits:
            print("  %-10s %s-%s" % (cat, D, R))
            continue
        shown = hits[:8]
        more = "  %s+%d more%s" % (D, len(hits) - len(shown), R) if len(hits) > len(shown) else ""
        print("  %-10s %s%s%s" % (cat, C, "  ".join(shown), R) + more)

    # ---- phase B -----------------------------------------------------
    hdr("B. Extracted from CI  (0 API calls)")
    paths = extract.workflow_paths(dest)
    if not paths:
        print("  no .github/workflows -- other CI: %s" % (inv["ci"] or "none"))
        return 0
    wfs = [extract.extract_workflow(dest, p) for p in paths]
    wfs.sort(key=lambda w: -w["rank"])
    print("  %d workflow file(s), ranked by authority over 'what runs on merge':\n" % len(wfs))
    for wf in wfs:
        flag = "%sPRIMARY%s" % (G, R) if wf is wfs[0] else "%srank %d%s" % (D, wf["rank"], R)
        print("  %-42s %-28s %s" % (
            wf["path"], "on: " + ",".join(wf["triggers"][:3] or ["?"]), flag))
        if wf["error"]:
            print("      %sPARSE ERROR: %s%s" % (Y, wf["error"], R))

    for wf in wfs:
        if wf["rank"] < 0 or not wf["jobs"]:
            continue
        hdr("  %s   %s(%s)%s" % (wf["path"], D, wf["name"], R))
        for k, v, ln in wf["env"]:
            print("    %sworkflow env%s  %s=%s  %s<- %s:%d%s" % (Y, R, k, v, D, wf["path"], ln, R))
        for j in wf["jobs"]:
            print("\n    %sjob %s%s  %s(%d steps, line %d)%s" % (
                B, j["id"], R, D, j["steps"], j["line"], R))
            if j["uses_workflow"]:
                print("      calls reusable workflow: %s  %s<- :%d%s"
                      % (j["uses_workflow"][0], D, j["uses_workflow"][1], R))
            for val, ln in j["runs_on"]:
                print("      runs-on      %s%s%s  %s<- :%d%s" % (C, val, R, D, ln, R))
            if j["container"]:
                print("      container    %s%s%s  %s<- :%d%s"
                      % (C, j["container"][0], R, D, j["container"][1], R))
            if j["matrix"]:
                print("      matrix       %s" % ", ".join(
                    "%s=[%s]" % (k, ",".join(v)) for k, v in j["matrix"].items()))
            for s in j["setups"]:
                tag = "from file" if s["from_file"] else ""
                print("      %stoolchain%s    %s %s%s%s %s %s<- :%d%s"
                      % (G, R, s["tool"], B, s["value"], R, tag, D, s["line"], R))
            for svc in j["services"]:
                bits = []
                if svc["ports"]:
                    bits.append("ports " + ",".join(svc["ports"]))
                if svc["env"]:
                    bits.append("env " + ",".join(k for k, _ in svc["env"]))
                print("      %sservice%s      %s %s%s%s  %s%s<- :%d%s"
                      % (Y, R, svc["name"], B, svc["image"] or "?", R,
                         "  ".join(bits) + "  " if bits else "", D, svc["line"], R))
            for k, v, ln in j["env"][:10]:
                print("      env          %s=%s  %s<- :%d%s" % (k, v[:60], D, ln, R))
            if len(j["env"]) > 10:
                print("      env          %s+%d more%s" % (D, len(j["env"]) - 10, R))
            for paths_, ln in j["caches"]:
                print("      cache        %s  %s<- :%d%s" % (paths_[:70], D, ln, R))
            runs = j["runs"] if args.all_runs else j["runs"][:12]
            for r in runs:
                wd = " %s(in %s)%s" % (D, r["wd"], R) if r["wd"] else ""
                print("      run          %s%s%s%s  %s<- :%d%s"
                      % (C, r["cmd"][:90], R, wd, D, r["line"], R))
            if len(j["runs"]) > len(runs):
                print("      run          %s+%d more (--all-runs)%s"
                      % (D, len(j["runs"]) - len(runs), R))
    return 0


if __name__ == "__main__":
    sys.exit(main())
