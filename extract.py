"""FACTCHECK phase B: extract from CI. Zero GitHub API calls.

The workflow YAML is the highest-value file in any repo and almost
nobody reads it. This pulls the six fields the spec names, keeping the
source line for every one of them.
"""
import os
import re

import yamlish

SETUP_ACTIONS = {
    "actions/setup-node":     ("node",   ["node-version", "node-version-file"]),
    "actions/setup-python":   ("python", ["python-version", "python-version-file"]),
    "actions/setup-go":       ("go",     ["go-version", "go-version-file"]),
    "actions/setup-java":     ("java",   ["java-version"]),
    "actions/setup-dotnet":   ("dotnet", ["dotnet-version"]),
    "ruby/setup-ruby":        ("ruby",   ["ruby-version"]),
    "erlef/setup-beam":       ("erlang", ["otp-version", "elixir-version"]),
    "dtolnay/rust-toolchain": ("rust",   ["toolchain"]),
    "actions-rs/toolchain":   ("rust",   ["toolchain"]),
    "shivammathur/setup-php": ("php",    ["php-version"]),
    "pnpm/action-setup":      ("pnpm",   ["version"]),
    "astral-sh/setup-uv":     ("uv",     ["version"]),
    "denoland/setup-deno":    ("deno",   ["deno-version"]),
    "oven-sh/setup-bun":      ("bun",    ["bun-version"]),
    "julia-actions/setup-julia": ("julia", ["version"]),
    "haskell-actions/setup":  ("ghc",    ["ghc-version"]),
    "subosito/flutter-action": ("flutter", ["flutter-version"]),
}

EXPR = re.compile(r"\$\{\{\s*([^}]+?)\s*\}\}")
MATRIX_REF = re.compile(r"^matrix\.([\w-]+)$")

# Triggers that mean "this runs on every merge" -- the spec's ground truth.
MERGE_TRIGGERS = {"push", "pull_request", "pull_request_target", "merge_group"}
SIDE_TRIGGERS = {"schedule", "workflow_dispatch", "release", "issues",
                 "issue_comment", "workflow_run", "repository_dispatch",
                 "pull_request_review", "discussion", "create", "deployment"}


def workflow_paths(root):
    d = os.path.join(root, ".github", "workflows")
    if not os.path.isdir(d):
        return []
    out = []
    for name in sorted(os.listdir(d)):
        if name.endswith((".yml", ".yaml")):
            out.append(os.path.join(".github", "workflows", name))
    return out


def _as_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return list(v)
    if isinstance(v, dict):
        return list(v.keys())
    return [v] if str(v) else []


def triggers_of(doc):
    on = doc.get("on", doc.get(True))  # some parsers coerce on->True; ours doesn't
    return [str(t) for t in _as_list(on)]


def resolve(value, matrix):
    """Expand ${{ matrix.x }} against the job's matrix; leave other exprs alone."""
    s = str(value)
    m = EXPR.fullmatch(s.strip())
    if m:
        ref = MATRIX_REF.match(m.group(1).strip())
        if ref and ref.group(1) in matrix:
            vals = [str(x) for x in matrix[ref.group(1)]]
            return " | ".join(vals) if vals else s
    return s


def resolve_in(text, matrix):
    """Expand ${{ matrix.x }} occurrences inside a larger string."""
    def sub(m):
        ref = MATRIX_REF.match(m.group(1).strip())
        if ref and ref.group(1) in matrix:
            return " | ".join(str(x) for x in matrix[ref.group(1)])
        return m.group(0)
    return EXPR.sub(sub, text)


def matrix_of(job):
    strat = job.get("strategy")
    if not isinstance(strat, dict):
        return {}
    mx = strat.get("matrix")
    if not isinstance(mx, dict):
        return {}
    out = {}
    for k, v in mx.items():
        if k in ("include", "exclude"):
            continue
        if isinstance(v, list):
            out[k] = [str(x) for x in v]
    inc = mx.get("include")
    if isinstance(inc, list):
        for entry in inc:
            if isinstance(entry, dict):
                for k, v in entry.items():
                    if not isinstance(v, (dict, list)):
                        out.setdefault(k, [])
                        if str(v) not in out[k]:
                            out[k].append(str(v))
    return out


def run_commands(step):
    """Individual command lines of a `run:` block, each with its own line no."""
    run = step.get("run")
    if run is None:
        return []
    base = getattr(run, "line", 0)
    text = str(run)
    if "\n" not in text.strip():
        return [(text.strip(), base)]
    # Block scalar content starts on the line after the `run: |` key.
    out = []
    for i, line in enumerate(text.split("\n")):
        s = line.strip()
        if s and not s.startswith("#"):
            out.append((s, base + 1 + i))
    return out


def run_block(step):
    """The whole `run:` script as one unit -- shell control flow must not be
    split into lines, or `if ... else ... fi` becomes five broken commands."""
    run = step.get("run")
    if run is None:
        return None
    base = getattr(run, "line", 0)
    text = str(run).rstrip("\n")
    if "\n" not in text.strip():
        return {"script": text.strip(), "line": base, "key_line": base, "nlines": 1}
    return {"script": text, "line": base + 1, "key_line": base,
            "nlines": len(text.split("\n"))}


def iter_steps(steps):
    """Flatten step lists, including ones nested under keys like `parallel:`."""
    for step in steps or []:
        if not isinstance(step, dict):
            continue
        if "run" in step or "uses" in step:
            yield step
        for key, val in step.items():
            if key in ("with", "env", "strategy"):
                continue
            if isinstance(val, list) and val and all(isinstance(x, dict) for x in val):
                for nested in iter_steps(val):
                    yield nested


WORKSPACE = re.compile(r"\$\{\{\s*github\.workspace\s*\}\}/?")


def normalise_wd(wd):
    """-> (directory, unknown).

    `${{ github.workspace }}` is the checkout root, so it resolves to the
    repo itself. Any other expression is computed by the runner and cannot be
    known here; saying so beats guessing, because a command run in the wrong
    directory is worse than one not run at all.
    """
    wd = WORKSPACE.sub("", str(wd or "")).strip()
    if "${{" in wd:
        return "", True
    return wd, False


def _defaults(node):
    """jobs.*.defaults.run / defaults.run -- where and how steps actually run."""
    out = {"wd": "", "shell": "", "wd_unknown": False}
    d = node.get("defaults") if isinstance(node, dict) else None
    if isinstance(d, dict):
        run = d.get("run")
        if isinstance(run, dict):
            out["wd"], out["wd_unknown"] = normalise_wd(run.get("working-directory", ""))
            out["shell"] = str(run.get("shell", ""))
    return out


def extract_job(job_id, job, matrix, wf_defaults=None):
    wf_defaults = wf_defaults or {"wd": "", "shell": "", "wd_unknown": False}
    job_defaults = _defaults(job)
    j = {
        "id": job_id,
        "defaults": {k: job_defaults[k] or wf_defaults[k]
                     for k in ("wd", "shell", "wd_unknown")},
        "name": str(job.get("name", job_id)),
        "line": getattr(job, "line", 0),
        "runs_on": [],
        "container": None,
        "services": [],
        "env": [],
        "matrix": matrix,
        "setups": [],
        "runs": [],
        "blocks": [],
        "caches": [],
        "uses_workflow": None,
        "steps": 0,
    }
    if "uses" in job:  # reusable workflow call, no steps of its own
        j["uses_workflow"] = (str(job["uses"]), job.kline("uses"))

    ro = job.get("runs-on")
    if ro is not None:
        ln = job.kline("runs-on")
        if isinstance(ro, list):
            j["runs_on"] = [(resolve(x, matrix), getattr(x, "line", ln)) for x in ro]
        elif isinstance(ro, dict):  # runs-on: {group:..., labels:[...]}
            for x in _as_list(ro.get("labels")):
                j["runs_on"].append((resolve(x, matrix), ln))
        else:
            j["runs_on"] = [(resolve(ro, matrix), ln)]

    cont = job.get("container")
    if isinstance(cont, dict) and "image" in cont:
        j["container"] = (str(cont["image"]), cont.kline("image"))
    elif isinstance(cont, str) and str(cont):
        j["container"] = (str(cont), job.kline("container"))

    svcs = job.get("services")
    if isinstance(svcs, dict):
        for name, cfg in svcs.items():
            ln = svcs.kline(name)
            entry = {"name": str(name), "line": ln, "image": None,
                     "ports": [], "env": [], "options": None}
            if isinstance(cfg, dict):
                if "image" in cfg:
                    entry["image"] = str(cfg["image"])
                    entry["line"] = cfg.kline("image", ln)
                entry["ports"] = [str(p) for p in _as_list(cfg.get("ports"))]
                senv = cfg.get("env")
                if isinstance(senv, dict):
                    entry["env"] = [(str(k), str(v)) for k, v in senv.items()]
                if cfg.get("options"):
                    entry["options"] = " ".join(str(cfg["options"]).split())
            elif isinstance(cfg, str):
                entry["image"] = str(cfg)
            j["services"].append(entry)

    jenv = job.get("env")
    if isinstance(jenv, dict):
        j["env"] = [(str(k), str(v), jenv.kline(k)) for k, v in jenv.items()]

    steps = job.get("steps")
    if isinstance(steps, list):
        flat = list(iter_steps(steps))
        j["steps"] = len(flat)
        for step in flat:
            uses = str(step.get("uses", ""))
            action = uses.split("@")[0].strip()
            ver = uses.split("@")[1] if "@" in uses else ""
            with_ = step.get("with") if isinstance(step.get("with"), dict) else {}
            if action in SETUP_ACTIONS:
                tool, keys = SETUP_ACTIONS[action]
                found = False
                for key in keys:
                    if key in with_:
                        raw = with_[key]
                        j["setups"].append({
                            "tool": tool if not key.startswith(("otp", "elixir"))
                                    else key.split("-")[0],
                            "action": action, "action_ref": ver,
                            "key": key,
                            "value": resolve(raw, matrix),
                            "raw": str(raw),
                            "line": with_.kline(key, step.kline("uses")),
                            "from_file": key.endswith("-file"),
                        })
                        found = True
                if not found:
                    j["setups"].append({
                        "tool": tool, "action": action, "action_ref": ver,
                        "key": None, "value": "(unpinned - action default)",
                        "raw": "", "line": step.kline("uses"), "from_file": False,
                    })
                if "cache" in with_:
                    j["caches"].append(("%s cache: %s" % (tool, with_["cache"]),
                                        with_.kline("cache")))
            elif action.endswith("/cache") or action.startswith("actions/cache"):
                paths = " ".join(str(with_.get("path", "")).split())
                j["caches"].append((paths or "(unspecified)",
                                    with_.kline("path", step.kline("uses"))))
            blk = run_block(step)
            if blk:
                blk["script"] = resolve_in(blk["script"], matrix)
                blk["step"] = str(step.get("name", ""))
                blk["shell"] = str(step.get("shell", "")) or j["defaults"]["shell"]
                _wd, _unknown = normalise_wd(step.get("working-directory", ""))
                blk["wd"] = _wd or j["defaults"]["wd"]
                blk["wd_unknown"] = _unknown or j["defaults"]["wd_unknown"]
                blk["if"] = str(step.get("if", ""))
                j["blocks"].append(blk)
            for cmd, ln in run_commands(step):
                j["runs"].append({
                    "cmd": resolve(cmd, matrix), "line": ln,
                    "step": str(step.get("name", "")),
                    "shell": str(step.get("shell", "")),
                    "wd": (normalise_wd(step.get("working-directory", ""))[0]
                           or j["defaults"]["wd"]),
                    "if": str(step.get("if", "")),
                })
            senv = step.get("env")
            if isinstance(senv, dict):
                for k, v in senv.items():
                    j["env"].append((str(k), str(v), senv.kline(k)))
    return j


def extract_workflow(root, relpath):
    text = open(os.path.join(root, relpath), encoding="utf-8", errors="replace").read()
    try:
        doc = yamlish.load(text)
    except Exception as exc:                      # never die on one bad file
        return {"path": relpath, "error": "%s: %s" % (type(exc).__name__, exc),
                "jobs": [], "triggers": [], "rank": -99, "name": relpath}
    if not isinstance(doc, dict):
        return {"path": relpath, "error": "not a mapping", "jobs": [],
                "triggers": [], "rank": -99, "name": relpath}
    trig = triggers_of(doc)
    wf = {
        "path": relpath,
        "name": str(doc.get("name", os.path.basename(relpath))),
        "triggers": trig,
        "env": [],
        "jobs": [],
        "error": None,
    }
    genv = doc.get("env")
    if isinstance(genv, dict):
        wf["env"] = [(str(k), str(v), genv.kline(k)) for k, v in genv.items()]
    wf_defaults = _defaults(doc)
    jobs = doc.get("jobs")
    if isinstance(jobs, dict):
        for jid, job in jobs.items():
            if isinstance(job, dict):
                wf["jobs"].append(extract_job(str(jid), job, matrix_of(job),
                                              wf_defaults))
    wf["rank"] = rank_workflow(wf)
    return wf


def rank_workflow(wf):
    """How much authority this workflow has as 'what runs on every merge'."""
    score = 0
    trig = set(wf["triggers"])
    score += 4 * len(trig & MERGE_TRIGGERS)
    if trig and not (trig & MERGE_TRIGGERS):
        score -= 4
    if trig & SIDE_TRIGGERS and not (trig & MERGE_TRIGGERS):
        score -= 2
    hay = (wf["path"] + " " + wf["name"]).lower()
    if re.search(r"\b(ci|test|tests|build|check|main|verify)\b", hay):
        score += 3
    # A workflow named for one hardware target, OS or accelerator is not the
    # repo's baseline CI, however many merges it runs on. llama.cpp has 50
    # workflows and the Snapdragon one is not how you build llama.cpp.
    if re.search(r"(snapdragon|android|ios\b|macos|windows|riscv|wasm|webgpu|"
                 r"vulkan|sycl|cann|opencl|openvino|musa|hip\b|cuda|ibm|s390|"
                 r"arm64|aarch64|cross|self-hosted|virtgpu|nix|flatpak|"
                 r"3rd-party|vendor|freebsd|musl|apple|darwin|osx)", hay):
        score -= 5
    # An unqualified name is the baseline by convention.
    if re.match(r"^(ci|main|test|tests|build|check)$",
                os.path.splitext(os.path.basename(wf["path"]))[0].lower()):
        score += 4
    if re.search(r"(release|publish|deploy|docs|stale|label|lock|greet|codeql|"
                 r"scorecard|dependabot|nightly|benchmark|fuzz|translat)", hay):
        score -= 3
    # Baseline CI is usually the big one: a narrow integration workflow has a
    # job or two, the workflow that gates merges has many.
    score += min(3, len(wf["jobs"]) // 3)
    for j in wf["jobs"]:
        if j["services"]:
            score += 2
        if any(re.search(r"\b(test|pytest|jest|vitest|rspec|go test|cargo test|"
                         r"mix test|npm t)\b", r["cmd"]) for r in j["runs"]):
            score += 2
            break
    return score
