# Notify (Slack / email)

**Namespace:** `jenkins.notify` ·
**FFL:** `src/jenkins_pipeline/ffl/jenkins_notify.ffl` ·
**Handlers:** `src/jenkins_pipeline/handlers/notify_handlers.py` ·
**Simulator:** `src/jenkins_pipeline/tools/_lib/notify.py` ·
**CLIs:** `tools/{slack-notify,email-notify}.{py,sh}`

## Overview

`jenkins.notify` is the **announce stage** — sending a Slack message or email on
a pipeline event (typically the final "deployed" notification). Two facets:
`SlackNotify` and `EmailNotify`. Each is a **deterministic simulator** returning
a delivery confirmation without sending anything.

## How it works

Unlike the other namespaces, notify facets return a **flat tuple**, not a
schema — so the handlers return the fields directly (no outer wrapping key):

- `SlackNotify` → `slack_notify(channel, message)` → handler returns `{"sent":
  True, "timestamp": "1708100000.000100"}`.
- `EmailNotify` → `email_notify(recipients, subject, body)` → handler returns
  `{"sent": True, "message_id": "<20240216120000.ABC123@jenkins.example.com>"}`.

Both always report `sent: True`.

## Fan-out

**Single-task per call — no fan-out.**

## Data & fields

These facets have **no `jenkins.types` schema** — their return clauses are inline
tuples: `SlackNotify => (sent: Boolean, timestamp: String)` and `EmailNotify =>
(sent: Boolean, message_id: String)`. The simulators return constant `timestamp`
/ `message_id` values; only `channel`/`recipients`/`subject` echo the inputs (and
those are dropped from the handler's return, which forwards just `sent` +
`timestamp`/`message_id`).

## External libraries / binaries

**None.** No Slack SDK, webhook client, or SMTP library — pure-stdlib
simulators.

## Facets & workflows

| Facet | Kind | Effect / Cost | Signature |
|---|---|---|---|
| `SlackNotify` | event | external / **cheap** | `SlackNotify(channel: String, message: String, color="good", mention="") => (sent: Boolean, timestamp: String)` |
| `EmailNotify` | event | external / **cheap** | `EmailNotify(recipients: String, subject: String, body: String, attach_log: Boolean = false) => (sent: Boolean, message_id: String)` |

Both are the cheapest external facets in the package. `SlackNotify` is used by
`DockerK8sDeploy`, `JavaMavenCI`-adjacent flows, and `FullCIPipeline` (the final
"Pipeline complete: …" message assembled with `++`).

## Cache / output

**No cache, no durable output.** No message is delivered; the returned
`timestamp`/`message_id` are simulated constants. CLI prints JSON.

## Gotchas & notes

- **Tuple returns, not schema wrapping.** These are the only two handlers that do
  **not** wrap under `result`/`info`/`report`/`artifact` — they return the tuple
  fields flat because the FFL return clause is an inline `(sent, …)` tuple, not a
  named schema. Keep this in mind when adding a notify facet.
- **`color`, `mention`, `body`, `attach_log` are declared but the simulator
  ignores them** (shape parity; the handler doesn't forward them either).
- **`sent` is always `True`** — a simulated notification never fails.

## Related specs

- [pipelines](pipelines.md) — the release-announcement step. · [deploy](deploy.md)
  — the event being announced. · [types](types.md) — note these two facets are
  the exception that uses no schema.
