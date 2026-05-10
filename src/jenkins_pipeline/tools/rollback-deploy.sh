#!/usr/bin/env bash
# Shell wrapper for rollback_deploy.py — see python file for argparse help.
exec python3 "$(dirname "$0")/rollback_deploy.py" "$@"
