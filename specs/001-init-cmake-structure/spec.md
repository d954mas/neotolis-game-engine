# Feature Specification: Project Structure & CMake Bootstrap

**Feature Branch**: `001-init-cmake-structure`  
**Created**: 2025-10-22  
**Status**: Draft  
**Input**: User description: "create project structure. Add cmake"

> Speckit specs MUST describe the C API, memory model, binary and RAM impact, microbench targets, and the CMake snippet that embeds engine sources into the target testbed. Keep all numbers testable.

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Unified Build Bootstrap (Priority: P1)

Maintainers need a ready-to-run project skeleton that builds the Speckit engine and sandbox testbed for both WebAssembly and Windows targets with one documented workflow.

**Why this priority**: Without a cross-target build foundation, no subsequent engine feature can be exercised or validated.

**Independent Test**: Run the documented configuration steps on a clean machine and confirm that `web-debug` and `win-debug` build artifacts are produced without manual project restructuring.

**Acceptance Scenarios**:

1. **Given** a fresh clone, **When** the maintainer configures the toolchains per documentation, **Then** both WebAssembly and Windows debug builds complete using the provided CMake project.
2. **Given** an existing checkout, **When** the maintainer regenerates build files, **Then** the engine sources remain embedded directly in the sandbox executable without creating standalone libraries.

---

### User Story 2 - Feature Module Scaffolding (Priority: P2)

Engine contributors require a predictable directory layout and placeholder files so new feature modules can be added without disrupting build rules or naming conventions.

**Why this priority**: A clear structure shortens onboarding time and enforces the principle of embedded feature isolation.

**Independent Test**: Create a new feature directory under `engine/features/` following documented steps and verify that adding it to the sandbox target requires only editing the localized CMake snippet.

**Acceptance Scenarios**:

1. **Given** the scaffolded directories, **When** a developer copies the sample module template, **Then** the new files compile as part of the sandbox build with no additional global configuration.

---

### User Story 3 - CI Baseline Targets (Priority: P3)

The delivery team needs default CTest, size-report, and microbench targets wired into the project so CI can enforce constitutional budgets from day one.

**Why this priority**: Automated gates prevent regressions and confirm the build system behaves consistently across contributors.

**Independent Test**: Trigger the baseline CI configuration (local or remote) and confirm the size-report and microbench targets execute, producing artifacts tracked for deltas.

**Acceptance Scenarios**:

1. **Given** the configured project, **When** CI runs the default pipeline, **Then** size-report and microbench results are generated and stored with the build artifacts.

### Edge Cases

- Toolchain prerequisites missing (e.g., Emscripten SDK not initialized) must surface actionable error guidance without requiring manual CMake edits.
- Windows environment lacks clang-cl: the project must fail gracefully with documentation pointing to required LLVM installation steps.
- Sandbox testbed omitted from the configure command must still allow engine-only configuration paths while warning that no runnable target will be produced.

## Requirements & Memory Model *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: The repository MUST include a root CMake project that configures Speckit for WebAssembly (Emscripten) and Windows (clang-cl) using `-Oz` and LTO defaults aligned with constitutional budgets.
- **FR-002**: CMake configuration MUST provide presets or documented cache scripts for `web-debug`, `web-release`, `win-debug`, and `win-release`, each invoking shared engine source lists.
- **FR-003**: The engine directory layout MUST follow the feature-oriented structure (`engine/core`, `engine/features/<module>`, `engine/platform/<target>`, `testbeds/<name>`) with paired `.c` and `.h` placeholders ready for future implementation.
- **FR-004**: A sandbox testbed MUST embed engine sources directly via `target_sources` without producing standalone libraries, demonstrating how downstream games will integrate modules.
- **FR-005**: The scaffold MUST expose a public header `engine/core/nt_engine.h` declaring initialization, frame, and shutdown entry points with documented configuration structs while stubbing logic until feature modules supply behavior.

### Key Entities *(include if feature involves data)*

- **BuildProfile**: Named configuration (e.g., `web-debug`, `win-release`) mapping to target platform, optimization level, and CI profile identifier.
- **EngineModule**: Feature-scoped directory containing paired source and header files plus optional platform-specific variants referenced by build profiles.

### Memory Model

- **Allocator**: `nt_alloc_*` defaults to the platform allocator placeholder; no dynamic allocations occur in this bootstrap stage.
- **Persistent Buffers**: None introduced—engine modules are stubs only.
- **Transient Scratch**: None—sample testbed runs without runtime allocations.
- **Failure Modes**: Initialization functions MUST return explicit status codes when downstream modules request allocators that are not yet configured.

## C API Surface & Embedding *(mandatory)*

### Public Headers

- `engine/core/nt_engine.h`: Declares lifecycle entry points and configuration structs for embedding applications.
- Additional headers: `engine/platform/web/nt_platform_web.h`, `engine/platform/win/nt_platform_win.h` providing platform hooks (stubs until populated).

### Function Table

| Symbol | Purpose | Thread Safety | Notes |
|--------|---------|---------------|-------|
| `nt_engine_init` | Initializes engine state according to provided configuration structs. | Yes — callers synchronize around a single init call. | Must return status codes if required modules unavailable. |
| `nt_engine_frame` | Advances the engine once per frame, invoking registered subsystems. | No — expect single-threaded call from main loop. | Stub implementation emits size-report instrumentation hooks only. |
| `nt_engine_shutdown` | Releases engine resources and resets state owned by the embedding app. | Yes — safe to call after `nt_engine_init` even if subsystems were not started. | Ensures no runtime allocations remain outstanding. |

### Embedding Snippet

```cmake
# Add the exact CMake lines that embed this feature into the consuming testbed
target_sources(${PROJECT_NAME}
    PRIVATE
        engine/core/nt_engine.c
        engine/core/nt_engine.h
        engine/platform/web/nt_platform_web.c
        engine/platform/web/nt_platform_web.h
        engine/platform/win/nt_platform_win.c
        engine/platform/win/nt_platform_win.h
)
```

## Resource Budgets & Performance *(mandatory)*

- **Binary Size Delta**: ≤ +5 KB for bootstrap scaffolding (keeps total `.wasm` ≤ 200 KB).
- **Per-Feature Budget**: ≤ 30 KB per future feature module; current scaffold introduces ≤ 10 KB combined for stubs.
- **Runtime RAM**: 0 bytes reserved at runtime; all allocations deferred to future features.
- **CPU/Frame Time Target**: `nt_engine_frame` stub executes in ≤ 0.1 ms on reference hardware, verifying minimal overhead.
- **CI Hooks**: `ctest -R size_report`, `ctest -R microbench_stub`, baseline `ctest` for lifecycle smoke tests.
- **Mitigations**: If stub code exceeds size or timing budgets, remove instrumentation or split optional diagnostics into off-by-default feature flags before merge.

## Observability & Operations *(mandatory)*

- **Instrumentation Plan**: Provide default size-report target capturing `.wasm` text/data sections and a microbench stub measuring `nt_engine_frame`. Emit lifecycle logs through the compile-time `NT_LOG_LEVEL` macro in debug builds to confirm wiring.
- **Validation Steps**: Execute `ctest --output-on-failure` for size-report and microbench targets in both web-debug and win-debug configurations; confirm artifacts upload in CI baseline run.
- **Operational Notes**: Document toolchain setup (Emscripten SDK 3.1.x, LLVM 17) and note that production builds disable debug logging by default while retaining instrumentation hooks for future subsystems.

## Dependencies & Assumptions

- Emscripten SDK 3.1.x and LLVM/clang-cl 17 are available and documented in the onboarding guide.
- Contributors have write access to configure CMake presets and run the provided CI workflow.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Maintainers can configure and build both WebAssembly and Windows debug targets in under 15 minutes following the documented steps.
- **SC-002**: CI baseline completes size-report and microbench targets with zero failures across `web-debug`, `web-release`, `win-debug`, and `win-release` profiles.
- **SC-003**: New contributors report ≤ 1 setup-related question during onboarding sessions after following the project structure guide.
- **SC-004**: Stub sandbox executable runs and logs lifecycle events on both target platforms within 5 seconds of launch, demonstrating functional build outputs.
