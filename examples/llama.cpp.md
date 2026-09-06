# FACTCHECK: ggml-org/llama.cpp

What it takes to run this repo, read from CI rather than from prose.

- **Primary CI:** [`.github/workflows/build-cpu.yml`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-cpu.yml#L1) — runs on workflow_dispatch, push, pull_request
- **Commit:** [`74a7c897f049`](https://github.com/ggml-org/llama.cpp/tree/74a7c897f049c17e7080423aa2111776eff6ebbf) on `master`
- **Method:** a [fixed precedence table](#method), applied as code. Same commit in, same document out.

**verified** = executed by CI or a container build  ·  *claimed* = prose a human wrote once

## Conflicts

Nothing in the prose contradicts what CI executes.

## Required but undocumented

CI needs these. The prose never mentions them — which is usually why a fresh clone does not run.

| What | Value | Source |
|---|---|---|
| `OPENBLAS_VERSION` | `0.3.23` | [`.github/workflows/build-cpu.yml:145`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-cpu.yml#L145) |
| `SDE_VERSION` | `9.33.0-2024-01-07` | [`.github/workflows/build-cpu.yml:146`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-cpu.yml#L146) |

## Runtime

| Tool | Version | Source | |
|---|---|---|---|
| java | `17` | [`.github/workflows/build-android.yml:48`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-android.yml#L48) | verified |
| node | `24` | [`.github/workflows/ui.yml:59`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/ui.yml#L59) | verified |
| python | `3.11` | [`.github/workflows/pre-tokenizer-hashes.yml:24`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/pre-tokenizer-hashes.yml#L24) | verified |

A higher-authority source was present but not literal, so the table fell through to what is shown above:

- `python`: `(unpinned - action default)` at [`.github/workflows/server-sanitize.yml:92`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/server-sanitize.yml#L92) could not be read as a version

## Install

- `sudo apt-get install -y --no-install-recommends` — [`.github/workflows/build-cpu.yml:73`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-cpu.yml#L73) · job ubuntu
- `sudo apt-get install -y gcc-14 g++-14` — [`.github/workflows/build-cpu.yml:82`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-cpu.yml#L82) · job ubuntu
- `python3 -m pip install --upgrade pip setuptools` — [`.github/workflows/build-cpu.yml:89`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-cpu.yml#L89) · job ubuntu
- `pip3 install ./gguf-py` — [`.github/workflows/build-cpu.yml:89`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-cpu.yml#L89) · job ubuntu
- `choco install ninja` — [`.github/workflows/build-cpu.yml:189`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-cpu.yml#L189) · job windows

## Build

- `cmake -B build` — [`.github/workflows/build-cpu.yml:105`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-cpu.yml#L105) · job ubuntu
- `time cmake --build build --config Release -j $(nproc)` — [`.github/workflows/build-cpu.yml:105`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-cpu.yml#L105) · job ubuntu
- `cmake -S . -B build -G "Ninja Multi-Config" -D CMAKE_TOOLCHAIN_FILE=cmake/x64-windows-llvm.cmake -DGGML_NATIVE=OFF -DGGML_OPENMP_FETCH=ON -DLLAMA_BUILD_SERVER=ON -DGGML_RPC=ON -DBUILD_SHARED_LIBS=OFF | -G "Ninja Multi-Config" -D CMAKE_TOOLCHAIN_FILE=cmake/x64-windows-llvm.cmake -DGGML_NATIVE=OFF -DLLAMA_BUILD_SERVER=ON -DGGML_RPC=ON -DGGML_BACKEND_DL=ON -DGGML_CPU_ALL_VARIANTS=ON -DGGML_OPENMP=OFF -DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS -DBLAS_INCLUDE_DIRS="$env:RUNNER_TEMP/openblas/include" -DBLAS_LIBRARIES="$env:RUNNER_TEMP/openblas/lib/openblas.lib" | -G "Ninja Multi-Config" -D CMAKE_TOOLCHAIN_FILE=cmake/arm64-windows-llvm.cmake -DGGML_NATIVE=OFF -DGGML_OPENMP_FETCH=ON -DLLAMA_BUILD_SERVER=ON '` — [`.github/workflows/build-cpu.yml:195`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-cpu.yml#L195) · job windows
- `cmake --build build --config Release -j ${env:NUMBER_OF_PROCESSORS}` — [`.github/workflows/build-cpu.yml:195`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-cpu.yml#L195) · job windows

## Test

- `ctest -L main --verbose --timeout 900` — [`.github/workflows/build-cpu.yml:126`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-cpu.yml#L126) · job ubuntu
- `ctest -L main -C Release --verbose --timeout 900` — [`.github/workflows/build-cpu.yml:210`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-cpu.yml#L210) · job windows

## Environment

| Variable | Value in CI | Source | |
|---|---|---|---|
| `OPENBLAS_VERSION` | `0.3.23` | [`.github/workflows/build-cpu.yml:145`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-cpu.yml#L145) | verified |
| `SDE_VERSION` | `9.33.0-2024-01-07` | [`.github/workflows/build-cpu.yml:146`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-cpu.yml#L146) | verified |

## Tested on

- `ubuntu-22.04 | ubuntu-24.04-arm` — [`.github/workflows/build-cpu.yml:57`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-cpu.yml#L57)
- `windows-2025` — [`.github/workflows/build-cpu.yml:142`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-cpu.yml#L142)

_Only these are evidenced. Other platforms may work; CI does not say so._

## Sources read

| Category | Files |
|---|---|
| ci | `.github/workflows/ai-issues.yml`, `.github/workflows/build-3rd-party.yml`, `.github/workflows/build-and-test-snapdragon.yml`, `.github/workflows/build-android.yml`, `.github/workflows/build-apple.yml`, `.github/workflows/build-cache.yml` _+44 more_ |
| container | _none found_ |
| manifest | `pyproject.toml`, `requirements.txt`, `Makefile` |
| lockfile | _none found_ |
| toolchain | _none found_ |
| env | _none found_ |
| prose | `README.md`, `CONTRIBUTING.md`, `docs/install.md` |

Workflows treated as evidence, in order of authority over what runs on every merge:

- [`.github/workflows/build-cpu.yml`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-cpu.yml#L1) — on workflow_dispatch, push, pull_request
- [`.github/workflows/build-sanitize.yml`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-sanitize.yml#L1) — on workflow_dispatch, push, pull_request
- [`.github/workflows/pre-tokenizer-hashes.yml`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/pre-tokenizer-hashes.yml#L1) — on push, pull_request
- [`.github/workflows/python-check-requirements.yml`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/python-check-requirements.yml#L1) — on push, pull_request
- [`.github/workflows/python-type-check.yml`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/python-type-check.yml#L1) — on push, pull_request
- [`.github/workflows/ui.yml`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/ui.yml#L1) — on workflow_dispatch, push, pull_request
- [`.github/workflows/build-apple.yml`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-apple.yml#L1) — on workflow_dispatch, push, pull_request
- [`.github/workflows/build-and-test-snapdragon.yml`](https://github.com/ggml-org/llama.cpp/blob/74a7c897f049c17e7080423aa2111776eff6ebbf/.github/workflows/build-and-test-snapdragon.yml#L1) — on workflow_dispatch, push, pull_request

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
