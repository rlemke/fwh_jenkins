#!/usr/bin/env bash
# Shell wrapper for security_scan.py — see python file for argparse help.
exec python3 "$(dirname "$0")/security_scan.py" "$@"
