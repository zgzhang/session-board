# Overview

Session Board records a maintainer test session as a few small JSON files.
The local check finishes when tests pass. Recording the session on the
status board is a separate step.

| Step | Command | What it does |
| --- | --- | --- |
| Local 1 | `python3 tools/index_export_folder.py` | Write `build/export-index.json` for the test suite |
| Local 2 | `python3 -m pytest` | Run the test suite and write `build/session-summary.json` |
| Record | `python3 tools/publish_session.py` | Load board config and runner identity, then publish the test report |

`make test` runs the local steps. `make publish` records the session.

The library helpers in `session_board` list a folder you pass in, or assemble a
report dict. Network access lives in `tools/publish_session.py`.
