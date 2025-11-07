# Tasks: Fail-Fast Quality Enforcement

**Input**: Design documents from `/specs/006-enforce-failfast-quality/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Each user story defines CTest or CI validations that must fail before implementation begins.  
**Instrumentation**: Binary size, RAM, linker mitigations, sanitizer coverage, formatting, and security-review metrics must be captured before marking a story complete.  
**Budgets**: Monitor ≤+4 KB binary growth, ≤32 MB RAM (+128 B/frame), and ≤0.1 ms (debug)/≤0.05 ms (release) frame overhead.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Provide common artifacts/scripts consumed by all phases.

- [X] T001 Create baseline artifact `ci/baselines/qa_failfast_policy.json` populated with the latest green `main` release median `qa_failfast_policy_microbench` and RAM telemetry.
- [X] T002 [P] Author JSON schema `ci/schemas/quality-gate-report.schema.json` covering `compiler_flags`, `linker_guards`, `sanitizer_matrix`, `formatting`, `static_analysis`, `binary_budget`, `memory_policy`, `microbench`, `security_review_hours`, and metadata sections.
- [X] T003 [P] Scaffold shared CLI helper `ci/scripts/quality-gate-report.sh` (argument parsing, preset detection, TODO markers) so later stories can plug in data collection.
- [X] T004 [P] Add reusable format-check script `ci/scripts/run-format-check.sh` that executes `clang-format --dry-run`, `cmake-format`, and license-header validation; expose configurable path filters for workflows.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Configure toolchains, warning/linker policies, and microbench hooks. No user story may start until this phase passes.

- [X] T005 Define zero-warning preset cache variables (e.g., `NT_FAILFAST_WARNING_FLAGS`) in root `CMakePresets.json`, ensuring every preset inherits `/Wall /WX /permissive-` (clang-cl) or `-Wall -Wextra -Wpedantic -Werror -fno-common` (emcc).
- [X] T006 [P] Wire sanitizer toggles into `cmake/toolchains/emscripten.cmake` and `cmake/toolchains/clang-cl.cmake`, exposing `NT_FAILFAST_SANITIZER=ON|OFF` options with debug ON and release OFF.
- [X] T007 Add skeleton `qa_failfast_policy_microbench` target plus `failfast` label inside `tests/microbench/CMakeLists.txt` referencing `testbeds/sandbox` so later stories can attach measurements.
- [X] T008 Add linker-guard preset cache variables (e.g., `NT_FAILFAST_LINK_FLAGS_WIN`, `NT_FAILFAST_LINK_FLAGS_WEB`) covering `/guard:ehcont /DYNAMICBASE /LTCG` and `-Wl,--no-undefined,-z,relro,-z,now` plus stack-protector toggles.
- [X] T009 [P] Include the linker-guard variables inside both toolchain files, exposing `NT_FAILFAST_LINK_ENFORCE=ON` by default so every preset inherits the flags.
- [X] T010 Establish third-party warning isolation by marking `third_party/cglm` (and other vendor trees) as `SYSTEM` includes and adding an opt-in interface `NT_FAILFAST_SUPPRESS_THIRDPARTY_WARNINGS` in `engine/CMakeLists.txt`, with documentation in `docs/contrib/warnings.md`.

**Checkpoint**: Tools, presets, microbench scaffolding, linker guard hooks, and third-party warning isolation in place.

---

## Phase 3: User Story 1 – CI rejects unsafe builds (Priority: P1) 🎯 MVP

**Goal**: Enforce zero-warning compilation/linking, static-analysis gates, third-party isolation proofs, and formatting checks across all presets.

**Independent Test**: Introduce an unused variable or `clang-tidy` null-deref fixture, run `cmake --build --preset win-debug`, and verify CI fails before linking with `/WX` plus artifacted analyzer defects.

### Tests (fail first)

- [X] T011 [US1] Add CTest script `tests/ci/test_warning_gate.cmake` that compiles `tests/fixtures/warning_violation.c` and expects the zero-warning policy to abort builds.
- [X] T012 [P] [US1] Add `tests/fixtures/clang_tidy/null_deref.c` plus corresponding `clang-tidy` config entry so the CI stage surfaces deliberate analyzer failures.

### Implementation

- [X] T013 [US1] Propagate compile/link warning interfaces and the third-party suppression target from `CMakePresets.json` into root `CMakeLists.txt`, ensuring every engine/testbed target also defines `NT_FAILFAST_STRICT`.
- [X] T014 [P] [US1] Update `engine/CMakeLists.txt` to apply the strict compile/link/third-party interfaces to `engine/core/nt_engine.c` and dependent modules without touching vendor directories.
- [X] T015 [US1] Add script `ci/scripts/check-linker-flags.sh` that scans build logs for linker warnings and confirms required guard flags; script exits non-zero on violation.
- [ ] T016 [P] [US1] Enhance `ci/workflows/web-debug.yml` with compile/link/error steps, clang-tidy/include-what-you-use, `check-linker-flags.sh`, and the shared format-check job.
- [ ] T017 [US1] Mirror the zero-warning/static-analysis/linker/format steps inside `ci/workflows/win-debug.yml`, including artifact uploads.
- [ ] T018 [P] [US1] Extend `ci/workflows/web-release.yml` and `ci/workflows/win-release.yml` to reuse the same compile/link/static/format checks so ship presets inherit the zero-warning policy.
- [ ] T019 [US1] Wire the shared format-check script (T004) into all workflows via a reusable job or workflow-call, ensuring every preset enforces zero-drift formatting.
- [ ] T020 [US1] Extend `ci/scripts/quality-gate-report.sh` to populate the `compiler_flags`, `linker_guards`, and `third_party_whitelist` sections based on build logs.

**Checkpoint**: CI blocks any warning or static-analysis defect, enforces linker guards, protects third-party code, and reports compile/link status for every preset.

---

## Phase 4: User Story 2 – Runtime instrumentation halts UB (Priority: P2)

**Goal**: Provide header-only fail-fast policies/macros, automatic frame guards, runtime RAM telemetry, and sanitizer-enabled debug builds while keeping release builds lean.

**Independent Test**: Run `ctest --preset web-debug --label-regex failfast`, intentionally double-free memory in `testbeds/sandbox`, and confirm `NT_FAILFAST_ASSERT` aborts within one frame while release builds show ≤0.05 ms overhead in `qa_failfast_policy_microbench`.

### Tests (fail first)

- [ ] T021 [US2] Add unit test `tests/unit/test_failfast_policy.c` validating `nt_failfast_policy_defaults()`, `NT_FAILFAST_ASSERT`, and release-mode fallbacks.
- [ ] T022 [P] [US2] Implement `tests/microbench/failfast_guard_bench.c` measuring `NT_FAILFAST_FRAME_GUARD` overhead (fail if >0.1 ms debug / >0.05 ms release).

### Implementation

- [ ] T023 [US2] Implement header-only `nt_failfast_policy` struct, enums, and macros (`NT_FAILFAST_ASSERT`, `NT_FAILFAST_FRAME_GUARD`, `nt_failfast_apply_policy`) inside `engine/core/nt_engine.h`.
- [ ] T024 [P] [US2] Update `engine/core/nt_engine.c` scheduler loops to invoke `NT_FAILFAST_FRAME_GUARD` at frame boundaries and emit violation snapshots via the existing logging backend.
- [ ] T025 [US2] Inject required compile definitions (`NT_FAILFAST_STRICT`, `NT_FAILFAST_POLICY_HASH`, `NT_FAILFAST_LOG_MODE`) into `testbeds/sandbox/CMakeLists.txt`, ensuring debug vs. release handling matches spec.
- [ ] T026 [P] [US2] Adjust `engine/platform/web/CMakePresets.json` and `engine/platform/win/CMakePresets.json` so debug presets enable ASan/UBSan flags while release presets explicitly disable sanitizers and set guard-lite mode.
- [ ] T027 [US2] Add runtime logging hooks in `testbeds/sandbox/main.c` that print `nt_failfast_violation_snapshot` records and integrate with existing telemetry counters.
- [ ] T028 [P] [US2] Instrument `engine/core/nt_engine.c` to collect runtime RAM telemetry (peak allocator usage, sanitizer shadow estimate, guard overhead) and expose it through existing telemetry counters.
- [ ] T029 [US2] Create `tests/ci/test_memory_budget.sh` that reads telemetry output/CI logs and fails when runtime RAM exceeds 32 MB or guard overhead exceeds 128 bytes/frame; register via CTest.
- [ ] T030 [US2] Tag all fail-fast CTest targets (unit, memory, microbench) under the `failfast` label inside `tests/CMakeLists.txt` for nightly automation.

**Checkpoint**: Sandbox aborts UB instantly under debug; release builds remain performant with guard-lite telemetry and RAM instrumentation.

---

## Phase 5: User Story 3 – Security review obtains hardening report (Priority: P3)

**Goal**: Produce auditable quality-gate reports and hardening manifests, enforce mitigations, gate release regressions, and capture measurable security-review time reductions.

**Independent Test**: Run `cmake --build --preset win-release`, execute the quality gate + regression scripts, and verify the resulting artifacts (report, hardening manifest, regression log) pass schema validation, list mitigations, and show ≤0.5% microbench/RAM regressions plus `security_review_hours ≤ 6`.

### Tests (fail first)

- [ ] T031 [US3] Create schema validation test `tests/ci/test_quality_gate_report.sh` that runs `node`/`jq` validation against `ci/schemas/quality-gate-report.schema.json`.
- [ ] T032 [P] [US3] Add CI steps inside `ci/workflows/web-debug.yml` and `ci/workflows/win-debug.yml` to run the schema validation script and fail when artifacts are missing sections or mismatched.

### Implementation

- [ ] T033 [US3] Complete `ci/scripts/quality-gate-report.sh` to ingest sanitizer coverage, formatter drift, static-analysis counts, binary/memory deltas, microbench stats, hardening manifest status, and `security_review_hours`.
- [ ] T034 [P] [US3] Update `ci/workflows/web-debug.yml` to call the script, upload `quality-gate-report-web-debug.json`, and retain the last 30 artifacts.
- [ ] T035 [US3] Mirror the artifact generation/upload inside `ci/workflows/win-debug.yml`, ensuring identical retention and metadata.
- [ ] T036 [US3] Extend `ci/workflows/web-release.yml` to run `ci/scripts/quality-gate-report.sh`, upload `quality-gate-report-web-release.json`, and retain artifacts alongside debug builds.
- [ ] T037 [US3] Mirror the release report generation/upload inside `ci/workflows/win-release.yml`, guaranteeing parity with debug workflows.
- [ ] T038 [US3] Implement `ci/scripts/check-release-regressions.sh` that loads `ci/baselines/qa_failfast_policy.json`, compares microbench and RAM metrics, and emits pass/fail with mitigation instructions.
- [ ] T039 [P] [US3] Integrate the regression checker into `ci/workflows/web-release.yml` and `ci/workflows/win-release.yml`, failing builds exceeding the ≤0.5% threshold.
- [ ] T040 [US3] Add release workflow steps that execute `tests/ci/test_memory_budget.sh` (or its CTest wrapper) and fail when runtime RAM exceeds the 32 MB + 128 B budget.
- [ ] T041 [US3] Implement `ci/scripts/generate-hardening-manifest.sh` that inspects build flags/artifacts per preset and outputs `ci/artifacts/hardening-manifest-${preset}.json`.
- [ ] T042 [P] [US3] Implement `ci/scripts/verify-hardening-manifest.sh` that parses the manifest and fails when required mitigations (stack canaries, CF guard, RELRO, FORTIFY, format gate) are missing.
- [ ] T043 [US3] Wire manifest generation, verification, regression checks, and memory-budget enforcement into both release workflows, uploading artifacts and blocking builds when verification fails.
- [ ] T044 [US3] Add `ci/scripts/security-review-metrics.sh` plus release workflow steps that prompt engineers for start/stop timestamps, compute `SECURITY_REVIEW_HOURS`, persist the history (append to `ci/baselines/qa_failfast_policy.json`), and pass the latest value to the quality gate script.
- [ ] T045 [US3] Update `docs/runbooks/release-quality.md` with instructions for recording review durations, supplying environment variables to CI, attaching manifests/reports, and handling mitigation waivers.

**Checkpoint**: Quality-gate reports and hardening manifests exist per preset, schema-validated, gated, and paired with measured review-time reductions.

---

## Final Phase: Polish & Cross-Cutting

- [ ] T046 Run `size-report`, `qa_failfast_policy_microbench`, `tests/ci/test_memory_budget.sh`, and `ci/scripts/check-release-regressions.sh` across all presets, documenting any >2% deltas with mitigation plans in `ci/workflows/README.md`.
- [ ] T047 [P] Refresh `specs/006-enforce-failfast-quality/quickstart.md` and onboarding notes to reference the new scripts, artifacts, and CI expectations validated in prior phases.

---

## Dependencies

1. Setup (Phase 1) → Foundational (Phase 2) → User Story phases.  
2. User Story order: US1 (zero-warning + linker/format enforcement) → US2 (runtime fail-fast + RAM telemetry) → US3 (quality-gate + hardening). Each story depends on completion of all earlier phases.  
3. Polish tasks begin only after every user story hits its checkpoint.

## Parallel Execution Examples

- Once warning/linker interfaces are in place, workflow updates for different presets can proceed simultaneously because they touch separate CI files.  
- After header-only policies land, scheduler instrumentation and preset toggles can advance in parallel, as one lives in `engine/core` while the other edits platform presets.  
- During US3, report generation, regression gating, and hardening manifest workstreams can run concurrently since they involve independent scripts and workflow sections.

## Implementation Strategy

1. **MVP (US1)**: Deliver zero-warning compilation/linking, static-analysis gates, third-party isolation, and format enforcement across all presets to satisfy SC-001 immediately.  
2. **Iterate to US2**: Layer in header-only policies, frame guards, and RAM telemetry so undefined behavior and memory overages fail-fast during debug while release builds remain performant (supports SC-002).  
3. **Finalize with US3**: Automate reports, hardening manifests, mitigation verification, regression checks, and security-review metrics so releases carry self-contained audit artifacts (addresses SC-003/SC-004).  
4. **Polish**: Re-run size/perf/RAM gates, refresh documentation, and ensure telemetry plus observability commitments remain satisfied before implementation work begins.
