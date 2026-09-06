# FACTCHECK: plausible/analytics

What it takes to run this repo, read from CI rather than from prose.

- **Primary CI:** [`.github/workflows/elixir.yml`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L1) — runs on pull_request, push, merge_group
- **Commit:** [`543b30185c10`](https://github.com/plausible/analytics/tree/543b30185c104ce17900d03c95d95429180acc0b) on `master`
- **Method:** a [fixed precedence table](#method), applied as code. Same commit in, same document out.

**verified** = executed by CI or a container build  ·  *claimed* = prose a human wrote once

## Conflicts

Nothing in the prose contradicts what CI executes.

## Required but undocumented

CI needs these. The prose never mentions them — which is usually why a fresh clone does not run.

| What | Value | Source |
|---|---|---|
| `BASE_URL` | `http://localhost:8111` | [`.github/workflows/elixir.yml:124`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L124) |
| `MINIO_HOST_FOR_CLICKHOUSE` | `172.17.0.1` | [`.github/workflows/elixir.yml:109`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L109) |
| `MIX_ENV` | `e2e_test \| test` | [`.github/workflows/elixir.yml:123`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L123) |

## Runtime

| Tool | Version | Source | |
|---|---|---|---|
| elixir | `1.20.4-otp-28` | [`.tool-versions:2`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.tool-versions#L2) | verified |
| erlang | `28.5.0.5` | [`.tool-versions:1`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.tool-versions#L1) | verified |
| node | `24.17.0` | [`.tool-versions:3`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.tool-versions#L3) | verified |

A higher-authority source was present but not literal, so the table fell through to what is shown above:

- `elixir`: `${{ steps.versions.outputs.elixir }}` at [`.github/workflows/elixir.yml:63`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L63) could not be read as a version
- `node`: `${{steps.versions.outputs.nodejs}}` at [`.github/workflows/node.yml:26`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/node.yml#L26) could not be read as a version
- `otp`: `${{ steps.versions.outputs.erlang }}` at [`.github/workflows/elixir.yml:64`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L64) could not be read as a version — and nothing lower supplied one

## Services required

| Service | Image | Where | Source |
|---|---|---|---|
| clickhouse | `clickhouse/clickhouse-server:25.11.5.8-alpine` | job build, ports 8123:8123 | [`.github/workflows/elixir.yml:42`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L42) |
| postgres | `postgres:18` | job e2e, ports 5432:5432 | [`.github/workflows/elixir.yml:127`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L127) |

## Install

- `npm install --prefix ./tracker` — [`.github/workflows/elixir.yml:94`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L94) · job build
- `mix deps.get --only $MIX_ENV` — [`.github/workflows/elixir.yml:99`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L99) · job build
- `npm install --prefix ./assets` — [`.github/workflows/elixir.yml:207`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L207) · job e2e
- `mix deps.get` — [`.github/workflows/elixir.yml:294`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L294) · job static

## Setup

- `mix do ecto.create, ecto.migrate` — [`.github/workflows/elixir.yml:101`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L101) · job build
- `mix assets.deploy` — [`.github/workflows/elixir.yml:208`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L208) · job e2e

## Build

- `mix compile --warnings-as-errors --all-warnings` — [`.github/workflows/elixir.yml:100`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L100) · job build
- `make minio` — [`.github/workflows/elixir.yml:104`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L104) · job build

## Test

- `mix test --include slow --include minio --include migrations --max-failures 1 --warnings-as-errors --partitions 6` — [`.github/workflows/elixir.yml:106`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L106) · job build
- `mix test --include slow --include migrations --max-failures 1 --warnings-as-errors --partitions 6` — [`.github/workflows/elixir.yml:113`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L113) · job build
- `npx playwright install --with-deps chromium` — [`.github/workflows/elixir.yml:225`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L225) · job e2e, in ./e2e
- `npx playwright merge-reports --reporter list ../all-e2e-blob-reports` — [`.github/workflows/elixir.yml:262`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L262) · job merge-sharded-e2e-test-report, in ./e2e

## Lint

- `npm --prefix ./e2e run typecheck` — [`.github/workflows/elixir.yml:220`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L220) · job e2e
- `mix format --check-formatted` — [`.github/workflows/elixir.yml:296`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L296) · job static
- `mix credo diff --from-git-merge-base origin/master` — [`.github/workflows/elixir.yml:299`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L299) · job static

## Environment

| Variable | Value in CI | Source | |
|---|---|---|---|
| `BASE_URL` | `http://localhost:8111` | [`.github/workflows/elixir.yml:124`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L124) | verified |
| `MINIO_HOST_FOR_CLICKHOUSE` | `172.17.0.1` | [`.github/workflows/elixir.yml:109`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L109) | verified |
| `MIX_ENV` | `e2e_test \| test` | [`.github/workflows/elixir.yml:123`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L123) | verified |

## Tested on

- `blacksmith-4vcpu-ubuntu-2404` — [`.github/workflows/elixir.yml:20`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L20)

_Only these are evidenced. Other platforms may work; CI does not say so._

## Sources read

| Category | Files |
|---|---|
| ci | `.github/workflows/all-checks-pass.yml`, `.github/workflows/build-private-images-ghcr.yml`, `.github/workflows/build-public-images-ghcr.yml`, `.github/workflows/codespell.yml`, `.github/workflows/comment-preview-url.yml`, `.github/workflows/elixir.yml` _+8 more_ |
| container | `Dockerfile` |
| manifest | `mix.exs`, `Makefile` |
| lockfile | `mix.lock` |
| toolchain | `.tool-versions` |
| env | _none found_ |
| prose | `README.md`, `CONTRIBUTING.md` |

Workflows treated as evidence, in order of authority over what runs on every merge:

- [`.github/workflows/elixir.yml`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/elixir.yml#L1) — on pull_request, push, merge_group
- [`.github/workflows/node.yml`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/node.yml#L1) — on push, pull_request, merge_group
- [`.github/workflows/codespell.yml`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/codespell.yml#L1) — on pull_request, push, merge_group
- [`.github/workflows/build-private-images-ghcr.yml`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/build-private-images-ghcr.yml#L1) — on push, pull_request
- [`.github/workflows/terraform-e2e.yml`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/terraform-e2e.yml#L1) — on push, pull_request
- [`.github/workflows/tracker.yml`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/tracker.yml#L1) — on workflow_dispatch, pull_request
- [`.github/workflows/all-checks-pass.yml`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/all-checks-pass.yml#L1) — on pull_request, merge_group
- [`.github/workflows/build-public-images-ghcr.yml`](https://github.com/plausible/analytics/blob/543b30185c104ce17900d03c95d95429180acc0b/.github/workflows/build-public-images-ghcr.yml#L1) — on push

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
