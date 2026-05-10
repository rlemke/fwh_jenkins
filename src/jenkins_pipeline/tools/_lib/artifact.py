"""Artifact simulators — archive, registry publish, Docker push."""

from __future__ import annotations

from typing import Any


def archive_artifacts(
    *,
    workspace_path: str = "/var/jenkins/workspace/app",
    includes: str = "**/*.jar",  # noqa: ARG001 — kept for API parity
) -> dict[str, Any]:
    """Simulate archiving build artifacts from *workspace_path*."""
    return {
        "name": "app-1.0.0.jar",
        "path": f"{workspace_path}/target/app-1.0.0.jar",
        "size_bytes": 15_728_640,
        "checksum": "sha256:a1b2c3d4e5f6789012345678abcdef0123456789",
        "registry_url": "",
        "tag": "1.0.0",
    }


def publish_to_registry(
    *,
    registry_url: str = "https://registry.example.com",
    version: str = "1.0.0",
    group_id: str = "com.example",
    artifact_path: str = "/target/app.jar",
) -> dict[str, Any]:
    """Simulate publishing to a Maven/npm-style registry."""
    return {
        "name": f"{group_id}:app",
        "path": artifact_path,
        "size_bytes": 15_728_640,
        "checksum": "sha256:b2c3d4e5f6789012345678abcdef0123456789ab",
        "registry_url": f"{registry_url}/{group_id.replace('.', '/')}/app/{version}",
        "tag": version,
    }


def docker_push(
    *,
    image_tag: str = "app:latest",
    registry_url: str = "registry.example.com",
) -> dict[str, Any]:
    """Simulate pushing a Docker image to a container registry."""
    tag = image_tag.split(":")[-1] if ":" in image_tag else "latest"
    image_name = image_tag.split(":")[0]
    return {
        "name": image_name,
        "path": f"{registry_url}/{image_tag}",
        "size_bytes": 256_000_000,
        "checksum": "sha256:c3d4e5f6789012345678abcdef0123456789abcd",
        "registry_url": f"{registry_url}/{image_name}",
        "tag": tag,
    }
