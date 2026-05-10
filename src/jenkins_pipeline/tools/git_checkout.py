#!/usr/bin/env python3
"""git-checkout — clone a repository at a branch (simulator).

Prints the simulated SCM result as JSON on stdout, with a one-line human
summary on stderr.
"""

from __future__ import annotations

import argparse
import json
import sys

from jenkins_pipeline.tools._lib.scm import git_checkout


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--repo", required=True, help="Repository URL or slug (e.g. github.com/example/app)")
    p.add_argument("--branch", default="main", help="Branch to check out (default: main)")
    args = p.parse_args()

    print(f"GitCheckout: {args.repo}@{args.branch}", file=sys.stderr)
    result = git_checkout(repo=args.repo, branch=args.branch)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
