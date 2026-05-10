#!/usr/bin/env python3
"""docker-push — simulate pushing a Docker image to a registry."""

from __future__ import annotations

import argparse
import json
import sys

from jenkins_pipeline.tools._lib.artifact import docker_push


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--image-tag", default="app:latest", dest="image_tag")
    p.add_argument("--registry", default="registry.example.com", dest="registry_url")
    args = p.parse_args()

    print(f"DockerPush: {args.image_tag}", file=sys.stderr)
    result = docker_push(image_tag=args.image_tag, registry_url=args.registry_url)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
