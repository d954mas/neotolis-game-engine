# Implementation Plan: Fail-Fast Quality Enforcement

**Branch**: `006-enforce-failfast-quality` | **Date**: 2025-11-07 | **Spec**: `/mnt/c/projects/nt_engine/specs/006-enforce-failfast-quality/spec.md`

## Summary

Zero-warning, fail-fast guardrails for every preset via header-only policies, strict compile/link flags, sanitizer/runtime instrumentation, and CI artifacts (quality gate report, hardening manifest, regression checks). Work spans `engine/core`, preset/toolchain configs, testbed wiring, CI workflows, and shared scripts.

## Technical Context

- **Language/Toolchains**: C23 using clang-cl 17 (Windows) and emcc/Clang 3.1.x (Web); release builds enforce `-Oz`+LTO, debug builds enable sanitizers.
- **Modules impacted**:
  - `engine/core/nt_engine.{c,h}` – add header-only policy struct/macros, scheduler guards, telemetry hooks.
  - Preset/toolchain files (`CMakePresets.json`, `cmake/toolchains/*.cmake`, `engine/CMakeLists.txt`) – propagate warning/linker presets, sanitizer toggles, third-party suppression.
  - `testbeds/sandbox` – consume macros, compile definitions, telemetry logging.
  - CI workflows `ci/workflows/{web,win}-{debug,release}.yml` – integrate warning/static/format checks, quality-gate reports, regression/memory tests.
  - Shared scripts under `ci/scripts/` (quality-gate-report, check-linker-flags, run-format-check, check-release-regressions, generate/verify hardening manifest, security-review metrics).
- **Runtime policies**: Debug: `NT_FAILFAST_STRICT=1`, ASan/UBSan, frame guards, RAM telemetry. Release: sanitizers off, guard-lite mode, ≤0.05 ms overhead.
- **Budgets**: +≤4 KB code delta, ≤5 KB total feature budget, `.wasm` ≤200 KB, runtime RAM ≤32 MB (≤128 B/frame overhead), microbench targets ≤0.1 ms (debug)/≤0.05 ms (release).
- **Observability**: Quality gate report (compiler/linker, sanitizer, formatting, static analysis, size/ram/microbench, security-review hours), hardening manifest, regression outputs stored per preset; release runbooks include all artifacts.
- **Edge handling**: Third-party warnings isolated via `SYSTEM` includes and optional suppression interface; release workflows run memory-budget tests even without sanitizers.

## Constitution Check

- **Binary Budget Supremacy** – Size-report + regression tasks guard budgets (pass).
- **Deterministic Memory Discipline** – No new allocators; telemetry + memory tests enforce limits (pass).
- **Performance-Oriented Portability** – Microbench/regression scripts cover both platforms/presets (pass).
- **Spec-Led Delivery** – Spec defines API/memory/CI; plan mirrors requirements (pass).
- **Embedded Feature Isolation** – Only embedded engine/testbed sources touched, no standalone libs (pass).

## Structure Overview

```text
engine/core/              # header + scheduler updates
engine/platform/{web,win} # preset/CMake adjustments
testbeds/sandbox/         # compile defs + telemetry
ci/workflows/             # debug/release gate enforcement
ci/scripts/               # shared automation tooling
tests/                    # warning gate, failfast policy, microbench, memory tests
docs/                     # contributor + release runbooks
```

## Phases

1. **Setup** – Baseline artifact (`ci/baselines/qa_failfast_policy.json`), quality-gate schema, CLI skeleton, shared format-check script.
2. **Foundational** – Warning/linker preset cache vars, sanitizer toggles, microbench target, linker guard flags, third-party warning isolation docs.
3. **User Story 1** (CI fails unsafe builds) – Warning-gate tests, propagate compile/link interfaces, add linker checker, update all workflows (debug + release), integrate format-check script, extend quality-gate reporting for compiler/link sections.
4. **User Story 2** (Runtime fail-fast) – Unit/microbench tests, header-only policy macros, scheduler guards, sandbox defs/logging, preset sanitizer toggles, RAM telemetry instrumentation + memory-budget tests, failfast test labeling.
5. **User Story 3** (Security-ready reporting) – Schema/validation tests, quality-gate report automation for all presets (debug + release), regression checker integration, release memory-budget enforcement, hardening manifest generation/verification, security-review metrics capture, runbook updates.
6. **Polish** – Re-run size/perf/RAM/regression checks across presets, refresh quickstart/onboarding docs.

## Complexity Tracking

No waivers currently required; scope stays within existing module boundaries.
