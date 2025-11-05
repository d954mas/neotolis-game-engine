"""Validation helpers for size-report CSV files."""
from __future__ import annotations

from dataclasses import dataclass
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
