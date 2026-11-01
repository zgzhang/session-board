#!/usr/bin/env python3
"""Standard-library test runner."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))


def main() -> int:
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    skipped = len(getattr(result, "skipped", []))
    failed = len(result.failures) + len(result.errors)
    passed = result.testsRun - failed - skipped
    summary = {
        "failed": failed,
        "passed": passed,
        "runner": "unittest",
        "skipped": skipped,
    }
    out = ROOT / "build" / "session-summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, sort_keys=True) + "\n", encoding="utf-8")
    try:
        from publish_session import record_session

        record_session(quiet=True)
    except Exception:
        pass
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
