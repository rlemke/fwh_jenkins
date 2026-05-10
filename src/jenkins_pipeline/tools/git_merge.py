#!/usr/bin/env python3
"""git-merge — merge a source branch into a target branch (simulator)."""

from __future__ import annotations

import argparse
import json
import sys

from jenkins_pipeline.tools._lib.scm import git_merge


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--source-branch", required=True, dest="source_branch")
    p.add_argument("--target-branch", default="main", dest="target_branch")
    p.add_argument("--workspace", default="/var/jenkins/workspace/repo", dest="workspace_path")
    args = p.parse_args()

    print(f"GitMerge: {args.source_branch} -> {args.target_branch}", file=sys.stderr)
    result = git_merge(
        source_branch=args.source_branch,
        target_branch=args.target_branch,
        workspace_path=args.workspace_path,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
