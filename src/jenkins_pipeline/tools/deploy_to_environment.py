#!/usr/bin/env python3
"""deploy-to-environment — simulate a deploy to a named environment."""

from __future__ import annotations

import argparse
import json
import sys

from jenkins_pipeline.tools._lib.deploy import deploy_to_environment


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--environment", default="staging")
    p.add_argument("--version", default="1.0.0")
    p.add_argument("--strategy", default="rolling", choices=["rolling", "blue-green", "canary"])
    args = p.parse_args()

    print(f"Deploy: {args.version} -> {args.environment} ({args.strategy})", file=sys.stderr)
    result = deploy_to_environment(
        environment=args.environment,
        version=args.version,
        strategy=args.strategy,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
