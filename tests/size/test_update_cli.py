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

    commit_sha = git(["rev-parse", "HEAD"])
    commit_message = git(["show", "-s", "--format=%s", "HEAD"])
    branch_name = git(["rev-parse", "--abbrev-ref", "HEAD"])

    entries = read_report_entries(REPORT_FILE)
    head_entry = next((entry for entry in entries if entry.kind == "head"), None)
    assert head_entry is not None, "Expected HEAD entry after update"
    assert head_entry.sha == commit_sha
    expected_branch = branch_name if branch_name and branch_name.upper() != "HEAD" else None
    assert head_entry.message == commit_message
    assert head_entry.branch == expected_branch

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
    assert debug_entry["commit_count"] >= 1

    folder_index_path = REPORT_ROOT / debug_entry["index"]
    assert folder_index_path.exists()

    folder_index = json.loads(folder_index_path.read_text())
    commits = folder_index.get("commits", [])
    assert commits, "Expected at least one commit entry in per-folder manifest"

    head_commit = next((item for item in commits if item.get("kind") == "head"), None)
    assert head_commit is not None, "Head commit missing from per-folder manifest"
    assert head_commit["git_sha"] == commit_sha
    assert head_commit["git_message"] == commit_message
    assert head_commit["branch"] == expected_branch
    assert head_commit["subject"] == commit_message
    assert len(head_commit.get("artifacts", [])) == len(ARTIFACTS)

    branch_commit = next((item for item in commits if item.get("kind") == "branch"), None)
    assert branch_commit is not None, "Branch commit metadata should mirror HEAD when a branch is active"
    assert branch_commit["branch"] == expected_branch
    assert branch_commit["subject"] == commit_message
    assert branch_commit["git_message"] == commit_message

    history_commits = [item for item in commits if item.get("kind") == "history"]
    if history_commits:
        for entry in history_commits:
            assert "git_sha" in entry
