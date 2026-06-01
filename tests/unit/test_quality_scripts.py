"""Quality tests: the quality scripts run successfully on this repository.

No business logic — these only invoke the tooling scripts and assert exit code 0.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = [
    "check_required_docs.py",
    "check_file_lengths.py",
    "check_json_configs.py",
]


@pytest.mark.parametrize("script", SCRIPTS)
def test_quality_script_runs_clean(script: str) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
