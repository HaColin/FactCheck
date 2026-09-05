# FACTCHECK

**Fact-check a repo's README against its CI.**

CI is ground truth: it executes on every merge. The README is prose nobody runs.
Given a public GitHub repo URL, FACTCHECK reads both, reconciles them, and writes
down what is actually true — with a file and line number behind every claim.

> The same result as an agent flailing through a repo for 200k tokens — but as a
> fixed evidence-collection protocol that costs one inference call and produces
> the same answer twice.

A [Rote](https://modiqo.com) Play. The source-precedence rule is *code*, not a
prompt, so the method is deterministic, captured, and produces the same answer
twice.

## Status

| Phase | What | State |
|---|---|---|
| A | Collect — shallow clone, inventory setup-bearing files | done |
| B | Extract from CI — runs-on, setup-\*, run, services, env, cache | done |
| C | Reconcile — source-precedence table, as code | done |
| D | Emit `FACTCHECK.md` with provenance | next |
| E | Emit executable `factcheck.sh` | todo |
| F | Issue mining (the only step that spends API rate limit) | todo |

Phases A–C make **zero GitHub API calls** — shallow clone only, so nothing counts
against the 60 req/hour unauthenticated budget. Issue mining is the only API step,
and it is optional: a rate-limit failure there must never fail the run.

## Try it

```sh
python3 factcheck.py https://github.com/netbox-community/netbox --quiet-ci
python3 factcheck.py --table          # just the precedence table
```

Stdlib-only Python 3. No pip install, no pyyaml, no jq.

```
  Services required
    postgres    postgres          .github/workflows/ci.yml:99  job test, ports 5432:5432
    redis       redis             .github/workflows/ci.yml:95  job test, ports 6379:6379

  Install
                pip install -r requirements.txt      .github/workflows/ci.yml:122

  Verified but undocumented  -- CI needs it, the prose never says so
    postgres     postgres         .github/workflows/ci.yml:99
    redis        redis            .github/workflows/ci.yml:95
```

The `services:` block is the sleeper. "You also need a Postgres on 5432" is the
most common reason a fresh clone won't run, and it is almost never in the README.

## How it decides

The precedence table is the method. It is a fixed lookup in `precedence.py`, not a
prompt, because a prompt would re-decide the ordering on every run and there would
be nothing deterministic to capture.

| Fact | Source order, highest authority first |
|---|---|
| runtime | `.tool-versions`/`.nvmrc` → CI `setup-*` → `Dockerfile FROM` → manifest engines → README |
| install | CI `run` → `Dockerfile RUN` → lockfile implies it → README |
| build / test / lint | CI `run` → manifest scripts → README |
| setup | CI `run` → `Dockerfile RUN` → README |
| services | CI `services:` → docker-compose → `.env.example` hints |
| env | CI `env:` → `.env.example` keys |
| os | CI `runs-on` → README |

Five rules decide what the table does with what it finds. Each exists because a
real repo produced a wrong answer without it:

1. **Only merge-triggered workflows are evidence.** CI is ground truth *because*
   it runs on every merge, so a workflow triggered only by issues, a schedule or a
   manual dispatch does not qualify.
2. **An unreadable value falls through.** plausible/analytics sets its Elixir
   version from `${{ steps.versions.outputs.elixir }}`. CI outranks
   `.tool-versions` in the table, but a non-literal value cannot win — and is
   never printed as an answer.
3. **One source disagreeing with itself is a set, not a conflict.** wagtail tests
   four Python versions across four jobs. That is the matrix, not a contradiction.
4. **A conflict needs two different kinds of source.** Two CI workflows pinning
   different tool versions is variation; the README contradicting CI is a finding.
5. **Constraints keep their operators.** `>=3.7` and `3.7` say different things,
   and stripping the operator turns every lower bound in every manifest into a
   false conflict with whatever CI actually runs.

Lockfile → install command is a pure mapping, no inference: `package-lock.json` →
`npm ci`, `uv.lock` → `uv sync`, `Cargo.lock` → `cargo build --locked`, and so on.

## Files

| File | Role |
|---|---|
| `yamlish.py` | Line-tracking YAML subset parser |
| `collect.py` | Phase A — clone and inventory |
| `extract.py` | Phase B — pull the six CI fields |
| `claims.py` | The claim model; provenance enforced in the constructor |
| `sources.py` | Phase C — every file, restated as claims |
| `precedence.py` | Phase C — the table and the resolution engine |
| `factcheck.py` | CLI |
| `sweep.py` | Parser validation harness (needs network) |
| `tests/` | Offline regression tests |

### Why a hand-rolled YAML parser

Two reasons, both load-bearing:

1. **Provenance.** `yaml.safe_load` discards line numbers. Every claim FACTCHECK
   emits has to cite `ci.yml:23`, so every value the parser returns carries the
   line it came from.
2. **Portability.** Stdlib-only means it runs wherever Python 3 does — no install
   step between a judge and a working demo.

A bonus: this parser is not YAML 1.1, so `on:` stays the string `"on"` instead of
being coerced to the boolean `True`, which is what a workflow file means by it.

## Validation

A hand-rolled parser fails *silently* — it stops early, raises nothing, and the
rest of the file disappears. So correctness is checked against an independent
grep: every `run:` key in a workflow (excluding `defaults: run:` and `run:` as an
action input) must surface as exactly one extracted block, and every child key of
`services:` as exactly one service.

```sh
python3 tests/test_yamlish.py      # offline
python3 tests/test_precedence.py   # offline
python3 sweep.py PostHog/posthog discourse/discourse ggml-org/llama.cpp
```

Across 25 repos — 824 workflow files, 1,821 jobs, 4,046 run blocks, 114 services —
both cross-checks reconcile exactly. Getting there meant fixing five constructs
that each silently discarded the rest of the document:

| Construct | Found in |
|---|---|
| Multi-line flow sequence (`paths: [` over many lines) | llama.cpp — killed 28 of 50 workflows |
| Flow collection opening on the line after its key | posthog |
| Multi-line plain scalar (`if: cond &&` wrapped) | posthog |
| Steps nested under `- parallel:` | discourse, posthog |
| `- # comment` as an entire sequence item | sentry |

Phase C over the same 25 repos produces 3,764 claims and 3 conflicts, each of
which was checked by hand against the files:

- **posthog** — `.nvmrc` pins Node 24.13.0; the desktop-build jobs run Node 22.
- **discourse** — the docs workflow pins Ruby 3.3 against a `~> 3.4` Gemfile and a
  README that says 3.4+.

An earlier pass reported ~45 conflicts. All but three were artifacts of the five
rules above being missing, and every one of them is now a test case. A tool that
invents a conflict in a repo the reader knows personally is worse than one that
finds nothing.

## Notes for phase D

- `defaults.run.working-directory` and `shell` are not captured yet; both are
  needed before `factcheck.sh` can be faithful.
- Images are often unpinned — netbox's CI says `image: postgres` with no tag.
  "PostgreSQL, version unpinned in CI" is honest; inventing `15` is not.
- Runtime facts can be multi-valued (`3.12 | 3.13 | 3.14`). The document should
  show the range; the script has to pick one deterministically.
