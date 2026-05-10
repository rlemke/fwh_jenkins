#!/usr/bin/env bash
# Shell wrapper for maven_build.py — see python file for argparse help.
exec python3 "$(dirname "$0")/maven_build.py" "$@"
