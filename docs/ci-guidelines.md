# CI Guidelines

## Size & Performance Regression Policy

1. CI workflows publish size-report and microbench artifacts for every preset.
2. If the size-report indicates a `.wasm` or native binary growth greater than **2%**:
   - Investigate the feature module responsible.
   - Evaluate whether optional diagnostics or logging can be disabled in release builds.
   - Document mitigation in the pull request description before merging.
3. Microbench regressions should remain within a ±2% window.
   - Rerun the benchmark locally using `ctest --preset <preset> -R US3_microbench_stub`.
   - Provide rationale and remediation plan when exceeding the threshold.
4. Any waiver must be co-signed by the project maintainer and tracked in the release notes.

## Artifact Retention

- Artifacts are uploaded per preset under `ci/workflows/*`.
- Retain at least the last 10 builds to compare against baselines.

## Local Validation Before Push

```bash
cmake --preset web-debug
cmake --build --preset web-debug
ctest --preset web-debug
```

Repeat for `win-debug` (from Windows) prior to opening a pull request.
