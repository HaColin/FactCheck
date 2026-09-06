"""FACTCHECK phase F: mine the issue tracker. The only step that spends rate limit.

When a person is stuck, they search the issue tracker. This captures that
step -- and it is the one part of FACTCHECK that touches the GitHub API, so
it is budgeted deliberately and never allowed to fail the run.

The ladder, in order:
  1. `gh auth token` -- most developers already have gh authenticated, so this
     is a token with zero signup friction (5000 req/hour, 30 searches/minute).
  2. Unauthenticated, with a hard query cap (search is 10/minute).
  3. On 403, exhaustion, or any network fault: return what was found so far
     and say the section was skipped. Phases A-E already produced a useful
     document with zero API calls; enrichment must never sink the run.
"""
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com/search/issues"

# Ordered by how often each phrasing actually surfaces a setup problem.
# Every entry is a quoted phrase or a label, because both can be verified
# against the returned issue -- see _relevant().
QUERIES = [
    ('"cannot install"', "install failure"),
    ('"installation failed"', "install failure"),
    ('"failed to build"', "build failure"),
    ('"connection refused"', "missing service"),
    ('label:setup', "labelled setup"),
]

MAX_QUERIES_AUTHED = 5
MAX_QUERIES_ANON = 2          # search is 10/minute unauthenticated; stay well under
PER_PAGE = 5
TIMEOUT = 8


def gh_token():
    """Rung one: a token the developer already has."""
    try:
        r = subprocess.run(["gh", "auth", "token"], capture_output=True,
                           text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    tok = (r.stdout or "").strip()
    return tok if r.returncode == 0 and tok else None


def _get(url, token):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "factcheck",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    if token:
        req.add_header("Authorization", "Bearer %s" % token)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


# A phrase match cannot tell "cannot install [this software]" from "cannot
# install [a device module in a bay]" -- netbox has both. These are the
# shapes that are reliably not setup problems.
FEATURE_SHAPED = re.compile(
    r"^\s*(\[?(feature|rfc|proposal|enhancement)\]?\b|support for\b|add support\b"
    r"|extend\b|allow\b|introduce\b|implement\b|consider\b)", re.I)
FEATURE_LABELS = {"enhancement", "feature", "feature request", "type: feature",
                  "kind/feature", "proposal", "rfc"}


def _relevant(term, item):
    """Does the issue actually match what was asked for?

    GitHub search falls back to loose matching -- `label:setup` on a repo with
    no such label returns anything mentioning "setup", which is how a feature
    request ends up filed as a setup gotcha. A phrase must appear in the title
    or body; a label query must actually carry the label.
    """
    if term.startswith("label:"):
        want = term.split(":", 1)[1].strip().lower()
        labels = item.get("labels") or []
        return any(str(l.get("name", "")).lower() == want for l in labels)
    title = str(item.get("title") or "")
    if FEATURE_SHAPED.match(title):
        return False
    labels = {str(l.get("name", "")).lower() for l in (item.get("labels") or [])}
    if labels & FEATURE_LABELS:
        return False
    phrase = term.strip('"').lower()
    hay = "%s\n%s" % (title, item.get("body") or "")
    return phrase in hay.lower()


def mine(owner, name, token=None, max_queries=None, sleep=1.0):
    """-> (findings, status, note). Never raises."""
    token = token if token is not None else gh_token()
    cap = max_queries if max_queries is not None else (
        MAX_QUERIES_AUTHED if token else MAX_QUERIES_ANON)
    findings, seen = [], set()
    status, note = "ok", ("authenticated via gh" if token
                          else "unauthenticated (capped at %d queries)" % cap)

    for i, (term, kind) in enumerate(QUERIES[:cap]):
        q = "repo:%s/%s is:issue %s" % (owner, name, term)
        url = "%s?q=%s&per_page=%d&sort=reactions&order=desc" % (
            API, urllib.parse.quote(q), PER_PAGE)
        try:
            data = _get(url, token)
        except urllib.error.HTTPError as exc:
            if exc.code in (403, 429):
                status = "rate_limited"
                note = "GitHub rate limit reached after %d quer%s" % (
                    i, "y" if i == 1 else "ies")
                break
            status = "error"
            note = "GitHub returned HTTP %d" % exc.code
            break
        except (urllib.error.URLError, OSError, ValueError, TimeoutError) as exc:
            status = "error"
            note = "could not reach the GitHub API (%s)" % type(exc).__name__
            break

        for item in (data.get("items") or [])[:PER_PAGE]:
            num = item.get("number")
            if num in seen or not _relevant(term, item):
                continue
            seen.add(num)
            findings.append({
                "number": num,
                "title": " ".join(str(item.get("title", "")).split())[:140],
                "url": item.get("html_url", ""),
                "state": item.get("state", ""),
                "comments": item.get("comments", 0),
                "reactions": (item.get("reactions") or {}).get("total_count", 0),
                "matched": kind,
            })
        if i + 1 < cap:
            time.sleep(sleep)          # stay inside the per-minute search budget

    # Most-discussed first: a setup problem many people hit outranks a quiet one.
    findings.sort(key=lambda f: (-(f["comments"] + f["reactions"]), f["number"]))
    return findings, status, note
