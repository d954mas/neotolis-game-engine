# Size Budget Baseline

| Preset      | Target Budget | Notes |
|-------------|---------------|-------|
| web-debug   | ≤ 200 KB wasm | Monitor size-report output; investigate growth > 2%. |
| web-release | ≤ 200 KB wasm | Treat increases with highest priority. |
| win-debug   | ≤ 500 KB binary | Debug symbols inflate size; acceptable if release stays within limits. |
| win-release | ≤ 300 KB binary | Ensure `/GL` and `/LTCG` remain enabled. |

## Procedure

1. Run `ctest --preset <preset> -R US3_size_report` to regenerate the size-report.
2. Compare against previous artifact uploaded by CI.
3. Document variance in the pull request body and update this table if budgets change.
