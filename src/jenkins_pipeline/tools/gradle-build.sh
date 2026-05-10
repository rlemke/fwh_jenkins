#!/usr/bin/env bash
# Shell wrapper for gradle_build.py — see python file for argparse help.
exec python3 "$(dirname "$0")/gradle_build.py" "$@"
