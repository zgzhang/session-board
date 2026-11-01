"""Assemble a maintainer session report from local pieces."""

from __future__ import annotations

import json
import sys

SCHEMA = "maintainer-session/v1"


def build_report(
    *,
    project: str,
    tests: dict[str, object] | None = None,
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    report: dict[str, object] = {
        "schema": SCHEMA,
        "project": project,
        "python": sys.version.split()[0],
        "platform": sys.platform,
        "tests": tests or {},
    }
    if extra:
        report.update(extra)
    return report


def format_report(report: dict[str, object]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)
