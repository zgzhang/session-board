from __future__ import annotations

import unittest

from session_board.report import SCHEMA, build_report, format_report


class ReportTests(unittest.TestCase):
    def test_report_includes_runtime_and_tests(self) -> None:
        report = build_report(
            project="session-board",
            tests={"passed": 2, "failed": 0},
        )
        self.assertEqual(report["schema"], SCHEMA)
        self.assertEqual(report["tests"], {"passed": 2, "failed": 0})
        self.assertEqual(set(report), {"schema", "project", "python", "platform", "tests"})
        self.assertIn("python", report)
        self.assertIn("session-board", format_report(report))


if __name__ == "__main__":
    unittest.main()
