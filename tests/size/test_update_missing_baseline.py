import subprocess
from pathlib import Path

import pytest

from reports.size.update import PLACEHOLDER_SHA, read_report_entries
REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_ROOT = REPO_ROOT / "reports" / "size"
TARGET_FOLDER = REPORT_ROOT / "sandbox" / "wasm" / "debug"
REPORT_FILE = TARGET_FOLDER / "report.txt"

PLACEHOLDER_WITHOUT_MASTER = """git_sha,git_message,file_name,size_bytes
HEAD,,,
"""


@pytest.fixture(autouse=True)
def reset_report_file():
    original = REPORT_FILE.read_text()
    REPORT_FILE.write_text(PLACEHOLDER_WITHOUT_MASTER)
    try:
        yield
    finally:
        REPORT_FILE.write_text(original)


def test_missing_master_placeholder_is_not_reintroduced():
    result = subprocess.run(
        [
            "python3",
            str(REPORT_ROOT / "update.py"),
            "--input",
            str(TARGET_FOLDER),
            "--output",
            "sandbox/wasm/debug",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr

    entries = read_report_entries(REPORT_FILE)
    master_entry = next((entry for entry in entries if entry.kind == "master"), None)
    assert master_entry is None, "MASTER rows should not be recreated when they are missing"

    head_entry = next((entry for entry in entries if entry.kind == "head"), None)
    assert head_entry is not None, "Expected HEAD entry after update"
    assert head_entry.sha != PLACEHOLDER_SHA, "HEAD entry should resolve to the current commit SHA"
