---

description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
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

- [ ] T001 Create/extend engine feature directories (paired `.c`/`.h`) per implementation plan
- [ ] T002 Update `testbeds/[target]/CMakeLists.txt` to embed new feature sources
- [ ] T003 [P] Configure clang-format, clang-tidy, and size-report tooling for the feature

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T004 Implement or extend memory arenas in `engine/features/memory/arena.c` (document capacity)
- [ ] T005 [P] Wire platform backends (WebGPU/WebGL2 or GLFW/OpenGL) needed by this feature
- [ ] T006 [P] Add configuration toggles / feature flags in `engine/core/nt_core.h`
- [ ] T007 Establish logging category and compile-time `NT_LOG_LEVEL` hooks
- [ ] T008 Update CI profiles (`ci/workflows/*.yml`) to run new microbench or size targets if required

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 1 (Required unless waiver approved) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation. Record any waiver in plan.md Complexity Tracking.**

- [ ] T010 [P] [US1] Add CTest unit target `tests/unit/test_[feature]_api.c`
- [ ] T011 [P] [US1] Create integration test `tests/integration/test_[journey].c` covering the new feature path
- [ ] T012 [US1] Register microbench target in `tests/microbench/CMakeLists.txt` and ensure it fails until implementation

### Implementation for User Story 1

- [ ] T013 [P] [US1] Implement public API in `engine/features/[feature]/[feature].h`
- [ ] T014 [US1] Implement core logic in `engine/features/[feature]/[feature].c`
- [ ] T015 [US1] Integrate allocator usage via `nt_alloc_*` with documented buffer sizes
- [ ] T016 [US1] Add logging at compile-time-controlled granularity
- [ ] T017 [US1] Wire feature into consuming testbed `testbeds/[target]/main.c`
- [ ] T018 [US1] Update size-report whitelist/thresholds if new assets are unavoidable

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2 (Required unless waiver approved) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation. Record any waiver in plan.md Complexity Tracking.**

- [ ] T019 [P] [US2] Contract test for secondary API in `tests/unit/test_[feature]_edge_cases.c`
- [ ] T020 [P] [US2] Integration test for cross-feature flow in `tests/integration/test_[journey]_p2.c`
- [ ] T021 [US2] Extend microbench coverage if execution path changes

### Implementation for User Story 2

- [ ] T022 [P] [US2] Add supplemental headers/source pair with guarded feature flag
- [ ] T023 [US2] Update `engine/core/nt_core.c` initializers to register the new behavior
- [ ] T024 [US2] Validate allocator pressure and adjust arena documentation if required
- [ ] T025 [US2] Capture size-report output and annotate expected deltas

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 3 (Required unless waiver approved) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation. Record any waiver in plan.md Complexity Tracking.**

- [ ] T026 [P] [US3] Contract test for fallback path in `tests/unit/test_[feature]_fallback.c`
- [ ] T027 [P] [US3] Integration test for error handling in `tests/integration/test_[journey]_errors.c`
- [ ] T028 [US3] Add size/memory monitor to CTest dashboard if behavior impacts budgets

### Implementation for User Story 3

- [ ] T029 [P] [US3] Implement fallback path in `engine/features/[feature]/[feature]_fallback.c`
- [ ] T030 [US3] Surface errors via `nt_status` codes, update headers
- [ ] T031 [US3] Verify logging toggles and runtime switches remain debug-only
- [ ] T032 [US3] Update documentation in `docs/[feature]/` if applicable

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] TXXX [P] Documentation updates in `docs/[feature]/`
- [ ] TXXX Code cleanup and refactoring (keep binary delta within budget)
- [ ] TXXX Performance optimization across all stories (update microbench baselines)
- [ ] TXXX [P] Additional unit tests in `tests/unit/`
- [ ] TXXX Security hardening / static analysis via clang-tidy
- [ ] TXXX Run `quickstart.md` validation on target testbeds
- [ ] TXXX Instrumentation verification across stories (size, memory, performance)

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

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

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
