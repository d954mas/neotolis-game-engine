# Manual Verification Checklist — Size Reporting Dashboard

## Scenario: Default Folder Visualization (sandbox/wasm/debug)

1. Run `python reports/size/update.py --folder sandbox/wasm/debug` to refresh manifest data.
2. Open `reports/size/report.html` in a desktop browser with local file access enabled.
3. Confirm the summary section shows the HEAD commit SHA/message from `index.json`.
4. Inspect the artifact table and verify:
   - All tracked files (index.html, sandbox.js, sandbox.wasm) appear with accurate sizes.
   - Delta columns display byte and percentage differences.
   - Rows with alerts (>2% or >25 KB) include a visual badge.
5. Observe the chart rendering:
   - HEAD and MASTER bars display side-by-side for each artifact.
   - Tooltip or legend identifies HEAD vs MASTER datasets.
6. Note any console errors; the page must load without JavaScript failures.

## Scenario: Alert Styling

1. Modify `reports/size/index.json` temporarily so one artifact has `alert: true`.
2. Reload the dashboard.
3. Confirm the corresponding table row has alert styling (e.g., red badge) and the chart emphasizes the alert (different color or annotation).
4. Revert the JSON changes after validation.

## Scenario: Manifest Refresh Logging

1. From terminal, run `python reports/size/update.py --folder sandbox/wasm/debug`.
2. Confirm console output includes the HEAD commit SHA and message.
3. Refresh the dashboard and ensure the updated metadata appears without caching issues.

Record findings and attach screenshots when anomalies occur.

## Scenario: Folder Switching

1. Run the update script for both debug and release folders:
   - `python reports/size/update.py --folder sandbox/wasm/debug`
   - `python reports/size/update.py --folder sandbox/wasm/release`
2. Load `reports/size/report.html` and note the default folder selection.
3. Change the folder selector to the alternate entry.
4. Confirm the summary and table update within two seconds (use a stopwatch if needed).
5. Verify the chart redraws with the new artifact sizes and commit metadata.
6. Switch back to the original folder and confirm data reverts accordingly.
