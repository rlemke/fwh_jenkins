#!/usr/bin/env python3
"""deploy-to-k8s — simulate a Kubernetes deploy."""

from __future__ import annotations

import argparse
import json
import sys

from jenkins_pipeline.tools._lib.deploy import deploy_to_k8s


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--cluster", default="default")
    p.add_argument("--namespace", default="default", dest="k8s_namespace")
    p.add_argument("--image-tag", default="app:latest", dest="image_tag")
    p.add_argument("--replicas", type=int, default=2)
    args = p.parse_args()

    print(f"DeployToK8s: {args.cluster}/{args.k8s_namespace}", file=sys.stderr)
    result = deploy_to_k8s(
        cluster=args.cluster,
        k8s_namespace=args.k8s_namespace,
        image_tag=args.image_tag,
        replicas=args.replicas,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
