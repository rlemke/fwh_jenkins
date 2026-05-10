#!/usr/bin/env python3
"""archive-artifacts — simulate archiving build artifacts."""

from __future__ import annotations

import argparse
import json
import sys

from jenkins_pipeline.tools._lib.artifact import archive_artifacts


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--workspace", default="/var/jenkins/workspace/app", dest="workspace_path")
    p.add_argument("--includes", default="**/*.jar")
    args = p.parse_args()

    print(f"ArchiveArtifacts: {args.workspace_path}", file=sys.stderr)
    result = archive_artifacts(workspace_path=args.workspace_path, includes=args.includes)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
