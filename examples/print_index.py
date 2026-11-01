#!/usr/bin/env python3
"""Pretty-print the export index written by tools/index_export_folder.py."""

from __future__ import annotations

from pathlib import Path


def main() -> int:
    path = Path(__file__).resolve().parents[1] / "build" / "export-index.json"
    if not path.is_file():
        print("no export index yet; run: python3 tools/index_export_folder.py")
        return 1
    print(path.read_text(encoding="utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
