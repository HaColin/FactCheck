"""FACTCHECK phase D: emit the document.

Every factual line carries the file and line it came from, rendered as a
link into the repo at the exact commit that was read. The rule from the
spec: if a claim cannot cite a file and a line, it does not go in.

The output is deterministic. No timestamps, no wall-clock, no ordering that
depends on a dict -- the same repo at the same commit renders byte-identical
output, which is the property that makes the method worth capturing.
"""
import os

import precedence

LEGEND = ("**verified** = executed by CI or a container build  ·  "
          "*claimed* = prose a human wrote once")

FACT_TITLES = [
    ("install", "Install"),
    ("setup", "Setup"),
    ("build", "Build"),
    ("test", "Test"),
    ("lint", "Lint"),
]


def blob(meta, path, line):
    return "%s/blob/%s/%s#L%d" % (meta["url"].rstrip("/"), meta["sha"], path, line)


def cite(meta, claim):
    return "[`%s:%d`](%s)" % (claim.path, claim.line,
                              blob(meta, claim.path, claim.line))


def _mark(tier):
    return "verified" if tier == "verified" else "claimed"


def render(meta, inv, wfs, report):
    out = []
    w = out.append

    w("# FACTCHECK: %s/%s" % (meta["owner"], meta["name"]))
    w("")
    w("What it takes to run this repo, read from CI rather than from prose.")
    w("")
    primary = meta.get("primary")
    if primary:
        w("- **Primary CI:** [`%s`](%s) — runs on %s"
          % (primary["path"], blob(meta, primary["path"], 1),
             ", ".join(primary["triggers"][:4]) or "?"))
    w("- **Commit:** [`%s`](%s/tree/%s) on `%s`"
      % (meta["sha"][:12], meta["url"].rstrip("/"), meta["sha"], meta["branch"]))
    w("- **Method:** a [fixed precedence table](#method), applied as code. "
      "Same commit in, same document out.")
    w("")
    w(LEGEND)
    w("")

    if not primary:
        w("> **No CI runs on merge in this repo.** Nothing below is verified — "
          "there is no executed configuration to check the prose against, so "
          "every line here is a claim someone wrote, carried through with its "
          "source attached.")
        w("")

    _conflicts(w, meta, report)
    _undocumented(w, meta, report)
    _runtime(w, meta, report)
    _services(w, meta, report)
    _commands(w, meta, report)
    _environment(w, meta, report)
    _os(w, meta, report)
    _unverified(w, meta, report)
    _sources(w, meta, inv, wfs)
    _method(w)

    return "\n".join(out).rstrip() + "\n"


def _h(w, title):
    w("## " + title)
    w("")


def _conflicts(w, meta, report):
    _h(w, "Conflicts")
    if not report.conflicts:
        if meta.get("primary"):
            w("Nothing in the prose contradicts what CI executes.")
        else:
            w("No CI to compare the prose against, so no conflict can be "
              "established either way.")
        w("")
        return
    w("Where the documentation and the executed configuration disagree. CI wins "
      "because CI runs; that is the only reason.")
    w("")
    grouped = []
    for res, losing, count in report.conflicts:
        for key, entries in grouped:
            if key == (res.fact, res.key):
                entries.append((losing, count))
                break
        else:
            grouped.append(((res.fact, res.key), [(losing, count)]))
    seen_res = {(r.fact, r.key): r for r, _, _ in report.conflicts}

    for key, entries in grouped:
        res = seen_res[key]
        w("### %s" % res.key)
        w("")
        w("- `%s` says **%s** — %s"
          % (res.winner.provider, res.value, cite(meta, res.winner)))
        for losing, count in entries:
            extra = "  _(and %d more like it)_" % (count - 1) if count > 1 else ""
            w("- `%s` says *%s* — %s%s"
              % (losing.provider, losing.value, cite(meta, losing), extra))
            if losing.note:
                w("  > %s" % losing.note.strip()[:180])
        w("")


def _undocumented(w, meta, report):
    rows = [r for r in report.undocumented if r.winner]
    if not rows:
        return
    _h(w, "Required but undocumented")
    w("CI needs these. The prose never mentions them — which is usually why a "
      "fresh clone does not run.")
    w("")
    w("| What | Value | Source |")
    w("|---|---|---|")
    for res in rows[:30]:
        w("| `%s` | %s | %s |" % (res.key, _fmt(res.value), cite(meta, res.winner)))
    if len(rows) > 30:
        w("")
        w("_%d more omitted._" % (len(rows) - 30))
    w("")


def _fmt(value):
    v = str(value or "").replace("|", "\\|")
    return "`%s`" % v if v else "—"


def _runtime(w, meta, report):
    rows = [r for r in report.by_fact("runtime") if r.winner]
    if not rows:
        return
    _h(w, "Runtime")
    w("| Tool | Version | Source | |")
    w("|---|---|---|---|")
    for res in rows:
        w("| %s | %s | %s | %s |" % (res.key, _fmt(res.value),
                                     cite(meta, res.winner), _mark(res.tier)))
    w("")
    fell = [r for r in rows if r.unresolved]
    if fell:
        w("A higher-authority source was present but not literal, so the table "
          "fell through to what is shown above:")
        w("")
        for res in fell[:6]:
            u = res.unresolved[0]
            w("- `%s`: `%s` at %s could not be read as a version"
              % (res.key, u.value[:60], cite(meta, u)))
        w("")


def _services(w, meta, report):
    rows = [r for r in report.by_fact("services") if r.winner]
    if not rows:
        return
    _h(w, "Services required")
    w("| Service | Image | Where | Source |")
    w("|---|---|---|---|")
    for res in rows:
        w("| %s | %s | %s | %s |"
          % (res.key, _fmt(res.value), res.winner.note or "—",
             cite(meta, res.winner)))
    w("")
    unpinned = [r for r in rows if ":" not in str(r.value or "")]
    if unpinned:
        w("_%s: the image is unpinned in CI, so no version is asserted here._"
          % ", ".join("`%s`" % r.key for r in unpinned))
        w("")


def _commands(w, meta, report):
    for fact, title in FACT_TITLES:
        rows = [r for r in report.by_fact(fact) if r.winner]
        if not rows:
            continue
        _h(w, title)
        for res in rows:
            for m in res.members[:12]:
                where = " · %s" % m.note if m.note else ""
                w("- `%s` — %s%s" % (str(m.value).replace("`", "'"),
                                     cite(meta, m), where))
        w("")


def _environment(w, meta, report):
    rows = [r for r in report.by_fact("env") if r.winner]
    if not rows:
        return
    _h(w, "Environment")
    w("| Variable | Value in CI | Source | |")
    w("|---|---|---|---|")
    for res in rows[:30]:
        w("| `%s` | %s | %s | %s |" % (res.key, _fmt(res.value),
                                       cite(meta, res.winner), _mark(res.tier)))
    if len(rows) > 30:
        w("")
        w("_%d more omitted._" % (len(rows) - 30))
    w("")


def _os(w, meta, report):
    rows = [r for r in report.by_fact("os") if r.winner]
    if not rows:
        return
    _h(w, "Tested on")
    for res in rows:
        for m in res.members[:8]:
            w("- `%s` — %s" % (m.value, cite(meta, m)))
    w("")
    w("_Only these are evidenced. Other platforms may work; CI does not say so._")
    w("")


def _unverified(w, meta, report):
    rows = [r for r in report.unverified if r.winner]
    if not rows:
        return
    _h(w, "Claimed, not verified")
    w("The prose gives these commands; nothing in CI executes them.")
    w("")
    for res in rows[:12]:
        for m in res.members[:4]:
            w("- `%s` — %s" % (str(m.value).replace("`", "'"), cite(meta, m)))
    w("")


def _sources(w, meta, inv, wfs):
    _h(w, "Sources read")
    w("| Category | Files |")
    w("|---|---|")
    for cat, _ in _categories():
        hits = inv.get(cat) or []
        shown = ", ".join("`%s`" % h for h in hits[:6])
        if len(hits) > 6:
            shown += " _+%d more_" % (len(hits) - 6)
        w("| %s | %s |" % (cat, shown or "_none found_"))
    w("")
    auth = [wf for wf in wfs if wf.get("authoritative")]
    if auth:
        w("Workflows treated as evidence, in order of authority over what runs "
          "on every merge:")
        w("")
        for wf in auth[:8]:
            w("- [`%s`](%s) — on %s" % (wf["path"], blob(meta, wf["path"], 1),
                                        ", ".join(wf["triggers"][:4])))
        w("")


def _categories():
    import collect
    return collect.CATEGORIES


def _method(w):
    _h(w, "Method")
    w("Each fact is resolved by walking a fixed list of sources and taking the "
      "first one that says something readable. The list is code, not a prompt, "
      "so the same commit always produces the same document.")
    w("")
    w("| Fact | Source order, highest authority first |")
    w("|---|---|")
    for fact, order in precedence.PRECEDENCE.items():
        w("| %s | %s |" % (fact, " → ".join("`%s`" % p for p in order)))
    w("")
    w("Rules the table applies:")
    w("")
    w("1. Only workflows triggered on push, pull request or merge queue count "
      "as evidence — CI is ground truth because it runs on every merge.")
    w("2. A value that is not literal (`${{ steps.x.outputs.y }}`) never wins, "
      "and is never printed as an answer.")
    w("3. One source disagreeing with itself is a matrix, not a conflict.")
    w("4. A conflict requires two different kinds of source.")
    w("5. Version constraints keep their operators: `>=3.7` is not `3.7`.")
    w("")
    w("---")
    w("")
    w("Generated by [FACTCHECK](https://github.com/HaColin/factcheck). "
      "No claim appears here without a file and a line behind it.")
