from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from session_board.inbox import list_names


class InboxTests(unittest.TestCase):
    def test_list_names_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "b.txt").write_text("x", encoding="utf-8")
            (folder / "a.csv").write_text("y", encoding="utf-8")
            names = list_names(folder)
            self.assertEqual(names, ["a.csv", "b.txt"])

    def test_missing_folder_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(NotADirectoryError):
                list_names(Path(tmp) / "missing")


if __name__ == "__main__":
    unittest.main()
