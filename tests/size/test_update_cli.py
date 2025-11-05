import json
import subprocess
from pathlib import Path

import pytest
from reports.size.update import read_report_entries

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_ROOT = REPO_ROOT / "reports" / "size"
TARGET_FOLDER = REPORT_ROOT / "sandbox" / "wasm" / "debug"
REPORT_FILE = TARGET_FOLDER / "report.txt"
INDEX_FILE = REPORT_ROOT / "index.json"
ARTIFACTS = ["index.html", "sandbox.js", "sandbox.wasm"]


def git(command: list[str]) -> str:
    result = subprocess.run(["git", *command], cwd=REPO_ROOT, check=True, capture_output=True, text=True)
    return result.stdout.strip()


@pytest.fixture(autouse=True)
def restore_report_file():
    original_report = REPORT_FILE.read_text()
    original_index = INDEX_FILE.read_text() if INDEX_FILE.exists() else None
    try:
        yield
    finally:
        REPORT_FILE.write_text(original_report)
        if original_index is None:
            if INDEX_FILE.exists():
                INDEX_FILE.unlink()
        else:
            INDEX_FILE.write_text(original_index)


def test_head_snapshot_updates_report_and_manifest(tmp_path):
    result = subprocess.run(
        ["python3", str(REPORT_ROOT / "update.py"), "--folder", "sandbox/wasm/debug"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr

    commit_sha = git(["rev-parse", "HEAD"])
    commit_message = git(["show", "-s", "--format=%s", "HEAD"])

    entries = read_report_entries(REPORT_FILE)
    head_entry = next((entry for entry in entries if entry.kind == "head"), None)
    assert head_entry is not None, "Expected HEAD entry after update"
    assert head_entry.sha == commit_sha
    assert head_entry.message == commit_message

    artifact_names = sorted(artifact.file_name for artifact in head_entry.artifacts)
    assert artifact_names == sorted(ARTIFACTS)
    for artifact in head_entry.artifacts:
        artifact_path = TARGET_FOLDER / artifact.file_name
        assert artifact_path.exists()
        assert artifact.size_bytes == artifact_path.stat().st_size

    assert INDEX_FILE.exists()
    manifest = json.loads(INDEX_FILE.read_text())
    folders = {entry["folder"]: entry for entry in manifest["folders"]}
    debug_entry = folders.get("sandbox/wasm/debug")
    assert debug_entry is not None
    assert debug_entry["head"]["git_sha"] == commit_sha
    assert debug_entry["head"]["git_message"] == commit_message
    assert len(debug_entry["artifacts"]) == len(ARTIFACTS)
