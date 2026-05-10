#!/usr/bin/env bash
# Shell wrapper for run_tests.py — see python file for argparse help.
exec python3 "$(dirname "$0")/run_tests.py" "$@"
