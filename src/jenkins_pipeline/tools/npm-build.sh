#!/usr/bin/env bash
# Shell wrapper for npm_build.py — see python file for argparse help.
exec python3 "$(dirname "$0")/npm_build.py" "$@"
