# Feature Specification: Size Report History Chart

**Feature Branch**: `004-add-history-chart`  
**Created**: 2025-11-06  
**Status**: Draft  
**Input**: User description: "Improve size report dashboard 1)After size trend add history line chart. History show total file size of all commits."

> Speckit specs MUST describe the C API, memory model, binary and RAM impact, microbench targets, and the CMake snippet that embeds engine sources into the target testbed. Keep all numbers testable.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Present historical growth (Priority: P1)

Release engineers need to see how total binary size evolves per commit immediately after the existing size trend summary so they can spot regressions before releases.

**Why this priority**: Without historical visibility the dashboard cannot support release go/no-go decisions, making this the critical slice.

**Independent Test**: Load the size-report dashboard with 30+ commits captured in the dataset; verify that the history line chart renders below the size trend module and displays all commits in order.

**Acceptance Scenarios**:

1. **Given** a repository with at least 10 recorded commits, **When** the size-report dashboard loads, **Then** a "History" line chart appears directly beneath the existing size trend card plotting total size per commit in chronological order with labelled axes.
2. **Given** a new commit is ingested into the size pipeline, **When** the dashboard refreshes, **Then** the chart includes the latest commit point with total size that matches the size-report dataset within ±1%.

---

### User Story 2 - Inspect commit context (Priority: P2)

Release engineers need to inspect individual commit points (size, hash, author timestamp) inside the chart to understand why the size changed.

**Why this priority**: Contextual commit insight accelerates regression triage and avoids external tooling lookups.

**Independent Test**: Click multiple history buttons and, separately, navigate with the keyboard and activate selections; confirm the tooltip panel shows commit hash, timestamp, message, and formatted size for each selection.

**Acceptance Scenarios**:

1. **Given** the history chart is visible, **When** a user clicks a history control button, **Then** the chart highlights the corresponding commit and the tooltip panel displays the commit hash, message, and total size formatted in KB or MB with one decimal place.
2. **Given** a user navigates via keyboard, **When** they press <kbd>Enter</kbd> or <kbd>Space</kbd> on a focused history button, **Then** the chart highlights that commit and the tooltip panel updates without shifting the page viewport, preserving context for assistive technologies.

---

### User Story 3 - Segment review windows (Priority: P3)

Release engineers want to switch between short (30 commits), medium (90 commits), and long (180 commits) history windows to zoom in on recent or long-term trends.

**Why this priority**: Adjustable windows help separate noise from systemic growth without exporting data.

**Independent Test**: Toggle each window control and confirm the chart redraws with the requested commit count and the selection persists for the active session.

**Acceptance Scenarios**:

1. **Given** the default window of 90 commits is active, **When** the user selects the 30-commit option, **Then** the chart redraws with the most recent 30 commits and stores that selection for subsequent dashboard visits within the session.

---

### Edge Cases

- Repository contains fewer than 5 commits: show the chart frame with a message "More history needed" and render available points without extrapolation.
- Commits missing size data (e.g., pipeline failure): skip the point, keep the last valid selection intact, and log a console warning highlighting the missing commit count.
- Data set exceeds 180 commits: decimate to the most recent 180 commits while maintaining chronological ordering and surface a truncation notice in the history message panel.

## Requirements & Memory Model *(mandatory)*

### Functional Requirements

- **FR-001**: The dashboard MUST append a "History" line chart immediately after the existing size trend component, rendering a Chart.js line series for the most recent commits in chronological order with clearly labelled axes.
- **FR-002**: History data MUST be loaded from `reports/size/index.json` and the selected folder’s `index.json`, aggregated into total artifact size per commit and sorted by commit timestamp; zero-filling is forbidden.
- **FR-003**: The chart MUST gracefully handle dataset edge cases (fewer than 5 commits, gaps, or >180 commits) by showing contextual messaging, logging warnings for skipped commits, and noting truncation without extrapolation.
- **FR-004**: The history controls MUST provide 30/90/180 commit windows, persist the selection via `sessionStorage` for the active session, and default to 90 commits when no preference exists.
- **FR-005**: Mouse clicks or keyboard activation (<kbd>Enter</kbd>/<kbd>Space</kbd>) MUST expose commit hash, localized timestamp, commit message, and total size formatted in kilobytes with one decimal precision, meeting WCAG focus visibility requirements.
- **FR-006**: The dashboard MUST record render timing via `performance.mark` / `performance.measure` with a ≤120 ms render budget and surface window selections or gaps via console logging for manual verification.

### Key Entities *(include if feature involves data)*

- **HistorySample**: Derived commit entry with fields `commitId`, `totalSizeBytes`, `committedAtEpochMs`, `label`, and `missingArtifacts` for gap detection. Metadata includes `gitSha`, `date`, `message`, and `kind`.
- **HistorySeries**: Client-side structure holding `samples[]`, `allSamples[]`, `windowMode`, `minSizeBytes`, `maxSizeBytes`, and `gaps` counts for rendering and messaging.
- **HistoryPrefs**: Session preference persisted via `sessionStorage` capturing the active `windowMode`.

### Memory Model

- **Data Structures**: `HistorySeries.samples` stores up to 180 entries (~32 bytes per sample) alongside cached metadata; total persistent footprint stays below 20 KB in browser memory.
- **Transient Scratch**: Tooltip string buffers and axis label builders reuse preallocated arrays within `history-chart.js`, releasing references after each render cycle.
- **Failure Modes**: If manifests fail to load or exceed limits, the dashboard surfaces a "History unavailable" banner, logs warnings to the console about missing commits, and falls back to displaying available points only.

## C API Surface & Embedding *(mandatory)*

### Public Headers

- `reports/size/history-chart.js`: Exports the history chart integration helpers consumed by `dashboard.js`.
- `reports/size/dashboard.js`: Existing entry point extended to hydrate history data and forward performance logs.

### Function Table

| Symbol | Purpose | Thread Safety | Notes |
|--------|---------|---------------|-------|
| `hydrateHistorySeries(manifest, folderIndex)` | Transform manifest commits into sorted `HistorySeries` samples respecting window defaults | Yes — pure data transform | Validates timestamps and aggregates artifact sizes |
| `renderHistoryChart(series, container)` | Draw Chart.js line series, labels, and edge-case messaging inside the supplied container | N/A (browser main thread) | Applies ≤120 ms render target, updates messaging panel for missing data or truncation |
| `attachHistoryControls(series, controlsRoot)` | Wire window controls, session persistence, and keyboard event handlers | N/A (browser main thread) | Persists preference via `sessionStorage` and announces changes |

### Embedding Snippet

```html
<section id="history-section" class="chart-section" aria-labelledby="history-title">
    <h2 id="history-title">Size History</h2>
    <div id="history-controls" class="history-controls"></div>
    <canvas id="history-chart" width="960" height="420"
        role="img"
        aria-label="Line chart showing total artifact size per commit"></canvas>
</section>
<script src="lib/chart.min.js"></script>
<script src="history-chart.js"></script>
<script src="dashboard.js"></script>
```

## Resource Budgets & Performance *(mandatory)*

- **Runtime Memory**: ≤ 180 samples retained in-memory alongside lightweight metadata; no additional browser storage beyond `sessionStorage` preference (~100 bytes).
- **Render Time Target**: ≤ 120 ms to hydrate and render the history chart after manifests resolve, measured via `performance.measure('history-chart-render')`.
- **CI / Validation Hooks**: Playwright or Puppeteer smoke for click/keyboard activation flows, console-log review in size-report CI artifact, and manual bundle spot-checks when assets change.

## Observability & Operations *(mandatory)*

- **Instrumentation Plan**: Capture `performance.mark('history-chart-start')` / `performance.mark('history-chart-end')`, log render-duration summaries plus missing commit notices to the console for validation, and document manual verification steps.
- **Validation Steps**: Execute automated or manual browser smoke covering window toggles and tooltip focus, review console output for warnings, and record load time samples via `reports/size/scripts/measure-history-load.js`.
- **Operational Notes**: Update the release runbook with a checklist referencing the history chart screenshot, notes on reviewing render timing logs, and guidance for tracking load-time trends during freeze weeks.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of Chromium CI dashboard loads render the history chart with all requested commits in under 2.0 seconds, measured via `performance.measure('history-chart-render')`.
- **SC-002**: Charted total size values stay within ±1% of the underlying size-report dataset across the latest 180 commits during automated verification.
- **SC-003**: During release dry-runs, 90% of participating release engineers can identify the commit responsible for a size spike in under 30 seconds using the chart alone.
- **SC-004**: Average time to resolve binary size regressions drops by 30% compared to the previous two releases, with notes captured in the release runbook’s history chart section.
