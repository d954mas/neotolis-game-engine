#!/usr/bin/env python3
"""
Instrumentation verification for the size-report CLI.

This script runs `reports/size/update.py` against a temporary dataset and
asserts that the CLI emits log lines containing measured sizes and alert
threshold markers. It is intended to be executed by CI (T023) and by
developers before landing changes that touch the size reporting workflow.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Unable to locate repository root (missing .git directory)")


def ensure_seed_report(report_path: Path) -> None:
    """Create a minimal CSV with a placeholder MASTER row."""
    seed = "\n".join(
        [
            "git_ref,file_name,size_bytes,git_sha,git_message",
            "MASTER,,,UNKNOWN,UNKNOWN",
        ]
    )
    report_path.write_text(f"{seed}\n", encoding="utf-8")


def main() -> int:
    script_path = Path(__file__).resolve()
    repo_root = find_repo_root(script_path.parent)
    reports_root = repo_root / "reports" / "size"
    fixtures_root = repo_root / "tests" / "size" / "fixtures" / "sandbox_wasm_debug"

    if not (reports_root / "update.py").exists():
        raise FileNotFoundError("reports/size/update.py not found – CLI scaffold missing?")
    if not fixtures_root.exists():
        raise FileNotFoundError("Fixture directory tests/size/fixtures/sandbox_wasm_debug is missing")

    manifest_path = reports_root / "index.json"
    original_manifest = manifest_path.read_text(encoding="utf-8") if manifest_path.exists() else None

    try:
        with tempfile.TemporaryDirectory(dir=reports_root) as temp_root_str:
            temp_root = Path(temp_root_str)
            target_folder = temp_root / "instrumentation"
            target_folder.mkdir(parents=True, exist_ok=True)

            # Seed artifacts
            for artifact in fixtures_root.iterdir():
                shutil.copy2(artifact, target_folder / artifact.name)

            ensure_seed_report(target_folder / "report.txt")

            relative_folder = f"{target_folder.relative_to(reports_root)}"
            result = subprocess.run(
                ["python3", str(reports_root / "update.py"), "--folder", relative_folder],
                cwd=repo_root,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    "Size-report CLI exited with a non-zero status:\n"
                    f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
                )

            stdout = result.stdout.strip().splitlines()
            size_line_present = any("master=" in line and "head=" in line for line in stdout)
            threshold_line_present = any("thresholds=" in line and "none" not in line for line in stdout)

            if not size_line_present or not threshold_line_present:
                raise AssertionError(
                    "CLI output missing instrumentation details. "
                    "Expect lines with measured sizes and alert thresholds.\n"
                    f"Captured stdout:\n{result.stdout}"
                )
    finally:
        # Restore manifest to avoid polluting tracked files
        if original_manifest is not None:
            manifest_path.write_text(original_manifest, encoding="utf-8")
        elif manifest_path.exists():
            manifest_path.unlink()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
