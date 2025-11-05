# Data Model — Size Reporting Dashboard

## Entities

### SizeReportSnapshot
- **Purpose**: Represents the size summary for a specific sandbox build variant (`<testbed>/<platform>/<configuration>`).
- **Fields**:
  - `folder_id` (string) — canonical path fragment (e.g., `sandbox/wasm/debug`); MUST match directory structure under `reports/size/`.
  - `master_sha` (string) — 40-char commit SHA used as baseline; MAY be `UNKNOWN` when baseline not yet captured.
  - `master_message` (string) — commit summary associated with the MASTER snapshot; MAY be `UNKNOWN` when baseline not yet captured.
  - `head_sha` (string) — 40-char commit SHA or `WORKTREE` label representing current measurement.
  - `head_message` (string) — commit summary for the HEAD snapshot (use Git subject line).
  - `updated_at` (ISO-8601) — timestamp of last HEAD update (optional metadata stored in CSV header or accompanying comment).
  - `artifacts` (list of `SizeReportRecord`) — ordered by `file_name`.
- **Relationships**: Owns many `SizeReportRecord` entries; one snapshot per folder.
- **Validation Rules**:
  - `folder_id` MUST exist on disk when update workflow runs.
  - `master_sha` MUST reference `master` branch unless explicitly overridden in documentation.
  - `master_message` and `head_message` MUST reflect Git commit subject lines ≤120 characters.
  - Exactly one `MASTER` row and one `HEAD` row must exist in CSV.
  - CSV file size MUST remain ≤30 KB.
- **State Transitions**:
  - `Initialize`: create snapshot with `master_sha=UNKNOWN`, `head_sha=<current>`.
  - `BaselineRefresh`: update `master_sha` to new accepted commit and recompute deltas.
  - `HeadUpdate`: recompute `head_sha` row while keeping `master_sha` untouched.

### SizeReportRecord
- **Purpose**: Captures the size metrics for a single artifact within a snapshot.
- **Fields**:
  - `git_ref` (enum: `MASTER`, `HEAD`, optional historical tags) — indicates baseline vs. current measurement.
  - `file_name` (string) — artifact filename relative to snapshot folder.
  - `size_bytes` (integer) — measured byte size, non-negative.
  - `git_sha` (string) — commit identifier associated with the row; duplicates across HEAD/MASTER entries.
  - `git_message` (string) — commit summary corresponding to `git_ref`; redundant across artifacts but persisted for CSV schema compatibility.
  - `delta_vs_master` (integer) — computed difference (`size_bytes(head) - size_bytes(master)`); stored in derived data for visualization.
- **Relationships**: Belongs to `SizeReportSnapshot`; grouped by `git_ref`.
- **Validation Rules**:
  - `file_name` MUST match actual artifact produced by build; missing files trigger workflow error.
  - `size_bytes` MUST be measured from filesystem, not manually entered.
  - `git_sha` MUST be a 40-character lowercase hex string or `UNKNOWN`.
  - `delta_vs_master` MUST flag thresholds (>2% or >25 KB) for visualization layer.

## Derived Views
- **FolderSummary**: Aggregated payload consumed by `report.html`; includes folder metadata, HEAD/MASTER rows, and computed deltas for chart rendering.
- **AlertBand**: Set of artifacts exceeding thresholds; used to surface callouts in HTML UI and CI logs.
