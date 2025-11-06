# Quickstart — Size Report History Chart

1. **Serve the dashboard locally**
   - From `reports/size/`, run `python -m http.server 8000` (or `npx serve .`) so `report.html` can fetch `index.json` without CORS issues.
   - Open `http://localhost:8000/report.html` in your browser to verify baseline behavior before changes.

2. **Create the history chart module**
   - Add `reports/size/history-chart.js` exporting helpers: `hydrateHistorySeries(manifest, folderIndex)`, `renderHistoryChart(series, container)`, and `attachHistoryControls()`.
   - Reference the new module from `report.html` (after `dashboard.js`) using `<script type="module" src="history-chart.js"></script>`.

3. **Wire data ingestion**
   - Update `dashboard.js` to: fetch `index.json`, resolve the selected folder’s `index.json`, transform commits into aggregated totals, and pass data to `history-chart.js`.
   - Validate folder datasets against `contracts/history-data.schema.json` during development (e.g., `npx ajv validate -s contracts/history-data.schema.json -d reports/size/sandbox/wasm/release/index.json`).

4. **Render the chart UI**
   - Insert a new section in `report.html` immediately after the size trend canvas containing the history chart container and window controls (30/90/180 commits).
   - Use the existing Chart.js library to plot totals; ensure tooltip + keyboard focus report commit hash, localized timestamp, and formatted KB size.

5. **Persist window preference**
   - Store the active window in `sessionStorage` (`historyWindow` key) using the dashboard’s preference helper; default to 90 commits if unset.
   - Restore the persisted selection on load and announce the change via `aria-live` region for accessibility.

6. **Verify performance targets**
   - Use browser devtools Performance tab to confirm the chart renders within 120 ms after `index.json` resolves; log timing via `performance.mark`.

7. **Instrumentation and smoke checks**
   - Verify `performance.mark` / `performance.measure` output and console logs for window selections, missing commits, and render duration.
   - Add a Playwright/Puppeteer smoke script (or manual checklist) covering window switching, tooltip info, keyboard navigation, and session persistence.

8. **Manual UX verification**
   - Test in Chromium and Firefox: hover and keyboard focus should expose identical details; ensure the chart announces updates via accessible name/description.
   - Toggle between 30/90/180 windows; confirm the chart transitions smoothly, selection persists within the session, and gap handling shows dashed segments when commits missing.
