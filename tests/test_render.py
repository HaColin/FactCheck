"""Tests for the emitted document.

Two properties matter more than layout: the same commit must render the same
bytes, and no factual line may appear without a citation behind it.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import precedence
import render
from claims import Claim

FAILED = []
META = {"owner": "acme", "name": "widget",
        "url": "https://github.com/acme/widget",
        "sha": "0123456789abcdef0123456789abcdef01234567", "branch": "main",
        "primary": {"path": ".github/workflows/ci.yml",
                    "triggers": ["push", "pull_request"]}}
INV = {"ci": [".github/workflows/ci.yml"], "container": [], "manifest":
       ["package.json"], "lockfile": ["package-lock.json"], "toolchain":
       [".nvmrc"], "env": [], "prose": ["README.md"]}


def check(name, got, want):
    if got != want:
        FAILED.append("%s: got %r, want %r" % (name, got, want))


def build_report():
    claims = [
        Claim("runtime", "node", "20", "ci-setup", ".github/workflows/ci.yml", 23),
        Claim("runtime", "node", "16", "readme", "README.md", 41,
              note="Requires Node 16 or later"),
        Claim("services", "postgres", "postgres:15", "ci-services",
              ".github/workflows/ci.yml", 31, note="job test, ports 5432:5432"),
        Claim("install", "install", "npm ci", "ci-run",
              ".github/workflows/ci.yml", 44, note="job test"),
        Claim("test", "test", "npm test", "ci-run",
              ".github/workflows/ci.yml", 48, note="job test"),
        Claim("env", "DATABASE_URL", "postgres://localhost/test", "ci-env",
              ".github/workflows/ci.yml", 12, note="job test"),
        Claim("os", "os", "ubuntu-22.04", "ci-runs-on",
              ".github/workflows/ci.yml", 20),
    ]
    return precedence.reconcile(claims, {".github/workflows/ci.yml": 20},
                                prose_text="A widget. Requires Node 16 or later.")


def test_deterministic():
    """Same input, same bytes. No timestamps, no dict-order dependence."""
    report = build_report()
    a = render.render(META, INV, [], report)
    b = render.render(META, INV, [], build_report())
    check("render is byte-identical across runs", a, b)


def test_every_fact_line_cites_a_source():
    doc = render.render(META, INV, [], build_report())
    bad = []
    for line in doc.split("\n"):
        # Table rows and bullets that assert a value must carry a link.
        if line.startswith("| `") or (line.startswith("- `")
                                      and " says " not in line):
            if "](https://github.com/acme/widget/blob/" not in line:
                bad.append(line)
    check("uncited factual lines", bad, [])


def test_conflict_is_reported_with_both_sides():
    doc = render.render(META, INV, [], build_report())
    check("conflicts section is not empty",
          "Nothing in the prose contradicts" in doc, False)
    check("winner shown", "says **20**" in doc, True)
    check("loser shown", "says *16*" in doc, True)
    check("loser line quoted", "Requires Node 16 or later" in doc, True)


def test_citations_point_at_the_read_commit():
    doc = render.render(META, INV, [], build_report())
    shas = set(re.findall(r"/blob/([0-9a-f]{40})/", doc))
    check("every citation pins the commit that was read", shas, {META["sha"]})


def test_no_placeholder_leaks():
    # The Method section documents the ${{ }} fallthrough rule on purpose, so
    # only the findings above it are checked.
    doc = render.render(META, INV, [], build_report()).split("## Method")[0]
    for bad in ("None", "${{", "%s", "nan"):
        if bad in doc:
            FAILED.append("document contains a leaked placeholder: %r" % bad)


def test_no_ci_says_nothing_is_verified():
    """A repo with no merge-triggered workflow must not imply verification."""
    meta = dict(META, primary=None)
    claims = [Claim("runtime", "node", "18", "readme", "README.md", 3)]
    report = precedence.reconcile(claims, {}, "needs node 18")
    doc = render.render(meta, INV, [], report)
    check("says there is no CI", "No CI runs on merge" in doc, True)
    check("does not claim prose agrees with CI",
          "Nothing in the prose contradicts" in doc, False)


def test_multiline_value_does_not_break_a_row():
    """apache/superset: a CI env value spanning lines broke the markdown row,
    and a broken row loses its citation -- an uncited claim in the document."""
    claims = [Claim("env", "DB_URL",
                    "mysql://a:b@localhost/x?opt=1|2\npostgresql://c:d@localhost/y",
                    "ci-env", ".github/workflows/ci.yml", 12,
                    note="job test")]
    report = precedence.reconcile(claims, {}, "")
    doc = render.render(META, INV, [], report)
    rows = [l for l in doc.split("\n") if l.startswith("| `DB_URL`")]
    check("the row appears", len(rows) > 0, True)
    for row in rows:
        check("row kept its citation",
              "](https://github.com/acme/widget/blob/" in row, True)
        check("literal pipe is escaped", "\\|" in row, True)


def test_unpinned_image_is_not_invented():
    """netbox's CI says `image: postgres`. The document must not say 15."""
    claims = [Claim("services", "postgres", "postgres", "ci-services",
                    ".github/workflows/ci.yml", 99, note="job test")]
    report = precedence.reconcile(claims, {}, "")
    doc = render.render(META, INV, [], report)
    check("says the image is unpinned", "unpinned in CI" in doc, True)
    check("invents no version", bool(re.search(r"postgres:\d", doc)), False)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    if FAILED:
        print("FAILED %d checks:" % len(FAILED))
        for f in FAILED:
            print("  - " + f)
        sys.exit(1)
    print("ok: %d render tests passed" % len(tests))
