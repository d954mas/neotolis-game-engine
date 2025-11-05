---
description: "Task list for Size Reporting Dashboard"
---

# Tasks: Size Reporting Dashboard

**Input**: Design documents from `/specs/003-add-size-reports/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Define failing CLI and dashboard verification checks before implementing story code. Record any waivers in plan.md Complexity Tracking (none approved).  
**Instrumentation**: Tasks include explicit steps to emit and validate size-report logs and CI artifacts prior to story completion.  
**Organization**: Tasks are grouped by user story so each slice remains independently testable.  
**Budgets**: Include size, RAM, and performance verification tasks; CI must fail on >2% regressions with mitigation guidance.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish size-report directories and baseline documentation scaffolding.

- [X] T001 Scaffold size-reporting directory tree in `reports/size/` (create `report.html` stub, `lib/` folder with vendored `chart.min.js`, and `sandbox/wasm/{debug,release}/report.txt` placeholders)
- [X] T002 Create baseline management guide in `reports/size/README.md` describing MASTER refresh workflow and approval notes

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Provide shared script scaffolding and fixtures required by all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T003 Create Python CLI scaffold with argparse entrypoints in `reports/size/update.py` (stub functions for head update and manifest regeneration)
- [X] T004 Prepare reusable fixture artifacts under `tests/size/fixtures/sandbox_wasm_debug/` with sample `.wasm`, `.js`, and `index.html` files for validation

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Capture build size snapshot (Priority: P1) 🎯 MVP

**Goal**: Enable engineers to regenerate HEAD size snapshots per sandbox folder while preserving MASTER baselines.  
**Independent Test**: Run `python reports/size/update.py --input output/sandbox/wasm/debug --output sandbox/wasm/debug` against fixture artifacts; verify HEAD row updates, MASTER row remains unchanged, and manifest captures deltas.

### Tests for User Story 1 (write first, ensure failing before implementation) ⚠️

- [X] T005 [P] [US1] Add CLI smoke test in `tests/size/test_update_cli.py` asserting HEAD row replacement, CSV schema validation, and commit SHA/message capture
- [X] T006 [P] [US1] Add missing-baseline regression test in `tests/size/test_update_missing_baseline.py` covering placeholder MASTER handling

### Implementation for User Story 1

- [X] T007 [US1] Implement HEAD snapshot update logic in `reports/size/update.py` to measure artifact sizes via `os.stat`, capture commit SHA + subject lines, and rewrite HEAD row
- [X] T008 [P] [US1] Implement CSV schema validation helpers in `reports/size/validators.py` enforcing `git_ref,file_name,size_bytes,git_sha,git_message`
- [X] T009 [US1] Add error handling and structured logging for missing artifacts or dirty worktrees in `reports/size/update.py`
- [X] T010 [US1] Generate summarized manifest `reports/size/index.json` with HEAD and MASTER size deltas plus commit SHA/message metadata for the processed folder
- [X] T011 [US1] Document CLI usage, alerts, and manual MASTER refresh steps in `reports/size/README.md`

**Checkpoint**: User Story 1 delivers an independently testable CLI workflow with logging, validation, and documentation.

---

## Phase 4: User Story 2 - Compare HEAD to MASTER visually (Priority: P2)

**Goal**: Provide reviewers a dashboard showing HEAD vs. MASTER deltas for a default sandbox folder with visual alerts.  
**Independent Test**: Open `reports/size/report.html` in a browser, load default folder data from `index.json`, and confirm table plus chart highlight >2% or >25 KB deltas.

### Tests for User Story 2 (write first) ⚠️

- [X] T012 [P] [US2] Create dashboard verification checklist in `tests/size/manual/report_dashboard.md` covering table accuracy and alert rendering

### Implementation for User Story 2

- [X] T013 [US2] Build base HTML layout and data bootstrap in `reports/size/report.html` loading default folder data from `reports/size/index.json` and wiring Chart.js assets
- [X] T014 [US2] Implement table rendering and delta formatting logic in `reports/size/dashboard.js` for HEAD vs. MASTER rows
- [X] T015 [US2] Instantiate Chart.js bar chart in `reports/size/dashboard.js` highlighting HEAD and MASTER sizes with threshold annotations
- [X] T016 [P] [US2] Add alert styling and responsive layout rules in `reports/size/report.css` and link from `report.html`

**Checkpoint**: User Story 2 yields a visual dashboard for a single folder with alerts and charting.

---

## Phase 5: User Story 3 - Review historical folders (Priority: P3)

**Goal**: Allow reviewers to switch between sandbox folders from one dashboard without stale data.  
**Independent Test**: Using fixtures for both debug and release, switch folders in `report.html` and confirm table/graph update within two seconds.

### Tests for User Story 3 (write first) ⚠️

- [X] T017 [US3] Extend manual checklist in `tests/size/manual/report_dashboard.md` with folder switching validation and latency measurements

### Implementation for User Story 3

- [X] T018 [US3] Extend manifest generation in `reports/size/update.py` to enumerate all `reports/size/**/report.txt` files with folder metadata
- [X] T019 [US3] Implement folder selector UI and state management in `reports/size/report.html` to change the active dataset
- [X] T020 [US3] Add dynamic refresh logic in `reports/size/dashboard.js` to reload table and chart within two seconds on folder changes

**Checkpoint**: All user stories are independently functional; dashboard covers multiple folders.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize CI integration, documentation, and instrumentation across stories.

- [X] T021 Integrate size-report update step in `ci/workflows/size-report.yml` to run `reports/size/update.py` for sandbox wasm debug/release and upload artifacts
- [X] T022 Update quickstart instructions in `specs/003-add-size-reports/quickstart.md` to reflect final CLI arguments, CI usage, and review steps
- [X] T023 [P] Add instrumentation verification script in `tests/size/scripts/verify_size_report.py` to assert CLI logs include measured sizes and alert thresholds

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No prerequisites — start immediately.  
- **Foundational (Phase 2)**: Depends on Setup completion — blocks all user stories.  
- **User Stories (Phases 3–5)**: Begin only after Foundational tasks finish; implement in priority order (P1 → P2 → P3) or parallel if staffed.  
- **Polish (Phase 6)**: Runs after all targeted user stories complete.

### User Story Dependencies

- **User Story 1 (P1)**: Requires foundational CLI scaffold and fixtures. Independent afterward.  
- **User Story 2 (P2)**: Requires User Story 1 manifest generation to supply data.  
- **User Story 3 (P3)**: Builds on manifest + dashboard from User Stories 1 and 2 to add folder switching.

### Within Each User Story

- Tests (manual or automated) MUST be written and fail before implementation proceeds.  
- CLI/data model changes precede dashboard updates.  
- Validate instrumentation and logging before closing the story.

### Parallel Opportunities

- T001 and T002 can run in parallel once repo branch is ready.  
- T005/T006 can be authored concurrently before implementing CLI logic.  
- T013/T016 may proceed in parallel with T014 once data loader contracts are defined.  
- Final-phase T021–T023 can be split across team members after stories complete.

---

## Parallel Example: User Story 1

```bash
# Execute failing smoke tests together before implementation
python -m pytest tests/size/test_update_cli.py
python -m pytest tests/size/test_update_missing_baseline.py

# Run CLI locally against fixtures after implementation
python reports/size/update.py --input output/sandbox/wasm/debug --output sandbox/wasm/debug
cat reports/size/sandbox/wasm/debug/report.txt
cat reports/size/index.json | jq .
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup)  
2. Complete Phase 2 (Foundational)  
3. Deliver Phase 3 (User Story 1) and validate CLI + manifest outputs  
4. Demonstrate CLI workflow and logs before moving forward

### Incremental Delivery

1. Finish Setup + Foundational to unblock development  
2. Ship User Story 1 (CLI + manifest) as MVP  
3. Layer in User Story 2 (dashboard visualization)  
4. Add User Story 3 (multi-folder navigation)  
5. Conclude with Phase 6 polish tasks and CI integration

### Parallel Team Strategy

- Team completes Phase 1 and Phase 2 together.  
- Developer A owns User Story 1 (CLI, manifest, documentation).  
- Developer B owns User Story 2 (dashboard UI + charting).  
- Developer C owns User Story 3 (folder switching enhancements).  
- After story completion, divide Phase 6 polish tasks (CI, quickstart, instrumentation verification).

---

## Notes

- [P] tasks involve separate files and can run concurrently without blocking dependencies.  
- Each user story stays independently testable with dedicated verification steps.  
- Ensure CLI logs and dashboard outputs meet instrumentation requirements before closing tasks.  
- Keep CSV and HTML assets under the 30 KB per-folder budget; run size checks during T021/T023.
