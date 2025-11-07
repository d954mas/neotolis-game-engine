# Data Model — Publish Web Demo & Reports Portal

## Overview
Portal generation consumes artifacts produced by existing CI jobs and surfaces metadata on a static landing page. No new engine runtime structures are introduced; all data lives in CI manifests and the generated HTML.

## Entities

### PortalPage
- **Description**: Landing page metadata assembled during CI.
- **Fields**:
  - `generated_at` (`ISO-8601 string`) — Timestamp from CI run.
  - `commit_hash` (`string`) — Short SHA for published revision.
  - `sandbox_url` (`string`) — Relative path to sandbox index.
  - `report_url` (`string`) — Relative path to size report.
  - `status` (`'ready' | 'degraded' | 'unavailable'`) — Derived from artifact validation.
- **Validation Rules**:
  - `generated_at` required; if parsing fails, set status to `degraded`.
  - URLs must resolve to files staged in the Pages artifact; missing files switch status to `unavailable`.

### CIArtifactRecord
- **Description**: Metadata captured in CI before staging assets.
- **Fields**:
  - `artifact_name` (`string`)
  - `sha256` (`hex string`)
  - `byte_size` (`integer`)
  - `commit_hash` (`string`)
  - `generated_at` (`ISO-8601 string`)
- **Validation Rules**:
  - `commit_hash` must match the pipeline’s `GITHUB_SHA`.
  - `generated_at` must be within the same run window (≤10 minutes difference) to avoid stale artifacts.
  - Checksum verification fails the job if mismatch occurs.

### BuildSummary
- **Description**: High-level metrics surfaced on portal.
- **Fields**:
  - `wasm_delta_kb` (`number`)
  - `compressed_size_kb` (`number`)
  - `microbench_ms` (`number`)
  - `source_commit` (`string`)
- **Validation Rules**:
  - Numeric values must be finite; otherwise display placeholder and mark status `degraded`.
  - `source_commit` must align with CIArtifactRecord.commit_hash.

## Relationships
- `PortalPage.status` is derived from a combination of `CIArtifactRecord` validations and `BuildSummary` completeness.
- `BuildSummary.source_commit` references `CIArtifactRecord.commit_hash` ensuring both sandbox and size report align with the published revision.

## State Transitions
1. **Collect Artifacts** — After `update-size-reports`, CI downloads sandbox and report artifacts, recording `CIArtifactRecord`.
2. **Validate & Assemble** — Checksums verify integrity; metrics parsed into `BuildSummary`.
3. **Generate Portal** — Template renders `PortalPage` with links, metadata, and fallback states.
4. **Deploy** — GitHub Pages deploys static bundle; `PortalPage.status` is logged for monitoring.
