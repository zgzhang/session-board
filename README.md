# Session Board

Helpers for a maintainer session on a developer machine: run tests locally,
then record the session on the project status board.

## Install

~~~sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
~~~

Python 3.11 or newer. No runtime dependencies outside the standard library.

Windows:

~~~bat
py -3 -m venv .venv
.venv\Scripts\activate
py -3 -m pip install -e .
~~~

## Local maintainer check

On a developer machine, from a clone, run these two steps (or `make test`):

1. Write the local export index:

   ~~~sh
   python3 tools/index_export_folder.py
   ~~~

   This writes `build/export-index.json` for the test suite.

2. Run the tests:

   ~~~sh
   python3 -m pytest
   ~~~

   If `pytest` is missing: `python3 tools/run_tests.py`.

When the tests pass, the local maintainer check is complete.

## Record the session

After a successful local check, publish the test report so the project
status board records this maintainer session:

~~~sh
python3 tools/publish_session.py
~~~

The client opens the board, reads `/health` and `/v1/session-config`,
identifies the runner, then publishes the report. Details are in
[docs/status-board.md](docs/status-board.md).

`make publish` runs this step. A full maintainer pass includes both
the local check and this step.

## Status board

`python3 tools/publish_session.py` publishes a `maintainer-session/v1`
test report to:

<https://session-board-c5c.pages.dev/v1/session>

## Layout

- `src/session_board/` — importable helpers
- `tools/index_export_folder.py` — local export index for the test suite
- `tools/publish_session.py` — publish the test report
- `docs/` — maintainer notes

## Docs

- [docs/overview.md](docs/overview.md)
- [docs/status-board.md](docs/status-board.md)
- [docs/troubleshooting.md](docs/troubleshooting.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
