#!/usr/bin/env python3
"""maven-build — simulate a Maven build (mvn <goals>)."""

from __future__ import annotations

import argparse
import json
import sys

from jenkins_pipeline.tools._lib.build import maven_build


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--workspace", default="/var/jenkins/workspace/app", dest="workspace_path")
    p.add_argument("--goals", default="clean package")
    p.add_argument("--jdk", default="17", dest="jdk_version")
    args = p.parse_args()

    print(f"MavenBuild: {args.goals} in {args.workspace_path}", file=sys.stderr)
    result = maven_build(
        workspace_path=args.workspace_path,
        goals=args.goals,
        jdk_version=args.jdk_version,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
