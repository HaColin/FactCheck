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
| C | Reconcile — source-precedence table, as code | next |
| D | Emit `FACTCHECK.md` with provenance | todo |
| E | Emit executable `factcheck.sh` | todo |
| F | Issue mining (the only step that spends API rate limit) | todo |

Phases A–C make **zero GitHub API calls** — shallow clone and
`raw.githubusercontent.com` only, so nothing counts against the 60 req/hour
unauthenticated budget. Issue mining is the only API step, and it is optional:
a rate-limit failure there must never fail the run.

## Try it

```sh
python3 ab.py https://github.com/netbox-community/netbox
```

Stdlib-only Python 3. No pip install, no pyyaml, no jq, no `gh`.

```
    job test  (9 steps, line 78)
      runs-on      ubuntu-latest  <- :82
      matrix       python-version=[3.12,3.13,3.14]
      toolchain    python 3.12 | 3.13 | 3.14  <- :118
      service      redis redis  ports 6379:6379  <- :95
      service      postgres postgres  ports 5432:5432  env POSTGRES_USER  <- :99
      run          pip install -r requirements.txt  <- :123
      run          python netbox/manage.py test netbox/ --parallel  <- :136
```

The `services:` block is the sleeper. "You also need a Postgres on 5432" is the
most common reason a fresh clone won't run, and it is almost never in the README.

## Files

| File | Role |
|---|---|
| `yamlish.py` | Line-tracking YAML subset parser |
| `collect.py` | Phase A — clone and inventory |
| `extract.py` | Phase B — pull the six CI fields |
| `ab.py` | Driver for phases A+B |
| `sweep.py` | Validation harness (needs network) |
| `tests/test_yamlish.py` | Offline regression tests |

### Why a hand-rolled YAML parser

Two reasons, both load-bearing:

1. **Provenance.** `yaml.safe_load` discards line numbers. Every claim FACTCHECK
   emits has to cite `ci.yml:23`, so every value the parser returns carries the
   line it came from.
2. **Portability.** Stdlib-only means it runs wherever Python 3 does — no
   install step between a judge and a working demo.

A bonus: this parser is not YAML 1.1, so `on:` stays the string `"on"` instead of
being coerced to the boolean `True`, which is what a workflow file means by it.

## Validation

A hand-rolled parser fails *silently* — it stops early, raises nothing, and the
rest of the file disappears. So correctness is checked against an independent
grep: every `run:` key in a workflow (excluding `defaults: run:` and `run:` as an
action input) must surface as exactly one extracted block, and every child key of
`services:` as exactly one service.

```sh
python3 sweep.py PostHog/posthog discourse/discourse ggml-org/llama.cpp
python3 tests/test_yamlish.py     # offline, no network
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

Each one is a test in `tests/test_yamlish.py`.

## Notes for phase C

- **Precedence needs an "unresolvable" state.** plausible/analytics sets its
  Elixir/OTP versions from `${{ steps.versions.outputs.erlang }}` — a step that
  reads `.tool-versions`. The lookup must detect a non-literal value and fall
  through to the next source rather than emit an expression as the answer.
- **Facts can be multi-valued.** netbox tests on Python `3.12 | 3.13 | 3.14`. The
  table returns one winning *source*; the value may still be a set. The document
  shows the range, `factcheck.sh` picks one deterministically.
- **Images are often unpinned.** netbox's CI says `image: postgres` with no tag.
  "PostgreSQL, version unpinned in CI" is honest; inventing `15` is the kind of
  hallucination that destroys trust in the whole document.
- Not yet captured: `defaults.run.working-directory` and `shell`, both needed for
  a faithful `factcheck.sh`.
