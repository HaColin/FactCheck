# FACTCHECK: expressjs/express

What it takes to run this repo, read from CI rather than from prose.

- **Primary CI:** [`.github/workflows/ci.yml`](https://github.com/expressjs/express/blob/023767fe9872e029271df1418f73401bff20ff40/.github/workflows/ci.yml#L1) — runs on push, pull_request, workflow_dispatch
- **Commit:** [`023767fe9872`](https://github.com/expressjs/express/tree/023767fe9872e029271df1418f73401bff20ff40) on `master`
- **Method:** a [fixed precedence table](#method), applied as code. Same commit in, same document out.

**verified** = executed by CI or a container build  ·  *claimed* = prose a human wrote once

## Conflicts

Nothing in the prose contradicts what CI executes.

## Runtime

| Tool | Version | Source | |
|---|---|---|---|
| node | `18 \| 19 \| 20 \| 21 \| 22 \| 23 \| 24 \| 25 \| 26` | [`.github/workflows/ci.yml:63`](https://github.com/expressjs/express/blob/023767fe9872e029271df1418f73401bff20ff40/.github/workflows/ci.yml#L63) | verified |

A higher-authority source was present but not literal, so the table fell through to what is shown above:

- `node`: `lts/*` at [`.github/workflows/ci.yml:36`](https://github.com/expressjs/express/blob/023767fe9872e029271df1418f73401bff20ff40/.github/workflows/ci.yml#L36) could not be read as a version

## Install

- `npm install --ignore-scripts --include=dev` — [`.github/workflows/ci.yml:39`](https://github.com/expressjs/express/blob/023767fe9872e029271df1418f73401bff20ff40/.github/workflows/ci.yml#L39) · job lint
- `npm install` — [`.github/workflows/ci.yml:71`](https://github.com/expressjs/express/blob/023767fe9872e029271df1418f73401bff20ff40/.github/workflows/ci.yml#L71) · job test

## Test

- `npm run test-ci` — [`.github/workflows/ci.yml:80`](https://github.com/expressjs/express/blob/023767fe9872e029271df1418f73401bff20ff40/.github/workflows/ci.yml#L80) · job test

## Lint

- `npm run lint` — [`package.json:92`](https://github.com/expressjs/express/blob/023767fe9872e029271df1418f73401bff20ff40/package.json#L92) · eslint .
- `npm run lint:fix` — [`package.json:93`](https://github.com/expressjs/express/blob/023767fe9872e029271df1418f73401bff20ff40/package.json#L93) · eslint . --fix

## Tested on

- `ubuntu-latest` — [`.github/workflows/ci.yml:28`](https://github.com/expressjs/express/blob/023767fe9872e029271df1418f73401bff20ff40/.github/workflows/ci.yml#L28)
- `ubuntu-latest | windows-latest` — [`.github/workflows/ci.yml:54`](https://github.com/expressjs/express/blob/023767fe9872e029271df1418f73401bff20ff40/.github/workflows/ci.yml#L54)

_Only these are evidenced. Other platforms may work; CI does not say so._

## Sources read

| Category | Files |
|---|---|
| ci | `.github/workflows/ci.yml`, `.github/workflows/codeql.yml`, `.github/workflows/legacy.yml`, `.github/workflows/scorecard.yml` |
| container | _none found_ |
| manifest | `package.json` |
| lockfile | _none found_ |
| toolchain | _none found_ |
| env | _none found_ |
| prose | `Readme.md` |

Workflows treated as evidence, in order of authority over what runs on every merge:

- [`.github/workflows/ci.yml`](https://github.com/expressjs/express/blob/023767fe9872e029271df1418f73401bff20ff40/.github/workflows/ci.yml#L1) — on push, pull_request, workflow_dispatch
- [`.github/workflows/legacy.yml`](https://github.com/expressjs/express/blob/023767fe9872e029271df1418f73401bff20ff40/.github/workflows/legacy.yml#L1) — on push, pull_request, workflow_dispatch
- [`.github/workflows/codeql.yml`](https://github.com/expressjs/express/blob/023767fe9872e029271df1418f73401bff20ff40/.github/workflows/codeql.yml#L1) — on push, pull_request, schedule, workflow_dispatch
- [`.github/workflows/scorecard.yml`](https://github.com/expressjs/express/blob/023767fe9872e029271df1418f73401bff20ff40/.github/workflows/scorecard.yml#L1) — on branch_protection_rule, schedule, push

## Method

Each fact is resolved by walking a fixed list of sources and taking the first one that says something readable. The list is code, not a prompt, so the same commit always produces the same document.

| Fact | Source order, highest authority first |
|---|---|
| runtime | `toolchain-file` → `ci-setup` → `dockerfile-from` → `manifest-engines` → `readme` |
| install | `ci-run` → `dockerfile-run` → `lockfile` → `readme` |
| build | `ci-run` → `manifest-scripts` → `readme` |
| test | `ci-run` → `manifest-scripts` → `readme` |
| lint | `ci-run` → `manifest-scripts` → `readme` |
| setup | `ci-run` → `dockerfile-run` → `readme` |
| services | `ci-services` → `docker-compose` → `env-example` |
| env | `ci-env` → `env-example` |
| os | `ci-runs-on` → `readme` |

Rules the table applies:

1. Only workflows triggered on push, pull request or merge queue count as evidence — CI is ground truth because it runs on every merge.
2. A value that is not literal (`${{ steps.x.outputs.y }}`) never wins, and is never printed as an answer.
3. One source disagreeing with itself is a matrix, not a conflict.
4. A conflict requires two different kinds of source.
5. Version constraints keep their operators: `>=3.7` is not `3.7`.

---

Generated by [FACTCHECK](https://github.com/HaColin/FactCheck). No claim appears here without a file and a line behind it.
