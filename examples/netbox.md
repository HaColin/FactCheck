# FACTCHECK: netbox-community/netbox

What it takes to run this repo, read from CI rather than from prose.

- **Primary CI:** [`.github/workflows/ci.yml`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/ci.yml#L1) — runs on push, pull_request
- **Commit:** [`eaf30a6fb00e`](https://github.com/netbox-community/netbox/tree/eaf30a6fb00ef0424e8bff276eec4c282b31f22c) on `main`
- **Method:** a [fixed precedence table](#method), applied as code. Same commit in, same document out.

**verified** = executed by CI or a container build  ·  *claimed* = prose a human wrote once

## Conflicts

Nothing in the prose contradicts what CI executes.

## Required but undocumented

CI needs these. The prose never mentions them — which is usually why a fresh clone does not run.

| What | Value | Source |
|---|---|---|
| `postgres` | `postgres` | [`.github/workflows/ci.yml:99`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/ci.yml#L99) |
| `redis` | `redis` | [`.github/workflows/ci.yml:95`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/ci.yml#L95) |

## Runtime

| Tool | Version | Source | |
|---|---|---|---|
| node | `20` | [`.github/workflows/ci.yml:162`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/ci.yml#L162) | verified |
| python | `3.12 \| 3.13 \| 3.14` | [`.github/workflows/ci.yml:118`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/ci.yml#L118) | verified |

## Services required

| Service | Image | Where | Source |
|---|---|---|---|
| postgres | `postgres` | job test, ports 5432:5432 | [`.github/workflows/ci.yml:99`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/ci.yml#L99) |
| redis | `redis` | job test, ports 6379:6379 | [`.github/workflows/ci.yml:95`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/ci.yml#L95) |

_`postgres`, `redis`: the image is unpinned in CI, so no version is asserted here._

## Install

- `python -m pip install --upgrade pip` — [`.github/workflows/ci.yml:122`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/ci.yml#L122) · job test
- `pip install -r requirements.txt` — [`.github/workflows/ci.yml:122`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/ci.yml#L122) · job test
- `pip install coverage tblib` — [`.github/workflows/ci.yml:122`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/ci.yml#L122) · job test
- `npm install -g yarn` — [`.github/workflows/ci.yml:165`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/ci.yml#L165) · job frontend

## Setup

- `python netbox/manage.py makemigrations --check` — [`.github/workflows/ci.yml:127`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/ci.yml#L127) · job test
- `python netbox/manage.py collectstatic --no-input` — [`.github/workflows/ci.yml:132`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/ci.yml#L132) · job test

## Build

- `python -m build` — [`.github/workflows/release.yml:91`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/release.yml#L91) · job build

## Test

- `python netbox/manage.py test netbox/ --parallel` — [`.github/workflows/ci.yml:136`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/ci.yml#L136) · job test
- `coverage run netbox/manage.py test netbox/ --parallel` — [`.github/workflows/ci.yml:140`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/ci.yml#L140) · job test

## Environment

| Variable | Value in CI | Source | |
|---|---|---|---|
| `NETBOX_CONFIGURATION` | `netbox.configuration_testing` | [`.github/workflows/ci.yml:84`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/ci.yml#L84) | verified |

## Tested on

- `ubuntu-latest` — [`.github/workflows/ci.yml:37`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/ci.yml#L37)

_Only these are evidenced. Other platforms may work; CI does not say so._

## Sources read

| Category | Files |
|---|---|
| ci | `.github/workflows/ci.yml`, `.github/workflows/claude-issue-triage.yml`, `.github/workflows/claude.yml`, `.github/workflows/close-incomplete-issues.yml`, `.github/workflows/close-stale-issues.yml`, `.github/workflows/codeql.yml` _+5 more_ |
| container | _none found_ |
| manifest | `pyproject.toml`, `requirements.txt` |
| lockfile | _none found_ |
| toolchain | _none found_ |
| env | _none found_ |
| prose | `README.md`, `CONTRIBUTING.md` |

Workflows treated as evidence, in order of authority over what runs on every merge:

- [`.github/workflows/ci.yml`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/ci.yml#L1) — on push, pull_request
- [`.github/workflows/release.yml`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/release.yml#L1) — on pull_request, push, workflow_dispatch
- [`.github/workflows/codeql.yml`](https://github.com/netbox-community/netbox/blob/eaf30a6fb00ef0424e8bff276eec4c282b31f22c/.github/workflows/codeql.yml#L1) — on push, pull_request, schedule

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
