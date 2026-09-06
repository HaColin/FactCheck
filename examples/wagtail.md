# FACTCHECK: wagtail/wagtail

What it takes to run this repo, read from CI rather than from prose.

- **Primary CI:** [`.github/workflows/test.yml`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L1) — runs on push, pull_request
- **Commit:** [`bddc5eaf2e77`](https://github.com/wagtail/wagtail/tree/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417) on `main`
- **Method:** a [fixed precedence table](#method), applied as code. Same commit in, same document out.

**verified** = executed by CI or a container build  ·  *claimed* = prose a human wrote once

## Conflicts

Nothing in the prose contradicts what CI executes.

## Required but undocumented

CI needs these. The prose never mentions them — which is usually why a fresh clone does not run.

| What | Value | Source |
|---|---|---|
| `DATABASE_ENGINE` | `django.db.backends.sqlite3 \| django.db.backends.postgresql \| django.db.backends.mysql` | [`.github/workflows/test.yml:83`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L83) |
| `DATABASE_HOST` | `localhost \| 127.0.0.1` | [`.github/workflows/test.yml:163`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L163) |
| `DATABASE_PASSWORD` | `postgres \| root` | [`.github/workflows/test.yml:165`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L165) |
| `DATABASE_USER` | `postgres \| root` | [`.github/workflows/test.yml:164`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L164) |
| `PYTHONWARNINGS` | `error` | [`.github/workflows/test.yml:178`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L178) |

## Runtime

| Tool | Version | Source | |
|---|---|---|---|
| node | `24` | [`.nvmrc:1`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.nvmrc#L1) | verified |
| python | `3.13 \| 3.11 \| 3.14 \| 3.12` | [`.github/workflows/test.yml:70`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L70) | verified |

## Services required

| Service | Image | Where | Source |
|---|---|---|---|
| elasticsearch | `docker.elastic.co/elasticsearch/elasticsearch:8.11.2 \| docker.elastic.co/elasticsearch/elasticsearch:7.17.13` | job test-sqlite-elasticsearch8, ports 9200:9200 | [`.github/workflows/test.yml:278`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L278) |
| postgres | `postgres:latest` | job test-postgres-elasticsearch7, ports 5432:5432 | [`.github/workflows/test.yml:335`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L335) |

## Install

- `uv sync --locked --extra testing --config-setting editable_mode=strict` — [`.github/workflows/test.yml:75`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L75) · job test-sqlite
- `uv pip install "Django>=5.2,<5.3 | Django>=6.0,<6.1"` — [`.github/workflows/test.yml:75`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L75) · job test-sqlite
- `sudo apt-get install -y libpq-dev` — [`.github/workflows/test.yml:146`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L146) · job test-postgres
- `uv pip install "psycopg2>=2.8.4 | psycopg>=3.1.8"` — [`.github/workflows/test.yml:152`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L152) · job test-postgres
- `uv pip install "Django>=5.2,<5.3 | Django>=6.1,<6.2 | git+https://github.com/django/django.git@stable/6.1.x#egg=Django | git+https://github.com/django/django.git@main#egg=Django"` — [`.github/workflows/test.yml:152`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L152) · job test-postgres
- `uv pip install mysqlclient` — [`.github/workflows/test.yml:244`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L244) · job test-mysql
- `uv pip install "Django>=5.2,<5.3 | Django>=6.0,<6.1 | Django>=6.1,<6.2"` — [`.github/workflows/test.yml:244`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L244) · job test-mysql
- `uv pip install "Django>=6.1,<6.2"` — [`.github/workflows/test.yml:302`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L302) · job test-sqlite-elasticsearch8
- `uv pip install "elasticsearch>=8,<9"` — [`.github/workflows/test.yml:302`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L302) · job test-sqlite-elasticsearch8
- `uv pip install certifi` — [`.github/workflows/test.yml:302`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L302) · job test-sqlite-elasticsearch8
- `uv pip install "psycopg2>=2.6"` — [`.github/workflows/test.yml:370`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L370) · job test-postgres-elasticsearch7
- `uv pip install "Django>=5.2,<5.3"` — [`.github/workflows/test.yml:370`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L370) · job test-postgres-elasticsearch7

## Setup

- `python manage.py makemigrations --check --dry-run` — [`.github/workflows/test.yml:180`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L180) · job test-postgres
- `python manage.py migrate` — [`.github/workflows/test.yml:180`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L180) · job test-postgres

## Build

- `npm run start` — [`package.json:146`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L146) · webpack --config ./client/webpack.config.js --mode development --progress --watch
- `npm run build` — [`package.json:147`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L147) · webpack --config ./client/webpack.config.js --mode production
- `npm run build-docs` — [`package.json:165`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L165) · typedoc
- `npm run build-storybook` — [`package.json:166`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L166) · storybook build -c client/storybook

## Test

- `npm run test` — [`package.json:159`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L159) · npm run test:unit
- `npm run test:unit` — [`package.json:160`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L160) · jest
- `npm run test:unit:watch` — [`package.json:161`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L161) · jest --watch
- `npm run test:unit:coverage` — [`package.json:162`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L162) · jest --coverage
- `npm run test:integration` — [`package.json:163`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L163) · ./client/tests/integration/node_modules/.bin/jest --config ./client/tests/integration/jest.config.js

## Lint

- `npm run fix:css` — [`package.json:149`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L149) · stylelint --fix **/*.scss
- `npm run fix:js` — [`package.json:150`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L150) · eslint --fix .
- `npm run format` — [`package.json:151`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L151) · prettier --write "**/?(.)*.{css,scss,js,ts,tsx,json,jsonc,yaml,yml}"
- `npm run lint:js` — [`package.json:153`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L153) · eslint --report-unused-disable-directives .
- `npm run lint:css` — [`package.json:154`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L154) · stylelint **/*.scss
- `npm run debug:eslint` — [`package.json:155`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L155) · eslint --print-config ./client/src/entrypoints/contrib/table_block/table.js
- `npm run lint:format` — [`package.json:156`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L156) · prettier --check "**/?(.)*.{css,scss,js,ts,tsx,json,jsonc,yaml,yml}"
- `npm run lint:ts` — [`package.json:158`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L158) · tsc --noEmit

## Environment

| Variable | Value in CI | Source | |
|---|---|---|---|
| `DATABASE_ENGINE` | `django.db.backends.sqlite3 \| django.db.backends.postgresql \| django.db.backends.mysql` | [`.github/workflows/test.yml:83`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L83) | verified |
| `DATABASE_HOST` | `localhost \| 127.0.0.1` | [`.github/workflows/test.yml:163`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L163) | verified |
| `DATABASE_PASSWORD` | `postgres \| root` | [`.github/workflows/test.yml:165`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L165) | verified |
| `DATABASE_USER` | `postgres \| root` | [`.github/workflows/test.yml:164`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L164) | verified |
| `PYTHONWARNINGS` | `error` | [`.github/workflows/test.yml:178`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L178) | verified |

## Tested on

- `ubuntu-26.04-arm` — [`.github/workflows/test.yml:49`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L49)

_Only these are evidenced. Other platforms may work; CI does not say so._

## Claimed, not verified

The prose gives these commands; nothing in CI executes them.

- `npm run start` — [`package.json:146`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L146)
- `npm run build` — [`package.json:147`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L147)
- `npm run build-docs` — [`package.json:165`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L165)
- `npm run build-storybook` — [`package.json:166`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L166)
- `npm run test` — [`package.json:159`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L159)
- `npm run test:unit` — [`package.json:160`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L160)
- `npm run test:unit:watch` — [`package.json:161`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L161)
- `npm run test:unit:coverage` — [`package.json:162`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/package.json#L162)

## Sources read

| Category | Files |
|---|---|
| ci | `.github/workflows/codeql-analysis.yml`, `.github/workflows/latest-deps.yml`, `.github/workflows/test.yml`, `.github/workflows/zizmor.yml`, `.circleci/config.yml` |
| container | _none found_ |
| manifest | `package.json`, `pyproject.toml`, `setup.py`, `Makefile` |
| lockfile | `package-lock.json`, `uv.lock` |
| toolchain | `.nvmrc` |
| env | _none found_ |
| prose | `README.md`, `docs/README.md` |

Workflows treated as evidence, in order of authority over what runs on every merge:

- [`.github/workflows/test.yml`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/test.yml#L1) — on push, pull_request
- [`.github/workflows/zizmor.yml`](https://github.com/wagtail/wagtail/blob/bddc5eaf2e77d6777b11d0e8cd4a3b62cf707417/.github/workflows/zizmor.yml#L1) — on push, pull_request

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
