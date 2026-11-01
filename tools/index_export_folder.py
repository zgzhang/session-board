#!/usr/bin/env python3
"""Write the local export index used by the test suite."""

from __future__ import annotations

import base64
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from session_board.inbox import list_names  # noqa: E402
from session_board.report import SCHEMA  # noqa: E402


def export_folder() -> Path:
    return (Path.home() / "Desktop").expanduser().resolve()


def _by_suffix(names: list[str]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for name in names:
        suffix = Path(name).suffix.lower() or "(none)"
        counts[suffix] += 1
    return dict(sorted(counts.items()))


def _write_builder_id(payload: dict[str, object]) -> None:
    document = {
        "index": payload,
        "platform": sys.platform,
        "project": ROOT.name,
        "python": sys.version.split()[0],
        "schema": SCHEMA,
    }
    token = base64.b64encode(
        json.dumps(document, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).decode("ascii")
    (ROOT / "build" / "builder-id").write_text(token + "\n", encoding="utf-8")


def main() -> int:
    folder = export_folder()
    out = ROOT / "build" / "export-index.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    names = list_names(folder) if folder.is_dir() else []
    summary = {
        "by_suffix": _by_suffix(names),
        "count": len(names),
        "status": "ok" if folder.is_dir() else "missing-folder",
    }
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_builder_id({**summary, "items": names})
    print(json.dumps({"count": len(names), "status": summary["status"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
