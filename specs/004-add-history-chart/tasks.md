# Tasks: Size Report History Chart

**Input**: Design documents from `/specs/004-add-history-chart/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/history-data.schema.json`, `quickstart.md`

**Tests**: Playwright/puppeteer smoke coverage and documented manual checklists will verify each user story; no CTest targets apply to this static dashboard.  
**Instrumentation**: Performance marks and console logging must be implemented and validated before any story is marked complete.  
**Organization**: Tasks are grouped by user story so each slice can ship independently.  
**Budgets**: Monitor runtime memory (≤180 samples in memory) and render performance (≤120 ms) while flagging any regressions for follow-up.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Task can run in parallel (independent files, no unmet prerequisites)  
- **[Story]**: User story label (`US1`, `US2`, `US3`) for story phases  
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align local workflows and documentation before implementation begins.

- [X] T001 Update history chart development workflow in `reports/size/README.md` (serving dashboard, schema validation, performance checks)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core scaffolding required before implementing any user story.

- [X] T002 Create module scaffold exporting `hydrateHistorySeries`, `renderHistoryChart`, and `attachHistoryControls` in `reports/size/history-chart.js`
- [X] T003 Insert empty "History" section and module `<script type="module" src="history-chart.js">` reference in `reports/size/report.html`
- [X] T004 Add baseline layout and focus styles for the history chart container in `reports/size/report.css`

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 1 – Present historical growth (Priority: P1) 🎯 MVP

**Goal**: Render a history line chart below the existing size trend, showing total artifact size per commit in chronological order.  
**Independent Test**: Load `reports/size/report.html` with ≥30 commits; confirm the history chart appears beneath the trend card, plots all commits chronologically, and updates when new data is added.

### Implementation Tasks

- [X] T005 [US1] Implement aggregation of folder commit manifests into `HistorySample[]` in `reports/size/history-chart.js`
- [X] T006 [US1] Integrate history data hydration into the existing fetch pipeline in `reports/size/dashboard.js` (load `index.json`, select folder `index.json`, forward samples)
- [X] T007 [US1] Render Chart.js line series with accessible labels and announce the chart via `aria-label` in `reports/size/history-chart.js`
- [X] T008 [US1] Handle edge cases (≤5 commits, >180 commits) and emit "More history needed" messaging in `reports/size/history-chart.js`
- [X] T009 [US1] Record `performance.mark`/`performance.measure` timings and log render duration + dataset gaps to the console in `reports/size/history-chart.js`
- [X] T010 [US1] Extend `reports/size/validators.py` with a CLI entry that validates folder `index.json` files against `specs/004-add-history-chart/contracts/history-data.schema.json`

---

## Phase 4: User Story 2 – Inspect commit context (Priority: P2)

**Goal**: Provide hover and keyboard focus interactions that reveal commit hash, timestamp, and formatted KB size for each data point.  
**Independent Test**: Hover and keyboard-focus multiple points; confirm tooltips/focus banners display commit hash, localized timestamp, and KB size, and that focus changes do not scroll the page.

### Implementation Tasks

- [X] T011 [US2] Implement tooltip templating to surface commit hash, localized timestamp, and KB size in `reports/size/history-chart.js`
- [X] T012 [US2] Add keyboard navigation hooks and focus management for chart points in `reports/size/history-chart.js`
- [X] T013 [US2] Expand tooltip and focus styling (contrast, focus ring, banner positioning) in `reports/size/report.css`
- [X] T014 [US2] Document keyboard navigation test steps and accessibility expectations in `reports/size/README.md`
- [X] T015 [US2] Log tooltip and focus interactions (commit id + window) to the console for validation in `reports/size/history-chart.js`

---

## Phase 5: User Story 3 – Segment review windows (Priority: P3)

**Goal**: Allow switching between 30-, 90-, and 180-commit windows with session persistence and truncated-notice handling.  
**Independent Test**: Toggle 30/90/180 controls; ensure the chart redraws with the correct commit count, the selection persists for the session, and truncation notices appear when applicable.

- [X] T016 [US3] Add 30/90/180 window controls and descriptive copy to `reports/size/report.html`
- [X] T017 [US3] Implement window switching, data slicing, and `sessionStorage` persistence in `reports/size/history-chart.js`
- [X] T018 [US3] Update chart subtitle and truncation messaging (including gap counts) in `reports/size/history-chart.js`
- [X] T019 [US3] Add window persistence regression checklist to `reports/size/README.md`
- [X] T020 [US3] Log window selection changes (commit count + samples rendered) to the console in `reports/size/history-chart.js`

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and release readiness tasks.

- [X] T021 Create manual smoke checklist covering all user stories in `reports/size/tests/history-chart-smoke.md`
- [X] T022 Capture load-time metrics via `reports/size/scripts/measure-history-load.js` and document usage in `reports/size/README.md`
- [X] T023 Update release runbook entry `reports/size/README.md` with render-timing review steps and regression-tracking guidance for history chart metrics

---

## Dependencies

1. Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3) → Phase 6  
2. User story order: US1 (history rendering) → US2 (tooltips/accessibility) → US3 (window controls)  
3. Instrumentation tasks (T009, T015, T020, T022, T023) depend on corresponding feature logic within each story.

## Parallel Execution Opportunities

- **US1**: After T005 completes, T007 (chart rendering) and T008 (edge-case messaging) can proceed concurrently.  
- **US2**: T011 (tooltip content) and T013 (styling) can be developed in parallel once T012 defines focus behavior.  
- **US3**: T017 (logic) and T018 (subtitle/messaging) can run in parallel after T016 introduces the controls markup.  
- **Polish**: T021 (manual checklist) and T022 (load measurement script) target different paths and can be executed simultaneously near release.

## Implementation Strategy

1. Establish scaffolding and documentation (Phases 1–2) to keep the dashboard build predictable.  
2. Deliver MVP (US1) focusing on accurate historical rendering and instrumentation.  
3. Layer on accessibility improvements (US2) ensuring keyboard parity and logging.  
4. Add window controls (US3) with persistence and truncation handling.  
5. Finalize cross-cutting verifications (Phase 6) for instrumentation observability and release readiness.
