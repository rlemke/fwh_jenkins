#!/usr/bin/env bash
# Shell wrapper for git_merge.py — see python file for argparse help.
exec python3 "$(dirname "$0")/git_merge.py" "$@"
