#!/usr/bin/env python3
"""CLI workflow for maintaining size-report CSV snapshots and manifest data."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Sequence

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
    message: str


class SizeReportError(RuntimeError):
    """Raised when the size-report workflow encounters a blocking issue."""


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


def read_report(report_path: Path) -> List[Dict[str, str]]:
    if not report_path.exists():
        return []
    with report_path.open(newline="", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        validators.ensure_header(reader.fieldnames)
        rows = list(reader)
        validators.ensure_rows(rows)
        return rows


def ensure_master_rows(rows: List[Dict[str, str]]) -> None:
    if any(row.get("git_ref") == "MASTER" for row in rows):
        return
    rows.append(
        {
            "git_ref": "MASTER",
            "file_name": "",
            "size_bytes": "",
            "git_sha": PLACEHOLDER_SHA,
            "git_message": PLACEHOLDER_MESSAGE,
        }
    )


def write_report(report_path: Path, rows: Iterable[Mapping[str, str]]) -> None:
    ordered = sorted(rows, key=validators.sort_key)
    with report_path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=validators.HEADER)
        writer.writeheader()
        for row in ordered:
            writer.writerow(row)


def update_head_snapshot(folder: Path, repo_root: Path, accept_master: str | None = None) -> GitMetadata:
    if not folder.exists() or not folder.is_dir():
        raise SizeReportError(f"Folder '{folder}' does not exist or is not a directory")
    report_path = folder / REPORT_FILENAME
    if not report_path.exists():
        raise SizeReportError(f"Report file '{report_path}' is missing")

    rows = read_report(report_path)
    ensure_master_rows(rows)
    for row in rows:
        if row.get("git_ref") == "MASTER":
            if not row.get("git_sha"):
                row["git_sha"] = PLACEHOLDER_SHA
            if not row.get("git_message"):
                row["git_message"] = PLACEHOLDER_MESSAGE

    artifacts = discover_artifacts(folder)
    if not artifacts:
        raise SizeReportError(f"No artifacts found in '{folder}'. Build outputs are required.")

    head_meta = current_head_metadata(repo_root)

    # Remove existing HEAD rows and rebuild
    rows = [row for row in rows if row.get("git_ref") != "HEAD"]
    for artifact in artifacts:
        rows.append(
            {
                "git_ref": "HEAD",
                "file_name": artifact.name,
                "size_bytes": str(artifact.stat().st_size),
                "git_sha": head_meta.sha,
                "git_message": head_meta.message,
            }
        )

    if accept_master:
        master_meta = metadata_for_ref(repo_root, accept_master)
        rows = [row for row in rows if row.get("git_ref") != "MASTER"]
        for artifact in artifacts:
            rows.append(
                {
                    "git_ref": "MASTER",
                    "file_name": artifact.name,
                    "size_bytes": str(artifact.stat().st_size),
                    "git_sha": master_meta.sha,
                    "git_message": master_meta.message,
                }
            )
    write_report(report_path, rows)
    return head_meta


def parse_report_rows(rows: Iterable[Mapping[str, str]]) -> Dict[str, Dict[str, object]]:
    grouped: Dict[str, Dict[str, object]] = {}
    for ref in ("MASTER", "HEAD"):
        grouped[ref] = {
            "git_sha": PLACEHOLDER_SHA,
            "git_message": PLACEHOLDER_MESSAGE,
            "artifacts": [],
        }

    for row in rows:
        ref = row.get("git_ref", "")
        target = grouped.setdefault(ref, {"git_sha": PLACEHOLDER_SHA, "git_message": PLACEHOLDER_MESSAGE, "artifacts": []})
        git_sha = row.get("git_sha") or PLACEHOLDER_SHA
        git_message = row.get("git_message") or PLACEHOLDER_MESSAGE
        target["git_sha"] = git_sha
        target["git_message"] = git_message
        file_name = row.get("file_name", "")
        if not file_name:
            continue
        size = row.get("size_bytes", "")
        size_int = int(size) if str(size).isdigit() else 0
        target["artifacts"].append({"file_name": file_name, "size_bytes": size_int})
    for ref in grouped:
        grouped[ref]["artifacts"] = sorted(grouped[ref]["artifacts"], key=lambda item: item["file_name"])
    return grouped


def compute_deltas(master_artifacts: List[Dict[str, object]], head_artifacts: List[Dict[str, object]]) -> List[Dict[str, object]]:
    master_sizes = {item["file_name"]: item["size_bytes"] for item in master_artifacts}
    deltas = []
    for head in head_artifacts:
        name = head["file_name"]
        head_size = head["size_bytes"]
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
        rows = read_report(report_path)
        summary = parse_report_rows(rows)
        deltas = compute_deltas(summary["MASTER"]["artifacts"], summary["HEAD"]["artifacts"])
        datasets.append(
            {
                "folder": str(report_path.parent.relative_to(root)),
                "report_path": str(report_path.relative_to(root)),
                "head": {
                    "git_sha": summary["HEAD"]["git_sha"],
                    "git_message": summary["HEAD"]["git_message"],
                },
                "master": {
                    "git_sha": summary["MASTER"]["git_sha"],
                    "git_message": summary["MASTER"]["git_message"],
                },
                "artifacts": deltas,
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


def log_artifact_summary(folder: str, manifest: MutableMapping[str, object]) -> None:
    folders: Sequence[Mapping[str, object]] = manifest.get("folders", [])  # type: ignore[assignment]
    match = next((item for item in folders if item.get("folder") == folder), None)
    if not match:
        print(f"No manifest entry found for {folder}; instrumentation summary skipped.", file=sys.stdout)
        return

    artifacts: Sequence[Mapping[str, object]] = match.get("artifacts", [])  # type: ignore[assignment]
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
        "--folder",
        required=True,
        help="Target folder relative to reports/size (e.g., sandbox/wasm/debug)",
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
    folder = root / args.folder
    try:
        head_meta = update_head_snapshot(folder, repo_root, accept_master=args.accept_master)
        manifest = regenerate_manifest(root)
        print(
            f"Updated HEAD snapshot for {args.folder}: {head_meta.sha} — {head_meta.message}",
            file=sys.stdout,
        )
        log_artifact_summary(args.folder, manifest)
    except SizeReportError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
