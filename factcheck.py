"""FACTCHECK: fact-check a repo's README against its CI.

    python3 factcheck.py https://github.com/OWNER/NAME [--all-runs] [--table]

Phases A, B and C. Zero GitHub API calls.
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import collect
import extract
import precedence
import sources

B = "\033[1m"; D = "\033[2m"; G = "\033[32m"; Y = "\033[33m"; C = "\033[36m"; R = "\033[0m"
if not sys.stdout.isatty():
    B = D = G = Y = C = R = ""


def hdr(text):
    print("\n%s%s%s" % (B, text, R))
    print(D + "-" * len(text) + R)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", nargs="?")
    ap.add_argument("--cache-dir", default=os.path.expanduser("~/.cache/factcheck"))
    ap.add_argument("--all-runs", action="store_true",
                    help="print every run command, not just the first 12 per job")
    ap.add_argument("--table", action="store_true",
                    help="print the source-precedence table and exit")
    ap.add_argument("--quiet-ci", action="store_true",
                    help="skip the phase B per-job dump")
    args = ap.parse_args()
    if args.table:
        print(precedence.table_as_text())
        return 0
    if not args.repo:
        ap.error("a repo URL is required (or --table)")

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
        if args.quiet_ci or wf["rank"] < 0 or not wf["jobs"]:
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

    phase_c(dest, inv, wfs)
    return 0


def cite(claim):
    return "%s%s:%d%s" % (D, claim.path, claim.line, R)


def phase_c(root, inv, wfs):
    hdr("C. Reconciled  (0 API calls)")
    prose = ""
    for p in inv.get("prose", []):
        prose += collect.read(root, p) or ""
    wf_rank = {wf["path"]: wf["rank"] for wf in wfs}
    claims = sources.gather(root, inv, wfs)
    report = precedence.reconcile(claims, wf_rank, prose)
    print("  %d claims from %d sources, ranked by a fixed table (--table)\n"
          % (len(claims), len(set(c.provider for c in claims))))

    def section(title, rows):
        if not rows:
            return
        print("  %s%s%s" % (B, title, R))
        for label, value, tail, tier in rows:
            mark = G if tier == "verified" else Y
            print("    %-11s %s%-38s%s %s" % (label, mark, value[:38], R, tail))
        print()

    rows = []
    for res in report.by_fact("runtime"):
        if not res.winner:
            continue
        rows.append((res.key, res.value, cite(res.winner) +
                     ("  %s(%s)%s" % (D, res.winner.provider, R)), res.tier))
    section("Runtime", rows)

    rows = []
    for res in report.by_fact("services"):
        if not res.winner:
            continue
        note = res.winner.note
        rows.append((res.key, res.value,
                     cite(res.winner) + ("  %s%s%s" % (D, note, R) if note else ""),
                     res.tier))
    section("Services required", rows)

    for fact, title in (("install", "Install"), ("setup", "Setup"),
                        ("build", "Build"), ("test", "Test"), ("lint", "Lint")):
        rows = []
        for res in report.by_fact(fact):
            for m in res.members[:6]:
                rows.append(("", m.value, cite(m), m.tier))
        section(title, rows)

    rows = []
    for res in report.by_fact("os"):
        for m in res.members[:6]:
            rows.append(("", m.value, cite(m), m.tier))
    section("Supported OS", rows)

    envs = [r for r in report.by_fact("env") if r.winner]
    if envs:
        print("  %sEnvironment%s  %s%d variables%s" % (B, R, D, len(envs), R))
        for res in envs[:8]:
            print("    %-28s %s%s%s  %s" % (res.key, G if res.tier == "verified" else Y,
                                            (res.value or "")[:24], R, cite(res.winner)))
        if len(envs) > 8:
            print("    %s+%d more%s" % (D, len(envs) - 8, R))
        print()

    if report.conflicts:
        print("  %s%sConflicts%s  %s-- the README disagrees with what CI executes%s"
              % (B, Y, R, D, R))
        for res, losing, count in report.conflicts:
            more = "  %s(and %d more like it)%s" % (D, count - 1, R) if count > 1 else ""
            print("    %s%s%s  %s says %s%s%s %s"
                  % (B, res.key, R, res.winner.provider, G, res.value, R,
                     cite(res.winner)))
            print("      %s%s says %s%s  %s%s" % (Y, losing.provider, losing.value, R,
                                                  cite(losing), more))
            if losing.note:
                print("        %s%s%s" % (D, losing.note[:88], R))
        print()

    if report.undocumented:
        print("  %sVerified but undocumented%s  %s-- CI needs it, the prose never says so%s"
              % (B, R, D, R))
        for res in [r for r in report.undocumented if r.winner][:10]:
            print("    %-12s %-30s %s" % (res.key, (res.value or "")[:30],
                                          cite(res.winner)))
        if len(report.undocumented) > 10:
            print("    %s+%d more%s" % (D, len(report.undocumented) - 10, R))
        print()

    unres = [r for r in report.resolutions if r.unresolved]
    if unres:
        print("  %sFell through%s  %s-- source said something unreadable, "
              "precedence moved on%s" % (B, R, D, R))
        for res in unres[:6]:
            u = res.unresolved[0]
            win = "-> %s %s" % (res.value, cite(res.winner)) if res.winner else "-> nothing lower"
            print("    %-10s %s%s%s %s %s" % (res.key, D, u.value[:44], R, cite(u), win))
        print()
    return report


if __name__ == "__main__":
    sys.exit(main())
