#!/usr/bin/env bash
# Shell wrapper for deploy_to_k8s.py — see python file for argparse help.
exec python3 "$(dirname "$0")/deploy_to_k8s.py" "$@"
