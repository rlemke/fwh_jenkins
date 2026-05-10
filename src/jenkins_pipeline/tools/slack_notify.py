#!/usr/bin/env python3
"""slack-notify — simulate sending a Slack notification."""

from __future__ import annotations

import argparse
import json
import sys

from jenkins_pipeline.tools._lib.notify import slack_notify


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--channel", default="#general")
    p.add_argument("--message", default="")
    args = p.parse_args()

    print(f"SlackNotify: {args.channel}", file=sys.stderr)
    result = slack_notify(channel=args.channel, message=args.message)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
