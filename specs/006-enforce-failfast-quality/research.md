# Research Findings — Fail-Fast Quality Enforcement

## CI Workflow Placement for Quality Gate Report

- **Decision**: Integrate the quality gate aggregation steps into the existing `ci/workflows/web-debug.yml` and `ci/workflows/win-debug.yml`, invoking a shared script (`ci/scripts/quality-gate-report.sh`) so both toolchains emit identical artifacts without introducing a new workflow file.
- **Rationale**: Keeping enforcement beside the preset-specific builds ensures warnings, sanitizers, and analysis gates fail immediately within the jobs that already compile/test the code. It avoids duplicating checkout/configure work while guaranteeing that both primary platforms publish reports every run.
- **Alternatives considered**: (a) A separate `quality.yml` workflow—rejected because it would rerun expensive builds and risk drifting from preset configurations. (b) Embedding the logic in release workflows—rejected since sanitizers/analysis are debug-only and would slow optimized builds unnecessarily.

## Quality Gate Report Schema

- **Decision**: Publish a JSON artifact named `quality-gate-report-${preset}.json` containing top-level sections: `compiler_flags`, `sanitizer_matrix`, `static_analysis`, `formatting`, `binary_budget`, and `memory_policy`, each with pass/fail booleans plus counts and deltas.
- **Rationale**: A structured JSON makes it easy to diff between runs, feed downstream dashboards, and prove compliance during audits. Aligning section names with spec requirements (flags, sanitizers, static analysis, formatting, memory/binary metrics) keeps scope obvious and enables automated gating.
- **Alternatives considered**: (a) Markdown summary—reject due to poor machine readability. (b) Multiple artifacts (one per section)—reject to avoid scatter and simplify retention policies.

## Release Microbench Baseline

- **Decision**: Use the latest green `main` branch release artifact (tagged `release/<date>`) as the canonical baseline; record its `qa_failfast_policy_microbench` median frame time and treat future release builds as regressions if they exceed +0.5% over that stored value.
- **Rationale**: Anchoring to the most recent certified release keeps comparisons realistic while reflecting current hardware/toolchain behavior. Using median microbench data avoids outliers and aligns with existing CI metrics.
- **Alternatives considered**: (a) Hard-coding an absolute ms target—reject because hardware/toolchain drifts make static limits brittle. (b) Comparing to the immediate previous commit—reject since short-term noise could trigger failures despite acceptable long-term performance.

## Warning-as-Error Flag Propagation (clang-cl + emcc)

- **Decision**: Centralize warning flags in preset-level CMake cache entries that expand to `/Wall /WX /permissive-` for clang-cl and `-Wall -Wextra -Wpedantic -Werror -fno-common` for emcc, ensuring `target_compile_options` inherits them via interface properties.
- **Rationale**: Using preset cache variables keeps flag lists synchronized across engine, testbeds, and tools while preventing duplication. Interface propagation ensures any new target automatically inherits the zero-warning policy.
- **Alternatives considered**: (a) Setting flags per target manually—reject due to maintenance burden. (b) Using `add_compile_options` globally—reject because it would also apply to third-party directories that need relaxed flags.

## Sanitizer Enablement Best Practices

- **Decision**: Enable ASan+UBSan only on debug presets, add `-fsanitize=address,undefined -fno-omit-frame-pointer` (and `-s ERROR_ON_UNDEFINED_SYMBOLS=1` for emcc) while ensuring release presets explicitly clear sanitizer flags and define `NT_FAILFAST_STRICT=0`.
- **Rationale**: This mirrors industry standard fail-fast setups: debug builds catch UB immediately, release builds stay lean. Explicitly clearing sanitizer flags avoids accidental propagation and provides deterministic performance.
- **Alternatives considered**: (a) Leaving sanitizers on for release—reject due to performance and binary size penalties. (b) Relying solely on runtime asserts—reject because many memory bugs would slip past compile time.

## CI Artifact Retention Pattern

- **Decision**: Store `quality-gate-report-*.json` alongside existing size-report artifacts, retaining the last 30 runs per workflow; include metadata (commit, preset, timestamps) so audits can trace enforcement history.
- **Rationale**: Co-locating artifacts simplifies governance reviews and leverages existing retention policies. Limiting to 30 runs balances traceability with storage costs.
- **Alternatives considered**: (a) Infinite retention—reject for cost and clutter. (b) Storing only the latest run—reject because auditors need historical proof of compliance trends.
