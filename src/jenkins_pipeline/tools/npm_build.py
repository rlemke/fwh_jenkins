#!/usr/bin/env python3
"""npm-build — simulate `npm run <script>` (npm/node build)."""

from __future__ import annotations

import argparse
import json
import sys

from jenkins_pipeline.tools._lib.build import npm_build


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--workspace", default="/var/jenkins/workspace/app", dest="workspace_path")
    p.add_argument("--script", default="build", dest="build_script")
    p.add_argument("--node-version", default="20", dest="node_version")
    args = p.parse_args()

    print(f"NpmBuild: {args.build_script} in {args.workspace_path}", file=sys.stderr)
    result = npm_build(
        workspace_path=args.workspace_path,
        build_script=args.build_script,
        node_version=args.node_version,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
