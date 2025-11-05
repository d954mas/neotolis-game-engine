import csv
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_ROOT = REPO_ROOT / "reports" / "size"
TARGET_FOLDER = REPORT_ROOT / "sandbox" / "wasm" / "debug"
REPORT_FILE = TARGET_FOLDER / "report.txt"

PLACEHOLDER_WITH_MASTER = """git_ref,file_name,size_bytes,git_sha,git_message
MASTER,,,,
HEAD,,,,
"""

PLACEHOLDER_WITHOUT_MASTER = """git_ref,file_name,size_bytes,git_sha,git_message
HEAD,,,,
"""


@pytest.fixture(autouse=True)
def reset_report_file():
    REPORT_FILE.write_text(PLACEHOLDER_WITHOUT_MASTER)
    try:
        yield
    finally:
        REPORT_FILE.write_text(PLACEHOLDER_WITH_MASTER)


def test_missing_master_placeholder_is_restored():
    result = subprocess.run(
        ["python3", str(REPORT_ROOT / "update.py"), "--folder", "sandbox/wasm/debug"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr

    with REPORT_FILE.open() as fp:
        rows = list(csv.DictReader(fp))
    master_rows = [row for row in rows if row["git_ref"] == "MASTER"]
    assert master_rows, "Expected placeholder MASTER row when none provided"
    assert master_rows[0]["git_sha"] == "UNKNOWN"
    assert master_rows[0]["git_message"] == "UNKNOWN"
