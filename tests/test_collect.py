"""Tests for input handling -- the first thing a stranger touches."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import collect

FAILED = []


def check(name, got, want):
    if got != want:
        FAILED.append("%s: got %r, want %r" % (name, got, want))


def test_shapes_people_actually_paste():
    cases = [
        "https://github.com/pallets/flask",
        "https://github.com/pallets/flask/",
        "https://github.com/pallets/flask.git",
        "http://github.com/pallets/flask",
        "https://www.github.com/pallets/flask",
        "github.com/pallets/flask",
        "pallets/flask",
        "git@github.com:pallets/flask.git",
        "ssh://git@github.com/pallets/flask",
        # What the address bar actually holds while you are reading a repo.
        "https://github.com/pallets/flask/tree/main",
        "https://github.com/pallets/flask/blob/main/README.md",
        "https://github.com/pallets/flask/issues?q=is%3Aopen",
        "https://github.com/pallets/flask#readme",
    ]
    for url in cases:
        try:
            owner, name, clone = collect.parse_repo_url(url)
        except Exception as exc:
            FAILED.append("%r raised %s" % (url, exc))
            continue
        check("owner from %r" % url, owner, "pallets")
        check("name from %r" % url, name, "flask")
        check("clone url from %r" % url, clone,
              "https://github.com/pallets/flask.git")


def test_bad_input_explains_itself():
    for url, expect in [
        ("https://gitlab.com/foo/bar", "not GitHub"),
        ("https://bitbucket.org/foo/bar", "not GitHub"),
        ("https://github.com/pallets", "names no repository"),
        ("not-a-url", "not a GitHub repository"),
        ("", "no repository given"),
    ]:
        try:
            collect.parse_repo_url(url)
        except collect.NotAGitHubRepo as exc:
            if expect not in str(exc):
                FAILED.append("%r said %r, wanted %r" % (url, str(exc), expect))
        except Exception as exc:
            FAILED.append("%r raised %s instead of NotAGitHubRepo" % (url, type(exc).__name__))
        else:
            FAILED.append("%r was accepted but is not a repo" % url)


def test_error_is_a_value_error():
    """Callers that catch ValueError keep working."""
    check("subclasses ValueError",
          issubclass(collect.NotAGitHubRepo, ValueError), True)


def test_system_library_table_is_conservative():
    """A prerequisite that is not really needed costs more trust than it earns."""
    import sources
    # These ship wheels; naming them would send readers to install nothing.
    for absent in ("psycopg2-binary", "pillow", "numpy", "cryptography", "lxml"):
        check("%s is not claimed to need system headers" % absent,
              absent in sources.SYSTEM_LIBS, False)
    # These reliably fail without headers.
    for present in ("psycopg2", "psycopg-c", "mysqlclient", "python-ldap"):
        check("%s is covered" % present, present in sources.SYSTEM_LIBS, True)
    for name, (needs, installs) in sources.SYSTEM_LIBS.items():
        check("%s says what it needs" % name, bool(needs), True)
        for mgr in ("apt", "brew", "pacman", "dnf"):
            check("%s has an install candidate for %s" % (name, mgr),
                  bool(installs.get(mgr)), True)


def test_node_and_ruby_native_dependencies():
    """mastodon's Gemfile needs libpq; the table is not Python-only."""
    import json
    import os
    import shutil
    import tempfile
    import sources
    tmp = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmp, "Gemfile"), "w") as fh:
            fh.write('source "https://rubygems.org"\ngem "rails"\ngem "pg", "~> 1.5"\n')
        with open(os.path.join(tmp, "package.json"), "w") as fh:
            json.dump({"dependencies": {"express": "^4", "canvas": "^2"}}, fh)
        found = {f["package"]: f for f in sources.system_libs(tmp, {"manifest": []})}
        check("ruby pg found", "pg" in found, True)
        check("pg cited to its Gemfile line", found["pg"]["line"], 3)
        check("node canvas found", "canvas" in found, True)
        check("packages without native builds are ignored",
              "rails" in found or "express" in found, False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_psycopg_extras_decide_whether_headers_are_needed():
    """`psycopg[c]` builds from source; `psycopg[binary]` does not."""
    import os
    import tempfile
    import sources
    tmp = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmp, "requirements.txt"), "w") as fh:
            fh.write("django==5.0\npsycopg[c,pool]==3.2\n")
        inv = {"manifest": ["requirements.txt"]}
        found = sources.system_libs(tmp, inv)
        check("psycopg[c] is flagged", [f["package"] for f in found], ["psycopg"])
        check("cited to its line", found[0]["line"], 2)

        with open(os.path.join(tmp, "requirements.txt"), "w") as fh:
            fh.write("psycopg[binary]==3.2\n")
        check("psycopg[binary] is not flagged", sources.system_libs(tmp, inv), [])
    finally:
        import shutil
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
    print("ok: %d input tests passed" % len(tests))
