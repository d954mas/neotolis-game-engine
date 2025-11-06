# Data Model — Size Report History Chart (Front-End)

## Overview
The dashboard consumes the existing manifest at `reports/size/index.json`, which lists folder-level commit indexes. History data is derived purely in JavaScript by aggregating artifact sizes from those commit entries, respecting the ≤180 sample window and without modifying native engine code.

## Entities

### SizeManifest
- **Description**: Root JSON document loaded from `reports/size/index.json`.
- **Fields**:
  - `generated_at` (`string`, ISO timestamp) — Used for freshness messaging.
  - `folders` (`SizeFolderEntry[]`) — Available size-report folders.
- **Validation**: `folders` must be non-empty; missing manifest triggers dashboard error state.

### SizeFolderEntry
- **Description**: Entry within the manifest pointing to a folder-specific commit index.
- **Fields**:
  - `folder` (`string`) — Folder name (e.g., `sandbox/wasm/release`).
  - `index` (`string`) — Relative path to folder index JSON (same origin).
  - `commit_count` (`number`) — Total commits recorded.
- **Validation**: Entries missing `index` are skipped and logged; dashboard only lists folders with accessible indexes.

### FolderCommitManifest
- **Description**: JSON document referenced by `SizeFolderEntry.index` (e.g., `sandbox/wasm/release/index.json`).
- **Fields**:
  - `generated_at` (`string`, ISO timestamp) — Folder-specific freshness marker.
  - `folder` (`string`) — Folder identifier (mirrors parent entry).
  - `commits` (`FolderCommit[]`) — Ordered array of commit records (latest first).
- **Validation**: `commits` array may be empty; loader enforces ascending order by `date` when building history samples.

### FolderCommit
- **Description**: Raw commit record as emitted by size reporting pipeline.
- **Fields**:
  - `kind` (`string`) — e.g., `head`, `branch`.
  - `id` (`string`) — Unique identifier used across dashboard.
  - `git_sha` (`string`) — Full SHA.
  - `git_message`, `subject` (`string`) — Commit metadata.
  - `branch` (`string`) — Branch name.
  - `date` (`string`, ISO timestamp) — Commit timestamp.
  - `artifacts` (`SizeArtifact[]`) — File-level size data.
- **Validation**: Commits missing `artifacts` default to empty array; invalid timestamps fall back to raw string for display but are excluded from history chart calculations.

### SizeArtifact
- **Description**: Metadata for a single file captured in a commit report.
- **Fields**:
  - `file_name` (`string`) — Path relative to artifact root.
  - `size_bytes` (`number`) — File size in bytes.
- **Validation**: `size_bytes` must be ≥ 0; negative or missing values are treated as 0 and logged.

### HistorySample
- **Description**: Derived data structure for the history chart representing total artifact size per commit.
- **Fields**:
  - `commitId` (`string`) — Borrowed from `FolderCommit.id` (fallback to `kind:git_sha`).
  - `totalSizeBytes` (`number`) — Sum of `artifacts[*].size_bytes`.
  - `committedAtEpochMs` (`number`) — Parsed epoch milliseconds from `FolderCommit.date`.
  - `label` (`string`) — Human-readable tooltip label (short SHA + message).
  - `missingArtifacts` (`boolean`) — Flag when artifacts array empty or data missing.
- **Relationships**: Collected within `HistorySeries.samples`.

### HistorySeries
- **Description**: Maintains active window state for rendering.
- **Fields**:
  - `samples` (`HistorySample[]`) — Visible entries after window slicing (newest first).
  - `allSamples` (`HistorySample[]`) — Full history (capped at 180 commits).
  - `windowMode` (`'30' | '90' | '180'`) — Active window length.
  - `minSizeBytes` / `maxSizeBytes` (`number`) — Computed bounds; if `samples` < 1, both set to 0.
  - `gaps` (`number`) — Count of missing sample positions caused by dataset omissions.
  - `truncated` (`boolean`) — Indicates whether the history was capped at 180 commits.
- **State Transitions**:
  1. **Init** → Build empty series with default window `'90'`.
  2. **Hydrate** → Parse folder commits into `HistorySample[]`, sorted ascending by `committedAtEpochMs`.
  3. **Window Apply** → Slice to requested window and recompute aggregates.
  4. **Render** → Chart reads immutable snapshot for drawing.

### HistoryPrefs
- **Description**: Session preference stored via `sessionStorage`.
- **Fields**:
  - `windowMode` (`'30' | '90' | '180'`)
  - `updatedAtEpochMs` (`number`)
- **Validation**: Values outside accepted set fallback to `'90'`.

## Validation Rules
- Manifest and folder indexes must be fetched relative to `report.html`; cross-origin requests are disallowed.
- Folder commit lists must be normalized to chronological order before charting; out-of-order entries trigger a console warning and are sorted client-side.
- History window selection persists per session; invalid stored values are ignored with a console warning.
- When fewer than 5 samples available, chart container persists but displays "More history needed" messaging while still plotting available points.
- Tooltip formatter converts bytes to KB with one decimal place and includes commit label + localized timestamp.

## Derived Data
- `totalSizeBytes` calculated as the sum of all artifact `size_bytes` per commit; commits missing artifacts count as 0 and increment `missingCommits`.
- Axis tick spacing computed with `(maxSizeBytes - minSizeBytes)` rounded to the nearest 10 KB to reduce label jitter.
- Gap markers inserted when dataset indicates missing commits between samples (difference in dates > 24h when commit count suggests more history).
