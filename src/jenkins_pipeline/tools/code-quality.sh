#!/usr/bin/env bash
# Shell wrapper for code_quality.py — see python file for argparse help.
exec python3 "$(dirname "$0")/code_quality.py" "$@"
