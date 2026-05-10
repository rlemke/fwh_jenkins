#!/usr/bin/env python3
"""run-tests — simulate running a test suite."""

from __future__ import annotations

import argparse
import json
import sys

from jenkins_pipeline.tools._lib.test import run_tests


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--framework", default="junit")
    p.add_argument("--suite", default="unit")
    args = p.parse_args()

    print(f"RunTests: {args.framework}/{args.suite}", file=sys.stderr)
    result = run_tests(framework=args.framework, suite=args.suite)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
