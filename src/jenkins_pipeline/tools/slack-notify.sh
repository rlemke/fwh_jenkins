#!/usr/bin/env bash
# Shell wrapper for slack_notify.py — see python file for argparse help.
exec python3 "$(dirname "$0")/slack_notify.py" "$@"
