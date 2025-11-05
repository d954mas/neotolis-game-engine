---

description: "Task list template for feature implementation"
---

# Tasks: Project Structure & CMake Bootstrap

**Input**: Design documents from `/specs/001-init-cmake-structure/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Define failing CTest targets (unit/integration/microbench/size) for every committed user story before implementation tasks begin. Only omit when plan.md documents an approved waiver.

**Instrumentation**: Add explicit tasks to implement and verify observability commitments before marking a story complete.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Budgets**: Include binary size, RAM, and performance verification tasks; flag any >2% regressions with mitigation notes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Engine sources live under `engine/` with paired `.c`/`.h` files per feature module
- Testbeds embed engine sources via `testbeds/<name>/CMakeLists.txt`
- Tests reside in `tests/unit/`, `tests/integration/`, `tests/microbench/`, and `tests/size/`
- Tooling, scripts, and CI configurations live under `ci/` and `scripts/` directories

<!-- 
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.
  
  The /speckit.tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/
  
  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment
  
  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and baseline toolchain hooks

- [X] T001 Clean repository root and create baseline directories (`cmake/`, `engine/`, `testbeds/`, `tests/`, `ci/workflows/`)
- [X] T002 [P] Initialize root `CMakeLists.txt` stub referencing engine, sandbox, and test directories
- [X] T003 Document prerequisite installations in `docs/requirements.md` (or new file) referencing research decisions
- [X] T004 [P] Create `cmake/toolchains/emscripten.cmake` and `cmake/toolchains/clang-cl.cmake` placeholders with required compiler detection
- [X] T005 [P] Generate `cmake/presets/CMakePresets.json` skeleton referencing planned presets
- [X] T006 Add `.editorconfig`/formatting defaults aligned with C23 style (if not present)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Embed stub engine core module files `engine/core/nt_engine.c` + `.h` with lifecycle function signatures
- [X] T008 Create sandbox target definition in `testbeds/sandbox/CMakeLists.txt` embedding core sources via `target_sources`
- [X] T009 [P] Configure preset entries for `web-debug` and `win-debug` (commands, generators, cache variables)
- [X] T010 [P] Configure preset entries for `web-release` and `win-release` with `-Oz`, LTO flags, and artifact directories
- [X] T011 Establish baseline CTest invocation in root `CMakeLists.txt` including `add_subdirectory(tests)`
- [X] T012 [P] Create CI workflow skeletons `ci/workflows/web-debug.yml` and `ci/workflows/win-debug.yml` executing matching presets
- [X] T013 [P] Create release workflow skeletons `ci/workflows/web-release.yml` and `ci/workflows/win-release.yml` executing matching presets
- [X] T014 Add quickstart scaffolding file `quickstart.md` with empty sections for install, configure, build, and test
- [X] T015 Ensure AGENTS.md records new technology stack entry (triggered via update-agent-context script post-plan)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Unified Build Bootstrap (Priority: P1) 🎯 MVP

**Goal**: Deliver a buildable cross-platform skeleton producing WebAssembly and Windows debug artifacts from presets.

**Independent Test**: On a clean machine, follow quickstart instructions to configure and build `web-debug` and `win-debug`; both builds complete without manual project modifications.

### Tests for User Story 1 (Required unless waiver approved) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation. Record any waiver in plan.md Complexity Tracking.**

- [X] T016 [P] [US1] Create lifecycle smoke test `tests/unit/test_engine_lifecycle.c` validating `nt_engine_init/frame/shutdown`
- [X] T017 [P] [US1] Add preset-aware CTest configuration in `tests/CMakeLists.txt`

### Implementation for User Story 1

- [X] T018 [US1] Flesh out root `CMakeLists.txt` with project definition, language standard, and inclusion of toolchain logic
- [X] T019 [P] [US1] Implement `cmake/toolchains/emscripten.cmake` with compiler flags, linker settings, and caching of artifact directories
- [X] T020 [P] [US1] Implement `cmake/toolchains/clang-cl.cmake` with Windows-specific flags and sanitizers for debug builds
- [X] T021 [US1] Complete `cmake/presets/CMakePresets.json` with configure/build/test presets for all four profiles
- [X] T022 [US1] Implement sandbox main loop in `testbeds/sandbox/main.c` calling `nt_engine_*` APIs
- [X] T023 [US1] Wire engine core module into sandbox via `testbeds/sandbox/CMakeLists.txt` ensuring no standalone libs
- [X] T024 [US1] Populate quickstart instructions for toolchain installation and preset usage
- [X] T025 [US1] Update `docs/onboarding.md` (or create) summarizing build bootstrap steps and expected outputs
- [ ] T026 [US1] Validate `cmake --preset web-debug` and `cmake --build --preset web-debug` on a clean build directory (document results)
- [ ] T027 [US1] Validate `cmake --preset win-debug` and `cmake --build --preset win-debug` on a Windows environment (document results)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Feature Module Scaffolding (Priority: P2)

**Goal**: Provide clear feature module templates and documentation so contributors can add new modules without modifying global build logic.

**Independent Test**: Duplicate the sample feature module, register it in sandbox `target_sources`, and confirm it compiles with no additional configuration changes.

### Tests for User Story 2 (Required unless waiver approved) ⚠️

- [X] T028 [P] [US2] Add compilation check in `tests/unit/test_feature_sample.c` ensuring sample module symbols link
- [X] T029 [US2] Extend documentation with step-by-step module duplication checklist verified through sandbox build

### Implementation for User Story 2

- [X] T030 [US2] Populate `engine/features/sample/nt_feature_sample.h` with API placeholders and documentation comments
- [X] T031 [US2] Populate `engine/features/sample/nt_feature_sample.c` with stub implementations referencing `nt_alloc_*` usage expectations
- [X] T032 [US2] Add platform shim headers `engine/platform/web/nt_platform_web.h` and `.c` with structured TODO comments for future subsystems
- [X] T033 [US2] Add platform shim headers `engine/platform/win/nt_platform_win.h` and `.c` with stubbed window/input hooks
- [X] T034 [US2] Document feature module creation workflow in `docs/feature-modules.md` including naming, file placement, and budget reminders
- [X] T035 [US2] Update sandbox CMake to include sample module via guarded option or always-on embedding per specification
- [ ] T036 [US2] Verify sample module duplication path by creating `engine/features/example_clone/` (temporary) and confirming build success; remove clone after verification

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - CI Baseline Targets (Priority: P3)

**Goal**: Integrate size-report and microbench CTest targets plus CI workflows that enforce constitutional budgets.

**Independent Test**: Run `ctest --preset <profile>` for all four presets and confirm size-report + microbench artifacts are generated and uploaded by CI jobs.

### Tests for User Story 3 (Required unless waiver approved) ⚠️

- [X] T037 [P] [US3] Add size-report target in `tests/size/CMakeLists.txt` capturing `.wasm` text/data sections
- [X] T038 [P] [US3] Add microbench stub target in `tests/microbench/CMakeLists.txt` measuring `nt_engine_frame`
- [X] T039 [US3] Extend CI workflows to archive size-report and microbench outputs, marking >2% regressions

### Implementation for User Story 3

- [X] T040 [US3] Implement `tests/microbench/test_frame_timing.c` stub measuring frame cost and emitting baseline metrics
- [X] T041 [US3] Implement size-report script or command integration (e.g., `wasm-opt --stats`) referenced by CTest target
- [X] T042 [US3] Update quickstart with instructions for running size-report and microbench targets locally
- [X] T043 [US3] Configure workflow matrices in `ci/workflows/*.yml` to execute tests for all presets with proper caching
- [X] T044 [US3] Document mitigation process for >2% regression in `docs/ci-guidelines.md`
- [ ] T045 [US3] Validate CI pipelines locally (using `act` or dry-run) to ensure environment variables/toolchains resolve
- [ ] T046 [US3] Capture sample artifacts and link them in `docs/ci-guidelines.md` for reference

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T047 Refresh AGENTS.md and README to reflect final structure and command set
- [X] T048 [P] Add clang-format/clang-tidy configuration and pre-commit hook instructions under `scripts/`
- [X] T049 Review binary size baseline; document thresholds in `docs/size-budget.md`
- [X] T050 [P] Harden toolchain detection with informative error messages (missing EMSDK, LLVM) in `cmake/toolchains/*`
- [X] T051 Ensure quickstart and onboarding docs undergo peer review; incorporate feedback
- [ ] T052 Validate `cmake --preset <preset>` + `ctest --preset <preset>` on clean CI agent image; record results
- [ ] T053 Remove temporary verification artifacts (e.g., example clone module) prior to merge

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Must complete before User Story 2 or 3; establishes build infrastructure
- **User Story 2 (P2)**: Depends on User Story 1 scaffolding; independent from User Story 3 once build system exists
- **User Story 3 (P3)**: Depends on User Story 1 for presets/builds; can proceed in parallel with User Story 2 after foundation

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
ctest --tests-regex "^US1_.*"        # unit + integration targets in C
ctest --tests-regex "^US1_MICRO.*"   # microbench + size-report targets

# Launch all modules for User Story 1 together:
Task: "Implement API header in engine/features/[feature]/[feature].h"
Task: "Implement core logic in engine/features/[feature]/[feature].c"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Document instrumentation commitments and validation steps alongside tasks
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
