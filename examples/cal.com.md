# FACTCHECK: calcom/cal.com

What it takes to run this repo, read from CI rather than from prose.

- **Primary CI:** [`.github/workflows/all-checks.yml`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.github/workflows/all-checks.yml#L1) — runs on merge_group, workflow_dispatch
- **Commit:** [`abffde336e74`](https://github.com/calcom/cal.com/tree/abffde336e744e15cf69626c10e436d6172bc406) on `main`
- **Method:** a [fixed precedence table](#method), applied as code. Same commit in, same document out.

**verified** = executed by CI or a container build  ·  *claimed* = prose a human wrote once

## Conflicts

Nothing in the prose contradicts what CI executes.

## Required but undocumented

CI needs these. The prose never mentions them — which is usually why a fresh clone does not run.

| What | Value | Source |
|---|---|---|
| `redis` | `redis:latest` | [`docker-compose.yml:28`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/docker-compose.yml#L28) |

## Runtime

| Tool | Version | Source | |
|---|---|---|---|
| node | `20` | [`.github/workflows/i18n.yml:31`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.github/workflows/i18n.yml#L31) | verified |
| npm | `>=7.0.0` | [`package.json:222`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/package.json#L222) | claimed |
| yarn | `>=4.12.0 \| 4.12.0` | [`package.json:223`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/package.json#L223) | claimed |

## Services required

| Service | Image | Where | Source |
|---|---|---|---|
| postgres | `postgres` | — | [`docker-compose.yml:15`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/docker-compose.yml#L15) |
| redis | `redis:latest` | ports ${REDIS_PORT:-6379}:6379 | [`docker-compose.yml:28`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/docker-compose.yml#L28) |

_`postgres`: the image is unpinned in CI, so no version is asserted here._

## Install

- `npm install -g npm@11.5.1` — [`.github/workflows/changesets.yml:33`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.github/workflows/changesets.yml#L33) · job release

## Setup

- `yarn workspace @calcom/prisma db-migrate` — [`README.md:230`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/README.md#L230)
- `yarn db-seed` — [`README.md:284`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/README.md#L284)
- `yarn seed-app-store` — [`README.md:689`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/README.md#L689)

## Build

- `npm run build` — [`package.json:30`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/package.json#L30) · turbo run build --filter=@calcom/web...
- `npm run build:ai` — [`package.json:31`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/package.json#L31) · turbo run build --filter="@calcom/ai"

## Test

- `npm run tdd` — [`package.json:67`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/package.json#L67) · vitest watch
- `npm run e2e` — [`package.json:68`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/package.json#L68) · NEXT_PUBLIC_IS_E2E=1 yarn playwright test --project=@calcom/web
- `npm run e2e:app-store` — [`package.json:69`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/package.json#L69) · NEXT_PUBLIC_IS_E2E=1 QUICK=true yarn playwright test --project=@calcom/app-store
- `npm run e2e:embed` — [`package.json:70`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/package.json#L70) · NEXT_PUBLIC_IS_E2E=1 yarn playwright test --project=@calcom/embed-core
- `npm run e2e:embed-react` — [`package.json:71`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/package.json#L71) · QUICK=true yarn playwright test --project=@calcom/embed-react
- `npm run test-playwright` — [`package.json:76`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/package.json#L76) · yarn playwright test --config=playwright.config.ts
- `npm run test` — [`package.json:77`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/package.json#L77) · TZ=UTC vitest run
- `npm run test:ui` — [`package.json:78`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/package.json#L78) · TZ=UTC vitest --ui

## Environment

| Variable | Value in CI | Source | |
|---|---|---|---|
| `ALLOWED_HOSTNAMES` | `'"cal.local:3000","localhost:3000"'` | [`.env.example:48`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L48) | claimed |
| `API_KEY_PREFIX` | `cal_` | [`.env.example:215`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L215) | claimed |
| `AUTH_BEARER_TOKEN_VERCEL` | — | [`.env.example:316`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L316) | claimed |
| `AVATARAPI_PASSWORD` | — | [`.env.example:182`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L182) | claimed |
| `AVATARAPI_USERNAME` | — | [`.env.example:181`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L181) | claimed |
| `AWAITING_PAYMENT_EMAIL_DELAY_MINUTES` | — | [`.env.example:246`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L246) | claimed |
| `BLACKLISTED_GUEST_EMAILS` | — | [`.env.example:398`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L398) | claimed |
| `CALCOM_APP_CREDENTIAL_ENCRYPTION_KEY` | `""` | [`.env.example:355`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L355) | claimed |
| `CALCOM_CREDENTIAL_SYNC_ENDPOINT` | `""` | [`.env.example:351`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L351) | claimed |
| `CALCOM_CREDENTIAL_SYNC_HEADER_NAME` | `"calcom-credential-sync-secret"` | [`.env.example:349`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L349) | claimed |
| `CALCOM_CREDENTIAL_SYNC_SECRET` | `""` | [`.env.example:347`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L347) | claimed |
| `CALCOM_SERVICE_ACCOUNT_ENCRYPTION_KEY` | — | [`.env.example:459`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L459) | claimed |
| `CALCOM_TELEMETRY_DISABLED` | — | [`.env.example:64`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L64) | claimed |
| `CALENDSO_ENCRYPTION_KEY` | — | [`.env.example:76`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L76) | claimed |
| `CAL_AI_CALL_RATE_PER_MINUTE` | `0.29` | [`.env.example:385`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L385) | claimed |
| `CAL_VIDEO_ASSUME_ROLE_ARN` | — | [`.env.example:416`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L416) | claimed |
| `CAL_VIDEO_BUCKET_NAME` | — | [`.env.example:414`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L414) | claimed |
| `CAL_VIDEO_BUCKET_REGION` | — | [`.env.example:415`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L415) | claimed |
| `CAL_VIDEO_MEETING_LINK_FOR_TESTING` | — | [`.env.example:420`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L420) | claimed |
| `CAL_VIDEO_RECORDING_TOKEN_SECRET` | — | [`.env.example:449`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L449) | claimed |
| `CLOSECOM_CLIENT_ID` | — | [`.env.example:268`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L268) | claimed |
| `CLOSECOM_CLIENT_SECRET` | — | [`.env.example:269`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L269) | claimed |
| `CLOUDFLARE_TURNSTILE_SECRET` | — | [`.env.example:262`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L262) | claimed |
| `CRON_API_KEY` | `'0cc0e6c35519bba620c9360cfe3e68d0'` | [`.env.example:67`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L67) | claimed |
| `CRON_ENABLE_APP_SYNC` | `false` | [`.env.example:71`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L71) | claimed |
| `CSP_POLICY` | — | [`.env.example:284`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L284) | claimed |
| `DATABASE_CHUNK_SIZE` | — | [`.env.example:455`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L455) | claimed |
| `DATABASE_DIRECT_URL` | `"postgresql://postgres:@localhost:5450/calendso"` | [`.env.example:20`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L20) | claimed |
| `DATABASE_URL` | `"postgresql://postgres:@localhost:5450/calendso"` | [`.env.example:17`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L17) | claimed |
| `DIRECTORY_IDS_TO_LOG` | — | [`.env.example:426`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.env.example#L426) | claimed |

_144 more omitted._

## Tested on

- `ubuntu-latest` — [`.github/workflows/all-checks.yml:80`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.github/workflows/all-checks.yml#L80)

_Only these are evidenced. Other platforms may work; CI does not say so._

## Claimed, not verified

The prose gives these commands; nothing in CI executes them.

- `npm run build` — [`package.json:30`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/package.json#L30)
- `npm run build:ai` — [`package.json:31`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/package.json#L31)
- `npm run tdd` — [`package.json:67`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/package.json#L67)
- `npm run e2e` — [`package.json:68`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/package.json#L68)
- `npm run e2e:app-store` — [`package.json:69`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/package.json#L69)
- `npm run e2e:embed` — [`package.json:70`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/package.json#L70)

## Sources read

| Category | Files |
|---|---|
| ci | `.github/workflows/all-checks.yml`, `.github/workflows/api-v2-production-build.yml`, `.github/workflows/api-v2-unit-tests.yml`, `.github/workflows/atoms-production-build.yml`, `.github/workflows/cache-clean.yml`, `.github/workflows/changesets.yml` _+44 more_ |
| container | `Dockerfile`, `docker-compose.yml` |
| manifest | `package.json` |
| lockfile | `yarn.lock` |
| toolchain | _none found_ |
| env | `.env.example` |
| prose | `README.md`, `CONTRIBUTING.md` |

Workflows treated as evidence, in order of authority over what runs on every merge:

- [`.github/workflows/all-checks.yml`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.github/workflows/all-checks.yml#L1) — on merge_group, workflow_dispatch
- [`.github/workflows/pr.yml`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.github/workflows/pr.yml#L1) — on pull_request_target, workflow_dispatch
- [`.github/workflows/run-ci.yml`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.github/workflows/run-ci.yml#L1) — on pull_request_target
- [`.github/workflows/cache-clean.yml`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.github/workflows/cache-clean.yml#L1) — on pull_request
- [`.github/workflows/cleanup-report.yml`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.github/workflows/cleanup-report.yml#L1) — on workflow_call, pull_request
- [`.github/workflows/i18n.yml`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.github/workflows/i18n.yml#L1) — on push
- [`.github/workflows/nextjs-bundle-analysis.yml`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.github/workflows/nextjs-bundle-analysis.yml#L1) — on workflow_call, workflow_dispatch, push
- [`.github/workflows/pr-welcome-bot.yml`](https://github.com/calcom/cal.com/blob/abffde336e744e15cf69626c10e436d6172bc406/.github/workflows/pr-welcome-bot.yml#L1) — on pull_request_target

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
