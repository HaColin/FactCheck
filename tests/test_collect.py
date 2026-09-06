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
