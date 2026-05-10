#!/usr/bin/env python3
"""rollback-deploy — simulate rolling back a previous deploy."""

from __future__ import annotations

import argparse
import json
import sys

from jenkins_pipeline.tools._lib.deploy import rollback_deploy


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--deploy-id", required=True, dest="deploy_id")
    p.add_argument("--environment", default="staging")
    args = p.parse_args()

    print(f"RollbackDeploy: {args.deploy_id}", file=sys.stderr)
    result = rollback_deploy(deploy_id=args.deploy_id, environment=args.environment)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
