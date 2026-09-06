"""FACTCHECK phase A: collect. Zero GitHub API calls.

Shallow clone with blobs filtered, then inventory the files that carry
setup facts. Nothing here touches api.github.com, so nothing here spends
the 60 req/hour unauthenticated budget.
"""
import os
import re
import subprocess

CATEGORIES = [
    ("ci",        [".github/workflows/", ".gitlab-ci.yml", ".circleci/config.yml",
                   "azure-pipelines.yml", ".travis.yml", "Jenkinsfile"]),
    ("container", ["Dockerfile", "docker-compose.yml", "docker-compose.yaml",
                   "compose.yml", "compose.yaml", ".devcontainer/devcontainer.json"]),
    ("manifest",  ["package.json", "pyproject.toml", "setup.py", "setup.cfg",
                   "requirements.txt", "Cargo.toml", "go.mod", "Gemfile",
                   "pom.xml", "build.gradle", "build.gradle.kts", "mix.exs",
                   "composer.json", "Makefile", "justfile", "Taskfile.yml"]),
    ("lockfile",  ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb",
                   "uv.lock", "poetry.lock", "Pipfile.lock", "requirements.lock",
                   "Cargo.lock", "go.sum", "Gemfile.lock", "mix.lock",
                   "composer.lock"]),
    ("toolchain", [".nvmrc", ".python-version", ".tool-versions", ".ruby-version",
                   "rust-toolchain", "rust-toolchain.toml", ".node-version",
                   ".go-version", ".sdkmanrc"]),
    ("env",       [".env.example", ".env.sample", ".env.template", ".env.dist"]),
    ("prose",     ["README", "INSTALL", "CONTRIBUTING", "DEVELOPMENT", "HACKING",
                   "docs/README", "docs/INSTALL", "docs/development",
                   "docs/CONTRIBUTING", "docs/getting-started"]),
]

REPO_RE = re.compile(
    r"(?:https?://(?:www\.)?github\.com/|git@github\.com:)([^/\s]+)/([^/\s]+?)(?:\.git)?/?$")


def parse_repo_url(url):
    """-> (owner, name, clone_url). Accepts owner/name shorthand too."""
    url = url.strip()
    m = REPO_RE.match(url)
    if not m:
        m = re.match(r"^([\w.-]+)/([\w.-]+)$", url)
        if not m:
            raise ValueError("not a GitHub repo URL: %r" % url)
    owner, name = m.group(1), m.group(2)
    return owner, name, "https://github.com/%s/%s.git" % (owner, name)


def clone(clone_url, dest):
    """Shallow, blobless clone. Blobs arrive on demand when we read a file."""
    if os.path.isdir(os.path.join(dest, ".git")):
        return dest
    subprocess.run(
        ["git", "clone", "--depth", "1", "--filter=blob:none", "--quiet",
         clone_url, dest],
        check=True, capture_output=True, text=True, timeout=300)
    return dest


def default_branch(root):
    r = subprocess.run(["git", "-C", root, "rev-parse", "--abbrev-ref", "HEAD"],
                       capture_output=True, text=True)
    return r.stdout.strip() or "HEAD"


def head_sha(root):
    r = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"],
                       capture_output=True, text=True)
    return r.stdout.strip()


def tracked_files(root):
    """Every path in the tree, from the index -- no blob fetch needed."""
    r = subprocess.run(["git", "-C", root, "ls-files"],
                       capture_output=True, text=True, check=True)
    return [p for p in r.stdout.splitlines() if p]


def inventory(root):
    """Map category -> [paths present], matching the phase A table."""
    files = tracked_files(root)
    lower = {p.lower(): p for p in files}
    found = {}
    for cat, patterns in CATEGORIES:
        hits = []
        for pat in patterns:
            if pat.endswith("/"):
                hits += [p for p in files
                         if p.startswith(pat) and p.rsplit(".", 1)[-1] in ("yml", "yaml")]
            elif cat == "prose":
                # README, README.md, readme.rst, docs/README.md ...
                pl = pat.lower()
                hits += [p for k, p in lower.items()
                         if k == pl or k.startswith(pl + ".")]
            else:
                p = lower.get(pat.lower())
                if p:
                    hits.append(p)
        seen, uniq = set(), []
        for h in hits:
            if h not in seen:
                seen.add(h)
                uniq.append(h)
        found[cat] = uniq
    return found


def read(root, relpath, limit=400_000):
    path = os.path.join(root, relpath)
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read(limit)
    except (OSError, IsADirectoryError):
        return None
