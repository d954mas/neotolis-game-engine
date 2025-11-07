# Feature Specification: Web Demo & Reports Portal

**Feature Branch**: `[005-publish-web-report]`  
**Created**: 2025-11-06  
**Status**: Draft  
**Input**: User description: "Create web page with examples and build report. Use github pages as hosting. index.html should have links to -sandbox -neotoilis-engine-report Use github actions ci. After update-size-reports task. Update web page for engine."

> Speckit specs MUST describe the C API, memory model, binary and RAM impact, microbench targets, and the CMake snippet that embeds engine sources into the target testbed. Keep all numbers testable.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Access Latest Web Demo (Priority: P1)

Stakeholders open the published portal landing page to explore the interactive sandbox and review the latest engine build report without pulling the repository.

**Why this priority**: Surfacing current demos and reports externally is the core reason for creating the web page, enabling fast validation and feedback.

**Independent Test**: Can be fully tested by visiting the published GitHub Pages URL after a successful pipeline run and verifying both primary links work end-to-end.

**Acceptance Scenarios**:

1. **Given** the latest `main` branch pipeline finished successfully, **When** a stakeholder opens `index.html`, **Then** the page shows clearly labeled links to the sandbox demo and the engine build report.
2. **Given** the stakeholder is on a mobile viewport (≤768 px width), **When** they tap the sandbox or report link, **Then** the destination opens and renders usable content without layout breakage.

---

### User Story 2 - Automated Publishing After Size Reports (Priority: P2)

The release engineer relies on automation so that the portal updates only when build size data is current, avoiding stale or inconsistent reports.

**Why this priority**: Publishing outdated data is a reputational risk; tying the site to the size-report stage safeguards accuracy.

**Independent Test**: Can be fully tested by triggering the CI pipeline, forcing `update-size-reports`, and confirming the portal deployment happens only after that job succeeds.

**Acceptance Scenarios**:

1. **Given** the `update-size-reports` task fails, **When** the pipeline finishes, **Then** the portal is not redeployed and the previous version remains live.

---

### User Story 3 - Review Build Metrics Snapshot (Priority: P3)

Product leadership reviews high-level binary size and performance trends from the report without downloading raw artifacts.

**Why this priority**: Enables data-driven decisions about feature scope and ensures the engine stays within platform limits.

**Independent Test**: Can be fully tested by opening the build report page and confirming required size, performance, and commit metadata are visible for the latest release.

**Acceptance Scenarios**:

1. **Given** a new release commit is merged to `main`, **When** the report page loads, **Then** it shows the matching commit hash, build timestamp, and binary size deltas for WebAssembly.

### Edge Cases

- Missing artifact: pipeline completes but sandbox `.wasm` asset is not produced; the portal must surface a clear unavailable-state message rather than a broken link.
- Cache staleness: GitHub Pages serves an older version; the portal must display the CI run timestamp so viewers can detect staleness.
- Partial publish: sandbox succeeds but report build fails; deployment must block to avoid mixed-content release.

## Requirements & Memory Model *(mandatory)*

### Functional Requirements

- **FR-001**: The landing page MUST present hero copy, a “Try the Sandbox” link, and an “Engine Build Report” link above the fold, each verified to return HTTP 200 on publish.
- **FR-002**: The portal MUST host the latest sandbox experience by copying the WebAssembly bundle generated from the `testbeds/sandbox` preset artifact in CI and enforcing a ≤200 KB compressed payload so the bundle remains within the established 3-second load budget on a 25 Mbps connection (no additional runtime measurement required).
- **FR-003**: The portal MUST embed the most recent size and performance summary by staging the full contents of the `reports/size` artifact (HTML, CSS, JS, JSON) produced during `update-size-reports`, including commit hash, build timestamp, and binary delta in kilobytes.
- **FR-004**: GitHub Pages deployment MUST be triggered only after both the sandbox build job and `update-size-reports` succeed in the CI pipeline; earlier failures MUST halt publication.
- **FR-005**: The site content MUST be rebuilt on every `main` branch merge and expose a footer timestamp sourced from CI run metadata to signal freshness.
- **FR-006**: The publishing workflow MUST verify sandbox and size report artifacts via checksum comparison before copying them into the GitHub Pages staging directory.
- **FR-007**: The deployment job MUST fail with a descriptive error if required artifacts are missing or older than the triggering commit.
- **FR-008**: Static HTML, CSS, and JSON assets for the portal MUST not exceed a combined 150 KB gzip size to stay within the GitHub Pages budget.

### Key Entities *(include if feature involves data)*

- **CI Artifact Record**: Describes a published asset (sandbox bundle or size report) with attributes `artifact_name`, `checksum`, `byte_size`, `commit_hash`, and `generated_at`.
- **Build Summary**: Aggregated size/performance data (WebAssembly binary delta, compressed size, CPU microbench median) associated with a `commit_hash`.

### Memory Model

- **Allocator**: No new engine allocators introduced; feature relies solely on CI-staged static files.
- **Persistent Buffers**: None required; engine binaries remain unchanged.
- **Transient Scratch**: Not applicable; portal generation runs in CI environment.
- **Failure Modes**: Publication aborts if artifact validation fails; engine runtime continues unaffected.

## C API Surface & Embedding *(mandatory)*

### Public Headers

- No new public headers introduced; engine API surface remains unchanged.

### Function Table

| Symbol | Purpose | Thread Safety | Notes |
|--------|---------|---------------|-------|
| _No new symbols_ | Portal consumes CI artifacts only; engine API unchanged | — | Zero binary impact |

### Embedding Snippet

```cmake
# Portal publication uses CI artifacts; no additional engine sources need embedding.
# Ensure sandbox preset remains available for CI packaging.
```

## Resource Budgets & Performance *(mandatory)*

- **Binary Size Delta**: 0 KB (engine binaries untouched; portal assets hosted separately).
- **Per-Feature Budget**: Portal static bundle ≤150 KB gzip — validated via artifact size check in CI.
- **Runtime RAM**: 0 bytes additional engine RAM; static site served from GitHub Pages.
- **CPU/Frame Time Target**: Portal sandbox launch latency ≤0.05 ms CPU overhead beyond current microbench when hosted from GitHub Pages cache.
- **CI Hooks**: `update-size-reports`, `web-sandbox-build`, `publish-web-portal` (new GitHub Pages deploy job consuming artifacts).
- **Mitigations**: If artifact sizes exceed budget or latency thresholds regress >2%, block deployment and notify release engineer for corrective action.

## Observability & Operations *(mandatory)*

- **Instrumentation Plan**: CI must expose artifact metadata (checksums, sizes, commit hash), binary size tables, and microbench timings as downloadable artifacts; GitHub Pages deployment step records status to build annotations and logs the elapsed time between `update-size-reports` completion and portal deployment for SC-001 monitoring.
- **Failure Diagnostics**: Portal publish workflow MUST emit descriptive failure annotations (artifacts missing, checksum mismatch, or stale timestamps) so operators can triage within the GitHub Actions UI.
- **Validation Steps**: `ctest --preset web-debug` ensures sandbox bundle passes existing tests; `update-size-reports` confirms binary deltas; a post-deploy smoke test requests `index.html`, sandbox, and report URLs to ensure HTTP 200 responses and checksum matches.
- **Operational Notes**: On-call checklist updated to include “Verify portal updated” item after each release; if deployment is blocked, fallback is to leave the previous site version live and note the issue in the release summary.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of successful `main` branch pipelines publish a portal update within 10 minutes of `update-size-reports` completion.
- **SC-002**: Portal bundle size remains ≤150 KB gzip and sandbox payload remains ≤200 KB gzip, providing calculated headroom for ≤3-second first contentful paint on a 25 Mbps connection without additional runtime measurement.
- **SC-003**: 0 broken links detected by weekly link checker scans across the sandbox and build report pages.
- **SC-004**: Stakeholder surveys report ≥80% satisfaction with the clarity of build metrics within two sprints of launch.

## Assumptions

- GitHub Pages is configured on the `gh-pages` branch with permissions to deploy from CI without manual approval.
- `update-size-reports` publishes the `reports/size` folder contents as a downloadable artifact every run.
- Sandbox artifacts remain under 200 KB compressed, allowing direct hosting without CDN offloading.
