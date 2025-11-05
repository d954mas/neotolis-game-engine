# Phase 0 Research — Size Reporting Dashboard

## Research Tasks Process

- Investigated outstanding unknowns from Technical Context.
- Reviewed repository constraints and spec requirements to ground decisions without adding new dependencies.
- Chose defaults that satisfy binary, memory, and CI expectations while minimizing cross-platform risk.

## Findings

### Decision: Use Python 3 CLI for `reports/size/update`
- **Rationale**: Python 3 is available on CI runners and developer environments already used for Speckit tooling, provides cross-platform file sizing (`os.stat`) and Git integration via `subprocess`, and simplifies CSV handling without external packages.
- **Alternatives Considered**:
  - **Bash + coreutils**: Lightweight but fragile on Windows and requires per-platform commands for file sizing; rejected to keep tooling portable.
  - **Node.js script**: Adds heavier runtime requirement not currently standard in the repo; unnecessary for CSV manipulation.

### Decision: Bundle Chart.js for dashboard visualizations
- **Rationale**: Chart.js offers proven, accessible chart components with annotation plugins, reducing custom code risk while aligning with the updated requirement allowing third-party libraries. Minified bundle can ship under `reports/size/lib/` without affecting engine binaries.
- **Alternatives Considered**:
  - **Vanilla `<canvas>` implementation**: Lightweight but requires bespoke rendering and interaction code; rejected to keep focus on size-report functionality.
  - **D3.js**: Powerful but larger footprint and steeper learning curve; Chart.js hits sweet spot between capability and complexity.

### Decision: Support cross-platform invocation but treat Windows CI as optional
- **Rationale**: Primary CI runners are Linux-based; tooling must run there. Windows support is desired locally but not a hard CI requirement. Documented quickstart will note PowerShell usage and Windows-friendly path handling.
- **Alternatives Considered**:
  - **Mandate Windows CI parity**: Adds maintenance overhead with limited benefit because size reports read generated WebAssembly artifacts; no dedicated Windows CI step needed.
  - **Ignore Windows compatibility**: Risky for developer workflows; rejected in favor of handling Windows path separators in Python script.
