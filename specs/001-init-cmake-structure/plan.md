# Implementation Plan: Project Structure & CMake Bootstrap

**Branch**: `001-init-cmake-structure` | **Date**: 2025-10-22 | **Spec**: [/mnt/c/projects/nt_engine/specs/001-init-cmake-structure/spec.md](/mnt/c/projects/nt_engine/specs/001-init-cmake-structure/spec.md)
**Input**: Feature specification from `/specs/001-init-cmake-structure/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/scripts/bash/setup-plan.sh` for the execution workflow.

## Summary

Bootstrap a cross-platform Speckit workspace that delivers a reusable CMake-based project structure, embeds engine sources directly into a sandbox testbed, and seeds CI-facing CTest targets (size-report and microbench) so future features inherit binary-size, performance, and memory governance from day one.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: C23 (clang-cl 17 on Windows, emcc/Clang 3.1.x for WebAssembly)  
**Primary Dependencies**: CMake ≥3.27, Emscripten SDK toolchain, LLVM/clang-cl 17, GLFW + WebGPU/WebGL2 stubs (placeholders only), cglm header-only math utilities  
**Storage**: None — project skeleton contains no persistent storage integrations  
**Testing**: CTest harness with stub lifecycle smoke tests, size-report (`ctest -R size_report`), microbench stub (`ctest -R microbench_stub`)  
**Target Platform**: WebAssembly (primary artifact), Windows desktop (secondary rapid iteration build)  
**Project Type**: Embedded engine sources consumed by per-testbed CMake targets (no standalone libs)  
**Performance Goals**: Maintain ≤0.1 ms stub frame cost; ensure CI reports size deltas and microbench timing on every configuration  
**Constraints**: `.wasm` total ≤200 KB, per-feature ≤30 KB, runtime RAM budget ≤32 MB, no dynamic allocations outside `nt_alloc_*` (none introduced here)  
**Scale/Scope**: Initial repository bootstrap; touches engine core/platform scaffolding, sandbox testbed, CI configuration, and documentation assets

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Binary Budget Supremacy**: Plan defines stub size ceilings (<5 KB overall) and mandates CI size-report hooks with mitigation steps for >2% growth.
- [x] **Deterministic Memory Discipline**: No runtime allocations introduced; lifecycle APIs remain stubbed with explicit allocator placeholders.
- [x] **Performance-Oriented Portability**: Microbench stub and dual-platform build presets included; plan schedules validation on web and Windows profiles.
- [x] **Spec-Led Delivery**: Approved specification linked above; all tasks trace back to defined requirements and success metrics.
- [x] **Embedded Feature Isolation**: Directory layout enforces paired `.c/.h` modules and sandbox embedding via `target_sources` (no libraries produced).

> Post-design review: No waivers required; all constitutional gates remain compliant.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
CMakeLists.txt                    # root project definition
cmake/toolchains/
├── emscripten.cmake              # web toolchain file
└── clang-cl.cmake                # windows toolchain file
cmake/presets/
└── CMakePresets.json             # web/win debug & release presets

engine/
├── core/
│   ├── nt_engine.c
│   └── nt_engine.h
├── platform/
│   ├── web/
│   │   ├── nt_platform_web.c
│   │   └── nt_platform_web.h
│   └── win/
│       ├── nt_platform_win.c
│       └── nt_platform_win.h
├── features/
│   └── sample/
│       ├── nt_feature_sample.c
│       └── nt_feature_sample.h
└── third_party/
    └── cglm/                     # header-only, subtree or vendor drop

testbeds/
└── sandbox/
    ├── CMakeLists.txt            # embeds engine sources via target_sources
    └── main.c                    # stub loop calling nt_engine APIs

tests/
├── unit/
│   └── test_engine_lifecycle.c
├── microbench/
│   └── test_frame_timing.c
└── size/
    └── CMakeLists.txt            # invokes size-report helper target

ci/
└── workflows/
    ├── web-debug.yml
    ├── web-release.yml
    ├── win-debug.yml
    └── win-release.yml
```

**Structure Decision**: Create a canonical engine scaffold with paired `.c/.h` files per module, centralize toolchain/preset assets under `cmake/`, embed sources in the sandbox testbed, and add CI/test directories so future features extend the same patterns without reshaping the repository.

## Phase Plan

### Phase 0 — Research & Decisions

- Confirm minimum supported versions for CMake, Emscripten SDK, and clang-cl.
- Document preset naming and artifact folder conventions that align with constitutional CI profiles.
- Validate baseline CTest targets capable of producing size and microbench artifacts without real subsystems.

### Phase 1 — Design & Scaffolding

- Author `CMakeLists.txt`, toolchain files, and presets implementing the research decisions.
- Scaffold engine directories (`core`, `platform`, `features/sample`) with placeholder `.c/.h` pairs and lifecycle stubs.
- Create sandbox application embedding engine sources and driving `nt_engine_*` calls.
- Configure `tests/` with lifecycle, size-report, and microbench stubs integrated into CTest.
- Draft quickstart/onboarding docs plus CI workflow shells referencing the presets.

### Phase 2 — Readiness & Handover

- Validate presets and tests across Windows and WebAssembly environments.
- Finalize CI workflows, ensuring artifacts are archived and thresholds logged.
- Review documentation and AGENTS context to confirm new technologies and commands are discoverable.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
