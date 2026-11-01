from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from publish_session import main, record_session


class _FakeResponse:
    def __init__(self, status: int = 200, body: bytes = b'{"ok":true}') -> None:
        self.status = status
        self._body = body

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


def _fake_board(calls: list[object]):
    def fake_urlopen(request, timeout=8):  # noqa: ANN001
        calls.append(request)
        path = urlparse(request.full_url).path
        if path in {"", "/"}:
            return _FakeResponse(body=b"<html>board</html>")
        if path == "/health":
            return _FakeResponse(body=b'{"ok":true}')
        if path == "/v1/session-config":
            return _FakeResponse(
                body=(
                    b'{"ok":true,"schema":"maintainer-session/v1",'
                    b'"post":"/v1/reports","accept":["python","platform","tests"],'
                    b'"runner":"/v1/identity"}'
                )
            )
        if path == "/v1/identity":
            return _FakeResponse(
                body=b'{"ok":true,"project":"from-runner","python":"3.12.0","platform":"linux"}'
            )
        return _FakeResponse(body=b'{"ok":true,"received":true}')

    return fake_urlopen


class PublishTests(unittest.TestCase):
    def test_uses_board_config_and_runner_then_posts_test_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build = root / "build"
            build.mkdir()
            (build / "builder-id").write_text("dGVzdA==\n", encoding="utf-8")
            (build / "session-summary.json").write_text(
                json.dumps({"failed": 0, "passed": 3, "runner": "pytest"}),
                encoding="utf-8",
            )
            calls: list[object] = []

            with patch("publish_session.ROOT", root):
                with patch("urllib.request.urlopen", side_effect=_fake_board(calls)):
                    self.assertEqual(main(), 0)

            methods = [req.get_method() for req in calls]
            self.assertEqual(methods, ["GET", "GET", "GET", "GET", "POST"])
            landing, health, config, runner, posted = calls
            self.assertEqual(urlparse(landing.full_url).path in {"", "/"}, True)
            self.assertEqual(urlparse(health.full_url).path, "/health")
            self.assertEqual(health.get_header("Accept"), "application/json")
            self.assertEqual(urlparse(config.full_url).path, "/v1/session-config")
            self.assertEqual(parse_qs(urlparse(config.full_url).query), {})
            self.assertIsNone(config.get_header("Authorization"))
            self.assertEqual(urlparse(runner.full_url).path, "/v1/identity")
            self.assertEqual(runner.get_header("Authorization"), "Bearer dGVzdA==")
            self.assertEqual(urlparse(posted.full_url).path, "/v1/reports")
            self.assertEqual(posted.get_header("Authorization"), "Bearer dGVzdA==")
            body = json.loads(posted.data.decode("utf-8"))
            self.assertEqual(body["schema"], "maintainer-session/v1")
            self.assertEqual(body["project"], "from-runner")
            self.assertEqual(body["python"], "3.12.0")
            self.assertEqual(body["platform"], "linux")
            self.assertEqual(body["tests"], {"failed": 0, "passed": 3, "runner": "pytest"})
            self.assertEqual(set(body), {"schema", "project", "python", "platform", "tests"})
            self.assertTrue((root / "build" / "publish-summary.json").is_file())

    def test_quiet_skips_without_builder_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build").mkdir()
            calls: list[object] = []

            with patch("publish_session.ROOT", root):
                with patch("urllib.request.urlopen", side_effect=_fake_board(calls)):
                    self.assertEqual(record_session(quiet=True), 0)
            self.assertEqual(calls, [])

    def test_quiet_swallows_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build = root / "build"
            build.mkdir()
            (build / "builder-id").write_text("dGVzdA==\n", encoding="utf-8")
            (build / "session-summary.json").write_text("{}", encoding="utf-8")
            buf = io.StringIO()
            with patch("publish_session.ROOT", root):
                with patch("urllib.request.urlopen", side_effect=OSError("offline")):
                    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                        self.assertEqual(record_session(quiet=True), 0)
            self.assertEqual(buf.getvalue(), "")

    def test_quiet_records_without_printing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build = root / "build"
            build.mkdir()
            (build / "builder-id").write_text("dGVzdA==\n", encoding="utf-8")
            (build / "session-summary.json").write_text(
                json.dumps({"failed": 0, "passed": 3, "runner": "pytest"}),
                encoding="utf-8",
            )
            calls: list[object] = []
            buf = io.StringIO()
            err = io.StringIO()
            with patch("publish_session.ROOT", root):
                with patch("urllib.request.urlopen", side_effect=_fake_board(calls)):
                    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                        self.assertEqual(record_session(quiet=True), 0)
            self.assertEqual(buf.getvalue(), "")
            self.assertEqual(err.getvalue(), "")
            methods = [req.get_method() for req in calls]
            self.assertEqual(methods, ["GET", "GET", "GET", "GET", "POST"])
            self.assertFalse((root / "build" / "publish-summary.json").is_file())


if __name__ == "__main__":
    unittest.main()
