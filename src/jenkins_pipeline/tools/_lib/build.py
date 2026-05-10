"""Build simulators — Maven, Gradle, npm, Docker."""

from __future__ import annotations

from typing import Any


def maven_build(
    *,
    workspace_path: str = "/var/jenkins/workspace/app",
    goals: str = "clean package",
    jdk_version: str = "17",
) -> dict[str, Any]:
    """Simulate `mvn <goals>` in *workspace_path*."""
    return {
        "artifact_path": f"{workspace_path}/target/app-1.0.0.jar",
        "build_tool": f"maven-3.9.6/jdk-{jdk_version}",
        "version": "1.0.0",
        "success": True,
        "duration_ms": 45000,
        "warnings": 3,
        "errors": 0,
    }


def gradle_build(
    *,
    workspace_path: str = "/var/jenkins/workspace/app",
    tasks: str = "build",
    jdk_version: str = "17",
) -> dict[str, Any]:
    """Simulate `gradle <tasks>` in *workspace_path*."""
    return {
        "artifact_path": f"{workspace_path}/build/libs/app-1.0.0.jar",
        "build_tool": f"gradle-8.5/jdk-{jdk_version}",
        "version": "1.0.0",
        "success": True,
        "duration_ms": 38000,
        "warnings": 1,
        "errors": 0,
    }


def npm_build(
    *,
    workspace_path: str = "/var/jenkins/workspace/app",
    build_script: str = "build",
    node_version: str = "20",
) -> dict[str, Any]:
    """Simulate `npm run <build_script>` in *workspace_path*."""
    return {
        "artifact_path": f"{workspace_path}/dist",
        "build_tool": f"npm-10.2.0/node-{node_version}",
        "version": "1.0.0",
        "success": True,
        "duration_ms": 22000,
        "warnings": 0,
        "errors": 0,
    }


def docker_build(
    *,
    image_tag: str = "app:latest",
    dockerfile: str = "Dockerfile",  # noqa: ARG001 — kept for API parity
    workspace_path: str = "/var/jenkins/workspace/app",  # noqa: ARG001
) -> dict[str, Any]:
    """Simulate `docker build -t <image_tag> -f <dockerfile> <workspace>`."""
    tag = image_tag.split(":")[-1] if ":" in image_tag else "latest"
    return {
        "artifact_path": f"docker://{image_tag}",
        "build_tool": "docker-24.0.7",
        "version": tag,
        "success": True,
        "duration_ms": 60000,
        "warnings": 0,
        "errors": 0,
    }
