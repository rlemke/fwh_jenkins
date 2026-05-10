"""Jenkins test event facet handlers.

Handles RunTests, CodeQuality, and SecurityScan event facets from the
jenkins.test namespace. Test simulators live in
``jenkins_pipeline.tools._lib.test`` and are also reachable via the
``run-tests``, ``code-quality``, and ``security-scan`` CLIs.
"""

import logging
import os
from typing import Any

from .shared.jenkins_utils import code_quality, run_tests, security_scan

log = logging.getLogger(__name__)

NAMESPACE = "jenkins.test"


def _run_tests_handler(payload: dict) -> dict[str, Any]:
    """Run a test suite."""
    step_log = payload.get("_step_log")
    framework = payload.get("framework", "junit")
    suite = payload.get("suite", "unit")
    if step_log:
        step_log(f"RunTests: {framework}/{suite}")
    return {"report": run_tests(framework=framework, suite=suite)}


def _code_quality_handler(payload: dict) -> dict[str, Any]:
    """Run a code quality analysis."""
    step_log = payload.get("_step_log")
    tool = payload.get("tool", "sonarqube")
    workspace = payload.get("workspace_path", "/var/jenkins/workspace/app")
    if step_log:
        step_log(f"CodeQuality: {tool}")
    return {"report": code_quality(tool=tool, workspace_path=workspace)}


def _security_scan_handler(payload: dict) -> dict[str, Any]:
    """Run a security vulnerability scan."""
    step_log = payload.get("_step_log")
    scanner = payload.get("scanner", "trivy")
    threshold = payload.get("severity_threshold", "HIGH")
    workspace = payload.get("workspace_path", "/var/jenkins/workspace/app")
    if step_log:
        step_log(f"SecurityScan: {scanner}")
    return {
        "report": security_scan(
            scanner=scanner, severity_threshold=threshold, workspace_path=workspace
        )
    }


# RegistryRunner dispatch adapter
_DISPATCH = {
    f"{NAMESPACE}.RunTests": _run_tests_handler,
    f"{NAMESPACE}.CodeQuality": _code_quality_handler,
    f"{NAMESPACE}.SecurityScan": _security_scan_handler,
}


def handle(payload: dict) -> dict:
    """RegistryRunner dispatch entrypoint."""
    facet_name = payload["_facet_name"]
    handler = _DISPATCH.get(facet_name)
    if handler is None:
        raise ValueError(f"Unknown facet: {facet_name}")
    return handler(payload)


def register_handlers(runner) -> None:
    """Register all facets with a RegistryRunner."""
    for facet_name in _DISPATCH:
        runner.register_handler(
            facet_name=facet_name,
            module_uri=f"file://{os.path.abspath(__file__)}",
            entrypoint="handle",
        )


def register_test_handlers(poller) -> None:
    """Register all test event facet handlers with the poller."""
    for fqn, func in _DISPATCH.items():
        poller.register(fqn, func)
        log.debug("Registered test handler: %s", fqn)
