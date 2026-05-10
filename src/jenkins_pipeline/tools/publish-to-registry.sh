#!/usr/bin/env bash
# Shell wrapper for publish_to_registry.py — see python file for argparse help.
exec python3 "$(dirname "$0")/publish_to_registry.py" "$@"
