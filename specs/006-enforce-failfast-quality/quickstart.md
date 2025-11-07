# Quickstart — Fail-Fast Quality Enforcement

## 1. Configure Build Presets
1. Run `cmake --preset web-debug` (or `win-debug`) to ensure the new warning/sanitizer cache variables propagate.
2. Confirm `NT_FAILFAST_STRICT=1` and sanitizer flags appear in the configure log; release presets must show `NT_FAILFAST_STRICT=0` and no sanitizer arguments.

## 2. Apply Header-Only Policies
1. Include `engine/core/nt_engine.h` in any testbed or feature needing direct policy access.
2. Call `nt_failfast_policy_defaults()` during initialization, adjust fields if needed, and invoke `nt_failfast_apply_policy()` before starting the main loop.
3. Use `NT_FAILFAST_ASSERT(expr, "stage_label")` inside debug-only code paths if additional coverage is required; macros compile away (except logging) in release.

## 3. Verify Sandbox Runtime Behavior
1. Launch `testbeds/sandbox` via the debug preset.
2. Trigger a controlled failure (e.g., double-free) to see `NT_FAILFAST_ASSERT` logs and process termination.
3. Inspect the generated `quality-gate-report-web-debug.json` artifact locally (found under `out/web-debug/quality`).

## 4. Validate CI Outputs
1. Push a branch and observe `ci/workflows/web-debug.yml` and `win-debug.yml`.
2. Ensure each workflow publishes `quality-gate-report-${preset}.json`, size-report deltas, and sanitizer logs.
3. For release workflows, verify microbench regression ≤0.5% compared to the stored baseline artifact.

## 5. Enforce Formatting & Static Analysis
1. Run `cmake --build --preset web-debug --target format-check clang-tidy` before opening a PR.
2. Resolve any zero-diff formatting or static analysis failures locally to keep CI green.
