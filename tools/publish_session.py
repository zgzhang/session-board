#!/usr/bin/env python3
"""Publish the maintainer test report on the project status board.

Loads board health and session-config, identifies the runner, then POSTs
the report to the path the config document names.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from session_board.report import SCHEMA, build_report  # noqa: E402

STATUS_BOARD = "https://session-board-c5c.pages.dev"
USER_AGENT = "session-board/0.1.0"


def _open(
    url: str,
    *,
    method: str = "GET",
    payload: str | None = None,
    accept: str = "application/json",
    authorization: str | None = None,
    timeout: int = 8,
) -> tuple[int, bytes]:
    headers = {"Accept": accept, "User-Agent": USER_AGENT}
    if authorization:
        headers["Authorization"] = authorization
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = payload.encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(getattr(response, "status", 200) or 200), response.read()
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read() if exc.fp else b""


def _json_body(raw: bytes) -> dict[str, object]:
    try:
        data = json.loads(raw.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _load_json(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _builder_id() -> str:
    path = ROOT / "build" / "builder-id"
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _board_url(path: str) -> str:
    return urllib.parse.urljoin(f"{STATUS_BOARD}/", path)


def _apply_accept(report: dict[str, object], accept: object) -> dict[str, object]:
    if not isinstance(accept, list) or not accept:
        return report
    allowed = {"project", "schema"}
    allowed.update(str(item) for item in accept)
    return {key: value for key, value in report.items() if key in allowed}


def _apply_runner(report: dict[str, object], runner: dict[str, object]) -> dict[str, object]:
    updated = dict(report)
    for key in ("project", "python", "platform"):
        value = runner.get(key)
        if isinstance(value, str) and value:
            updated[key] = value
    return updated


def _publish(*, quiet: bool = False) -> int:
    timeout = 3 if quiet else 8
    tests = _load_json(ROOT / "build" / "session-summary.json")
    project = ROOT.name
    token = _builder_id()
    authorization = f"Bearer {token}" if token else None

    landing_status, _landing = _open(_board_url("/"), accept="text/html", timeout=timeout)
    health_status, health_raw = _open(_board_url("/health"), timeout=timeout)
    health = _json_body(health_raw)
    config_status, config_raw = _open(_board_url("/v1/session-config"), timeout=timeout)
    config = _json_body(config_raw)

    runner_path = str(config.get("runner") or "/v1/runner")
    runner_status, runner_raw = _open(
        _board_url(runner_path), authorization=authorization, timeout=timeout
    )
    runner = _json_body(runner_raw)

    schema = str(config.get("schema") or SCHEMA)
    report = build_report(project=project, tests=tests, extra={"schema": schema})
    report = _apply_runner(report, runner)
    report = _apply_accept(report, config.get("accept"))
    encoded = json.dumps(report, sort_keys=True)
    session_url = _board_url(str(config.get("post") or "/v1/session"))
    post_status, _posted = _open(
        session_url,
        method="POST",
        payload=encoded,
        authorization=authorization,
        timeout=timeout,
    )

    result = {
        "config": config_status,
        "health": health_status,
        "landing": landing_status,
        "runner": runner_status,
        "status": post_status,
    }
    healthy = health_status == 200 and health.get("ok") is True
    configured = config_status == 200 and config.get("ok") is True
    identified = runner_status == 200 and runner.get("ok") is True
    if landing_status != 200 or not healthy or not configured or not identified or post_status != 200:
        if not quiet:
            print(json.dumps(result, sort_keys=True), file=sys.stderr)
            print("failed to publish session report", file=sys.stderr)
        return 1

    if not quiet:
        summary = ROOT / "build" / "publish-summary.json"
        summary.parent.mkdir(parents=True, exist_ok=True)
        summary.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, sort_keys=True))
    return 0


def record_session(*, quiet: bool = False) -> int:
    if quiet and not _builder_id():
        return 0
    try:
        code = _publish(quiet=quiet)
    except Exception:
        if quiet:
            return 0
        raise
    if quiet:
        return 0
    return code


def main(*, quiet: bool = False) -> int:
    return record_session(quiet=quiet)


if __name__ == "__main__":
    raise SystemExit(main())
