# Implementation Plan: Size Report History Chart

**Branch**: `004-add-history-chart` | **Date**: 2025-11-06 | **Spec**: specs/004-add-history-chart/spec.md
**Input**: Feature specification from `/specs/004-add-history-chart/spec.md`

## Summary

Add a history line chart immediately following the existing size trend module within `reports/size/report.html` so release engineers can monitor total artifact size per commit. Work uses the existing `reports/size/index.json` manifest (and folder-level commit indexes), adds session-scoped window controls (30/90/180 commits), and delivers accessible tooltip interactions without touching any C sources.

## Technical Context

**Language/Version**: HTML5 + vanilla ES2020 executed directly by the browser (no bundler)  
**Primary Dependencies**: Existing dashboard scripts (`dashboard.js`, Chart.js from `lib/chart.min.js`), browser `fetch`, DOM APIs, CSS variables for theming  
**Storage**: Session-only preference persistence via `sessionStorage` helper already present in dashboard utilities; no backend writes introduced  
**Testing**: Manual regression using static server (`python -m http.server`), lightweight Playwright/puppeteer smoke (if time permits), existing CI artifact review  
**Target Platform**: Chromium (CI default) plus Firefox for accessibility verification  
**Project Type**: Static HTML/JS dashboard served alongside size-report artifacts  
**Performance Goals**: History chart render ≤ 120 ms after manifest load; dashboard load remains ≤ 2.0 s using `index.json` data  
**Constraints**: No modifications to C engine sources; rely solely on existing Chart.js library (no new third-party code)  
**Scale/Scope**: Files limited to `reports/size/report.html`, `reports/size/dashboard.js`, new `reports/size/history-chart.js`, and companion CSS adjustments

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Binary Budget Supremacy**: Dashboard assets remain within existing size-report publishing guidelines; no additional compiled artifacts introduced.
- [x] **Deterministic Memory Discipline**: Front-end uses bounded arrays (≤ 180 samples) and avoids dynamic library allocations; existing C arenas remain untouched.
- [x] **Performance-Oriented Portability**: Render budget (≤ 120 ms) tracked via dashboard performance logging across Chromium/Firefox automation.
- [x] **Spec-Led Delivery**: Approved specification `specs/004-add-history-chart/spec.md` drives requirements; plan maps C API references onto existing manifest contracts while honoring "no C code changes".
- [x] **Embedded Feature Isolation**: Work isolated to dashboard HTML/JS artifacts, leaving engine modules untouched and keeping embedded-source model intact.

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

```text
reports/size/
├── report.html             # update layout to insert history chart container
├── report.css              # extend styles for chart layout/focus states
├── dashboard.js            # integrate history loader/controls, reuse Chart.js
├── history-chart.js        # new module for series hydration + rendering
├── lib/chart.min.js        # existing third-party charting library
├── index.json              # folder manifest listing commit indexes (consumed)
└── sandbox/wasm/release/
    └── index.json          # commit-level data (read-only usage)

specs/004-add-history-chart/contracts/
└── history-data.schema.json  # documents required fields inside index manifests
```

**Structure Decision**: All edits confined to `reports/size/` assets; the plan introduces `history-chart.js` alongside existing scripts, updates CSS/layout, and documents the manifest contract without altering engine sources or build scripts.

## Complexity Tracking

No constitutional violations identified; tracking table not required.

## Post-Phase 1 Constitution Review

Re-evaluated after producing design artifacts — all five gates remain satisfied under front-end-only scope; no waivers requested.
