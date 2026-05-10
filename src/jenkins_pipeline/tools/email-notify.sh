#!/usr/bin/env bash
# Shell wrapper for email_notify.py — see python file for argparse help.
exec python3 "$(dirname "$0")/email_notify.py" "$@"
