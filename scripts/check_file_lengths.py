#!/usr/bin/env python3
"""Quality gate: enforce a maximum line count for Python files.

Tooling only — no project business logic. Checks Python files under src/, tests/,
and scripts/; exits non-zero if any exceeds the limit. Generated/venv/cache files
are ignored. Paths are relative to the repository root.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_LINES = 150
CHECK_DIRS = ("src", "tests", "scripts")
IGNORE_PARTS = {
    ".venv",
    "__pycache__",
    ".ruff_cache",
    ".pytest_cache",
    ".mypy_cache",
    "build",
    "dist",
    ".git",
}


def python_files() -> list[Path]:
    """Collect Python files in the checked directories, skipping ignored paths."""
    found: list[Path] = []
    for name in CHECK_DIRS:
        base = ROOT / name
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            if IGNORE_PARTS.isdisjoint(path.parts):
                found.append(path)
    return found


def count_lines(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def main() -> int:
    violations: list[tuple[Path, int]] = []
    for path in python_files():
        lines = count_lines(path)
        if lines > MAX_LINES:
            violations.append((path.relative_to(ROOT), lines))
    if violations:
        print(f"FILE-SIZE violations (> {MAX_LINES} lines):")
        for rel, lines in violations:
            print(f"  - {rel}: {lines} lines")
        return 1
    print(f"OK: all checked Python files <= {MAX_LINES} lines.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
