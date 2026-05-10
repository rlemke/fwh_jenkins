#!/usr/bin/env python3
"""email-notify — simulate sending an email notification."""

from __future__ import annotations

import argparse
import json
import sys

from jenkins_pipeline.tools._lib.notify import email_notify


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--recipients", required=True, help="Comma-separated email addresses")
    p.add_argument("--subject", required=True)
    p.add_argument("--body", default="")
    args = p.parse_args()

    print(f"EmailNotify: {args.subject}", file=sys.stderr)
    result = email_notify(recipients=args.recipients, subject=args.subject, body=args.body)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
