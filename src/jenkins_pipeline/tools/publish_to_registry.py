#!/usr/bin/env python3
"""publish-to-registry — simulate publishing an artifact to a registry."""

from __future__ import annotations

import argparse
import json
import sys

from jenkins_pipeline.tools._lib.artifact import publish_to_registry


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--registry", default="https://registry.example.com", dest="registry_url")
    p.add_argument("--version", default="1.0.0")
    p.add_argument("--group-id", default="com.example", dest="group_id")
    p.add_argument("--artifact-path", default="/target/app.jar", dest="artifact_path")
    args = p.parse_args()

    print(f"PublishToRegistry: v{args.version} -> {args.registry_url}", file=sys.stderr)
    result = publish_to_registry(
        registry_url=args.registry_url,
        version=args.version,
        group_id=args.group_id,
        artifact_path=args.artifact_path,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
