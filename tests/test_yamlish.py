"""Offline regression tests for the parser.

Every case below is a real construct found in a real repo's workflows that
silently truncated the document -- the parser stopped early, returned no
error, and the rest of the file (usually most of the jobs) vanished. That
failure mode is invisible without a cross-check, so it gets a test.

    python3 tests/test_yamlish.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import extract
import yamlish

FAILED = []


def check(name, got, want):
    if got != want:
        FAILED.append("%s\n     got:  %r\n     want: %r" % (name, got, want))


def test_multiline_flow_sequence():
    """ggml-org/llama.cpp: `paths: [` spanning lines killed 28 of 50 workflows."""
    doc = yamlish.load(
        "on:\n"
        "  push:\n"
        "    paths: [\n"
        "      'a.c',\n"
        "      'b.h',\n"
        "    ]\n"
        "jobs:\n"
        "  build:\n"
        "    runs-on: ubuntu-24.04\n")
    check("multiline flow: entries", [str(x) for x in doc["on"]["push"]["paths"]],
          ["a.c", "b.h"])
    check("multiline flow: doc survives", list(doc["jobs"]), ["build"])


def test_flow_opening_on_next_line():
    """PostHog/posthog: `needs:` then `[` on its own line."""
    doc = yamlish.load(
        "jobs:\n"
        "  a:\n"
        "    needs:\n"
        "      [\n"
        "        jest,\n"
        "        lint,\n"
        "      ]\n"
        "    runs-on: ubuntu-latest\n"
        "  b:\n"
        "    runs-on: macos-14\n")
    check("flow next line: entries", [str(x) for x in doc["jobs"]["a"]["needs"]],
          ["jest", "lint"])
    check("flow next line: later jobs survive", list(doc["jobs"]), ["a", "b"])


def test_multiline_plain_scalar():
    """PostHog/posthog: `if:` wrapped across lines swallowed the job's steps."""
    doc = yamlish.load(
        "jobs:\n"
        "  a:\n"
        "    if: needs.x.outputs.go == 'true' &&\n"
        "        github.repository == 'o/r'\n"
        "    steps:\n"
        "      - run: make test\n")
    check("plain fold: value", str(doc["jobs"]["a"]["if"]),
          "needs.x.outputs.go == 'true' && github.repository == 'o/r'")
    check("plain fold: steps survive",
          str(doc["jobs"]["a"]["steps"][0]["run"]), "make test")


def test_plain_scalar_starting_on_next_line():
    """PostHog/posthog: `if:` with a trailing comment, value on the line below."""
    doc = yamlish.load(
        "jobs:\n"
        "  a:\n"
        "    if: # why this gate exists\n"
        "      ${{ !cancelled() &&\n"
        "      github.actor != 'dependabot[bot]' }}\n"
        "    steps:\n"
        "      - run: make test\n")
    check("deferred scalar: steps survive",
          str(doc["jobs"]["a"]["steps"][0]["run"]), "make test")


def test_comment_only_sequence_item():
    """getsentry/sentry: `- # note` with the mapping on the following lines."""
    doc = yamlish.load(
        "steps:\n"
        "  - # get a non-default token\n"
        "    uses: some/action@v4\n"
        "    id: token\n"
        "  - name: after\n"
        "    run: echo hi\n")
    check("comment item: count", len(doc["steps"]), 2)
    check("comment item: first parsed", str(doc["steps"][0]["id"]), "token")
    check("comment item: second survives", str(doc["steps"][1]["run"]), "echo hi")


def test_nested_parallel_steps():
    """discourse/discourse: steps nested under `- parallel:`."""
    doc = yamlish.load(
        "steps:\n"
        "  - run: setup\n"
        "  - parallel:\n"
        "      - name: Rubocop\n"
        "        run: bundle exec rubocop\n"
        "      - name: ESLint\n"
        "        run: pnpm lint:js\n")
    runs = [str(s["run"]) for s in extract.iter_steps(doc["steps"])]
    check("nested steps", runs, ["setup", "bundle exec rubocop", "pnpm lint:js"])


def test_block_scalar_stays_whole():
    """Shell control flow must not be split into separate commands."""
    doc = yamlish.load(
        "steps:\n"
        "  - run: |\n"
        "      if [ -f x ]; then\n"
        "        echo yes\n"
        "      fi\n"
        "  - run: echo after\n")
    blk = extract.run_block(doc["steps"][0])
    check("block scalar: whole", blk["script"],
          "if [ -f x ]; then\n  echo yes\nfi")
    check("block scalar: line", blk["line"], 3)
    check("block scalar: next step", str(doc["steps"][1]["run"]), "echo after")


def test_malformed_flow_terminates():
    """Found by fuzzing: `x: {]` looped forever.

    Neither the key token nor the value token consumed a character, so the
    index never moved. A repo with one malformed workflow would have hung the
    tool indefinitely -- worse than crashing, because nothing says why.
    """
    import signal

    def _timeout(sig, frame):
        raise AssertionError("parse did not terminate")

    cases = ["x: {]", "x: [}", "a: {:}", "b: [,,,]", "c: {a: [}", "d: {]}[{",
             "e: [", "f: {", "g: [{]}", "h: {[}]", "i: {,,}", "j: [[[[[[",
             "k: }}}}", "l: {'unclosed", 'm: ["unclosed']
    old = signal.signal(signal.SIGALRM, _timeout)
    try:
        for src in cases:
            signal.setitimer(signal.ITIMER_REAL, 5.0)
            try:
                yamlish.load(src)
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
    finally:
        signal.signal(signal.SIGALRM, old)
    check("malformed flow still yields a mapping",
          isinstance(yamlish.load("x: {]"), dict), True)


def test_on_is_not_true():
    """YAML 1.1 turns `on:` into the boolean True. A workflow means "on"."""
    doc = yamlish.load("on: push\njobs: {}\n")
    check("on stays a string", "on" in doc, True)


def test_line_numbers():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "fixture_workflow.yml")
    doc = yamlish.load_file(path)
    job = doc["jobs"]["test"]
    check("line: runs-on value", job["runs-on"].line, 9)
    check("line: service image", job["services"]["postgres"]["image"].line, 18)
    check("folded scalar", str(job["services"]["postgres"]["options"]),
          "--health-cmd pg_isready --health-interval 10s")
    check("matrix flow seq", [str(x) for x in job["strategy"]["matrix"]["node"]],
          ["18", "20"])


def test_extract_services_and_setup():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "fixture_workflow.yml")
    root = os.path.dirname(os.path.dirname(path))
    wf = extract.extract_workflow(root, "tests/fixture_workflow.yml")
    job = [j for j in wf["jobs"] if j["id"] == "test"][0]
    check("triggers", wf["triggers"], ["push"])
    check("service image", job["services"][0]["image"], "postgres:15")
    check("matrix resolved into setup",
          [s["value"] for s in job["setups"] if s["tool"] == "node"], ["18 | 20"])
    check("runs-on", [v for v, _ in job["runs_on"]], ["ubuntu-22.04"])


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    if FAILED:
        print("FAILED %d of %d checks:" % (len(FAILED), len(tests)))
        for f in FAILED:
            print("  - " + f)
        sys.exit(1)
    print("ok: %d regression tests passed" % len(tests))
