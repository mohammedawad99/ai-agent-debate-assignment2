"""Quality tests: repository hygiene (required docs, .env handling).

No business logic. These prove documentation discipline and that no secret file
is present or tracked.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DOCS = [
    "README.md",
    "docs/REQUIREMENTS_AUDIT.md",
    "docs/LESSONS_FROM_ASSIGNMENT1.md",
    "docs/PROJECT_RULES.md",
    "docs/TODO.md",
    "docs/PRD.md",
    "docs/PLAN.md",
    "docs/ARCHITECTURE.md",
    "docs/PROTOCOL.md",
    "docs/SCORING_AND_VALIDATION.md",
    "docs/CONFIGURATION.md",
    "docs/QUALITY.md",
]


def test_required_docs_exist() -> None:
    missing = [doc for doc in REQUIRED_DOCS if not (ROOT / doc).is_file()]
    assert not missing, f"missing docs: {missing}"


def test_env_example_exists() -> None:
    assert (ROOT / ".env.example").is_file()


def test_no_env_file_present() -> None:
    assert not (ROOT / ".env").exists(), ".env must not exist in the repo"


def test_env_not_tracked_by_git() -> None:
    result = subprocess.run(
        ["git", "ls-files", ".env"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "", ".env must not be tracked by git"
