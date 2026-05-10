#!/usr/bin/env bash
# Shell wrapper for docker_build.py — see python file for argparse help.
exec python3 "$(dirname "$0")/docker_build.py" "$@"
