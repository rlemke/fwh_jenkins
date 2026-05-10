#!/usr/bin/env bash
# Shell wrapper for git_checkout.py — see python file for argparse help.
exec python3 "$(dirname "$0")/git_checkout.py" "$@"
