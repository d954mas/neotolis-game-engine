# Tasks: GLFW FetchContent Wiring

**Input**: Design documents from `/specs/008-add-gltf-dep/`
**Prerequisites**: plan.md, spec.md, data-model.md, quickstart.md, contracts/

**Tests**: Manual configure/build + optional sandbox smoke check (no CI tasks).

## Phase 1: Setup

- [X] T001 Remove legacy cache toggles from `CMakeLists.txt` so FetchContent is the sole mechanism

## Phase 2: Foundational

- [X] T002 Ensure `cmake/presets/CMakePresets.json` no longer passes cache-related variables; rely on defaults only

## Phase 3: User Story 1 – Fetch GLFW via FetchContent (P1)

**Independent Test**: `cmake --preset win-debug` downloads GLFW and logs status.

- [X] T003 [US1] Update `testbeds/sandbox/CMakeLists.txt` to declare/download GLFW directly via FetchContent and log whether a download occurred
- [X] T004 [US1] Set `GLFW_BUILD_EXAMPLES/TESTS/DOCS OFF` + `GLFW_INCLUDE_NONE ON` before `FetchContent_MakeAvailable` to honor size budgets
- [X] T005 [US1] Document the pinned version/tag in `engine/third_party/README.md`

## Phase 4: User Story 2 – Consumer linking (P2)

**Independent Test**: `target_link_libraries(sandbox_app PRIVATE glfw)` builds and optional smoke logs success.

- [X] T006 [US2] Link `sandbox_app` against `glfw` and add the optional `NT_SANDBOX_ENABLE_GLFW_SMOKE` definition gate
- [X] T007 [US2] Implement the smoke block in `testbeds/sandbox/main.c` (`glfwInit/glfwTerminate` when the flag is enabled)
- [X] T008 [P] [US2] Document the linking + smoke instructions in `docs/feature-modules.md`

## Phase 5: Polish

- [X] T009 Update `specs/008-add-gltf-dep/quickstart.md` with the simplified configure + smoke steps
