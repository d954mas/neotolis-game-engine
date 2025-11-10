# Feature Specification: Fail-Fast Quality Enforcement

**Feature Branch**: `006-enforce-failfast-quality`  
**Created**: 2025-11-07  
**Status**: Draft  
**Input**: User description: "Goal: Improve C code quality with a strict fail-fast approach. Minimize bugs before runtime (via compilation and static analysis) and catch remaining issues as early as possible during runtime. Ensure fail-fast behavior (asserts, sanitizers, UB detectors). Policy: zero warnings, treat all warnings as errors. 1) **Compiler/Linker flags** 2) **Sanitizers** 3) **Static analysis** 4) **Style & formatting gates**: 5) **Security hardening** 6) **Memory tools (runtime/heap)**: 7) **Fail-fast coding policy** (C-level) 8)Other if needed"

> Speckit specs MUST describe the C API, memory model, binary and RAM impact, microbench targets, and the CMake snippet that embeds engine sources into the target testbed. Keep all numbers testable.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - CI rejects unsafe builds (Priority: P1)

Build engineers need every preset (`win-*`, `web-*`) to fail immediately when a compiler warning, linker warning, or static-analysis defect appears so that the main branch never accepts regressions.

**Why this priority**: Preventing regressions before merge eliminates rework and is the fastest way to cut downstream crashes and QA churn.

**Independent Test**: Introduce an intentional warning or `clang-tidy` defect in a branch and confirm CI blocks merge before artifacts publish.

**Acceptance Scenarios**:

1. **Given** a developer introduces an unused variable into engine/core, **When** `cmake --build --preset win-debug` executes in CI, **Then** the job fails before linking with `/WX` output and the pipeline status is red.
2. **Given** `clang-tidy` finds a potential null dereference in `engine/features/sample`, **When** the static-analysis stage runs inside `ci/workflows/web-debug.yml` (mirrored in `ci/workflows/win-debug.yml`), **Then** the stage publishes the defect list and the merge request remains blocked.

---

### User Story 2 - Runtime instrumentation halts UB (Priority: P2)

Feature developers running `testbeds/sandbox` (debug presets) must be able to enable sanitizers plus header-only fail-fast policies so that undefined behavior, heap misuse, or contract violations abort within the frame they occur—without adding new engine source files or sprinkling manual guard calls, while release presets prioritize raw performance.

**Why this priority**: Fast feedback in the sandbox surfaces the defects not caught by compilation and protects the runtime from cascading corruption.

**Independent Test**: Execute the sandbox debug preset with `NT_FAILFAST_STRICT=1` and intentionally double-free memory; verify the process stops with a fail-fast assertion report even though no additional guard calls were inserted into engine modules.

**Acceptance Scenarios**:

1. **Given** ASan is enabled through the debug preset, **When** a developer double-frees an arena allocation, **Then** the runtime terminates before the next frame and emits a fail-fast snapshot through the existing logging backend (no new buffers).
2. **Given** WebAssembly sanitizers lack full heap coverage, **When** the automatic frame-level checkpoint macro issued by the sandbox scheduler detects an inconsistent guard word, **Then** it raises a fatal violation that surfaces in the browser console and CI upload. Release presets skip this guard to preserve frame time but continue to record warning counters.

---

### User Story 3 - Security review obtains hardening report (Priority: P3)

Security reviewers and stakeholders require a single report artifact that proves stack protection, control-flow hardening, style conformance, and policy compliance before a release build is signed.

**Why this priority**: Compliance evidence shortens audit cycles and prevents blocking issues during release certification.

**Independent Test**: Run the release preset with `NT_FAILFAST_POLICY=release` and confirm the generated report enumerates active mitigations plus pass/fail counts.

**Acceptance Scenarios**:

1. **Given** a release candidate build finishes, **When** the quality report generator runs, **Then** it lists each enforced mitigation (stack canaries, CF guard, RELRO, format gate) and the report is archived with the build artifacts.

---

### Edge Cases

- Third-party or external headers (e.g., `third_party/cglm`) emit warnings under `/WX` or `-Werror`; policy must isolate or whitelist them without muting engine warnings.
- Sanitizers unavailable in certain environments (e.g., Emscripten release) must degrade gracefully while still running the frame-level fail-fast macros defined in `nt_engine.h`.
- Memory ceilings for WebAssembly (≤32 MB) require sanitizer shadow memory plus compiler-inserted guards to remain inside the documented allocation; if a preset cannot enable a tool without exceeding the cap, it must fall back to the strict assert policy instead of allocating new buffers. Release presets always operate in guard-lite mode to protect frame budget.

## Assumptions

- No new engine `.c` or `.h` translation units may be added for this feature; all runtime logic lives within existing `engine/core/nt_engine.{c,h}` through macros or inline helpers. (New test fixtures or CI helper files remain permitted.)
- Toolchains (clang-cl 17, emcc/Clang 3.1.x) expose ASan, UBSan, and relevant hardening flags on both Windows and Web debug presets; release presets intentionally disable sanitizer instrumentation to preserve maximum performance while still enforcing strict compile-time flags and runtime asserts.
- Existing logging and telemetry plumbing can emit fail-fast snapshots without extra buffers; only compile-time formatting helpers will be introduced.

## Requirements & Memory Model *(mandatory)*

### Functional Requirements

- **FR-001**: All ship and debug presets must set `NT_FAILFAST_STRICT=1`, enable the highest warning set supported by the compiler (e.g., `/Wall /WX` on clang-cl, `-Wall -Wextra -Wpedantic -Werror -fno-common` on Emscripten), and propagate these flags to every engine, testbed, and tool target.
- **FR-002**: Linker invocations must enable undefined-symbol and stack-protector enforcement (`/guard:ehcont`, `-Wl,--no-undefined`, `/DYNAMICBASE`, etc.) and treat linker warnings as errors so that binaries never emit best-effort images.
- **FR-003**: Sanitizer matrices must exist for both toolchains but run only in debug presets: Windows debug builds run AddressSanitizer + UndefinedBehaviorSanitizer; Web debug builds run AddressSanitizer-lite + integer-overflow traps, each triggered through dedicated `ctest` labels. Release presets disable sanitizer instrumentation entirely but retain strict asserts and mitigation flags.
- **FR-004**: Static-analysis gates (clang-tidy, include-what-you-use, optional cppcheck) must run automatically inside CI; any new violation breaks the build and publishes a human-readable summary in the artifact bundle.
- **FR-005**: Style and formatting gates must apply `clang-format`, `cmake-format`, and license headers; zero-diff enforcement is required through a formatting check job that fails when files drift from canonical style.
- **FR-006**: A security-hardening manifest must document required mitigations (stack canaries, Control-Flow Guard, PAC/BTI equivalents, RELRO, FORTIFY) per preset, and release presets must fail if any mitigation is disabled or unsupported.
- **FR-007**: Memory tools must rely on compiler-provided sanitizers (ASan, LSan, UBSan, integer-overflow traps) toggled via presets; no custom allocator or new `.c` modules may be introduced.
- **FR-008**: The public header `engine/core/nt_engine.h` must expose a header-only `nt_failfast_policy` struct along with macros (`NT_FAILFAST_ASSERT`, `NT_FAILFAST_FRAME_GUARD`) that expand to existing `nt_assert`/`nt_abort` plumbing so runtime enforcement requires no new translation units.
- **FR-009**: The engine scheduler inside `engine/core/nt_engine.c` must call `NT_FAILFAST_FRAME_GUARD` at the start/end of each frame automatically so feature teams gain fail-fast coverage without modifying their subsystems; this change must reuse existing functions and avoid creating additional source files.
- **FR-010**: CI must publish a consolidated “quality gate report” artifact containing compiler flag summaries, sanitizer coverage %, analyzer findings, style results, and memory-tool status for each preset before the build is considered releasable.

### Key Entities

- **`nt_failfast_policy`**: Header-only struct declared in `engine/core/nt_engine.h` describing warning tier, sanitizer_mask, heap_guard_mode, release/report toggles, and expected reaction (abort vs. log); applied at compile time through macros.
- **`nt_failfast_violation_snapshot`**: Lightweight struct produced on the stack when `NT_FAILFAST_ASSERT` trips; contains stage label, failing expression, thread id, and preset so tooling can log it without persistent storage.
- **`nt_quality_gate_result`**: Summary object emitted by CI, capturing counts for compiler/linker warnings, analyzer defects, formatter mismatches, sanitizer runtime faults, and mitigation status.

### Memory Model

- **Allocator**: No new allocator; fail-fast instrumentation uses existing `nt_engine` globals and stack storage only.
- **Persistent Buffers**: None added; policy data is embedded in `.rodata` via compile-time structs and existing diagnostic counters are reused.
- **Transient Scratch**: ≤256 bytes on the stack per violation snapshot to format assert context before passing it to the logging backend.
- **Failure Modes**: If a preset cannot enable sanitizers because the toolchain exceeds memory limits, `NT_FAILFAST_POLICY_SANITIZER` falls back to strict asserts and the build log must note the downgrade; no dynamic allocation is permitted for this feature.

## C API Surface & Embedding *(mandatory)*

### Public Headers

- `engine/core/nt_engine.h`: Adds the `nt_failfast_policy` struct definition, policy helper macros, and documentation for the strict fail-fast expectations that ship with each preset; remains header-only.

### Function Table

| Symbol | Purpose | Thread Safety | Notes |
|--------|---------|---------------|-------|
| `nt_failfast_policy_defaults(nt_failfast_policy *out_policy)` | Header-only helper that seeds policy with strict defaults expected by CI and sandbox presets. | Yes — writes to caller memory only. | <0.01 ms; no allocations. |
| `nt_failfast_apply_policy(const nt_failfast_policy *policy)` | Static inline adapter that forwards policy bits into the existing `nt_engine_config`; no new `.c` code required. | Not thread-safe (call during init). | Expands to a few stores in `nt_engine.c`. |
| `NT_FAILFAST_ASSERT(expr, label)` | Macro that wraps `nt_assert` to abort immediately with sanitized context; available throughout the codebase without extra includes. | Inherits `nt_assert` guarantees. | Adds ≤2 instructions when assertions enabled. |
| `NT_FAILFAST_FRAME_GUARD(label)` | Macro used by the scheduler to stamp frame boundaries, compare sanitizer downgrade flags, and raise alerts if inconsistencies appear. | Yes — uses existing atomic frame counter. | <0.02 ms per frame on Web microbench. |

### Embedding Snippet

```cmake
# Enforce fail-fast policy without adding new translation units
target_sources(testbeds_sandbox
    PRIVATE
        engine/core/nt_engine.c
        engine/core/nt_engine.h
)

target_compile_definitions(testbeds_sandbox
    PRIVATE
        NT_FAILFAST_STRICT=1
        NT_ENABLE_SAFESTACK=1
        NT_FAILFAST_POLICY_HASH=\"sandbox\"
)
```

## Resource Budgets & Performance *(mandatory)*

- **Binary Size Delta**: ≤+4 KB code delta (header-only assert macros + scheduler guards) to keep `.wasm` ≤200 KB; `size-report` fails on regressions >4 KB attributable to this feature. Sanitizer instrumentation growth applies only to debug presets and must be reported separately.
- **Per-Feature Budget**: ≤5 KB effective budget (mostly compile-time macros); debug presets must document when sanitizers add >5% size overhead and justify the temporary increase, while release presets must stay within the baseline.
- **Runtime RAM**: No new persistent RAM; sanitizer shadow memory is managed by toolchains and must keep total usage ≤32 MB in debug presets; release presets must run without sanitizer shadow memory and incur ≤128 bytes additional stack per frame.
- **CPU/Frame Time Target**: ≤0.1 ms per frame on `testbeds/sandbox` (WebAssembly, 60 FPS) with frame guards active in debug; release presets must remain within existing frame budgets (≤0.05 ms overhead) with guards compiled to no-ops except telemetry counters.
- **CI Hooks**: `qa_failfast_policy_microbench` (microbenchmark), `size-report` (binary delta), `failfast_ctest` (sanitizer + runtime asserts), `format-check`.
- **Mitigations**: If CPU or size exceeds limits by >2%, CI must fail and recommend toggling down optional sanitizer passes (e.g., disable integer-trap) before accepting the merge.

## Observability & Operations *(mandatory)*

- **Instrumentation Plan**: Emit sanitizer summaries (debug-only), formatter diffs, warning counters, release mitigation matrices, linker guard status, runtime RAM telemetry, frame-overhead telemetry, and the `security_review_hours` metric as JSON artifacts; expose `NT_FAILFAST_LOG_MODE=stdout|artifact` compile definitions so the existing logging backend prints fail-fast assertions without additional runtime buffers. Quality gate reports must include sections for compiler flags, linker guards, formatter drift, memory budgets, microbench results, and audit metrics.
- **Validation Steps**: Nightly pipeline runs both toolchains with sanitizers + static analysis for debug presets, then executes `ctest --preset web-debug --label-regex failfast` and `ctest --preset win-debug --label-regex failfast`; release presets run `qa_failfast_policy_microbench` in no-sanitizer mode, execute `tests/ci/test_memory_budget.sh` to enforce the ≤32 MB + 128 B limits, and verify that `NT_FAILFAST_FRAME_GUARD` counters still increment.
- **Operational Notes**: Release runbooks must include the quality gate report, hardening manifest, regression/baseline output, and the recorded `security_review_hours` metric (target ≤6 engineer-hours, baseline 10). On-call must monitor for repeated fail-fast aborts in telemetry, and waivers (e.g., temporarily disabling a sanitizer) require a documented tracking ticket linked within the report.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of CI builds for all presets fail if a single compiler or linker warning is emitted, verified by instrumentation that counts warnings and enforces zero tolerance.
- **SC-002**: Debug sanitizer runs detect and abort ≥95% of injected heap/UB faults within one frame (≤16 ms) during automated sandbox tests, while release presets show ≤0.5% frame-time regression compared to prior baseline.
- **SC-003**: Quality gate reports show zero outstanding static-analysis violations and zero formatting drift before a release branch can be tagged; audits confirm the report is attached to every release artifact.
- **SC-004**: Security review time per release is captured in the quality gate report (`security_review_hours`); the baseline (2025-Q3 release) is 10 engineer-hours, and success is ≤6 engineer-hours for two consecutive releases thanks to automated manifests and reports.
