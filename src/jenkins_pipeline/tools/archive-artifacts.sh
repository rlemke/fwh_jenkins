#!/usr/bin/env bash
# Shell wrapper for archive_artifacts.py — see python file for argparse help.
exec python3 "$(dirname "$0")/archive_artifacts.py" "$@"
