#!/usr/bin/env python3
"""code-quality — simulate a code quality analysis run."""

from __future__ import annotations

import argparse
import json
import sys

from jenkins_pipeline.tools._lib.test import code_quality


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--tool", default="sonarqube")
    p.add_argument("--workspace", default="/var/jenkins/workspace/app", dest="workspace_path")
    args = p.parse_args()

    print(f"CodeQuality: {args.tool}", file=sys.stderr)
    result = code_quality(tool=args.tool, workspace_path=args.workspace_path)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
