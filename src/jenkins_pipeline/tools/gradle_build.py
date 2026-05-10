#!/usr/bin/env python3
"""gradle-build — simulate a Gradle build (gradle <tasks>)."""

from __future__ import annotations

import argparse
import json
import sys

from jenkins_pipeline.tools._lib.build import gradle_build


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--workspace", default="/var/jenkins/workspace/app", dest="workspace_path")
    p.add_argument("--tasks", default="build")
    p.add_argument("--jdk", default="17", dest="jdk_version")
    args = p.parse_args()

    print(f"GradleBuild: {args.tasks} in {args.workspace_path}", file=sys.stderr)
    result = gradle_build(
        workspace_path=args.workspace_path,
        tasks=args.tasks,
        jdk_version=args.jdk_version,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
