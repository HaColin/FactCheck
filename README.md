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

## Run it

```sh
rote play run https://play.modiqo.ai/factcheck/factcheck@1.6.2 \
  repo_url=https://github.com/netbox-community/netbox
```

With no [rote](https://rote.dev) installed, one line does the whole thing —
installs rote, signs you in, shows what the play will do, and asks before
running it:

```sh
curl -fsSL "https://play.modiqo.ai/install?play=factcheck/factcheck@1.6.2" | sh
```

It writes `FACTCHECK.md` and `factcheck.sh` into the directory you ran from.
Needs `python3` and `git`; no pip install, no API key, no GitHub token. Running
it with no arguments is fine — it shows the play, its access and its inputs,
then prompts for the repository.

Or skip rote entirely and run the analysis directly:

```sh
git clone https://github.com/HaColin/FactCheck && cd FactCheck
python3 factcheck.py https://github.com/netbox-community/netbox
```

## Status

| Phase | What | State |
|---|---|---|
| A | Collect — shallow clone, inventory setup-bearing files | done |
| B | Extract from CI — runs-on, setup-\*, run, services, env, cache | done |
| C | Reconcile — source-precedence table, as code | done |
| D | Emit `FACTCHECK.md` with provenance | done |
| E | Emit executable `factcheck.sh` | done |
| F | Issue mining (the only step that spends API rate limit) | done |

Phases A–C make **zero GitHub API calls** — shallow clone only, so nothing counts
against the 60 req/hour unauthenticated budget. Issue mining is the only API step,
and it is optional: a rate-limit failure there must never fail the run.

## Try it

```sh
python3 factcheck.py https://github.com/netbox-community/netbox --quiet-ci
python3 factcheck.py https://github.com/discourse/discourse -o FACTCHECK.md -s factcheck.sh
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
| `render.py` | Phase D — emit `FACTCHECK.md` |
| `script.py` | Phase E — emit `factcheck.sh` |
| `issues.py` | Phase F — mine the issue tracker (opt-in) |
| `factcheck.py` | CLI |
| `examples/` | Documents and scripts generated for six real repos |
| `sweep.py` | Parser validation harness (needs network) |
| `tests/` | Offline regression tests |
| `play/` | The rote Play package: `main.ts`, `deps.toml`, presentation fixture |
| `build-play.sh` | Vendors the modules into `play/resources/` before lint or publish |

### Why a hand-rolled YAML parser

Two reasons, both load-bearing:

1. **Provenance.** `yaml.safe_load` discards line numbers. Every claim FACTCHECK
   emits has to cite `ci.yml:23`, so every value the parser returns carries the
   line it came from.
2. **Portability.** Stdlib-only means it runs wherever Python 3 does — no install
   step between a judge and a working demo.

A bonus: this parser is not YAML 1.1, so `on:` stays the string `"on"` instead of
being coerced to the boolean `True`, which is what a workflow file means by it.

## The rote Play

Published at **https://play.modiqo.ai/factcheck/factcheck@1.6.2** — public, and
runnable by anyone:

```sh
rote play run https://play.modiqo.ai/factcheck/factcheck@1.6.2 \
  repo_url=https://github.com/netbox-community/netbox
```

Or with no rote installed at all, one line:

```sh
curl -fsSL "https://play.modiqo.ai/install?play=factcheck/factcheck@1.6.2" | sh
```

| Parameter | Required | Default |
|---|---|---|
| `repo_url` | yes | — |
| `out_dir` | no | `.` — where you ran from |
| `mine_issues` | no | `no` |

The package holds the analysis as `resources/*.py` and addresses it with
`@resource{factcheck.py}`, so the play is self-contained: nothing is fetched at
run time, and the only host requirements are `python3` and `git`, declared in
`deps.toml`.

### Publishing a new version

The package lives in `play/` **in this repo**, not under `~/.rote/flows/`. That is
deliberate. Running the published play installs it to `~/.rote/flows/factcheck/`,
and when the authoring package sat at that same path the installer's artifacts
(`factcheck/`, `.factcheck.install.lock`) landed inside it — entries the package
classifier does not recognise, which failed every subsequent
`rote play lint` with `FLOW_PACKAGE_CAPTURE_FAILED`. Keeping the source here
gives the installer sole ownership of that directory, and has the better side
effect that the Play definition is version-controlled.

```sh
./build-play.sh                                   # vendor the modules
rote play lint  play/main.ts
rote play bump  play/main.ts --minor
rote registry play push play/main.ts factcheck
```

Only `rote play release <name>` needs a registered name; every other step takes a
path, which is what makes this layout work.

## Does the script actually work?

Two repos have been taken from `git clone` to a running test suite using nothing
but the generated `factcheck.sh`:

- **pallets/flask** — `uv sync`, then the full tox matrix, mypy and pyright, all
  green, exit 0.
- **expressjs/express** — the Node case: `npm install`, then `npm run test-ci`,
  1260 tests passing with coverage, exit 0.
- **netbox-community/netbox** — the harder case: `--with-services` starts the
  Postgres and Redis containers CI declares, using the credentials CI declares
  for them (`POSTGRES_USER=netbox`, not a generic default — a generic password
  starts a database the project cannot authenticate against), then installs,
  checks migrations and collects static files.

Everything below was found by doing that rather than by reading the code:

| Found by running it | Fix |
|---|---|
| `pip install` stopped on a missing `pg_config` | the system-packages table above |
| `docker run` used a generic password | services carry their declared `env:` |
| A failed `docker run` aborted with no explanation | names the service and port, suggests what to do |
| `python -m build` ran from `release.yml` | the script is scoped to the primary workflow; packaging a wheel is not how you run a repo |

## Validation

A hand-rolled parser fails *silently* — it stops early, raises nothing, and the
rest of the file disappears. So correctness is checked against an independent
grep: every `run:` key in a workflow (excluding `defaults: run:` and `run:` as an
action input) must surface as exactly one extracted block, and every child key of
`services:` as exactly one service.

```sh
python3 tests/all.py     # every offline suite: parser, precedence, document
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

## The document

`-o` writes `FACTCHECK.md`. Every factual line links into the repo at the exact
commit that was read, so a reader can check any claim in one click:

```markdown
| postgres | `postgres:15` | job test, ports 5432:5432 | [`ci.yml:31`](…/blob/<sha>/…#L31) |
```

The output is deterministic — no timestamps, no wall-clock, no ordering that
depends on a dict. The same commit renders byte-identical output, which is what
makes the method worth capturing rather than re-deriving. `tests/test_render.py`
asserts it, along with the rule that no factual line may appear without a
citation, and that an unpinned `image: postgres` never becomes `postgres:15`.

Six examples are checked in under `examples/`, chosen to cover the range: a
database service the README never mentions (netbox), a native build (llama.cpp),
a monorepo (cal.com), and a README provably stale against its own CI
(discourse — the docs workflow pins Ruby 3.3 against a `~> 3.4` Gemfile).

## The script

`-s` writes `factcheck.sh`: the install and run sequence, derived from CI steps,
with every line citing where it came from.

CI runs on a disposable machine, as a user who can install anything, with its
services already provisioned. A developer's laptop is none of those things, so
the commands are not replayed blindly. Four fixed rules decide what survives:

| Rule | Why |
|---|---|
| Anything not literal (`${{ … }}`) is dropped | Guessing at an unexpanded expression is how a script does something nobody asked for |
| Anything that publishes is dropped | `npm publish`, `docker push`, `gh release` change the world outside this machine |
| Anything needing root is printed, not run | A generated script does not get to `sudo`, and a global `npm i -g` writes outside the project |
| `rm -rf` and friends are printed, not run | A human should be in the loop |

What it does instead of guessing:

- **Checks before it acts.** Reports the runtime versions CI pins against what is
  actually installed, and probes each service's port.
- **Turns `services:` into something runnable.** A CI service block becomes the
  exact `docker run` that satisfies it — `--with-services` starts them, otherwise
  the command is printed for the reader to run.
- **Carries CI's environment across.** `mix deps.get --only $MIX_ENV` is not a
  runnable command until `MIX_ENV` exists, so resolved `env:` blocks are exported
  with their citations. Where two jobs set the same variable differently, the
  document shows both and the script takes the highest-authority one.
- **Says what it could not bring.** Variables referenced by commands but never set
  by CI are listed up front rather than failing halfway through.

One limit, stated in the generated header: commands are taken individually from CI
steps, so an `if` wrapped around one in the original workflow is not reproduced.

`--dry-run` prints every command and runs none of them. `tests/test_script.py`
generates a script, asks `bash -n` whether it is valid, and executes it under
`--dry-run` — a generator that emits broken shell should fail its own tests.

## System packages

`pip install` is not the whole story. netbox's `requirements.txt` pulls `psycopg`,
which builds against libpq; CI never mentions it because the runner image already
has it. A fresh clone gets partway through the install and stops on a missing
`pg_config`.

A dependency implying a system package is the same kind of deterministic mapping
as a lockfile implying its install command, so it gets the same treatment: a fixed
table, cited to the requirements line that triggered it, with the install command
for apt, brew, pacman and dnf. The document lists them; the script prints them and
installs nothing, because this needs root.

It covers Python, Node and Ruby: mastodon's `pg` gem and node-gyp packages like
`canvas` need headers for the same reason. The table is deliberately
conservative — `psycopg2-binary`, `Pillow`, `sharp` and `nokogiri` ship prebuilt
binaries and are absent. A prerequisite that is not really required wastes the
reader's time and costs more trust than it earns.

## Issue mining

`--issues yes` searches the tracker for reported setup problems. It is the only
step that touches the GitHub API, so it is budgeted and it fails soft:

1. `gh auth token` — most developers already have `gh` authenticated, so this is
   a token with no signup friction (30 searches/minute).
2. Unauthenticated, capped at two queries, staying inside the 10/minute budget.
3. On a 403, exhaustion, or any network fault: keep whatever was found, mark the
   section skipped, and emit the document anyway. Phases A–E already produced a
   useful document with zero API calls; enrichment must never sink the run.

**It is off by default, and that is deliberate.** Everything else in the document
is derived from one commit and renders byte-identical every time. The tracker
changes underneath you, so mining it is opt-in and the section says so.

Keyword matching cannot tell *"cannot install [this software]"* from *"cannot
install [a device module in a bay]"* — netbox has both. Two filters carry most
of the weight: a phrase must actually appear in the issue title or body (GitHub
search falls back to loose matching), and feature-shaped titles are dropped
(`Support for…`, `Extend…`, anything labelled `enhancement`). What survives on
apache/airflow is *"Setting up Airflow for local development is hard"* and
*"Airflow Helm chart fails on Apple Silicon + kind"*. The section is titled for
what it is — issues matching a setup-failure phrase, not a verdict.

## Notes

- Images are often unpinned — netbox's CI says `image: postgres` with no tag.
  "PostgreSQL, version unpinned in CI" is honest; inventing `15` is not.
- Runtime facts can be multi-valued (`3.12 | 3.13 | 3.14`). The document shows
  the range; the script has to pick one deterministically.
- Which workflow counts as "primary" is a heuristic, and on a repo with fifty
  workflows and no baseline CI it is a judgement call. The document names the
  workflow it read and cites every line, so the reader can see what was chosen.
