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
4. Inspect `report.txt` to confirm the HEAD metadata row includes the latest commit SHA and current branch name. Prior commits remain beneath the HEAD block as `HISTORY` entries; only the HEAD block is rewritten on subsequent runs.
5. Commit updated `report.txt`, per-folder `index.json`, and the root manifest as needed.

## Review Dashboard

1. Open `reports/size/report.html` (Chart.js loads from `reports/size/lib/chart.min.js`).
2. Use the folder selector to choose a sandbox configuration, then pick any two recorded commits from the dropdowns (HEAD vs. history, branch snapshots, or accepted baselines). The metadata, table, and chart refresh instantly, with alert badges highlighting threshold breaches.

## Updating MASTER Baselines

Use baseline updates only after size regressions are approved. Accepting a baseline adds a `MASTER` entry in addition to the standard HEAD and history rows.

1. Ensure the branch containing the new baseline is merged into `master`.
2. Execute `python reports/size/update.py --input output/sandbox/wasm/debug --output sandbox/wasm/debug --accept-master <commit-sha>`.
3. Verify that the MASTER rows now point to the accepted commit (SHA + message).
4. Document the change in release notes and rerun the dashboard to confirm clean state.

## CI Integration

- CI should invoke `reports/size/update.py` after sandbox builds.
- Upload `report.txt`, `index.json`, and `report.html` as artifacts.
- Fail the pipeline if alerts are emitted without acknowledged mitigation.

## Troubleshooting

- Missing MASTER row: This is expected unless a baseline is accepted. Rerun with `--accept-master <commit-sha>` after approval to promote a commit.
- Missing artifacts: Rebuild the sandbox output or adjust the tracked file list.
- Chart rendering issues: Confirm `lib/chart.min.js` ships alongside `report.html`.
- Git metadata errors: Verify the repository has the required commits locally and that the specified ref exists.
