# Quickstart — Size Reporting Dashboard

1. **Build sandbox artifacts**
   - Run the standard CMake preset to produce `sandbox/wasm/{debug,release}` artifacts.
   - Confirm `.wasm`, `.js`, and `index.html` exist before running the CLI.

2. **Update HEAD snapshot**
   - Execute `python3 reports/size/update.py --folder sandbox/wasm/debug` (repeat for `sandbox/wasm/release`).
   - The CLI prints per-artifact size measurements plus alert thresholds (`percent>2`, `bytes>25000`) after regenerating `index.json`.
   - `report.txt` now keeps a compact metadata row per commit; the latest HEAD block is rewritten while prior commits remain for historical comparison.

3. **Verify instrumentation**
   - Run `python3 tests/size/scripts/verify_size_report.py`.
   - The script provisions a temporary dataset and fails if CLI logs omit measured sizes or alert markers.

4. **Review dashboard**
   - Open `reports/size/report.html` (Chart.js loads from `reports/size/lib/chart.min.js`).
   - Use the folder selector to hop between sandbox configurations; table + chart highlight alerts inline.

5. **Refresh MASTER baseline (release acceptance only)**
   - After approval, run `python3 reports/size/update.py --folder <folder> --accept-master <commit-sha>` to promote HEAD to MASTER.
   - Document the baseline change in `reports/size/README.md` per runbook guidance.

6. **CI integration**
   - Build workflows (`ci/workflows/web-debug.yml`, `ci/workflows/web-release.yml`, `ci/workflows/win-debug.yml`, `ci/workflows/win-release.yml`) now run `reports/size/update.py` for debug and release folders in parallel immediately after each build, keeping `index.json` and `report.txt` fresh.
   - The dedicated `ci/workflows/size-report.yml` workflow still runs on pushes to `003-add-size-reports` to provide a focused artifact upload (`size-report-dashboard`). Pipelines should fail if new alerts appear without mitigation notes.
