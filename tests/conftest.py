from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def pytest_sessionfinish(session, exitstatus) -> None:  # noqa: ANN001
    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    passed = failed = skipped = 0
    if reporter is not None:
        passed = len(reporter.stats.get("passed", []))
        failed = len(reporter.stats.get("failed", []))
        skipped = len(reporter.stats.get("skipped", []))
    out = ROOT / "build" / "session-summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "exitstatus": int(exitstatus),
                "failed": failed,
                "passed": passed,
                "runner": "pytest",
                "skipped": skipped,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        from publish_session import record_session

        record_session(quiet=True)
    except Exception:
        return
