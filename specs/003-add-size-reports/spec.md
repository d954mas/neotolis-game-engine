# Feature Specification: Size Reporting Dashboard

**Feature Branch**: `003-add-size-reports`  
**Created**: 2025-11-05  
**Status**: Draft  
**Input**: User description: "1)create a folder reports/size 2)For example reports/size/sandbox/wasm/debug will have report.txt 3)File use csv format. git-sha(sha from master and head(current state), file_name, size HEAD sandbox.wasm 190000 index.html 1000005)Create script to update that file(replace head with current state, keep sha) 6)Make reports/size/report.html to show report table and graph for visual review should show all folders to choose(sandbox/wasm/debug, sandbox/wasm/release) when select folder show table and graph of files"

> Speckit specs MUST describe the C API, memory model, binary and RAM impact, microbench targets, and the CMake snippet that embeds engine sources into the target testbed. Keep all numbers testable.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Capture build size snapshot (Priority: P1)

Build engineers need a repeatable way to record the current build artifact sizes for each sandbox target so they can detect regressions before releasing.

**Why this priority**: Without a baseline snapshot, downstream reviews and CI size gates cannot operate, making this the foundational capability.

**Independent Test**: Run the size-report update workflow for a single folder (e.g., sandbox/wasm/debug) and verify that a CSV-formatted `report.txt` is created/updated with current HEAD data while preserving the MASTER baseline row.

**Acceptance Scenarios**:

1. **Given** a built sandbox/wasm/debug output and an existing MASTER row, **When** the engineer runs the size-report update workflow, **Then** the HEAD row is replaced with the latest commit SHA and measured sizes for every tracked artifact.
2. **Given** no existing report file for a tracked folder, **When** the engineer runs the size-report update workflow, **Then** a new CSV-formatted `report.txt` is created with a HEAD row and a placeholder MASTER row recorded as unavailable.

---

### User Story 2 - Compare HEAD to MASTER visually (Priority: P2)

Release reviewers want to understand whether the current branch increases binary size relative to the MASTER baseline without digging through raw CSV files.

**Why this priority**: Visual confirmation reduces the risk of shipping oversized builds and speeds up release reviews.

**Independent Test**: Open `reports/size/report.html`, select a tracked folder, and confirm that the table and graph highlight size deltas between HEAD and MASTER for each artifact.

**Acceptance Scenarios**:

1. **Given** HEAD sizes that exceed MASTER by more than 2%, **When** the reviewer selects the folder in the HTML report, **Then** the interface flags the affected files visually (e.g., badge or color) and lists the precise delta.

---

### User Story 3 - Review historical folders (Priority: P3)

Tooling owners need to switch between multiple tracked sandbox folders (e.g., wasm debug vs. wasm release) from a single entry point to avoid duplicated dashboards.

**Why this priority**: Central navigation reduces upkeep and ensures consistent review practices across configurations.

**Independent Test**: From `reports/size/report.html`, switch between sandbox/wasm/debug and sandbox/wasm/release and confirm each selection loads the correct CSV dataset without page reload errors.

**Acceptance Scenarios**:

1. **Given** multiple tracked folder datasets exist, **When** the reviewer changes the folder selection, **Then** the table and graph refresh with the new dataset within two seconds and no stale data is shown.

### Edge Cases

- Missing baseline: Document how the workflow behaves when MASTER commit data is unavailable (e.g., first-time recording or detached baseline).
- Artifact mismatch: Specify behavior when a tracked artifact is absent in the working directory (skip vs. error).
- Commit resolution: Define fallback when the repository cannot resolve the referenced master branch (e.g., offline environment).

## Requirements & Memory Model *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST include a `reports/size/<testbed>/<platform>/<configuration>/report.txt` file for each tracked sandbox variant, containing CSV rows with the schema `git_ref,file_name,size_bytes,git_sha,git_message`.
- **FR-002**: Each CSV MUST maintain one `MASTER` row representing the latest baseline commit SHA from the default branch and one `HEAD` row representing the current working commit SHA and commit message (summary line); additional historical rows MAY be appended but MUST preserve the latest HEAD replacement behavior and MUST populate both `git_sha` and `git_message`.
- **FR-003**: A documented CLI workflow (`reports/size/update` script or equivalent entry point) MUST regenerate the HEAD row by measuring current artifact sizes and replace only the HEAD row while leaving MASTER untouched.
- **FR-004**: The workflow MUST surface validation failures (missing artifacts, unreadable reports, unstaged changes preventing measurement) via a non-zero exit code and human-readable message.
- **FR-005**: `reports/size/report.html` MUST enumerate all folders under `reports/size/**/report.txt`, allow the reviewer to select one, and render both a sortable table of file sizes and a graph (trend or bar) comparing HEAD vs. MASTER for every artifact using a maintained third-party charting library (e.g., Chart.js bundled under `reports/size/lib/`).
- **FR-006**: Visualizations MUST flag any artifact whose HEAD size exceeds MASTER by >2% or >25 KB, whichever is larger, and display the absolute delta; the selected charting library MUST support annotated thresholds.
- **FR-007**: Documentation within the spec folder MUST explain how to update MASTER baselines manually (e.g., when a new release is accepted) without corrupting historical data.

### Key Entities *(include if feature involves data)*

- **SizeReportSnapshot**: Aggregates artifact size records for a specific `<testbed>/<platform>/<configuration>` triplet; attributes include `folder_id`, `master_sha`, `head_sha`, `artifacts[]`, `last_updated`.
- **SizeReportRecord**: Represents a single artifact entry with `file_name`, `size_bytes`, `git_ref`, and `delta_vs_master`; belongs to exactly one `SizeReportSnapshot`.

### Memory Model

- **Allocator**: No new engine runtime allocator usage; reporting workflows operate as tooling with ≤1 MB heap usage during CSV parsing/generation.
- **Persistent Buffers**: None added to the engine binary; artifacts are stored as text files in `reports/size`.
- **Transient Scratch**: Tooling may allocate transient buffers up to 256 KB when loading CSV data; lifetime is limited to the execution of the update or visualization pipeline.
- **Failure Modes**: If CSV parsing exceeds memory limits or files are missing, the workflow MUST abort and report the failure without leaving partial files on disk.

## C API Surface & Embedding *(mandatory)*

### Public Headers

- No new public headers are introduced; existing engine runtime APIs remain unchanged because the feature delivers offline reporting.

### Function Table

| Symbol | Purpose | Thread Safety | Notes |
|--------|---------|---------------|-------|
| _None_ | Reporting occurs entirely outside the runtime; no new `nt_` symbols are exported. | Not applicable | Guarantees zero impact on shipped binaries. |

### Embedding Snippet

```cmake
# Size reporting integrates as a post-build workflow.
add_custom_target(<variant>_size_report
    COMMAND <size-report-command> --folder <sandbox/wasm/debug>
    WORKING_DIRECTORY <repo-root>
    COMMENT "Update size report for <variant>"
)
add_dependencies(<variant>_size_report <variant_build_target>)
```

## Resource Budgets & Performance *(mandatory)*

- **Binary Size Delta**: 0 KB — the reporting assets are not compiled into shipped binaries; they remain as repository artifacts to keep `.wasm` ≤ 200 KB.
- **Per-Feature Budget**: Repository tooling may include a third-party charting bundle (e.g., Chart.js minified ≈ 70 KB) stored under `reports/size/lib/`; no limit is imposed on dashboard asset size so long as compiled engine binaries remain within constitutional budgets.
- **Runtime RAM**: 0 bytes — no runtime allocations are introduced; all processing happens during tooling execution.
- **CPU/Frame Time Target**: Not applicable to runtime; update workflow must finish in <10 seconds for a folder containing ≤25 artifacts on a CI agent with 2 vCPUs.
- **CI Hooks**: Add a `size-report` CI step that runs the update workflow for sandbox wasm debug/release and uploads the CSV + HTML artifacts.
- **Mitigations**: If HEAD sizes exceed MASTER thresholds, the workflow MUST fail and instruct engineers to reduce asset size or accept a baseline update following documented approval.

## Observability & Operations *(mandatory)*

- **Instrumentation Plan**: The update workflow MUST log the measured size for each artifact, the delta vs. MASTER, and the commit SHA values. CI MUST capture these logs and publish the updated CSV/HTML as artifacts for downstream review.
- **Validation Steps**: QA MUST (1) run the update workflow locally, (2) verify the CSV diff includes the expected HEAD SHA and size deltas, and (3) open `report.html` in a browser to confirm table, graph, and folder selector behaviors. CI validation MUST re-run these steps headlessly and archive the outputs.
- **Operational Notes**: The release runbook MUST include instructions for refreshing the MASTER baseline after release acceptance and guidance for resolving missing baseline data (e.g., rerun workflow once the master branch SHA is accessible). Assumes the default branch is named `master`; if renamed, update the labeling convention to match.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of tracked sandbox folders produce a HEAD vs. MASTER CSV snapshot whenever the update workflow runs.
- **SC-002**: Reviewers can open the HTML report and switch folders with updated data in ≤2 seconds on a standard developer laptop.
- **SC-003**: Any artifact exceeding the >2% or >25 KB growth threshold is clearly flagged in both CSV log output and the HTML visualization in 100% of test runs.
- **SC-004**: Release reviews confirm binary size compliance in under 5 minutes, reducing manual file-inspection time by at least 50% compared to pre-feature baselines.
