#!/usr/bin/env python3
"""Quality gate: verify all config/*.json files parse as valid JSON.

Tooling only — no project business logic. Exits non-zero if any config file is
invalid or if no config files are found. Paths are relative to the repo root.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"


def invalid_configs() -> list[tuple[str, str]]:
    """Return (filename, error) for each config file that fails to parse."""
    problems: list[tuple[str, str]] = []
    for path in sorted(CONFIG_DIR.glob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append((path.name, str(exc)))
    return problems


def main() -> int:
    files = sorted(CONFIG_DIR.glob("*.json"))
    if not files:
        print("ERROR: no config/*.json files found.")
        return 1
    problems = invalid_configs()
    if problems:
        print("INVALID config JSON:")
        for name, err in problems:
            print(f"  - {name}: {err}")
        return 1
    print(f"OK: all {len(files)} config JSON files valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
