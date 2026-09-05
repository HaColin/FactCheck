"""Tests for the reconciliation rules.

The precedence table is the method this Play captures, so its behaviour is
pinned here rather than left to whatever the code happens to do today. Each
version-comparison case below came from a real repo that produced a wrong
answer before the rule existed.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import precedence
import sources
from claims import Claim

FAILED = []


def check(name, got, want):
    if got != want:
        FAILED.append("%s: got %r, want %r" % (name, got, want))


def test_version_agreement():
    cases = [
        # a           b            agree?  why it is here
        ("16",        "20",        False),  # the headline conflict
        ("20",        "20.11.0",   True),   # shared prefix
        ("3.9+",      "3.12",      True),   # README lower bound
        (">=18",      "20",        True),   # manifest lower bound
        (">=3.9",     "3.8",       False),
        ("^18.0.0",   "20",        False),  # caret pins the major
        ("~3.10",     "3.10.4",    True),   # npm tilde
        ("~> 3.4",    "3.3",       False),  # Ruby/Elixir arrow is a lower bound
        ("~> 1.18",   "1.20.4",    True),
        ("18 || 20",  "20",        True),   # engines alternatives
        (">=24 <25",  "24.13.0",   True),   # compound range, posthog
        (">= 22 <25", "24.11.0",   True),   # spaced compound range, grafana
        (">= 22 <25", "25.1",      False),
        ("20.x",      "20.11",     True),
    ]
    for a, b, want in cases:
        check("versions_agree(%r, %r)" % (a, b), precedence.versions_agree(a, b), want)


def test_unresolved_falls_through():
    """plausible/analytics: CI reads its version from a step's output.

    The CI value outranks .tool-versions in the table, but it is not literal,
    so it must not win -- and it must not be printed as the answer either.
    """
    ci = Claim("runtime", "elixir", "${{ steps.versions.outputs.elixir }}",
               "ci-setup", ".github/workflows/elixir.yml", 63, resolved=False)
    pin = Claim("runtime", "elixir", "1.18.4", "toolchain-file",
                ".tool-versions", 2)
    res = precedence.resolve("runtime", "elixir", [ci, pin])
    check("winner falls through to the pin", res.winner.provider, "toolchain-file")
    check("value is literal", res.value, "1.18.4")
    check("the unreadable claim is still recorded", len(res.unresolved), 1)


def test_matrix_is_a_set_not_a_conflict():
    """wagtail: four jobs, four Python versions, one workflow. Not a fight."""
    group = [Claim("runtime", "python", v, "ci-setup",
                   ".github/workflows/test.yml", line)
             for v, line in (("3.11", 70), ("3.12", 142), ("3.13", 239), ("3.14", 297))]
    res = precedence.resolve("runtime", "python", group)
    check("no conflicts within one source", len(res.conflicts), 0)
    check("all versions kept", sorted(res.values), ["3.11", "3.12", "3.13", "3.14"])


def test_cross_source_disagreement_is_a_conflict():
    """The product: prose that contradicts what CI executes."""
    ci = Claim("runtime", "node", "20", "ci-setup",
               ".github/workflows/ci.yml", 23)
    readme = Claim("runtime", "node", "16", "readme", "README.md", 41)
    res = precedence.resolve("runtime", "node", [ci, readme])
    check("CI wins", res.winner.provider, "ci-setup")
    check("README is reported as a conflict", len(res.conflicts), 1)
    check("conflict cites its line", res.conflicts[0].cite, "README.md:41")


def test_precedence_order_is_the_table():
    """Every source present at once: the table alone decides."""
    group = [
        Claim("runtime", "node", "18", "readme", "README.md", 5),
        Claim("runtime", "node", "19", "manifest-engines", "package.json", 9),
        Claim("runtime", "node", "20", "dockerfile-from", "Dockerfile", 1),
        Claim("runtime", "node", "21", "ci-setup", ".github/workflows/ci.yml", 7),
        Claim("runtime", "node", "22", "toolchain-file", ".nvmrc", 1),
    ]
    for expected in ("toolchain-file", "ci-setup", "dockerfile-from",
                     "manifest-engines", "readme"):
        res = precedence.resolve("runtime", "node", group)
        check("winner is %s" % expected, res.winner.provider, expected)
        group = [c for c in group if c.provider != expected]
        if not group:
            break


def test_services_pinned_beats_unpinned():
    group = [Claim("services", "postgres", "postgres", "ci-services", "ci.yml", 9),
             Claim("services", "postgres", "postgres:17", "ci-services", "ci.yml", 20)]
    res = precedence.resolve("services", "postgres", group)
    check("keeps the pinned image", res.values, ["postgres:17"])


def test_lockfile_install_mapping():
    pairs = dict(sources.LOCKFILE_INSTALL)
    check("npm", pairs["package-lock.json"], "npm ci")
    check("uv", pairs["uv.lock"], "uv sync")
    check("cargo", pairs["Cargo.lock"], "cargo build --locked")


def test_command_classification():
    cases = [("npm ci", "install"), ("pytest -q", "test"), ("cargo build", "build"),
             ("ruff check .", "lint"), ("bin/rails db:migrate", "setup"),
             ("uv sync", "install"), ("go test ./...", "test"), ("ls -la", None)]
    for cmd, want in cases:
        check("classify(%r)" % cmd, sources.classify(cmd), want)


def test_claim_requires_provenance():
    try:
        Claim("runtime", "node", "20", "readme", "", 0)
    except ValueError:
        return
    FAILED.append("a claim without a file:line was allowed to exist")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    if FAILED:
        print("FAILED %d checks:" % len(FAILED))
        for f in FAILED:
            print("  - " + f)
        sys.exit(1)
    print("ok: %d precedence tests passed" % len(tests))
