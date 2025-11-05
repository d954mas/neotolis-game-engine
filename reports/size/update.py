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
LEGACY_HEADER = ["git_ref", "file_name", "size_bytes", "git_sha", "git_message"]


@dataclass
class GitMetadata:
    sha: str
    message: str


@dataclass
class Artifact:
    file_name: str
    size_bytes: int


@dataclass
class SnapshotEntry:
    kind: str  # "master", "head", or "history"
    sha: str
    message: str
    artifacts: List[Artifact]


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
    message = run_git(["show", "-s", "--format=%s", "HEAD"], repo_root)
    return GitMetadata(sha=sha, message=message)


def metadata_for_ref(repo_root: Path, ref: str) -> GitMetadata:
    sha = run_git(["rev-parse", ref], repo_root)
    message = run_git(["show", "-s", "--format=%s", ref], repo_root)
    return GitMetadata(sha=sha, message=message)


def discover_artifacts(folder: Path) -> List[Path]:
    artifacts = [p for p in folder.iterdir() if p.is_file() and p.name not in ARTIFACT_EXCLUDES]
    return sorted(artifacts, key=lambda p: p.name)


def read_report_entries(report_path: Path) -> List[SnapshotEntry]:
    if not report_path.exists():
        return []
    with report_path.open(newline="", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        header = reader.fieldnames or []
        rows: List[Dict[str, str]] = list(reader)

    if header == validators.HEADER:
        validators.ensure_rows(rows)
        return _rows_to_entries(rows)
    if header == LEGACY_HEADER:
        return convert_legacy_rows(rows)
    raise SizeReportError(
        f"Unexpected report header {header}. Expected {validators.HEADER} or legacy {LEGACY_HEADER}."
    )


def _rows_to_entries(rows: List[Dict[str, str]]) -> List[SnapshotEntry]:
    entries: List[SnapshotEntry] = []
    current: SnapshotEntry | None = None
    master_assigned = False
    head_assigned = False

    for row in rows:
        size_field = (row.get("size_bytes") or "").strip()
        if not size_field:
            sha_field = (row.get("git_sha") or "").strip()
            message_field = (row.get("git_message") or "").strip()
            file_field = (row.get("file_name") or "").strip()
            label = (file_field or sha_field).strip().upper()

            if label == "HEAD":
                commit_kind = "head"
            elif label == "MASTER":
                commit_kind = "master"
            elif label == "HISTORY":
                commit_kind = "history"
            else:
                commit_kind = None

            if commit_kind == "head":
                commit_sha = (
                    message_field
                    if is_hex_sha(message_field)
                    else (sha_field if is_hex_sha(sha_field) else PLACEHOLDER_SHA)
                )
                commit_message = (
                    message_field if message_field and not is_hex_sha(message_field) else PLACEHOLDER_MESSAGE
                )
            elif commit_kind == "master":
                commit_sha = (
                    message_field
                    if is_hex_sha(message_field)
                    else (sha_field if is_hex_sha(sha_field) else PLACEHOLDER_SHA)
                )
                commit_message = (
                    message_field if message_field and not is_hex_sha(message_field) else PLACEHOLDER_MESSAGE
                )
            else:
                commit_sha = sha_field if is_hex_sha(sha_field) else PLACEHOLDER_SHA
                commit_message = message_field or file_field or PLACEHOLDER_MESSAGE
                if not master_assigned:
                    commit_kind = "master"
                elif not head_assigned:
                    commit_kind = "head"
                else:
                    commit_kind = "history"

            current = SnapshotEntry(
                kind=commit_kind,
                sha=commit_sha or PLACEHOLDER_SHA,
                message=commit_message or PLACEHOLDER_MESSAGE,
                artifacts=[],
            )
            if commit_kind == "master":
                master_assigned = True
            elif commit_kind == "head":
                head_assigned = True
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


def convert_legacy_rows(rows: List[Dict[str, str]]) -> List[SnapshotEntry]:
    order: List[str] = []
    grouped: Dict[str, SnapshotEntry] = {}

    for row in rows:
        ref = (row.get("git_ref") or "").strip()
        sha_value = (row.get("git_sha") or "").strip() or PLACEHOLDER_SHA
        message_value = (row.get("git_message") or "").strip() or PLACEHOLDER_MESSAGE
        key = ref
        kind = "history"
        if ref == "HEAD":
            kind = "head"
            key = "HEAD"
        elif ref == "MASTER":
            kind = "master"
            key = "MASTER"
        else:
            key = sha_value

        if key not in grouped:
            grouped[key] = SnapshotEntry(
                kind=kind,
                sha=sha_value,
                message=message_value,
                artifacts=[],
            )
            order.append(key)
        entry = grouped[key]
        entry.sha = sha_value
        entry.message = message_value

        file_name = (row.get("file_name") or "").strip()
        size_field = (row.get("size_bytes") or "").strip()
        if file_name:
            size_value = int(size_field) if size_field.isdigit() else 0
            entry.artifacts.append(Artifact(file_name=file_name, size_bytes=size_value))

    for entry in grouped.values():
        entry.artifacts = sorted(entry.artifacts, key=lambda item: item.file_name)

    # Ensure master entry exists even if absent in legacy data
    if "MASTER" not in grouped:
        order.insert(0, "MASTER")
        grouped["MASTER"] = SnapshotEntry(
            kind="master",
            sha=PLACEHOLDER_SHA,
            message=PLACEHOLDER_MESSAGE,
            artifacts=[],
        )

    entries: List[SnapshotEntry] = []
    for key in order:
        entries.append(grouped[key])
    return entries


def format_entry_label(entry: SnapshotEntry) -> str:
    sha = entry.sha or PLACEHOLDER_SHA
    display_sha = sha if len(sha) <= 7 else sha[:7]
    message = entry.message or PLACEHOLDER_MESSAGE
    if entry.kind == "head":
        return f"HEAD — {display_sha}"
    if entry.kind == "master":
        return f"MASTER — {display_sha}"
    if message == PLACEHOLDER_MESSAGE:
        return display_sha
    return f"{display_sha} — {message}"


def write_report_entries(report_path: Path, entries: List[SnapshotEntry]) -> None:
    with report_path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=validators.HEADER)
        writer.writeheader()
        for entry in entries:
            if entry.kind == "master" and entry.sha == PLACEHOLDER_SHA and not entry.artifacts:
                continue
            writer.writerow(
                {
                    "git_sha": entry.sha or PLACEHOLDER_SHA,
                    "git_message": entry.message or PLACEHOLDER_MESSAGE,
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


def update_head_snapshot(
    input_folder: Path, output_folder: Path, repo_root: Path, accept_master: str | None = None
) -> GitMetadata:
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
    master_entry: SnapshotEntry | None = None
    history_entries: List[SnapshotEntry] = []
    previous_head: SnapshotEntry | None = None

    for entry in existing_entries:
        if entry.kind == "master":
            if entry.sha == PLACEHOLDER_SHA and not entry.artifacts:
                continue
            master_entry = entry
        elif entry.kind == "head":
            previous_head = entry
        else:
            history_entries.append(entry)

    head_meta = current_head_metadata(repo_root)

    head_artifacts = [
        Artifact(file_name=artifact.name, size_bytes=artifact.stat().st_size) for artifact in artifacts
    ]
    head_entry = SnapshotEntry(kind="head", sha=head_meta.sha, message=head_meta.message, artifacts=head_artifacts)

    if accept_master:
        master_meta = metadata_for_ref(repo_root, accept_master)
        master_entry = SnapshotEntry(
            kind="master",
            sha=master_meta.sha,
            message=master_meta.message,
            artifacts=[Artifact(file_name=a.file_name, size_bytes=a.size_bytes) for a in head_artifacts],
        )

    if master_entry is not None and head_entry is not None and master_entry.sha == head_entry.sha:
        master_map = {artifact.file_name: artifact.size_bytes for artifact in master_entry.artifacts}
        head_map = {artifact.file_name: artifact.size_bytes for artifact in head_entry.artifacts}
        if master_map == head_map:
            master_entry = None

    if master_entry is not None and not master_entry.artifacts:
        master_entry = None

    if previous_head and previous_head.sha not in (PLACEHOLDER_SHA, head_entry.sha):
        history_entries = [entry for entry in history_entries if entry.sha != previous_head.sha]
        history_entries.insert(
            0,
            SnapshotEntry(
                kind="history",
                sha=previous_head.sha,
                message=previous_head.message,
                artifacts=[Artifact(file_name=a.file_name, size_bytes=a.size_bytes) for a in previous_head.artifacts],
            ),
        )

    # Remove any stale history entry matching the current HEAD sha
    history_entries = [entry for entry in history_entries if entry.sha != head_entry.sha]

    entries_to_write: List[SnapshotEntry] = []
    if master_entry is not None:
        entries_to_write.append(master_entry)
    entries_to_write.append(head_entry)
    entries_to_write.extend(history_entries)
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


def regenerate_manifest(root: Path) -> Dict[str, object]:
    datasets = []
    for report_path in sorted(root.glob("**/report.txt")):
        entries = read_report_entries(report_path)
        if not entries:
            continue

        master_entry = next((entry for entry in entries if entry.kind == "master"), None)
        head_entry = next((entry for entry in entries if entry.kind == "head"), None)

        comparison_base = master_entry
        if comparison_base is None:
            comparison_base = next((entry for entry in entries if entry.kind == "history"), None)
        if comparison_base is None:
            comparison_base = head_entry

        comparison_target = head_entry or comparison_base

        base_artifacts = comparison_base.artifacts if comparison_base else []
        target_artifacts = comparison_target.artifacts if comparison_target else []
        deltas = compute_deltas(base_artifacts, target_artifacts)

        commits_payload = [
            {
                "kind": entry.kind,
                "id": f"{entry.kind}:{entry.sha or PLACEHOLDER_SHA}",
                "git_sha": entry.sha or PLACEHOLDER_SHA,
                "git_message": entry.message or PLACEHOLDER_MESSAGE,
                "label": format_entry_label(entry),
                "artifacts": [
                    {
                        "file_name": artifact.file_name,
                        "size_bytes": artifact.size_bytes,
                    }
                    for artifact in entry.artifacts
                ],
            }
            for entry in entries
        ]

        datasets.append(
            {
                "folder": str(report_path.parent.relative_to(root)),
                "report_path": str(report_path.relative_to(root)),
                "commits": commits_payload,
                "comparison": {
                    "base_id": f"{comparison_base.kind}:{comparison_base.sha or PLACEHOLDER_SHA}" if comparison_base else None,
                    "base_sha": comparison_base.sha if comparison_base else PLACEHOLDER_SHA,
                    "base_message": comparison_base.message if comparison_base else PLACEHOLDER_MESSAGE,
                    "base_label": format_entry_label(comparison_base) if comparison_base else "",
                    "target_id": f"{comparison_target.kind}:{comparison_target.sha or PLACEHOLDER_SHA}" if comparison_target else None,
                    "target_sha": comparison_target.sha if comparison_target else PLACEHOLDER_SHA,
                    "target_message": comparison_target.message if comparison_target else PLACEHOLDER_MESSAGE,
                    "target_label": format_entry_label(comparison_target) if comparison_target else "",
                    "artifacts": deltas,
                },
                "head": {
                    "git_sha": head_entry.sha if head_entry else PLACEHOLDER_SHA,
                    "git_message": head_entry.message if head_entry else PLACEHOLDER_MESSAGE,
                } if head_entry else None,
                "master": {
                    "git_sha": master_entry.sha,
                    "git_message": master_entry.message,
                } if master_entry else None,
            }
        )
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "folders": datasets,
    }
    with (root / MANIFEST_FILENAME).open("w", encoding="utf-8") as fp:
        json.dump(manifest, fp, indent=2)
    return manifest


def format_percent(value: object) -> str:
    if isinstance(value, (int, float)):
        return f"{value:+.2f}%"
    return "n/a"


def log_artifact_summary(folder: str, manifest: MutableMapping[str, Any]) -> None:
    folders: Sequence[Mapping[str, Any]] = manifest.get("folders", [])  # type: ignore[assignment]
    match = next((item for item in folders if item.get("folder") == folder), None)
    if not match:
        print(f"No manifest entry found for {folder}; instrumentation summary skipped.", file=sys.stdout)
        return

    comparison: Mapping[str, Any] | None = match.get("comparison")  # type: ignore[assignment]
    if comparison:
        base_label = comparison.get("base_label", comparison.get("base_sha", "base"))
        target_label = comparison.get("target_label", comparison.get("target_sha", "target"))
        artifacts: Sequence[Mapping[str, Any]] = comparison.get("artifacts", [])  # type: ignore[assignment]
        print(f"Default comparison: {base_label} → {target_label}", file=sys.stdout)
    else:
        artifacts = match.get("artifacts", [])  # type: ignore[assignment]
        print("Default comparison: MASTER → HEAD", file=sys.stdout)

    print(f"Artifacts measured ({len(artifacts)}):", file=sys.stdout)
    alert_total = 0
    for artifact in artifacts:
        file_name = str(artifact.get("file_name") or "<unknown>")
        master_size = int(artifact.get("master_size") or 0)
        head_size = int(artifact.get("head_size") or 0)
        delta_bytes = int(artifact.get("delta_bytes") or 0)
        thresholds = artifact.get("thresholds") or []
        if artifact.get("alert"):
            alert_total += 1
        if isinstance(thresholds, Sequence) and not isinstance(thresholds, (str, bytes)):
            threshold_label = ", ".join(str(item) for item in thresholds) or "none"
        else:
            threshold_label = str(thresholds) if thresholds else "none"
        percent = format_percent(artifact.get("delta_percent"))
        print(
            f"  - {file_name}: master={master_size}B head={head_size}B delta={delta_bytes}B ({percent}) thresholds={threshold_label}",
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
    parser.add_argument(
        "--accept-master",
        dest="accept_master",
        help="When provided, promote the measured HEAD snapshot to MASTER using the supplied Git ref.",
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
            accept_master=args.accept_master,
        )
        manifest = regenerate_manifest(root)
        print(
            f"Updated HEAD snapshot for {output_label}: {head_meta.sha} — {head_meta.message}",
            file=sys.stdout,
        )
        log_artifact_summary(output_label.as_posix(), manifest)
    except SizeReportError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
