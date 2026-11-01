"""List direct child names of a folder."""

from __future__ import annotations

from pathlib import Path


def list_names(folder: Path) -> list[str]:
    folder = folder.expanduser().resolve()
    if not folder.is_dir():
        raise NotADirectoryError(folder)
    return sorted(item.name for item in folder.iterdir())
