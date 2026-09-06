"""Failure-path tests, run through the CLI as a subprocess.

These paths are the ones that only execute when something has already gone
wrong, which is exactly why they rot: a missing import in an error branch
stays invisible until a stranger hits it. Running the real command catches
that; importing the module does not.

Needs network for the cases that clone. Skips those if it is unavailable.
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(os.path.dirname(HERE), "factcheck.py")
FAILED = []


def check(name, got, want):
    if got != want:
        FAILED.append("%s: got %r, want %r" % (name, got, want))


def run(*args, **kw):
    return subprocess.run([sys.executable, CLI] + list(args),
                          capture_output=True, text=True, timeout=300, **kw)


def online():
    r = subprocess.run(["git", "ls-remote", "https://github.com/pallets/flask"],
                       capture_output=True, text=True, timeout=60)
    return r.returncode == 0


def test_bad_input_never_traces():
    for bad in ("https://gitlab.com/a/b", "not-a-url", "https://github.com/only-owner"):
        r = run(bad, "--quiet-ci", "-o", os.devnull)
        check("%s exits 2" % bad, r.returncode, 2)
        check("%s prints no traceback" % bad, "Traceback" in r.stderr, False)
        check("%s explains itself" % bad, len(r.stderr.strip()) > 10, True)


def test_missing_repo_never_traces():
    if not online():
        return
    r = run("HaColin/definitely-not-real-xyz", "--quiet-ci", "-o", os.devnull)
    check("exits 1", r.returncode, 1)
    check("no traceback", "Traceback" in r.stderr, False)
    check("names the repo", "cannot clone" in r.stderr, True)


def test_unwritable_output_never_traces():
    if not online():
        return
    tmp = tempfile.mkdtemp()
    try:
        ro = os.path.join(tmp, "ro")
        os.makedirs(ro)
        os.chmod(ro, 0o500)
        r = run("pallets/flask", "--quiet-ci", "-o", os.path.join(ro, "x.md"))
        check("exits 1", r.returncode, 1)
        check("no traceback", "Traceback" in r.stderr, False)
        check("says what it could not write", "cannot write" in r.stderr, True)
    finally:
        os.chmod(os.path.join(tmp, "ro"), 0o700)
        shutil.rmtree(tmp, ignore_errors=True)


def test_interrupted_clone_recovers():
    """A clone killed partway leaves a .git with no HEAD. Reusing it failed
    every later run with the same error until the cache was deleted by hand."""
    if not online():
        return
    tmp = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmp, "pallets__flask", ".git"))
        out = os.path.join(tmp, "out.md")
        r = run("pallets/flask", "--quiet-ci", "--cache-dir", tmp, "-o", out)
        check("recovers and succeeds", r.returncode, 0)
        check("no traceback", "Traceback" in r.stderr, False)
        check("wrote the document", os.path.exists(out), True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    if FAILED:
        print("FAILED %d checks:" % len(FAILED))
        for f in FAILED:
            print("  - " + f)
        sys.exit(1)
    print("ok: %d robustness tests passed" % len(tests))
