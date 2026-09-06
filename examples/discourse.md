# FACTCHECK: discourse/discourse

What it takes to run this repo, read from CI rather than from prose.

- **Primary CI:** [`.github/workflows/tests.yml`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L1) — runs on pull_request, push
- **Commit:** [`5e9779d4cd41`](https://github.com/discourse/discourse/tree/5e9779d4cd418af07a6ed01005d558eda76f2f69) on `main`
- **Method:** a [fixed precedence table](#method), applied as code. Same commit in, same document out.

**verified** = executed by CI or a container build  ·  *claimed* = prose a human wrote once

## Conflicts

Where the documentation and the executed configuration disagree. CI wins because CI runs; that is the only reason.

### ruby

- `ci-setup` says **3.3** — [`.github/workflows/developer-docs-publish.yml:37`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/developer-docs-publish.yml#L37)
- `manifest-engines` says *~> 3.4* — [`Gemfile:3`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/Gemfile#L3)
- `readme` says *3.4+* — [`README.md:48`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/README.md#L48)
  > Before you get started, ensure you have the following minimum versions: [Ruby 3.4+ , [PostgreSQL 15 , [Redis 7 .

## Required but undocumented

CI needs these. The prose never mentions them — which is usually why a fresh clone does not run.

| What | Value | Source |
|---|---|---|
| `CAPYBARA_DEFAULT_MAX_WAIT_TIME` | `20` | [`.github/workflows/tests.yml:54`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L54) |
| `CHEAP_SOURCE_MAPS` | `1` | [`.github/workflows/tests.yml:57`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L57) |
| `CHECKOUT_TIMEOUT` | `10` | [`.github/workflows/tests.yml:308`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L308) |
| `DBUS_SESSION_BUS_ADDRESS` | `unix:path=/dev/null` | [`.github/workflows/tests.yml:58`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L58) |
| `EMBER_ENV` | `development` | [`.github/workflows/tests.yml:60`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L60) |
| `LOAD_PLUGINS` | — | [`.github/workflows/tests.yml:192`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L192) |
| `MINIO_RUNNER_INSTALL_DIR` | `/home/discourse/.minio_runner` | [`.github/workflows/tests.yml:59`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L59) |
| `MINIO_RUNNER_LOG_LEVEL` | `WARN` | [`.github/workflows/tests.yml:55`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L55) |
| `PGPASSWORD` | `discourse` | [`.github/workflows/tests.yml:52`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L52) |
| `PGUSER` | `discourse` | [`.github/workflows/tests.yml:51`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L51) |
| `PLAYWRIGHT_BROWSERS_PATH` | `/home/discourse/.cache/ms-playwright` | [`.github/workflows/tests.yml:63`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L63) |
| `QUNIT_REUSE_BUILD` | `1` | [`.github/workflows/tests.yml:62`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L62) |
| `RAILS_ENV` | `test` | [`.github/workflows/tests.yml:50`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L50) |
| `TEMPORARY_DB_PORT` | `11000 \| 11001` | [`.github/workflows/tests.yml:193`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L193) |

## Runtime

| Tool | Version | Source | |
|---|---|---|---|
| node | `24` | [`.github/workflows/developer-docs-lint.yml:41`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/developer-docs-lint.yml#L41) | verified |
| npm | `please-use-pnpm` | [`package.json:50`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/package.json#L50) | claimed |
| pnpm | `^10 \| 10.34.5` | [`package.json:52`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/package.json#L52) | claimed |
| ruby | `3.3` | [`.github/workflows/developer-docs-publish.yml:37`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/developer-docs-publish.yml#L37) | verified |
| yarn | `please-use-pnpm` | [`package.json:51`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/package.json#L51) | claimed |

A higher-authority source was present but not literal, so the table fell through to what is shown above:

- `pnpm`: `(unpinned - action default)` at [`.github/workflows/developer-docs-lint.yml:37`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/developer-docs-lint.yml#L37) could not be read as a version

## Install

- `bundle install --jobs $(($(nproc) - 1))` — [`.github/workflows/tests.yml:133`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L133) · job build
- `pnpm install --frozen-lockfile` — [`.github/workflows/tests.yml:140`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L140) · job build

## Setup

- `bin/rake db:create` — [`.github/workflows/tests.yml:179`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L179) · job build
- `bin/rake db:migrate` — [`.github/workflows/tests.yml:183`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L183) · job build
- `bin/rake parallel:create parallel:migrate` — [`.github/workflows/tests.yml:187`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L187) · job build

## Build

- `npm run lint:types` — [`package.json:38`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/package.json#L38) · ember-tsc -b
- `npm run types:generate` — [`package.json:39`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/package.json#L39) · pnpm --dir=frontend/discourse-i18n ember-tsc && pnpm --dir=frontend/discourse-types generate-external
- `npm run types:watch` — [`package.json:40`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/package.json#L40) · pnpm types:generate && pnpm ember-tsc -b --watch --preserveWatchOutput
- `npm run build` — [`package.json:45`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/package.json#L45) · pnpm --silent --dir=frontend/discourse build

## Test

- `pnpm test` — [`.github/workflows/tests.yml:280`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L280) · job build, in frontend/asset-processor
- `pnpm playwright-install` — [`.github/workflows/tests.yml:303`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L303) · job build

## Lint

- `bundle exec rubocop` — [`.github/workflows/linting.yml:74`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/linting.yml#L74) · job build
- `pnpm prettier -v` — [`.github/workflows/linting.yml:93`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/linting.yml#L93) · job build
- `pnpm lint:prettier` — [`.github/workflows/linting.yml:93`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/linting.yml#L93) · job build

## Environment

| Variable | Value in CI | Source | |
|---|---|---|---|
| `CAPYBARA_DEFAULT_MAX_WAIT_TIME` | `20` | [`.github/workflows/tests.yml:54`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L54) | verified |
| `CHEAP_SOURCE_MAPS` | `1` | [`.github/workflows/tests.yml:57`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L57) | verified |
| `CHECKOUT_TIMEOUT` | `10` | [`.github/workflows/tests.yml:308`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L308) | verified |
| `DBUS_SESSION_BUS_ADDRESS` | `unix:path=/dev/null` | [`.github/workflows/tests.yml:58`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L58) | verified |
| `EMBER_ENV` | `development` | [`.github/workflows/tests.yml:60`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L60) | verified |
| `LOAD_PLUGINS` | — | [`.github/workflows/tests.yml:192`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L192) | verified |
| `MINIO_RUNNER_INSTALL_DIR` | `/home/discourse/.minio_runner` | [`.github/workflows/tests.yml:59`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L59) | verified |
| `MINIO_RUNNER_LOG_LEVEL` | `WARN` | [`.github/workflows/tests.yml:55`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L55) | verified |
| `PGPASSWORD` | `discourse` | [`.github/workflows/tests.yml:52`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L52) | verified |
| `PGUSER` | `discourse` | [`.github/workflows/tests.yml:51`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L51) | verified |
| `PLAYWRIGHT_BROWSERS_PATH` | `/home/discourse/.cache/ms-playwright` | [`.github/workflows/tests.yml:63`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L63) | verified |
| `QUNIT_REUSE_BUILD` | `1` | [`.github/workflows/tests.yml:62`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L62) | verified |
| `RAILS_ENV` | `test` | [`.github/workflows/tests.yml:50`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L50) | verified |
| `TEMPORARY_DB_PORT` | `11000 \| 11001` | [`.github/workflows/tests.yml:193`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L193) | verified |

## Tested on

- `ubuntu-latest` — [`.github/workflows/tests.yml:371`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L371)

_Only these are evidenced. Other platforms may work; CI does not say so._

## Claimed, not verified

The prose gives these commands; nothing in CI executes them.

- `npm run lint:types` — [`package.json:38`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/package.json#L38)
- `npm run types:generate` — [`package.json:39`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/package.json#L39)
- `npm run types:watch` — [`package.json:40`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/package.json#L40)
- `npm run build` — [`package.json:45`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/package.json#L45)

## Sources read

| Category | Files |
|---|---|
| ci | `.github/workflows/backport.yml`, `.github/workflows/check-pr-body.yml`, `.github/workflows/dependabot-bundler-checksums.yml`, `.github/workflows/dependabot-pnpm-dedupe.yml`, `.github/workflows/developer-docs-lint.yml`, `.github/workflows/developer-docs-publish.yml` _+13 more_ |
| container | `.devcontainer/devcontainer.json` |
| manifest | `package.json`, `Gemfile` |
| lockfile | `pnpm-lock.yaml`, `Gemfile.lock` |
| toolchain | _none found_ |
| env | _none found_ |
| prose | `README.md`, `CONTRIBUTING.md`, `docs/INSTALL.md` |

Workflows treated as evidence, in order of authority over what runs on every merge:

- [`.github/workflows/tests.yml`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/tests.yml#L1) — on pull_request, push
- [`.github/workflows/migration-tests.yml`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/migration-tests.yml#L1) — on pull_request, push
- [`.github/workflows/licenses.yml`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/licenses.yml#L1) — on pull_request, push
- [`.github/workflows/linting.yml`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/linting.yml#L1) — on pull_request, push
- [`.github/workflows/check-pr-body.yml`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/check-pr-body.yml#L1) — on pull_request_target
- [`.github/workflows/developer-docs-lint.yml`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/developer-docs-lint.yml#L1) — on pull_request, push
- [`.github/workflows/developer-docs-publish.yml`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/developer-docs-publish.yml#L1) — on push, pull_request
- [`.github/workflows/dependabot-bundler-checksums.yml`](https://github.com/discourse/discourse/blob/5e9779d4cd418af07a6ed01005d558eda76f2f69/.github/workflows/dependabot-bundler-checksums.yml#L1) — on push

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

Generated by [FACTCHECK](https://github.com/HaColin/factcheck). No claim appears here without a file and a line behind it.
