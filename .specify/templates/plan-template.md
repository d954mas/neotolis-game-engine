# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/scripts/bash/setup-plan.sh` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: C23 (clang-cl on Windows, emcc/Clang for WebAssembly)  
**Primary Dependencies**: GLFW, WebGPU (with WebGL2 fallback), cglm (header-only), internal `nt_alloc_*` allocator  
**Storage**: N/A unless feature explicitly adds persisted assets (document in spec)  
**Testing**: CTest (unit, integration, microbench, size-report)  
**Target Platform**: WebAssembly (primary), Windows desktop (secondary rapid iteration)
**Project Type**: Embedded engine sources consumed by per-testbed CMake targets  
**Performance Goals**: Maintain 60 FPS equivalent loops; enforce CI microbench targets across win/web builds  
**Constraints**: `.wasm` ≤ 200 KB, per-feature code ≤ 30 KB, runtime RAM ≤ 32 MB, no hidden allocations  
**Scale/Scope**: Feature-scoped increments; define impacted feature modules and expected consumers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [ ] **Binary Budget Supremacy**: Planned work quantifies expected binary deltas for WebAssembly and Windows; mitigations exist for >2% regressions.
- [ ] **Deterministic Memory Discipline**: Memory usage is preallocated via arenas/fixed buffers and documented allocators; no hidden growth paths remain.
- [ ] **Performance-Oriented Portability**: Microbench coverage, performance targets, and dual-platform validation steps are captured before implementation.
- [ ] **Spec-Led Delivery**: An approved spec exists with C API, memory model, binary/RAM impact, and embedding CMake snippet; plan links to it.
- [ ] **Embedded Feature Isolation**: Tasks map to feature modules with paired `.c/.h` files and keep the engine embedded in consuming testbeds.

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
engine/
├── core/
│   ├── nt_core.c
│   └── nt_core.h
├── features/
│   ├── sprite_batch/
│   │   ├── sprite_batch.c
│   │   └── sprite_batch.h
│   └── memory/
│       ├── arena.c
│       └── arena.h
├── platform/
│   ├── web/
│   │   ├── web_gpu_backend.c
│   │   └── web_gpu_backend.h
│   └── win/
│       ├── win_gpu_backend.c
│       └── win_gpu_backend.h
└── third_party/
    └── cglm/  # header-only

testbeds/
├── sandbox/
│   ├── CMakeLists.txt  # lists required engine sources
│   └── main.c
└── benchmarks/
    ├── CMakeLists.txt
    └── microbench_main.c

ci/
├── toolchains/
│   ├── emscripten.cmake
│   └── clang-cl.cmake
└── workflows/
    ├── web-debug.yml
    └── win-release.yml
```

**Structure Decision**: [Explain which modules are touched, list new/updated directories, and confirm headers/sources remain paired per feature]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
