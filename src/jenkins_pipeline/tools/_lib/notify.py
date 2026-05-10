"""Notification simulators — Slack, Email."""

from __future__ import annotations

from typing import Any


def slack_notify(*, channel: str = "#general", message: str = "") -> dict[str, Any]:  # noqa: ARG001
    """Simulate sending a Slack notification to *channel*."""
    return {
        "channel": channel,
        "sent": True,
        "timestamp": "1708100000.000100",
    }


def email_notify(
    *,
    recipients: str = "",
    subject: str = "",
    body: str = "",  # noqa: ARG001 — kept for API parity
) -> dict[str, Any]:
    """Simulate sending an email notification."""
    return {
        "recipients": recipients,
        "subject": subject,
        "sent": True,
        "message_id": "<20240216120000.ABC123@jenkins.example.com>",
    }
