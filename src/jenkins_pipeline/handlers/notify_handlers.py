"""Jenkins notification event facet handlers.

Handles SlackNotify and EmailNotify event facets from the jenkins.notify
namespace. Simulators live in ``jenkins_pipeline.tools._lib.notify``
(also reachable via the ``slack-notify`` and ``email-notify`` CLIs).
"""

import logging
import os
from typing import Any

from .shared.jenkins_utils import email_notify, slack_notify

log = logging.getLogger(__name__)

NAMESPACE = "jenkins.notify"


def _slack_notify_handler(payload: dict) -> dict[str, Any]:
    """Send a Slack notification."""
    step_log = payload.get("_step_log")
    channel = payload.get("channel", "#general")
    message = payload.get("message", "")
    if step_log:
        step_log(f"SlackNotify: {channel}")
    result = slack_notify(channel=channel, message=message)
    return {"sent": result["sent"], "timestamp": result["timestamp"]}


def _email_notify_handler(payload: dict) -> dict[str, Any]:
    """Send an email notification."""
    step_log = payload.get("_step_log")
    recipients = payload.get("recipients", "")
    subject = payload.get("subject", "")
    if step_log:
        step_log(f"EmailNotify: {subject}")
    result = email_notify(recipients=recipients, subject=subject)
    return {"sent": result["sent"], "message_id": result["message_id"]}


# RegistryRunner dispatch adapter
_DISPATCH = {
    f"{NAMESPACE}.SlackNotify": _slack_notify_handler,
    f"{NAMESPACE}.EmailNotify": _email_notify_handler,
}


def handle(payload: dict) -> dict:
    """RegistryRunner dispatch entrypoint."""
    facet_name = payload["_facet_name"]
    handler = _DISPATCH.get(facet_name)
    if handler is None:
        raise ValueError(f"Unknown facet: {facet_name}")
    return handler(payload)


def register_handlers(runner) -> None:
    """Register all facets with a RegistryRunner."""
    for facet_name in _DISPATCH:
        runner.register_handler(
            facet_name=facet_name,
            module_uri=f"file://{os.path.abspath(__file__)}",
            entrypoint="handle",
        )


def register_notify_handlers(poller) -> None:
    """Register all notify event facet handlers with the poller."""
    for fqn, func in _DISPATCH.items():
        poller.register(fqn, func)
        log.debug("Registered notify handler: %s", fqn)
