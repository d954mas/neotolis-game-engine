"""Validation helpers for size-report CSV and JSON manifests."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

HEADER = ["git_sha", "git_message", "file_name", "size_bytes"]


@dataclass
class ValidationError(Exception):
    message: str

    def __str__(self) -> str:  # pragma: no cover - simple delegator
        return self.message


def ensure_header(fieldnames: Iterable[str] | None) -> None:
    if list(fieldnames or []) != HEADER:
        raise ValidationError(
            f"Unexpected CSV header. Expected {HEADER}, got {list(fieldnames or [])}."
        )


def ensure_rows(rows: Iterable[Mapping[str, str]]) -> None:
    current_label = None
    for row in rows:
        size = (row.get("size_bytes") or "").strip()
        if not size:
            label = (row.get("git_sha") or "").strip()
            if not label:
                raise ValidationError("Metadata row missing git_sha identifier")
            current_label = label
            continue
        if current_label is None:
            raise ValidationError("Artifact row encountered before any metadata row")
        if not size.isdigit():
            raise ValidationError(f"Invalid size_bytes '{size}'")
        filename = (row.get("file_name") or "").strip()
        if not filename:
            raise ValidationError("Artifact row missing file_name")


def _validate_commit_artifacts(artifacts: object, errors: list[str], prefix: str) -> None:
    if not isinstance(artifacts, list):
        errors.append(f"{prefix}.artifacts must be an array")
        return
    for idx, artifact in enumerate(artifacts):
        path = f"{prefix}.artifacts[{idx}]"
        if not isinstance(artifact, dict):
            errors.append(f"{path} must be an object")
            continue
        file_name = artifact.get("file_name")
        if not isinstance(file_name, str) or not file_name:
            errors.append(f"{path}.file_name must be a non-empty string")
        size_bytes = artifact.get("size_bytes")
        if not isinstance(size_bytes, int) or size_bytes < 0:
            errors.append(f"{path}.size_bytes must be a non-negative integer")


def _validate_commit_entry(commit: object, index: int, errors: list[str]) -> None:
    prefix = f"commits[{index}]"
    if not isinstance(commit, dict):
        errors.append(f"{prefix} must be an object")
        return
    required_fields = ("id", "git_sha", "date", "artifacts")
    for field in required_fields:
        if field not in commit:
            errors.append(f"{prefix}.{field} is required")
    commit_id = commit.get("id")
    if commit_id is not None and not isinstance(commit_id, str):
        errors.append(f"{prefix}.id must be a string")
    git_sha = commit.get("git_sha")
    if git_sha is not None and not isinstance(git_sha, str):
        errors.append(f"{prefix}.git_sha must be a string")
    date = commit.get("date")
    if date is not None and not isinstance(date, str):
        errors.append(f"{prefix}.date must be an ISO timestamp string")
    _validate_commit_artifacts(commit.get("artifacts"), errors, prefix)


def validate_history_index(path: Path) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"{path} does not exist"]
    except json.JSONDecodeError as exc:
        return [f"{path} is not valid JSON: {exc}"]

    errors: list[str] = []
    if not isinstance(data, dict):
        return [f"{path} must contain a JSON object at the top level"]

    if "generated_at" not in data:
        errors.append("generated_at is required at the top level")
    if "folder" not in data:
        errors.append("folder is required at the top level")
    commits = data.get("commits")
    if not isinstance(commits, list):
        errors.append("commits must be an array at the top level")
    else:
        for idx, commit in enumerate(commits):
            _validate_commit_entry(commit, idx, errors)

    return errors


def _build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate size report CSV files or history index manifests."
    )
    subparsers = parser.add_subparsers(dest="command")

    history_parser = subparsers.add_parser(
        "history",
        help="Validate a folder history manifest (index.json).",
    )
    history_parser.add_argument(
        "path",
        type=Path,
        help="Path to a folder-level index.json file.",
    )

    return parser


def _run_cli(args: argparse.Namespace) -> int:
    if args.command == "history":
        errors = validate_history_index(args.path)
        if errors:
            for error in errors:
                print(f"[history-chart] {error}", file=sys.stderr)
            return 1
        print(f"[history-chart] {args.path} ✓ valid")
        return 0

    print("No command specified. Try '--help' for usage.", file=sys.stderr)
    return 1


def main() -> int:
    parser = _build_cli()
    args = parser.parse_args()
    return _run_cli(args)


if __name__ == "__main__":
    sys.exit(main())
