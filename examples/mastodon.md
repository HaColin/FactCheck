# FACTCHECK: mastodon/mastodon

What it takes to run this repo, read from CI rather than from prose.

- **Primary CI:** [`.github/workflows/test-ruby.yml`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L1) — runs on merge_group, push, pull_request
- **Commit:** [`0a32b4a83183`](https://github.com/mastodon/mastodon/tree/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d) on `main`
- **Method:** a [fixed precedence table](#method), applied as code. Same commit in, same document out.

**verified** = executed by CI or a container build  ·  *claimed* = prose a human wrote once

## Conflicts

Nothing in the prose contradicts what CI executes.

## System packages

Your language's package manager does not install these — `pip`, `npm` and `bundler` all build against them rather than providing them. CI's runner image already has them, which is why its workflow never mentions them, and why a fresh clone fails partway through the install with an error about a missing header.

| Because of | It needs | Debian/Ubuntu | macOS | Arch |
|---|---|---|---|---|
| [`pg`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/Gemfile#L13) at `Gemfile:13` | pg_config, from the PostgreSQL client library | `libpq-dev` | `libpq` | `postgresql-libs` |

## Required but undocumented

CI needs these. The prose never mentions them — which is usually why a fresh clone does not run.

| What | Value | Source |
|---|---|---|
| `ALLOW_NOPAM` | `true` | [`.github/workflows/test-ruby.yml:114`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L114) |
| `BUNDLE_WITH` | `pam_authentication test \| test` | [`.github/workflows/test-ruby.yml:122`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L122) |
| `CAS_ENABLED` | `true` | [`.github/workflows/test-ruby.yml:121`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L121) |
| `DB_HOST` | `localhost` | [`.github/workflows/test-ruby.yml:109`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L109) |
| `DB_PASS` | `postgres` | [`.github/workflows/test-ruby.yml:111`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L111) |
| `DB_USER` | `postgres` | [`.github/workflows/test-ruby.yml:110`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L110) |
| `ES_ENABLED` | `true` | [`.github/workflows/test-ruby.yml:349`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L349) |
| `ES_HOST` | `localhost` | [`.github/workflows/test-ruby.yml:350`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L350) |
| `ES_PORT` | `9200` | [`.github/workflows/test-ruby.yml:351`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L351) |
| `LOCAL_DOMAIN` | `localhost:3000` | [`.github/workflows/test-ruby.yml:217`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L217) |
| `LOCAL_HTTPS` | `false` | [`.github/workflows/test-ruby.yml:218`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L218) |
| `OIDC_ENABLED` | `true` | [`.github/workflows/test-ruby.yml:118`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L118) |
| `OIDC_SCOPE` | `read` | [`.github/workflows/test-ruby.yml:119`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L119) |
| `PAM_CONTROLLED_SERVICE` | `pam_test_controlled` | [`.github/workflows/test-ruby.yml:117`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L117) |
| `PAM_DEFAULT_SERVICE` | `pam_test` | [`.github/workflows/test-ruby.yml:116`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L116) |
| `PAM_ENABLED` | `true` | [`.github/workflows/test-ruby.yml:115`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L115) |
| `SAML_ENABLED` | `true` | [`.github/workflows/test-ruby.yml:120`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L120) |
| `SECRET_KEY_BASE_DUMMY` | `1` | [`.github/workflows/test-ruby.yml:33`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L33) |

## Runtime

| Tool | Version | Source | |
|---|---|---|---|
| node | `24.19` | [`.nvmrc:1`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.nvmrc#L1) | verified |
| ruby | `4.0.6` | [`.ruby-version:1`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.ruby-version#L1) | verified |
| yarn | `4.18.0` | [`package.json:4`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/package.json#L4) | claimed |

A higher-authority source was present but not literal, so the table fell through to what is shown above:

- `ruby`: `(unpinned - action default)` at [`.github/workflows/bundler-audit.yml:35`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/bundler-audit.yml#L35) could not be read as a version

## Services required

| Service | Image | Where | Source |
|---|---|---|---|
| postgres | `postgres:14-alpine` | job test, ports 5432:5432 | [`.github/workflows/test-ruby.yml:86`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L86) |
| redis | `redis:7-alpine` | job test, ports 6379:6379 | [`.github/workflows/test-ruby.yml:99`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L99) |

## Install

- `bundle install` — [`Gemfile.lock:1`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/Gemfile.lock#L1) · implied by the lockfile

## Setup

- `bin/rails assets:precompile` — [`.github/workflows/test-ruby.yml:62`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L62) · job build
- `bin/rails db:setup` — [`.github/workflows/test-ruby.yml:153`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L153) · job test
- `./bin/rails db:create db:schema:load db:seed` — [`.github/workflows/test-ruby.yml:251`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L251) · job test-e2e

## Build

- `yarn build-storybook` — [`.github/workflows/chromatic.yml:55`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/chromatic.yml#L55) · job chromatic

## Test

- `bin/flatware rspec` — [`.github/workflows/test-ruby.yml:169`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L169) · job test
- `yarn run playwright install --with-deps chromium` — [`.github/workflows/test-ruby.yml:262`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L262) · job test-e2e
- `yarn run playwright install-deps chromium` — [`.github/workflows/test-ruby.yml:266`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L266) · job test-e2e
- `bin/rspec spec/system --tag streaming --tag js` — [`.github/workflows/test-ruby.yml:268`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L268) · job test-e2e
- `bin/rspec --tag search` — [`.github/workflows/test-ruby.yml:389`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L389) · job test-search

## Lint

- `yarn lint:css --custom-formatter @csstools/stylelint-formatter-github` — [`.github/workflows/lint-css.yml:40`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/lint-css.yml#L40) · job lint

## Environment

| Variable | Value in CI | Source | |
|---|---|---|---|
| `ALLOW_NOPAM` | `true` | [`.github/workflows/test-ruby.yml:114`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L114) | verified |
| `BUNDLE_WITH` | `pam_authentication test \| test` | [`.github/workflows/test-ruby.yml:122`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L122) | verified |
| `CAS_ENABLED` | `true` | [`.github/workflows/test-ruby.yml:121`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L121) | verified |
| `DB_HOST` | `localhost` | [`.github/workflows/test-ruby.yml:109`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L109) | verified |
| `DB_PASS` | `postgres` | [`.github/workflows/test-ruby.yml:111`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L111) | verified |
| `DB_USER` | `postgres` | [`.github/workflows/test-ruby.yml:110`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L110) | verified |
| `ES_ENABLED` | `true` | [`.github/workflows/test-ruby.yml:349`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L349) | verified |
| `ES_HOST` | `localhost` | [`.github/workflows/test-ruby.yml:350`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L350) | verified |
| `ES_PORT` | `9200` | [`.github/workflows/test-ruby.yml:351`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L351) | verified |
| `LOCAL_DOMAIN` | `localhost:3000` | [`.github/workflows/test-ruby.yml:217`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L217) | verified |
| `LOCAL_HTTPS` | `false` | [`.github/workflows/test-ruby.yml:218`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L218) | verified |
| `OIDC_ENABLED` | `true` | [`.github/workflows/test-ruby.yml:118`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L118) | verified |
| `OIDC_SCOPE` | `read` | [`.github/workflows/test-ruby.yml:119`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L119) | verified |
| `PAM_CONTROLLED_SERVICE` | `pam_test_controlled` | [`.github/workflows/test-ruby.yml:117`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L117) | verified |
| `PAM_DEFAULT_SERVICE` | `pam_test` | [`.github/workflows/test-ruby.yml:116`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L116) | verified |
| `PAM_ENABLED` | `true` | [`.github/workflows/test-ruby.yml:115`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L115) | verified |
| `RAILS_ENV` | `test` | [`.github/workflows/test-ruby.yml:113`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L113) | verified |
| `SAML_ENABLED` | `true` | [`.github/workflows/test-ruby.yml:120`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L120) | verified |
| `SECRET_KEY_BASE_DUMMY` | `1` | [`.github/workflows/test-ruby.yml:33`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L33) | verified |

## Tested on

- `ubuntu-latest` — [`.github/workflows/test-ruby.yml:21`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L21)

_Only these are evidenced. Other platforms may work; CI does not say so._

## Sources read

| Category | Files |
|---|---|
| ci | `.github/workflows/build-container-image.yml`, `.github/workflows/build-nightly.yml`, `.github/workflows/build-push-pr.yml`, `.github/workflows/build-releases.yml`, `.github/workflows/build-security.yml`, `.github/workflows/bundler-audit.yml` _+16 more_ |
| container | `Dockerfile`, `docker-compose.yml`, `.devcontainer/devcontainer.json` |
| manifest | `package.json`, `Gemfile` |
| lockfile | `yarn.lock`, `Gemfile.lock` |
| toolchain | `.nvmrc`, `.ruby-version` |
| env | _none found_ |
| prose | `README.md`, `CONTRIBUTING.md`, `docs/DEVELOPMENT.md` |

Workflows treated as evidence, in order of authority over what runs on every merge:

- [`.github/workflows/test-ruby.yml`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-ruby.yml#L1) — on merge_group, push, pull_request
- [`.github/workflows/test-js.yml`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-js.yml#L1) — on merge_group, push, pull_request
- [`.github/workflows/test-migrations.yml`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/test-migrations.yml#L1) — on merge_group, push, pull_request
- [`.github/workflows/format-check.yml`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/format-check.yml#L1) — on merge_group, push, pull_request
- [`.github/workflows/bundler-audit.yml`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/bundler-audit.yml#L1) — on merge_group, push, pull_request, schedule
- [`.github/workflows/lint-css.yml`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/lint-css.yml#L1) — on merge_group, push, pull_request
- [`.github/workflows/lint-haml.yml`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/lint-haml.yml#L1) — on merge_group, push, pull_request
- [`.github/workflows/lint-js.yml`](https://github.com/mastodon/mastodon/blob/0a32b4a831838ef1f363a915c2e71e2a1b52cf0d/.github/workflows/lint-js.yml#L1) — on merge_group, push, pull_request

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
