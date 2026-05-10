"""Test simulators — `run_tests`, `code_quality`, `security_scan`."""

from __future__ import annotations

from typing import Any


def run_tests(*, framework: str = "junit", suite: str = "unit") -> dict[str, Any]:
    """Simulate running a test suite."""
    return {
        "framework": framework,
        "suite": suite,
        "total": 342,
        "passed": 335,
        "failed": 2,
        "skipped": 5,
        "duration_ms": 28000,
        "report_path": f"/var/jenkins/workspace/app/target/surefire-reports/{suite}-report.xml",
        "coverage_pct": 87.3,
    }


def code_quality(
    *,
    tool: str = "sonarqube",
    workspace_path: str = "/var/jenkins/workspace/app",
) -> dict[str, Any]:
    """Simulate a code-quality analysis run."""
    return {
        "tool": tool,
        "issues": 42,
        "critical": 0,
        "major": 5,
        "minor": 37,
        "report_path": f"{workspace_path}/target/sonar-report.json",
        "passed": True,
    }


def security_scan(
    *,
    scanner: str = "trivy",
    severity_threshold: str = "HIGH",  # noqa: ARG001 — kept for API parity
    workspace_path: str = "/var/jenkins/workspace/app",
) -> dict[str, Any]:
    """Simulate a security vulnerability scan."""
    return {
        "tool": scanner,
        "issues": 8,
        "critical": 0,
        "major": 2,
        "minor": 6,
        "report_path": f"{workspace_path}/target/security-report.json",
        "passed": True,
    }
