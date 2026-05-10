#!/usr/bin/env python3
"""security-scan — simulate a security vulnerability scan."""

from __future__ import annotations

import argparse
import json
import sys

from jenkins_pipeline.tools._lib.test import security_scan


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--scanner", default="trivy")
    p.add_argument("--severity-threshold", default="HIGH", dest="severity_threshold")
    p.add_argument("--workspace", default="/var/jenkins/workspace/app", dest="workspace_path")
    args = p.parse_args()

    print(f"SecurityScan: {args.scanner}", file=sys.stderr)
    result = security_scan(
        scanner=args.scanner,
        severity_threshold=args.severity_threshold,
        workspace_path=args.workspace_path,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
