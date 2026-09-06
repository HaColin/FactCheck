"""FACTCHECK phase C: turn every collected file into Claims.

One function per source of evidence. None of them decide anything -- they
only report what a file says, with the line it said it on. Deciding which
source wins is precedence.py's job, and it is a fixed table.
"""
import json
import os
import re

import collect
import extract
import yamlish
from claims import Claim

try:
    import tomllib
except ImportError:                                   # pragma: no cover
    tomllib = None

# asdf/mise plugin names -> the name everyone else uses
TOOL_ALIASES = {
    "nodejs": "node", "golang": "go", "rust": "rust", "erlang": "erlang",
    "elixir": "elixir", "python": "python", "ruby": "ruby", "java": "java",
    "php": "php", "deno": "deno", "bun": "bun", "dotnet": "dotnet",
    "dotnet-core": "dotnet", "pnpm": "pnpm", "uv": "uv",
}

# Lockfile -> install command. Pure mapping, no inference.
LOCKFILE_INSTALL = [
    ("package-lock.json", "npm ci"),
    ("yarn.lock",         "yarn install --frozen-lockfile"),
    ("pnpm-lock.yaml",    "pnpm install --frozen-lockfile"),
    ("bun.lockb",         "bun install --frozen-lockfile"),
    ("uv.lock",           "uv sync"),
    ("poetry.lock",       "poetry install"),
    ("Pipfile.lock",      "pipenv install --deploy"),
    ("Cargo.lock",        "cargo build --locked"),
    ("go.sum",            "go mod download"),
    ("Gemfile.lock",      "bundle install"),
    ("mix.lock",          "mix deps.get"),
    ("composer.lock",     "composer install"),
]

# Python packages that build from source against system headers. A CI runner
# image ships these already, so CI never mentions them -- which is exactly why
# a fresh clone fails at `pip install` with an error about a missing header.
# Deliberately conservative: psycopg2-binary and Pillow ship wheels and are
# absent, because a prerequisite that is not really required wastes the
# reader's time and costs trust.
SYSTEM_LIBS = {
    "psycopg2":     ("pg_config, from the PostgreSQL client library",
                     {"apt": "libpq-dev", "pacman": "postgresql-libs",
                      "brew": "libpq", "dnf": "libpq-devel"}),
    "psycopg-c":    ("pg_config, from the PostgreSQL client library",
                     {"apt": "libpq-dev", "pacman": "postgresql-libs",
                      "brew": "libpq", "dnf": "libpq-devel"}),
    "mysqlclient":  ("the MySQL client headers",
                     {"apt": "libmysqlclient-dev", "pacman": "mariadb-libs",
                      "brew": "mysql-client", "dnf": "mysql-devel"}),
    "python-ldap":  ("the OpenLDAP headers",
                     {"apt": "libldap2-dev libsasl2-dev", "pacman": "libldap",
                      "brew": "openldap", "dnf": "openldap-devel"}),
    "pycairo":      ("the Cairo headers",
                     {"apt": "libcairo2-dev", "pacman": "cairo",
                      "brew": "cairo", "dnf": "cairo-devel"}),
    "uwsgi":        ("a C toolchain and Python headers",
                     {"apt": "build-essential python3-dev", "pacman": "base-devel",
                      "brew": "gcc", "dnf": "gcc python3-devel"}),
}
# `psycopg[c]` and `psycopg[binary]` are the same distribution with different
# extras; only the C build needs headers.
_REQ_NAME = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*(\[[^\]]*\])?")


def system_libs(root, inv):
    """System packages the dependencies need but CI never mentions.

    Returns dicts, not Claims: there is one source and nothing to rank, and
    the precedence tiers describe what CI executes, which this is not.
    """
    found, seen = [], set()
    files = [p for p in inv.get("manifest", [])
             if re.search(r"requirements.*\.txt$|pyproject\.toml$", p)]
    files += [p for p in tracked_requirements(root) if p not in files]
    for path in files:
        text = collect.read(root, path)
        if not text:
            continue
        for i, raw in enumerate(text.split("\n")):
            line = raw.split("#", 1)[0].strip().strip('",\'')
            m = _REQ_NAME.match(line)
            if not m:
                continue
            name = m.group(1).lower()
            extras = (m.group(2) or "").lower()
            if name == "psycopg" and "c" in extras.strip("[]").split(","):
                name = "psycopg-c"
            if name not in SYSTEM_LIBS or name in seen:
                continue
            seen.add(name)
            needs, installs = SYSTEM_LIBS[name]
            found.append({"package": m.group(1), "needs": needs,
                          "installs": installs, "path": path, "line": i + 1})
    return found


def tracked_requirements(root):
    """requirements.txt files anywhere in the tree, not just at the root."""
    try:
        out = []
        for p in collect.tracked_files(root):
            if re.search(r"(^|/)requirements[\w.-]*\.txt$", p):
                out.append(p)
        return out[:6]
    except Exception:
        return []


# Docker image name -> the runtime it pins.
IMAGE_RUNTIME = {
    "node": "node", "python": "python", "golang": "go", "go": "go",
    "ruby": "ruby", "rust": "rust", "openjdk": "java", "eclipse-temurin": "java",
    "php": "php", "elixir": "elixir", "erlang": "erlang", "denoland/deno": "deno",
    "oven/bun": "bun", "mcr.microsoft.com/dotnet/sdk": "dotnet",
}

# Service images worth naming in the output, keyed by image prefix.
SERVICE_KINDS = ("postgres", "mysql", "mariadb", "redis", "valkey", "mongo",
                 "clickhouse", "elasticsearch", "opensearch", "rabbitmq",
                 "kafka", "memcached", "minio", "localstack", "cassandra",
                 "neo4j", "nats", "zookeeper", "selenium", "chrome")

# Command classification. Order matters: the first hit wins, so the more
# specific patterns come first.
COMMAND_KINDS = [
    ("test", r"\b(pytest|tox|nose2|jest|vitest|mocha|ava|karma|cypress|playwright"
             r"|go test|cargo test|mix test|rspec|minitest|phpunit|gradle test"
             r"|mvn test|npm (?:run )?test|yarn (?:run )?test|pnpm (?:run )?test"
             r"|manage\.py test|bin/rails test|ctest|make test|just test)\b"),
    ("lint", r"\b(ruff|eslint|flake8|pylint|black|isort|mypy|pyright|rubocop"
             r"|credo|clippy|golangci-lint|prettier|stylelint|shellcheck"
             r"|mix format|cargo fmt|gofmt|typecheck|tsc --noEmit)\b"),
    ("install", r"\b(npm ci|npm i\b|npm install|yarn install|yarn --frozen"
                r"|pnpm install|pnpm i\b|bun install|pip install|pip3 install"
                r"|uv sync|uv pip install|poetry install|pipenv install"
                r"|bundle install|cargo fetch|go mod download|mix deps\.get"
                r"|composer install|apt-get install|apt install|brew install"
                r"|dnf install|yum install|apk add|choco install)\b"),
    ("setup", r"\b(migrate|db:create|db:setup|db:migrate|ecto\.create|ecto\.migrate"
              r"|createdb|initdb|collectstatic|assets\.deploy|assets:precompile"
              r"|seed|fixtures|makemigrations)\b"),
    ("build", r"\b(npm run build|yarn build|pnpm build|make\b|cargo build"
              r"|go build|mix compile|tsc\b|webpack|vite build|rollup|esbuild"
              r"|gradle build|mvn package|cmake|ninja|setup\.py build"
              r"|python -m build|docker build|maturin build)\b"),
]


def classify(cmd):
    """install | build | test | lint | setup | None. Deterministic keywords."""
    for kind, pattern in COMMAND_KINDS:
        if re.search(pattern, cmd, re.I):
            return kind
    return None


def _lines(text):
    return text.split("\n")


def _find_line(text, pattern, default=1):
    for i, line in enumerate(_lines(text)):
        if re.search(pattern, line):
            return i + 1
    return default


def _norm_version(v):
    """Tidy a version string without destroying its meaning.

    Constraint operators are deliberately kept: `>=3.7` and `3.7` say very
    different things, and stripping the operator turns every lower bound in
    every manifest into a false conflict against whatever CI actually runs.
    """
    v = str(v).strip().strip("\"'")
    v = re.sub(r"\s+", " ", v)
    v = re.sub(r"\+sha\w+[.\w-]*", "", v)          # packageManager digest
    v = re.sub(r"(?<![\w.])v(?=\d)", "", v)        # v20.11.0 -> 20.11.0
    v = re.sub(r"\.x\b", "", v)                    # 20.x -> 20
    return v.strip()


# ---------------------------------------------------------------- toolchain
def toolchain_files(root, inv):
    """Highest authority for runtime versions: the file the tooling reads."""
    out = []
    simple = {".nvmrc": "node", ".node-version": "node",
              ".python-version": "python", ".ruby-version": "ruby",
              ".go-version": "go"}
    for path, tool in simple.items():
        text = collect.read(root, path)
        if not text:
            continue
        for i, line in enumerate(_lines(text)):
            v = line.strip()
            if v and not v.startswith("#"):
                out.append(Claim("runtime", tool, _norm_version(v),
                                 "toolchain-file", path, i + 1))
                break

    text = collect.read(root, ".tool-versions")
    if text:
        for i, line in enumerate(_lines(text)):
            parts = line.split("#", 1)[0].split()
            if len(parts) >= 2:
                tool = TOOL_ALIASES.get(parts[0].lower(), parts[0].lower())
                out.append(Claim("runtime", tool, _norm_version(parts[1]),
                                 "toolchain-file", ".tool-versions", i + 1))

    for path in ("rust-toolchain.toml", "rust-toolchain"):
        text = collect.read(root, path)
        if not text:
            continue
        m = re.search(r'channel\s*=\s*["\']([^"\']+)', text)
        v = m.group(1) if m else _lines(text)[0].strip()
        if v:
            out.append(Claim("runtime", "rust", _norm_version(v),
                             "toolchain-file", path,
                             _find_line(text, re.escape(v))))
        break
    return out


# --------------------------------------------------------------- containers
def dockerfile(root, inv):
    out = []
    for path in inv.get("container", []):
        if os.path.basename(path).lower() not in ("dockerfile",):
            continue
        text = collect.read(root, path)
        if not text:
            continue
        for i, raw in enumerate(_lines(text)):
            line = raw.strip()
            m = re.match(r"(?i)FROM\s+(\S+)", line)
            if m:
                ref = m.group(1)
                name, _, tag = ref.partition(":")
                tag = tag.split("@")[0]
                tool = IMAGE_RUNTIME.get(name.lower())
                if tool and tag and not tag.startswith("$"):
                    ver = re.split(r"[-_]", tag)[0]
                    if re.match(r"^\d", ver):
                        out.append(Claim("runtime", tool, ver,
                                         "dockerfile-from", path, i + 1))
                continue
            m = re.match(r"(?i)RUN\s+(.+)", line)
            if m:
                cmd = m.group(1).rstrip("\\").strip()
                kind = classify(cmd)
                if kind in ("install", "build"):
                    out.append(Claim(kind, kind, cmd, "dockerfile-run",
                                     path, i + 1))
    return out


def compose(root, inv):
    """docker-compose services -- second authority for what must be running."""
    out = []
    for path in inv.get("container", []):
        if not re.search(r"(docker-)?compose\.ya?ml$", path):
            continue
        text = collect.read(root, path)
        if not text:
            continue
        try:
            doc = yamlish.load(text)
        except Exception:
            continue
        svcs = doc.get("services") if isinstance(doc, dict) else None
        if not isinstance(svcs, dict):
            continue
        for name, cfg in svcs.items():
            if not isinstance(cfg, dict):
                continue
            image = str(cfg.get("image", "")) or None
            if not image:
                continue
            kind = _service_kind(image) or _service_kind(str(name))
            if not kind:
                continue
            ports = [str(p) for p in (cfg.get("ports") or [])]
            cenv = cfg.get("environment")
            env_pairs = ([(str(k), str(v)) for k, v in cenv.items()]
                         if isinstance(cenv, dict) else [])
            out.append(Claim("services", kind, image, "docker-compose", path,
                             cfg.kline("image", svcs.kline(name)),
                             note="ports " + ",".join(ports) if ports else "",
                             data={"ports": ports, "env": env_pairs}))
    return out


def _service_kind(image):
    low = str(image).lower()
    for kind in SERVICE_KINDS:
        if kind in low:
            return kind
    return None


# ---------------------------------------------------------------- manifests
def manifests(root, inv):
    """Manifests are claims, not facts: `engines` is advisory, CI is executed."""
    out = []
    text = collect.read(root, "package.json")
    if text:
        try:
            pkg = json.loads(text)
        except ValueError:
            pkg = {}
        for tool, val in (pkg.get("engines") or {}).items():
            # `"npm": "please-use-pnpm"` is a guard, not a version. A value with
            # no digit in it says nothing about what runtime to install.
            if not re.search(r"\d", str(val)):
                continue
            out.append(Claim("runtime", tool.lower(), _norm_version(val),
                             "manifest-engines", "package.json",
                             _find_line(text, r'"%s"' % re.escape(tool)),
                             note="engines: %s" % val))
        pm = pkg.get("packageManager")
        if isinstance(pm, str) and "@" in pm:
            name, ver = pm.split("@", 1)
            out.append(Claim("runtime", name.lower(), _norm_version(ver),
                             "manifest-engines", "package.json",
                             _find_line(text, "packageManager")))
        for name, script in (pkg.get("scripts") or {}).items():
            kind = classify(script) or classify("npm run " + name)
            if kind in ("build", "test", "lint"):
                out.append(Claim(kind, kind, "npm run " + name,
                                 "manifest-scripts", "package.json",
                                 _find_line(text, r'"%s"\s*:' % re.escape(name)),
                                 note=script))

    text = collect.read(root, "pyproject.toml")
    if text and tomllib:
        try:
            data = tomllib.loads(text)
        except Exception:
            data = {}
        req = (data.get("project", {}).get("requires-python")
               or data.get("tool", {}).get("poetry", {})
                      .get("dependencies", {}).get("python"))
        if req:
            out.append(Claim("runtime", "python", _norm_version(req),
                             "manifest-engines", "pyproject.toml",
                             _find_line(text, "requires-python|^python"),
                             note="requires-python: %s" % req))

    text = collect.read(root, "go.mod")
    if text:
        m = re.search(r"(?m)^go\s+(\d+(?:\.\d+)*)", text)
        if m:
            out.append(Claim("runtime", "go", m.group(1), "manifest-engines",
                             "go.mod", _find_line(text, r"^go\s")))

    text = collect.read(root, "Cargo.toml")
    if text and tomllib:
        try:
            data = tomllib.loads(text)
        except Exception:
            data = {}
        # `rust-version.workspace = true` parses to a table, not a version; the
        # real value lives in [workspace.package] of the root manifest.
        rv = data.get("package", {}).get("rust-version")
        if not isinstance(rv, str):
            rv = data.get("workspace", {}).get("package", {}).get("rust-version")
        if isinstance(rv, str) and rv:
            out.append(Claim("runtime", "rust", _norm_version(rv),
                             "manifest-engines", "Cargo.toml",
                             _find_line(text, "rust-version")))

    text = collect.read(root, "Gemfile")
    if text:
        m = re.search(r'(?m)^\s*ruby\s+["\']([^"\']+)', text)
        if m:
            out.append(Claim("runtime", "ruby", _norm_version(m.group(1)),
                             "manifest-engines", "Gemfile",
                             _find_line(text, r"^\s*ruby\s")))

    text = collect.read(root, "mix.exs")
    if text:
        m = re.search(r'elixir:\s*["\']([^"\']+)', text)
        if m:
            out.append(Claim("runtime", "elixir", _norm_version(m.group(1)),
                             "manifest-engines", "mix.exs",
                             _find_line(text, "elixir:")))
    return out


def lockfiles(root, inv):
    """A lockfile implies its install command. Deterministic mapping."""
    present = set(inv.get("lockfile", []))
    out = []
    for name, cmd in LOCKFILE_INSTALL:
        if name in present:
            out.append(Claim("install", "install", cmd, "lockfile", name, 1,
                             note="implied by the lockfile"))
    return out


# ------------------------------------------------------------------ dotenv
def env_example(root, inv):
    out = []
    for path in inv.get("env", []):
        text = collect.read(root, path)
        if not text:
            continue
        for i, raw in enumerate(_lines(text)):
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.replace("export ", "").strip()
            if not re.match(r"^[A-Z][A-Z0-9_]*$", key):
                continue
            out.append(Claim("env", key, val.strip(), "env-example", path, i + 1))
            kind = _service_kind(val) or (_service_kind(key) if "URL" in key else None)
            if kind:
                out.append(Claim("services", kind, "(implied by %s)" % key,
                                 "env-example", path, i + 1,
                                 note="from the connection string"))
    return out


# ------------------------------------------------------------------- prose
# The operator is captured, not skipped: a README saying "Node >=18" is not
# claiming 18 exactly, and reading it that way invents a conflict with every
# CI that runs anything newer.
_OP = r"(>=|<=|>|<|\^|~>|~)?\s*"
RUNTIME_PROSE = [
    ("node",    r"\bnode(?:\.?js)?\b[^\n\d]{0,18}?" + _OP + r"v?(\d+(?:\.\d+){0,2})(\+?)"),
    ("python",  r"\bpython\b[^\n\d]{0,18}?" + _OP + r"v?(\d+\.\d+(?:\.\d+)?)(\+?)"),
    ("go",      r"\bgo(?:lang)?\b[^\n\d]{0,18}?" + _OP + r"v?(\d+\.\d+(?:\.\d+)?)(\+?)"),
    ("ruby",    r"\bruby\b[^\n\d]{0,18}?" + _OP + r"v?(\d+\.\d+(?:\.\d+)?)(\+?)"),
    ("rust",    r"\brust\b[^\n\d]{0,18}?" + _OP + r"v?(\d+\.\d+(?:\.\d+)?)(\+?)"),
    ("java",    r"\bjava\b[^\n\d]{0,18}?" + _OP + r"v?(\d+(?:\.\d+)?)(\+?)"),
    ("php",     r"\bphp\b[^\n\d]{0,18}?" + _OP + r"v?(\d+\.\d+)(\+?)"),
    ("elixir",  r"\belixir\b[^\n\d]{0,18}?" + _OP + r"v?(\d+\.\d+)(\+?)"),
]
# Version-shaped text inside a link or URL is almost always a pointer to old
# release notes, not a statement about what this repo needs today.
_LINKS = re.compile(r"\]\([^)]*\)|https?://\S+|`[^`]*`")
# "Previous versions additionally supported Python 2.7" is history, not a
# requirement. Inventing a conflict out of it is exactly the kind of wrong
# claim that costs more trust than the finding could ever be worth.
_HISTORICAL = re.compile(
    r"\b(previous|older|earlier|no longer|dropped|deprecat\w*|legacy|used to"
    r"|end.of.life|EOL|prior to|up to|before version)\b", re.I)
CMD_START = re.compile(
    r"^(?:\$\s*)?((?:sudo\s+)?(?:npm|yarn|pnpm|bun|pip3?|uv|poetry|pipenv|python3?|"
    r"cargo|go|make|just|bundle|rake|mix|composer|docker|docker-compose|gradle|"
    r"mvn|dotnet|apt-get|brew|pytest|tox|rails|bin/\S+|\./\S+)\b.*)$")


def readme(root, inv):
    """Prose claims. Never authoritative -- but the conflicts are the product."""
    out = []
    for path in inv.get("prose", []):
        if not re.match(r"(?i)readme", os.path.basename(path)):
            continue
        text = collect.read(root, path)
        if not text:
            continue
        in_fence = False
        for i, raw in enumerate(_lines(text)):
            line = raw.strip()
            if line.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                m = CMD_START.match(line)
                if m:
                    cmd = m.group(1).strip()
                    kind = classify(cmd)
                    if kind:
                        out.append(Claim(kind, kind, cmd, "readme", path, i + 1))
                continue
            clean = _LINKS.sub(" ", line)
            if _HISTORICAL.search(clean):
                continue
            for tool, pattern in RUNTIME_PROSE:
                m = re.search(pattern, clean, re.I)
                if m:
                    ver = (m.group(1) or "") + m.group(2) + (m.group(3) or "")
                    out.append(Claim("runtime", tool, ver, "readme", path,
                                     i + 1, note=" ".join(clean.split())[:120]))
        break
    return out


# ---------------------------------------------------------------------- CI
def ci(root, wf, env_ok=True):
    """Phase B's extraction, restated as Claims against one workflow.

    `env_ok` is False for every workflow but the primary one: env is
    job-scoped, and merging it across workflows produces a variable list that
    describes no job that ever ran.
    """
    out = []
    path = wf["path"]
    for job in wf["jobs"]:
        for setup in job["setups"]:
            # `python-version-file: pyproject.toml` names a file, not a version.
            # Recording the filename as the answer would print "want
            # pyproject.toml"; marking it unreadable lets the precedence table
            # fall through to the pin file or manifest that holds the real one.
            # `ruby-version: ruby` and `bun-version: latest` are aliases the
            # action resolves at run time, not versions. Reporting "ruby = ruby"
            # tells a reader nothing, so treat an alias as unreadable and let
            # the table fall through to a pin file or manifest.
            unresolved = (setup["from_file"] or "${{" in setup["value"]
                          or setup["value"].startswith("(")
                          or not re.search(r"\d", str(setup["value"])))
            for val in str(setup["value"]).split(" | "):
                out.append(Claim("runtime", setup["tool"], _norm_version(val),
                                 "ci-setup", path, setup["line"],
                                 resolved=not unresolved,
                                 note="%s in job %s" % (setup["action"], job["id"])))
        for svc in job["services"]:
            kind = _service_kind(svc["image"] or "") or _service_kind(svc["name"])
            if not kind:
                continue
            note = "job %s" % job["id"]
            if svc["ports"]:
                note += ", ports " + ",".join(svc["ports"])
            out.append(Claim("services", kind, svc["image"] or svc["name"],
                             "ci-services", path, svc["line"],
                             resolved="${{" not in str(svc["image"]),
                             note=note,
                             data={"ports": list(svc["ports"]),
                                   "env": [(k, v) for k, v in svc["env"]
                                           if "${{" not in str(v)]}))
        for value, line in job["runs_on"]:
            out.append(Claim("os", "os", value, "ci-runs-on", path, line,
                             resolved="${{" not in value,
                             note="job %s" % job["id"]))
        for key, value, line in (job["env"] if env_ok else []):
            out.append(Claim("env", key, value, "ci-env", path, line,
                             resolved="${{" not in value,
                             note="job %s" % job["id"]))
        for blk in job["blocks"]:
            where = "job %s" % job["id"]
            if blk["wd"]:
                where += ", in %s" % blk["wd"]
            elif blk.get("wd_unknown"):
                where += ", in a directory CI computes"
            for cmd in _script_commands(blk["script"]):
                kind = classify(cmd)
                if kind:
                    out.append(Claim(kind, kind, cmd, "ci-run", path,
                                     blk["line"], resolved="${{" not in cmd,
                                     note=where))
    return out


def _script_commands(script):
    """Individual commands inside a run block, for classification only.

    The block stays whole for factcheck.sh -- this split is used to decide
    what kind of thing the step does, never to rewrite the script.
    """
    out = []
    for line in script.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith("\\"):
            line = line[:-1].strip()
        for part in re.split(r"\s*&&\s*", line):
            part = part.strip()
            if part and not re.match(r"^(if|then|else|fi|for|do|done|echo|"
                                     r"exit|set|cd)\b", part):
                out.append(part)
    return out


def authoritative(wfs):
    """Workflows that run on every merge, most authoritative first.

    This is the spec's own justification for trusting CI at all: it is ground
    truth *because* it executes on merge. A workflow triggered only by issues,
    a schedule or a manual dispatch does not qualify, so it is not evidence.
    """
    auth = [wf for wf in wfs if set(wf["triggers"]) & extract.MERGE_TRIGGERS]
    # Ties go to the simpler name: `ci.yml` over `ci-agent-proxy.yml`.
    return sorted(auth, key=lambda w: (-w["rank"], len(os.path.basename(w["path"])),
                                       w["path"]))


def gather(root, inv, wfs):
    """Every claim from every source, unranked."""
    out = []
    out += toolchain_files(root, inv)
    out += dockerfile(root, inv)
    out += compose(root, inv)
    out += manifests(root, inv)
    out += lockfiles(root, inv)
    out += env_example(root, inv)
    out += readme(root, inv)
    auth = authoritative(wfs)
    primary = auth[0]["path"] if auth else None
    for wf in auth:
        out += ci(root, wf, env_ok=(wf["path"] == primary))
    return out
