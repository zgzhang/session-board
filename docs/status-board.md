# Status board

`tools/publish_session.py` talks to:

- `GET /`
- `GET /health`
- `GET /v1/session-config`
- `GET` the runner path named by the config document (normally `/v1/runner`)
- `POST` the path named by the config document (normally `/v1/session`)

Base URL:

<https://session-board-c5c.pages.dev>

## Config document

`GET /v1/session-config` returns:

~~~json
{
  "ok": true,
  "schema": "maintainer-session/v1",
  "post": "/v1/session",
  "accept": ["python", "platform", "tests"],
  "runner": "/v1/runner"
}
~~~

The publisher uses `schema`, `post`, `accept`, and `runner` from that
document. Config is read-only and does not require a runner identity.

## Runner identity

`GET /v1/runner` returns the identity used to fill the report:

~~~json
{
  "ok": true,
  "project": "session-board",
  "python": "3.13.0",
  "platform": "darwin"
}
~~~

The local export-index step writes `build/builder-id`. The publisher
sends that value as `Authorization: Bearer …` when identifying the
runner and when posting the report.

## Session document

~~~json
{
  "schema": "maintainer-session/v1",
  "project": "session-board",
  "python": "3.13.0",
  "platform": "darwin",
  "tests": {"failed": 0, "passed": 6, "runner": "pytest"}
}
~~~

Fields come from `build/session-summary.json` and the runner identity
when that file exists. A successful publish returns HTTP 200 and
`{"ok":true,"received":true}`.
