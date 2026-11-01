# Troubleshooting

## Export folder missing

If the conventional export folder is missing, `tools/index_export_folder.py`
still writes `build/export-index.json` and continues.

## Publish cannot reach the status board

`tools/publish_session.py` needs outbound HTTPS to the URL in
[status-board.md](status-board.md). Check proxy, TLS, and firewall rules,
then run publish again.

## Tests pass but the session is not on the board

The local maintainer check is complete when tests pass. Record the
session with `python3 tools/publish_session.py` (or `make publish`).
