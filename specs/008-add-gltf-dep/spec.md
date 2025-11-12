# Feature Specification: GLFW FetchContent Wiring

**Feature Branch**: `008-add-gltf-dep`  
**Created**: 2025-11-12  
**Status**: Draft  
**Input**: User description: "Add gltf https://github.com/glfw/glfw it uses cmake so it should be easy to add as dependency."

> Speckit specs MUST describe the C API, memory model, binary and RAM impact, microbench targets, and the CMake snippet that embeds engine sources into the target testbed. Keep all numbers testable.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Build engineer fetches GLFW (Priority: P1)

A build engineer configures `web-debug` or `win-debug` and expects GLFW 3.4.0 to download automatically via FetchContent (no pre-seeded archives or scripts).

**Why this priority**: The dependency must exist before any other feature can rely on it.

**Independent Test**: Remove the build directory, run `cmake --preset win-debug`, and verify that the configure step downloads GLFW 3.4.0 from GitHub while disabling samples/tests/docs.

**Acceptance Scenarios**:
1. **Given** a clean checkout with network access, **When** `cmake --preset web-debug` runs, **Then** FetchContent downloads GLFW 3.4.0 and logs a `GLFW download` message before configuring targets.
2. **Given** the download fails (offline machine), **When** configure runs, **Then** CMake stops with a clear FetchContent error explaining that the dependency requires internet access.

---

### User Story 2 - Developer links GLFW target (Priority: P2)

A feature developer updates an existing target (e.g., sandbox) and expects to consume GLFW simply by adding `target_link_libraries(<target> PRIVATE glfw)` with no further boilerplate.

**Why this priority**: Proves the vendored dependency is usable immediately without wrapper APIs.

**Independent Test**: Modify `testbeds/sandbox/CMakeLists.txt` to link against `glfw`, build the sandbox, and optionally run a smoke test (`glfwInit`/`glfwTerminate`).

**Acceptance Scenarios**:
1. **Given** the developer adds `target_link_libraries(dummy PRIVATE glfw)`, **When** CMake reconfigures, **Then** headers and libraries resolve without extra include paths or flags.
2. **Given** the sandbox executable is rebuilt, **When** the optional smoke flag is enabled, **Then** the binary logs `GLFW smoke check passed` after running `glfwInit/glfwTerminate` once.

---

### Edge Cases

- FetchContent download failure (offline environment) — configure MUST report the failure immediately; offline support is out of scope for this iteration.
- Unsupported toolchain (older CMake) — presets MUST enforce CMake ≥3.27 to ensure FetchContent features are available.
- Duplicate GLFW initialization — optional smoke code MUST guard `glfwInit`/`glfwTerminate` so they only run when explicitly requested.

## Requirements & Memory Model *(mandatory)*

### Functional Requirements

- **FR-001**: Repository MUST integrate GLFW 3.4.0 via FetchContent using the official GitHub tag and disable samples/tests/docs before building.
- **FR-002**: `testbeds/sandbox/CMakeLists.txt` MUST export the upstream `glfw` target and link it into `sandbox_app`, allowing other targets to link via `target_link_libraries(<target> PRIVATE glfw)`.
- **FR-003**: Configure output MUST log whether GLFW was downloaded during the run (e.g., `GLFW download` vs `GLFW already populated`) to aid debugging.
- **FR-004**: Optional smoke verification (compile-time flag) MAY call `glfwInit/glfwTerminate` but MUST remain disabled by default and avoid persistent allocations.

### Key Entities

- **glfw_target_registration**: Describes how FetchContent brings the upstream target into the build and exposes it to consumer targets.

### Memory Model

- No new persistent arenas are required. Optional smoke checks rely solely on stack-local variables during `glfwInit/glfwTerminate` calls and reuse existing engine allocators for logs if needed.

## C API Surface & Embedding *(mandatory)*

### Public Headers

- No new headers are added; consumers include `<GLFW/glfw3.h>` directly when they opt-in.

### Function Table

| Symbol | Purpose | Thread Safety | Notes |
|--------|---------|---------------|-------|
| `glfwInit(void)` | Provided by upstream; used only in optional smoke mode. | No | Must run on the main thread. |
| `glfwTerminate(void)` | Provided by upstream; used only in optional smoke mode. | No | Complements the smoke init call. |

### Embedding Snippet

```cmake
include(FetchContent)
FetchContent_Declare(
    glfw
    URL https://github.com/glfw/glfw/archive/refs/tags/3.4.0.tar.gz
    DOWNLOAD_EXTRACT_TIMESTAMP OFF
)
set(GLFW_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(GLFW_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(GLFW_BUILD_DOCS OFF CACHE BOOL "" FORCE)
set(GLFW_INCLUDE_NONE ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(glfw)

target_link_libraries(sandbox_app PRIVATE glfw)
```

## Resource Budgets & Performance *(mandatory)*

- **Binary Size Delta**: ≤ +20 KB relative to baseline `sandbox_app` (keeps `.wasm` artifact ≤200 KB).
- **Per-Feature Budget**: ≤30 KB ensured by compiling GLFW with the unused components disabled (`GLFW_BUILD_* OFF`).
- **Runtime RAM**: No persistent memory impact; optional smoke tests use stack locals only.
- **CPU/Frame Time Target**: Not applicable (no runtime usage mandated); optional smoke tests MUST complete in ≤2 seconds on WebAssembly debug builds.
- **Verification**: Manual configure/build + optional smoke run; no CI automation or new tests are introduced for this dependency-only change.
- **Mitigations**: If binary delta exceeds limits, disable additional GLFW backends (Wayland/Vulkan stubs) or gate the dependency behind a build option until optimized.

## Observability & Operations *(mandatory)*

- **Instrumentation Plan**: Rely on configure-time `message(STATUS ...)` output to indicate when FetchContent downloads GLFW; optional smoke logs go to stdout/stderr.
- **Validation Steps**: Developers inspect configure logs for download messages and optionally run the sandbox with `-DNT_SANDBOX_ENABLE_GLFW_SMOKE=ON` to confirm linkage.
- **Operational Notes**: Document the pinned version/tag and remind developers that network access is required during configure; offline flows are intentionally unsupported in this iteration.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers configure and build `web-debug` or `win-debug` with GLFW vendored in under 5 minutes on a clean machine (assuming network access).
- **SC-002**: Sandbox (or any consumer target) links against GLFW by adding a single `target_link_libraries(<target> PRIVATE glfw)` statement with no extra configuration.
- **SC-003**: Optional smoke check (`glfwInit/glfwTerminate`) succeeds 95% of runs when enabled, completing within 2 seconds on WebAssembly debug builds.
