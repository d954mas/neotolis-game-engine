# Size Reporting Workflow

This directory contains size-reporting assets for Speckit sandbox builds. Use the included tooling to capture reproducible HEAD snapshots, keep prior commits as historical records, and produce dashboards for review. MASTER baselines are optional and only written when explicitly accepted.

## Directory Layout

- `report.html` – reviewer dashboard (loads Chart.js from `lib/chart.min.js`).
- `lib/chart.min.js` – bundled charting library.
- `update.py` – CLI workflow for regenerating reports (implemented in User Story 1).
- `sandbox/wasm/<configuration>/report.txt` – CSV snapshots for each tracked build variant (one metadata row per commit followed by artifact rows; previous commits remain intact and only the HEAD block is rewritten).
- `index.json` – Root manifest listing available folders and the relative path to each folder-specific index.
- `sandbox/<path>/index.json` – Per-folder commit manifest with artifact sizes for every recorded snapshot.

## Refreshing HEAD Snapshots

1. Build the desired sandbox target (e.g., `sandbox-wasm-debug`).
2. Run `python reports/size/update.py --input output/sandbox/wasm/debug --output sandbox/wasm/debug` (adjust the `--input` path to match your build artifacts). The `--output` directory must live under `reports/size` and will be created if it does not exist.
3. Review CLI output for threshold alerts (>2% or >25 KB deltas).
4. Inspect `report.txt` to confirm the HEAD metadata row includes the latest commit SHA and subject. When the working tree has no outstanding changes outside `reports/`, a companion `BRANCH` row preserves the active branch name. Only HEAD (and optional BRANCH) rows are maintained; previous HEAD data is not retained once rewritten.
5. Commit updated `report.txt`, per-folder `index.json`, and the root manifest as needed.

> Legacy CSV headers (pre-BRANCH/HEAD format) are no longer supported; rerun the CLI to regenerate any older reports before use.

## Review Dashboard

1. Open `reports/size/report.html` (Chart.js loads from `reports/size/lib/chart.min.js`).
2. Use the folder selector to choose a sandbox configuration, then pick any two recorded commits from the dropdowns (HEAD vs. history, branch snapshots, or accepted baselines). The metadata, table, and chart refresh instantly, with alert badges highlighting threshold breaches.

## History Chart Development Workflow

The `/specs/004-add-history-chart/` specification adds a history line chart rendered entirely in the browser. Use the following workflow while iterating:

1. **Serve the dashboard locally** – From `reports/size/`, run `python -m http.server 8000` (or `npx serve .`) so `report.html` can load `index.json` without CORS issues. Open `http://localhost:8000/report.html` and watch the browser console for history chart logs.
2. **Validate manifest shape** – Run `python3 -m jsonschema -i sandbox/wasm/release/index.json ../specs/004-add-history-chart/contracts/history-data.schema.json` (adjust the manifest path as needed) to confirm commit entries remain compatible with the chart loader.
3. **Inspect console instrumentation** – The history module emits `performance.mark` / `performance.measure` entries and logs window selections plus missing commit gaps. Confirm these logs appear while toggling commit windows or loading data sets with known gaps.
4. **Measure render timing** – Use the browser Performance panel or call `performance.measure('history-chart-render')` in the devtools console to ensure the chart hydrates within the ≤120 ms target defined in the spec. Alternatively, run `node reports/size/scripts/measure-history-load.js http://localhost:8000/report.html` (requires Playwright) to capture render timing automatically.
5. **UX verification checklist** – Hover and press <kbd>Tab</kbd> to move focus into the history controls, then use <kbd>Arrow</kbd> keys / <kbd>Home</kbd> / <kbd>End</kbd> to cycle through commits. Confirm each point announces commit hash, localized timestamp, and KB size, that focus rings meet WCAG contrast requirements, and that the “More history needed” banner appears when fewer than five commits are available.
6. **Window persistence regression checklist**
   - Select a window option (30/90/180 commits), reload the page in the same tab, and verify the selection persists.
   - Open a second tab pointing to `report.html`; confirm the stored window mode applies there as well.
   - Clear session storage (or close the browser session) and ensure the dashboard falls back to the default 90-commit view.

## Updating MASTER Baselines

Use baseline updates only after size regressions are approved. Accepting a baseline adds a `MASTER` entry in addition to the standard HEAD and history rows.

1. Ensure the branch containing the new baseline is merged into `master`.
2. Execute `python reports/size/update.py --input output/sandbox/wasm/debug --output sandbox/wasm/debug --accept-master <commit-sha>`.
3. Verify that the MASTER rows now point to the accepted commit (SHA + message).
4. Document the change in release notes and rerun the dashboard to confirm clean state.

## Release Runbook Notes

- [ ] Capture and archive a screenshot of the history chart after the final baseline update for release sign-off.
- [ ] Run `node reports/size/scripts/measure-history-load.js <deployed-dashboard-url>` to record render duration, sample count, and gaps before approving the release.
- [ ] Review deployment logs for `history-chart: render complete` and `history-chart: window selection change` entries to ensure instrumentation remains active.
- [ ] Reset the history window to the default 90-commit view after validation so reviewers see the expected range on initial load.

## CI Integration

- CI should invoke `reports/size/update.py` after sandbox builds.
- Upload `report.txt`, `index.json`, and `report.html` as artifacts.
- Fail the pipeline if alerts are emitted without acknowledged mitigation.

## Troubleshooting

- Missing MASTER row: This is expected unless a baseline is accepted. Rerun with `--accept-master <commit-sha>` after approval to promote a commit.
- Missing artifacts: Rebuild the sandbox output or adjust the tracked file list.
- Chart rendering issues: Confirm `lib/chart.min.js` ships alongside `report.html`.
- Git metadata errors: Verify the repository has the required commits locally and that the specified ref exists.
