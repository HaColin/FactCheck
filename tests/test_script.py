"""Tests for the generated setup script.

A script is a sharper object than a document: a wrong line in a document
misleads, a wrong line in a script runs. These tests hold the generator to
the conservative rules -- and check the output is valid bash by asking bash.
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import precedence
import script
from claims import Claim

FAILED = []
META = {"owner": "acme", "name": "widget",
        "url": "https://github.com/acme/widget",
        "sha": "0123456789abcdef0123456789abcdef01234567", "branch": "main",
        "primary": {"path": ".github/workflows/ci.yml",
                    "triggers": ["push", "pull_request"]}}
CI = ".github/workflows/ci.yml"


def check(name, got, want):
    if got != want:
        FAILED.append("%s: got %r, want %r" % (name, got, want))


def report_with(claims):
    return precedence.reconcile(claims, {CI: 20}, "")


def base_claims():
    return [
        Claim("runtime", "python", "3.12", "ci-setup", CI, 10),
        Claim("services", "postgres", "postgres:15", "ci-services", CI, 31,
              note="job test, ports 5432:5432"),
        Claim("env", "MIX_ENV", "test", "ci-env", CI, 12, note="job test"),
        Claim("install", "install", "pip install -r requirements.txt",
              "ci-run", CI, 44, note="job test"),
        Claim("test", "test", "pytest -q", "ci-run", CI, 48, note="job test"),
    ]


def generate(claims=None):
    return script.render_script(META, report_with(claims or base_claims()))


def test_is_valid_bash():
    sh = generate()
    with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as fh:
        fh.write(sh)
        path = fh.name
    try:
        r = subprocess.run(["bash", "-n", path], capture_output=True, text=True)
        check("bash -n accepts the script", (r.returncode, r.stderr), (0, ""))
    finally:
        os.unlink(path)


def test_dry_run_executes_cleanly():
    """--dry-run must print everything and run none of it."""
    sh = generate()
    with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as fh:
        fh.write(sh)
        path = fh.name
    try:
        r = subprocess.run(["bash", path, "--dry-run"], capture_output=True,
                           text=True, timeout=30)
        check("exit code", r.returncode, 0)
        check("shows the install command",
              "pip install -r requirements.txt" in r.stdout, True)
        check("cites the source line", CI + ":44" in r.stdout, True)
    finally:
        os.unlink(path)


def test_dangerous_commands_are_not_run():
    cases = [
        ("npm publish", "drop"),
        ("docker push acme/widget", "drop"),
        ("gh release create v1", "drop"),
        ("echo x >> $GITHUB_ENV", "drop"),
        # django: initdb -D "$GITHUB_WORKSPACE/.tmp/pgdata" is runner-only.
        ('initdb -D "$GITHUB_WORKSPACE/.tmp/pgdata"', "drop"),
        ("cp x $RUNNER_TEMP/y", "drop"),
        ("pip install ${{ matrix.pkg }}", "drop"),
        ("sudo apt-get install -y libpq-dev", "manual"),
        ("npm install -g yarn", "manual"),
        ("rm -rf build", "manual"),
        ("pip install -r requirements.txt", "keep"),
        ("pytest -q", "keep"),
    ]
    for cmd, want in cases:
        check("classify_command(%r)" % cmd, script.classify_command(cmd)[0], want)


def test_root_commands_are_printed_not_executed():
    claims = base_claims() + [
        Claim("install", "install", "sudo apt-get install -y libpq-dev",
              "ci-run", CI, 40, note="job test")]
    sh = generate(claims)
    check("shown to the reader", "libpq-dev" in sh, True)
    check("never handed to step()", "step '.github/workflows/ci.yml:40'" in sh,
          False)


def test_env_export_picks_one_value():
    """Two jobs, two values. A document can show both; a script cannot."""
    claims = base_claims() + [
        Claim("env", "MIX_ENV", "e2e_test", "ci-env", CI, 99, note="job e2e")]
    sh = generate(claims)
    exports = [l for l in sh.split("\n") if l.startswith("export MIX_ENV=")]
    check("exactly one export", len(exports), 1)
    check("no joined value", "|" in exports[0], False)


def test_env_key_that_is_not_a_shell_identifier():
    """keycloak: CI sets `old-version`; `export old-version=…` is a runtime
    syntax error that bash -n does not catch."""
    claims = base_claims() + [
        Claim("env", "old-version", "24.0.4", "ci-env", CI, 20, note="job test")]
    sh = generate(claims)
    check("never exported", "export old-version=" in sh, False)
    check("still reported to the reader", "old-version" in sh, True)


def test_service_becomes_a_runnable_docker_command():
    sh = generate()
    check("port checked", "port_open 5432" in sh, True)
    check("docker command offered",
          "docker run -d --name factcheck-postgres -p 5432:5432" in sh, True)
    check("uses the pinned image", "postgres:15" in sh, True)


def test_deterministic():
    check("same input, same script", generate(), generate())


def test_header_states_its_limits():
    # The header wraps across comment lines, so strip the `#` markers and
    # normalise whitespace before looking for the phrases.
    head = generate().split("\nset -euo")[0]
    sh = " ".join(l.lstrip("#").strip() for l in head.split("\n"))
    sh = " ".join(sh.split())
    for phrase in ("disposable machine", "publishes", "needing sudo",
                   "is not reproduced here"):
        if phrase not in sh:
            FAILED.append("header does not mention %r" % phrase)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    if FAILED:
        print("FAILED %d checks:" % len(FAILED))
        for f in FAILED:
            print("  - " + f)
        sys.exit(1)
    print("ok: %d script tests passed" % len(tests))
