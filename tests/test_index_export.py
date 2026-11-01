from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from index_export_folder import main


class IndexExportTests(unittest.TestCase):
    def test_writes_summary_and_builder_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            folder = home / "export"
            folder.mkdir()
            (folder / "notes.md").write_text("placeholder-body", encoding="utf-8")
            (folder / "shot.png").write_bytes(b"\x89PNG")
            with patch("index_export_folder.ROOT", home):
                with patch("index_export_folder.export_folder", return_value=folder):
                    self.assertEqual(main(), 0)
            payload = json.loads((home / "build" / "export-index.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["count"], 2)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["by_suffix"], {".md": 1, ".png": 1})
            self.assertEqual(set(payload), {"by_suffix", "count", "status"})
            token = (home / "build" / "builder-id").read_text(encoding="utf-8").strip()
            self.assertGreater(len(token), 8)

    def test_missing_folder_writes_empty_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            missing = home / "export"
            with patch("index_export_folder.ROOT", home):
                with patch("index_export_folder.export_folder", return_value=missing):
                    self.assertEqual(main(), 0)
            payload = json.loads((home / "build" / "export-index.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["count"], 0)
            self.assertEqual(payload["status"], "missing-folder")
            self.assertEqual(payload["by_suffix"], {})
            self.assertNotIn("items", payload)
            self.assertTrue((home / "build" / "builder-id").is_file())


if __name__ == "__main__":
    unittest.main()
