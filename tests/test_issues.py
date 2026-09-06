"""Tests for issue mining, the only step that spends API rate limit.

The rule from the spec: a Play that dies at the last step in front of a judge
scores zero on functionality. Phases A-E already produce a useful document
with no API calls, so every failure here must degrade rather than raise.
"""
import os
import sys
import urllib.error

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import issues

FAILED = []


def check(name, got, want):
    if got != want:
        FAILED.append("%s: got %r, want %r" % (name, got, want))


def stub(response=None, error=None):
    def _get(url, token):
        if error:
            raise error
        return response or {"items": []}
    issues._get = _get


def item(number, title, body="", labels=(), comments=0):
    return {"number": number, "title": title, "body": body,
            "labels": [{"name": l} for l in labels], "comments": comments,
            "html_url": "https://github.com/o/r/issues/%d" % number,
            "state": "open", "reactions": {"total_count": 0}}


def restore():
    import importlib
    importlib.reload(issues)


def test_rate_limit_degrades_instead_of_raising():
    stub(error=urllib.error.HTTPError("u", 403, "rate limited", {}, None))
    found, status, note = issues.mine("o", "r", token="t")
    check("status", status, "rate_limited")
    check("no findings invented", found, [])
    check("note explains", "rate limit" in note.lower(), True)
    restore()


def test_network_failure_degrades():
    stub(error=urllib.error.URLError("no route to host"))
    found, status, _ = issues.mine("o", "r", token="t")
    check("status", status, "error")
    check("no findings invented", found, [])
    restore()


def test_partial_results_survive_a_later_failure():
    """Two queries in, the third 403s. The first two findings still count."""
    calls = {"n": 0}

    def _get(url, token):
        calls["n"] += 1
        if calls["n"] >= 2:
            raise urllib.error.HTTPError("u", 403, "rate limited", {}, None)
        return {"items": [item(7, "Cannot install on Ubuntu", "cannot install")]}

    issues._get = _get
    found, status, _ = issues.mine("o", "r", token="t", sleep=0)
    check("kept what it found", [f["number"] for f in found], [7])
    check("still reports the limit", status, "rate_limited")
    restore()


def test_phrase_must_actually_appear():
    stub({"items": [item(1, "Unrelated bug", "nothing relevant here"),
                    item(2, "Cannot install on Ubuntu", "cannot install fails")]})
    found, status, _ = issues.mine("o", "r", token="t", max_queries=1, sleep=0)
    check("loose matches dropped", [f["number"] for f in found], [2])
    restore()


def test_feature_requests_are_not_setup_problems():
    """netbox: 'cannot install' appears in issues about device modules."""
    stub({"items": [
        item(1, "Support for half-width device types", "cannot install"),
        item(2, "Extend the {module} variable", "cannot install"),
        item(3, "Failed building wheel for psycopg-c", "cannot install"),
        item(4, "Docker build broken", "cannot install", labels=["enhancement"]),
    ]})
    found, _, _ = issues.mine("o", "r", token="t", max_queries=1, sleep=0)
    check("only the real one survives", [f["number"] for f in found], [3])
    restore()


def test_label_query_requires_the_label():
    """`label:setup` on a repo without it returns anything mentioning setup."""
    stub({"items": [item(1, "Something about setup", "setup"),
                    item(2, "Real one", "", labels=["setup"])]})
    found, _, _ = issues.mine("o", "r", token="t", max_queries=5, sleep=0)
    nums = [f["number"] for f in found]
    check("unlabelled match dropped", 1 in nums, False)
    check("labelled match kept", 2 in nums, True)
    restore()


def test_unauthenticated_cap_is_lower():
    check("anon cap below authed cap",
          issues.MAX_QUERIES_ANON < issues.MAX_QUERIES_AUTHED, True)
    check("anon cap stays inside the 10/min search budget",
          issues.MAX_QUERIES_ANON <= 3, True)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    if FAILED:
        print("FAILED %d checks:" % len(FAILED))
        for f in FAILED:
            print("  - " + f)
        sys.exit(1)
    print("ok: %d issue-mining tests passed" % len(tests))
