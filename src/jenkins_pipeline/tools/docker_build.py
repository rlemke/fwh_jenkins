#!/usr/bin/env python3
"""docker-build — simulate `docker build -t <image_tag>`."""

from __future__ import annotations

import argparse
import json
import sys

from jenkins_pipeline.tools._lib.build import docker_build


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--image-tag", default="app:latest", dest="image_tag")
    p.add_argument("--dockerfile", default="Dockerfile")
    p.add_argument("--workspace", default="/var/jenkins/workspace/app", dest="workspace_path")
    args = p.parse_args()

    print(f"DockerBuild: {args.image_tag}", file=sys.stderr)
    result = docker_build(
        image_tag=args.image_tag,
        dockerfile=args.dockerfile,
        workspace_path=args.workspace_path,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
