#!/usr/bin/env python3
"""Quality gate: verify all required project documents exist.

Tooling only — no project business logic. Exits non-zero if any required doc is
missing. Paths are resolved relative to the repository root (this file's parent's
parent), never hardcoded as absolute.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

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


def find_missing() -> list[str]:
    """Return required docs that are not present as files."""
    return [doc for doc in REQUIRED_DOCS if not (ROOT / doc).is_file()]


def main() -> int:
    missing = find_missing()
    if missing:
        print("MISSING required docs:")
        for doc in missing:
            print(f"  - {doc}")
        return 1
    print(f"OK: all {len(REQUIRED_DOCS)} required docs present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
