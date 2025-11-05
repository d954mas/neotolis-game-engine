"""Validation helpers for size-report CSV files."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

HEADER = ["git_ref", "file_name", "size_bytes", "git_sha", "git_message"]
ALLOWED_REFS = {"HEAD", "MASTER"}


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
    for row in rows:
        ref = row.get("git_ref", "").strip().upper()
        if ref not in ALLOWED_REFS:
            raise ValidationError(f"Invalid git_ref '{row.get('git_ref')}'")
        size = row.get("size_bytes", "").strip()
        if size and not size.isdigit():
            raise ValidationError(f"Invalid size_bytes '{size}' for ref {ref}")
        sha = row.get("git_sha", "").strip()
        if sha and sha != "UNKNOWN" and len(sha) != 40:
            raise ValidationError(f"Invalid git_sha '{sha}' for ref {ref}")


def sort_key(row: Mapping[str, str]) -> tuple[int, str]:
    ref_order = 0 if row.get("git_ref") == "MASTER" else 1
    return (ref_order, row.get("file_name") or "")
