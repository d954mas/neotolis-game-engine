#!/usr/bin/env python3
"""CLI workflow for maintaining size-report CSV snapshots and manifest data."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, MutableMapping, Sequence

# Support running as a script by ensuring package imports succeed
if __package__ is None or __package__ == "":
    PACKAGE_ROOT = Path(__file__).resolve().parent
    sys.path.insert(0, str(PACKAGE_ROOT.parent.parent))
    from reports.size import validators  # type: ignore
else:  # pragma: no cover - script execution path only
    from . import validators  # type: ignore

REPORT_FILENAME = "report.txt"
MANIFEST_FILENAME = "index.json"
PLACEHOLDER_SHA = "UNKNOWN"
PLACEHOLDER_MESSAGE = "UNKNOWN"
ARTIFACT_EXCLUDES = {REPORT_FILENAME, MANIFEST_FILENAME, "README.md"}
@dataclass
class GitMetadata:
    sha: str
    subject: str
    branch: str | None = None
    date_iso: str | None = None


@dataclass
class Artifact:
    file_name: str
    size_bytes: int


@dataclass
class SnapshotEntry:
    kind: str  # "head" or "branch"
    sha: str
    message: str
    artifacts: List[Artifact]
    branch: str | None = None
    subject: str | None = None
    date_iso: str | None = None


class SizeReportError(RuntimeError):
    """Raised when the size-report workflow encounters a blocking issue."""


def is_hex_sha(candidate: str) -> bool:
    return len(candidate) == 40 and all(ch in "0123456789abcdef" for ch in candidate.lower())


def run_git(args: List[str], cwd: Path) -> str:
    from subprocess import run  # local import to avoid global dependency during import time

    result = run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SizeReportError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def current_head_metadata(repo_root: Path) -> GitMetadata:
    sha = run_git(["rev-parse", "HEAD"], repo_root)
    subject = run_git(["show", "-s", "--format=%s", "HEAD"], repo_root)
    commit_date = run_git(["show", "-s", "--format=%cI", "HEAD"], repo_root)
    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_root)
    if branch.upper() == "HEAD":
        branch = None
    return GitMetadata(sha=sha, subject=subject, branch=branch, date_iso=commit_date)


def metadata_for_ref(repo_root: Path, ref: str) -> GitMetadata:
    sha = run_git(["rev-parse", ref], repo_root)
    subject = run_git(["show", "-s", "--format=%s", ref], repo_root)
    commit_date = run_git(["show", "-s", "--format=%cI", ref], repo_root)
    return GitMetadata(sha=sha, subject=subject, date_iso=commit_date)


def discover_artifacts(folder: Path) -> List[Path]:
    artifacts = [p for p in folder.iterdir() if p.is_file() and p.name not in ARTIFACT_EXCLUDES]
    return sorted(artifacts, key=lambda p: p.name)


def worktree_has_changes_outside_reports(repo_root: Path) -> bool:
    status_output = run_git(["status", "--porcelain"], repo_root)
    for raw_line in status_output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        path_fragment = line[2:] if len(line) > 2 else ""
        path_fragment = path_fragment.strip()
      #  print(f"path_fragment: {path_fragment}")
        if " -> " in path_fragment:
            path_fragment = path_fragment.split(" -> ", 1)[1].strip()
        if path_fragment.startswith('"') and path_fragment.endswith('"'):
            path_fragment = path_fragment[1:-1]
        if not path_fragment:
            continue
        if not path_fragment.startswith("reports/"):
            return True
    return False


def read_report_entries(report_path: Path) -> List[SnapshotEntry]:
    if not report_path.exists():
        return []
    with report_path.open(newline="", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        header = reader.fieldnames or []
        rows: List[Dict[str, str]] = list(reader)

    if header != validators.HEADER:
        raise SizeReportError(f"Unexpected report header {header}. Expected {validators.HEADER}.")
    validators.ensure_rows(rows)
    return _rows_to_entries(rows)


def _rows_to_entries(rows: List[Dict[str, str]]) -> List[SnapshotEntry]:
    entries: List[SnapshotEntry] = []
    current: SnapshotEntry | None = None
    master_assigned = False
    head_assigned = False
    branch_assigned = False

    for row in rows:
        size_field = (row.get("size_bytes") or "").strip()
        if not size_field:
            sha_field = (row.get("git_sha") or "").strip()
            message_field = (row.get("git_message") or "").strip()
            file_field = (row.get("file_name") or "").strip()
            label = (file_field or sha_field).strip().upper()

            commit_kind = None
            if label == "HEAD":
                commit_kind = "head"
            elif label == "MASTER":
                commit_kind = "master"
            elif label == "BRANCH":
                commit_kind = "branch"
            elif label == "HISTORY":
                commit_kind = "history"

            commit_branch: str | None = None
            commit_subject: str | None = None

            if commit_kind == "head":
                commit_sha = (
                    message_field
                    if is_hex_sha(message_field)
                    else (sha_field if is_hex_sha(sha_field) else PLACEHOLDER_SHA)
                )
                commit_message = message_field or PLACEHOLDER_MESSAGE
                commit_subject = message_field or None
            elif commit_kind == "master":
                commit_sha = (
                    message_field
                    if is_hex_sha(message_field)
                    else (sha_field if is_hex_sha(sha_field) else PLACEHOLDER_SHA)
                )
                commit_message = message_field if message_field else PLACEHOLDER_MESSAGE
                commit_subject = commit_message
            elif commit_kind == "branch":
                commit_sha = (
                    message_field
                    if is_hex_sha(message_field)
                    else (sha_field if is_hex_sha(sha_field) else PLACEHOLDER_SHA)
                )
                commit_branch = message_field or None
                commit_message = commit_branch or PLACEHOLDER_MESSAGE
            else:
                commit_sha = sha_field if is_hex_sha(sha_field) else PLACEHOLDER_SHA
                commit_message = message_field or file_field or PLACEHOLDER_MESSAGE
                if commit_kind is None:
                    if not master_assigned:
                        commit_kind = "master"
                        master_assigned = True
                    elif not head_assigned:
                        commit_kind = "head"
                        head_assigned = True
                    elif not branch_assigned:
                        commit_kind = "branch"
                        branch_assigned = True
                    else:
                        commit_kind = "history"
                if commit_kind == "history":
                    commit_subject = message_field or commit_message
                commit_branch = message_field if commit_kind in {"head", "branch"} else None

            current = SnapshotEntry(
                kind=commit_kind or "history",
                sha=commit_sha or PLACEHOLDER_SHA,
                message=commit_message or PLACEHOLDER_MESSAGE,
                artifacts=[],
                branch=commit_branch,
                subject=commit_subject,
                date_iso=None,
            )
            if current.kind == "master":
                master_assigned = True
            elif current.kind == "head":
                head_assigned = True
            elif current.kind == "branch":
                branch_assigned = True
            entries.append(current)
        else:
            if current is None:
                raise SizeReportError("Encountered artifact row before metadata section header")
            file_name = (row.get("file_name") or "").strip()
            if not file_name:
                raise SizeReportError("Artifact row missing file_name")
            try:
                size_value = int(size_field)
            except ValueError as exc:  # pragma: no cover - validated earlier
                raise SizeReportError(f"Invalid size '{size_field}' for artifact '{file_name}'") from exc
            current.artifacts.append(Artifact(file_name=file_name, size_bytes=size_value))
    return entries


def format_entry_label(entry: SnapshotEntry) -> str:
    sha = entry.sha or PLACEHOLDER_SHA
    display_sha = sha if len(sha) <= 7 else sha[:7]
    branch = entry.branch
    subject = entry.subject or entry.message or PLACEHOLDER_MESSAGE

    if entry.kind == "head":
        label_branch = branch or entry.message or PLACEHOLDER_MESSAGE
        parts = ["HEAD", label_branch, subject or PLACEHOLDER_MESSAGE, display_sha]
        return "-".join(parts)
    if entry.kind == "branch":
        parts = [branch or PLACEHOLDER_MESSAGE, subject or PLACEHOLDER_MESSAGE, display_sha]
        return "-".join(parts)
    if entry.kind == "master":
        parts = ["MASTER", subject or PLACEHOLDER_MESSAGE, display_sha]
        return "-".join(parts)
    parts = [subject or PLACEHOLDER_MESSAGE, display_sha]
    return "-".join(parts)


def write_report_entries(report_path: Path, entries: List[SnapshotEntry]) -> None:
    with report_path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=validators.HEADER)
        writer.writeheader()
        for entry in entries:
            if entry.sha in (None, "", PLACEHOLDER_SHA) and not entry.artifacts:
                # Skip placeholder rows that carry no useful data.
                continue
            if entry.kind == "head":
                metadata_message = entry.branch or PLACEHOLDER_MESSAGE
            elif entry.kind == "branch":
                metadata_message = entry.branch or entry.message or PLACEHOLDER_MESSAGE
            else:
                metadata_message = entry.subject or entry.message or PLACEHOLDER_MESSAGE
            writer.writerow(
                {
                    "git_sha": entry.sha or PLACEHOLDER_SHA,
                    "git_message": metadata_message,
                    "file_name": entry.kind.upper(),
                    "size_bytes": "",
                }
            )
            for artifact in sorted(entry.artifacts, key=lambda item: item.file_name):
                writer.writerow(
                    {
                        "git_sha": "",
                        "git_message": "",
                        "file_name": artifact.file_name,
                        "size_bytes": str(artifact.size_bytes),
                    }
                )


def update_head_snapshot(input_folder: Path, output_folder: Path, repo_root: Path) -> GitMetadata:
    if not input_folder.exists() or not input_folder.is_dir():
        raise SizeReportError(f"Input folder '{input_folder}' does not exist or is not a directory")
    output_folder.mkdir(parents=True, exist_ok=True)
    report_path = output_folder / REPORT_FILENAME

    artifacts = discover_artifacts(input_folder)
    if not artifacts:
        raise SizeReportError(f"No artifacts found in '{input_folder}'. Build outputs are required.")

    if report_path.exists():
        existing_entries = read_report_entries(report_path)
    else:
        existing_entries = []

    branch_entries: List[SnapshotEntry] = []
    seen_branch_keys: set[tuple[str, str]] = set()
    for entry in existing_entries:
        if entry.kind != "branch":
            continue
        branch_name_entry = entry.branch or entry.message or ""
        sha_entry = entry.sha or ""
        if not branch_name_entry or not sha_entry or sha_entry == PLACEHOLDER_SHA:
            continue
        key = (branch_name_entry, sha_entry)
        if key in seen_branch_keys:
            continue
        seen_branch_keys.add(key)
        entry_subject = entry.subject
        entry_date = None
        if is_hex_sha(sha_entry):
            try:
                meta = metadata_for_ref(repo_root, sha_entry)
                entry_date = meta.date_iso
                if not entry_subject or entry_subject == PLACEHOLDER_MESSAGE:
                    entry_subject = meta.subject
            except SizeReportError:
                entry_date = None
        branch_entries.append(
            SnapshotEntry(
                kind="branch",
                sha=sha_entry,
                message=entry.message,
                artifacts=[
                    Artifact(file_name=a.file_name, size_bytes=a.size_bytes) for a in entry.artifacts
                ],
                branch=branch_name_entry,
                subject=entry_subject,
                date_iso=entry_date,
            )
        )

    head_meta = current_head_metadata(repo_root)
    branch_name = head_meta.branch
    head_message = head_meta.subject or PLACEHOLDER_MESSAGE

    head_artifacts = [
        Artifact(file_name=artifact.name, size_bytes=artifact.stat().st_size) for artifact in artifacts
    ]
    head_entry = SnapshotEntry(
        kind="head",
        sha=head_meta.sha,
        message=head_message,
        artifacts=head_artifacts,
        branch=branch_name,
        subject=head_meta.subject,
        date_iso=datetime.now(timezone.utc).isoformat(),
    )

    branch_entry: SnapshotEntry | None = None
    if branch_name and not worktree_has_changes_outside_reports(repo_root):
        branch_entry = SnapshotEntry(
            kind="branch",
            sha=head_meta.sha,
            message=head_meta.subject,
            artifacts=[Artifact(file_name=a.file_name, size_bytes=a.size_bytes) for a in head_artifacts],
            branch=branch_name,
            subject=head_meta.subject,
            date_iso=head_meta.date_iso,
        )

    entries_to_write: List[SnapshotEntry] = []
    entries_to_write.append(head_entry)
    branch_keys = {(entry.branch or "", entry.sha or "") for entry in branch_entries}
    if branch_entry is not None:
        key = (branch_entry.branch or "", branch_entry.sha or "")
        if key not in branch_keys:
            branch_entries.insert(0, branch_entry)
            branch_keys.add(key)
    entries_to_write.extend(branch_entries)
    write_report_entries(report_path, entries_to_write)
    return head_meta


def compute_deltas(master_artifacts: Sequence[Artifact], head_artifacts: Sequence[Artifact]) -> List[Dict[str, object]]:
    master_sizes = {item.file_name: item.size_bytes for item in master_artifacts}
    deltas = []
    for head in head_artifacts:
        name = head.file_name
        head_size = head.size_bytes
        master_size = master_sizes.get(name, 0)
        delta = head_size - master_size
        delta_percent = None
        if master_size > 0:
            delta_percent = round((delta / master_size) * 100, 2)
        elif head_size > 0:
            delta_percent = 100.0
        threshold_bytes = abs(delta) >= 25_000
        threshold_percent = delta_percent is not None and abs(delta_percent) >= 2.0
        thresholds = []
        if threshold_percent:
            thresholds.append("percent>2")
        if threshold_bytes:
            thresholds.append("bytes>25000")
        deltas.append(
            {
                "file_name": name,
                "head_size": head_size,
                "master_size": master_size,
                "delta_bytes": delta,
                "delta_percent": delta_percent,
                "alert": bool(thresholds),
                "thresholds": thresholds,
            }
        )
    return deltas


def regenerate_manifest(
    root: Path, repo_root: Path, updated_folder: Path | None = None
) -> Dict[str, object]:
    generated_at = datetime.now(timezone.utc).isoformat()
    summary_entries: List[Dict[str, object]] = []
    updated_relative: Path | None = None
    if updated_folder is not None:
        updated_relative = Path(updated_folder)

    for report_path in sorted(root.glob("**/report.txt")):
        entries = read_report_entries(report_path)
        if not entries:
            continue

        for entry in entries:
            meta: GitMetadata | None = None
            if is_hex_sha(entry.sha):
                try:
                    meta = metadata_for_ref(repo_root, entry.sha)
                except SizeReportError:
                    meta = None

            needs_subject = entry.subject is None or entry.subject == PLACEHOLDER_MESSAGE
            if entry.kind in {"head", "branch"}:
                needs_subject = True

            if needs_subject:
                if meta is not None:
                    entry.subject = meta.subject
                else:
                    entry.subject = entry.message or PLACEHOLDER_MESSAGE

            if entry.kind == "head":
                if entry.branch is None:
                    entry.branch = entry.message if entry.message != PLACEHOLDER_MESSAGE else entry.branch
                entry.date_iso = generated_at
            elif entry.kind == "branch":
                if entry.branch is None:
                    entry.branch = entry.message if entry.message != PLACEHOLDER_MESSAGE else None
                if entry.date_iso is None and meta is not None:
                    entry.date_iso = meta.date_iso

        commits_payload = []
        for entry in entries:
            branch_fragment = entry.branch or "NO_BRANCH"
            commits_payload.append(
                {
                    "kind": entry.kind,
                    "id": f"{entry.kind}:{branch_fragment}:{entry.sha or PLACEHOLDER_SHA}",
                    "git_sha": entry.sha or PLACEHOLDER_SHA,
                    "git_message": entry.subject or entry.message or PLACEHOLDER_MESSAGE,
                    "branch": entry.branch,
                    "subject": entry.subject or entry.message or PLACEHOLDER_MESSAGE,
                    "date": entry.date_iso or generated_at,
                    "label": format_entry_label(entry),
                    "artifacts": [
                        {
                            "file_name": artifact.file_name,
                            "size_bytes": artifact.size_bytes,
                        }
                        for artifact in entry.artifacts
                    ],
                }
            )

        folder_relative = report_path.parent.relative_to(root)
        folder_index_path = report_path.parent / "index.json"
        existing_generated_at: str | None = None
        if folder_index_path.exists():
            try:
                with folder_index_path.open(encoding="utf-8") as existing_fp:
                    existing_index = json.load(existing_fp)
                existing_generated_at = str(existing_index.get("generated_at") or "")
                if not existing_generated_at:
                    existing_generated_at = None
            except (json.JSONDecodeError, OSError, TypeError):
                existing_generated_at = None

        folder_is_updated = updated_relative is None or folder_relative == updated_relative
        folder_generated_at = generated_at if folder_is_updated else (existing_generated_at or generated_at)
        folder_index = {
            "generated_at": folder_generated_at,
            "folder": folder_relative.as_posix(),
            "report_path": report_path.relative_to(root).as_posix(),
            "commits": commits_payload,
        }
        with folder_index_path.open("w", encoding="utf-8") as folder_fp:
            json.dump(folder_index, folder_fp, indent=2)

        summary_entries.append(
            {
                "folder": folder_relative.as_posix(),
                "index": folder_index_path.relative_to(root).as_posix(),
                "commit_count": len(commits_payload),
            }
        )

    manifest = {
        "generated_at": generated_at,
        "folders": summary_entries,
    }
    with (root / MANIFEST_FILENAME).open("w", encoding="utf-8") as fp:
        json.dump(manifest, fp, indent=2)
    return manifest


def format_percent(value: object) -> str:
    if isinstance(value, (int, float)):
        return f"{value:+.2f}%"
    return "n/a"


def format_commit_label_from_dict(commit: Mapping[str, Any]) -> str:
    label = commit.get("label")
    if label:
        return str(label)
    branch = commit.get("branch")
    sha = str(commit.get("git_sha") or PLACEHOLDER_SHA)
    short_sha = sha if len(sha) <= 7 else sha[:7]
    kind = str(commit.get("kind") or "").upper()
    if branch:
        if kind == "BRANCH":
            return f"{branch} — {short_sha}"
        return f"{kind or 'HEAD'} — {branch}"
    if kind:
        return f"{kind} — {short_sha}"
    return short_sha


def log_artifact_summary(folder: str, manifest: MutableMapping[str, Any], root: Path) -> None:
    folders: Sequence[Mapping[str, Any]] = manifest.get("folders", [])  # type: ignore[assignment]
    match = next((item for item in folders if item.get("folder") == folder), None)
    if not match:
        print(f"No manifest entry found for {folder}; instrumentation summary skipped.", file=sys.stdout)
        return

    index_rel = match.get("index")
    if not index_rel:
        print("No per-folder index reference found; instrumentation summary skipped.", file=sys.stdout)
        return

    index_path = (root / index_rel).resolve()
    if not index_path.exists():
        print(f"Folder index '{index_path}' missing; instrumentation summary skipped.", file=sys.stdout)
        return

    with index_path.open(encoding="utf-8") as fp:
        folder_index = json.load(fp)

    commits: Sequence[Mapping[str, Any]] = folder_index.get("commits", [])  # type: ignore[assignment]
    if not commits:
        print("No commits recorded; instrumentation summary skipped.", file=sys.stdout)
        return

    base_commit = commits[0]
    target_commit = commits[1] if len(commits) > 1 else commits[0]

    # Prefer the HEAD snapshot as the comparison target.
    target_commit = next((item for item in commits if str(item.get("kind")).lower() == "head"), target_commit)
    base_commit = next(
        (
            item
            for item in commits
            if str(item.get("kind")).lower() == "branch"
            and item is not target_commit
            and item.get("git_sha") != target_commit.get("git_sha")
        ),
        base_commit,
    )
    if not base_commit or base_commit == target_commit:
        base_commit = next((item for item in commits if str(item.get("kind")).lower() == "branch"), base_commit)
    if not base_commit:
        base_commit = target_commit

    base_label = format_commit_label_from_dict(base_commit)
    target_label = format_commit_label_from_dict(target_commit)
    print(f"Default comparison: {base_label} → {target_label}", file=sys.stdout)

    base_sizes = {item["file_name"]: item["size_bytes"] for item in base_commit.get("artifacts", [])}
    target_sizes = {item["file_name"]: item["size_bytes"] for item in target_commit.get("artifacts", [])}
    artifact_names = sorted(set(base_sizes) | set(target_sizes))

    print(f"Artifacts measured ({len(artifact_names)}):", file=sys.stdout)
    alert_total = 0
    for name in artifact_names:
        base_size = base_sizes.get(name, 0)
        head_size = target_sizes.get(name, 0)
        delta_bytes = head_size - base_size
        delta_percent = None
        if base_size > 0:
            delta_percent = (delta_bytes / base_size) * 100
        elif head_size > 0:
            delta_percent = 100.0
        exceeds_bytes = abs(delta_bytes) >= 25_000
        exceeds_percent = delta_percent is not None and abs(delta_percent) >= 2.0
        thresholds = []
        if exceeds_percent:
            thresholds.append("percent>2")
        if exceeds_bytes:
            thresholds.append("bytes>25000")
        if thresholds:
            alert_total += 1
        threshold_label = ", ".join(thresholds) if thresholds else "none"
        print(
            f"  - {name}: base={base_size}B head={head_size}B delta={delta_bytes}B ({format_percent(delta_percent)}) "
            f"thresholds={threshold_label}",
            file=sys.stdout,
        )
    print(f"Alert thresholds triggered: {alert_total}", file=sys.stdout)

def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update HEAD size snapshot and regenerate dashboards."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Directory containing built artifacts to measure (absolute or relative to repo root).",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Directory under reports/size where report.txt resides (absolute or relative to reports/size).",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    args = parse_args(argv)
    root = Path(__file__).resolve().parent
    repo_root = root.parent.parent

    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = (repo_root / args.input).resolve()

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = (root / args.output).resolve()

    try:
        output_label = output_path.relative_to(root)
    except ValueError:
        print(
            f"Error: Output directory '{output_path}' must live under {root}",
            file=sys.stderr,
        )
        return 1
    try:
        head_meta = update_head_snapshot(
            input_path,
            output_path,
            repo_root,
        )
        manifest = regenerate_manifest(root, repo_root, output_label)
        print(
            f"Updated HEAD snapshot for {output_label}: {head_meta.sha} — {head_meta.subject}",
            file=sys.stdout,
        )
        log_artifact_summary(output_label.as_posix(), manifest, root)
    except SizeReportError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
