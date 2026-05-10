"""Jenkins artifact event facet handlers.

Handles ArchiveArtifacts, PublishToRegistry, and DockerPush event facets
from the jenkins.artifact namespace. Simulators live in
``jenkins_pipeline.tools._lib.artifact`` (also reachable via the
``archive-artifacts``, ``publish-to-registry``, ``docker-push`` CLIs).
"""

import logging
import os
from typing import Any

from .shared.jenkins_utils import archive_artifacts, docker_push, publish_to_registry

log = logging.getLogger(__name__)

NAMESPACE = "jenkins.artifact"


def _archive_artifacts_handler(payload: dict) -> dict[str, Any]:
    """Archive build artifacts."""
    step_log = payload.get("_step_log")
    workspace = payload.get("workspace_path", "/var/jenkins/workspace/app")
    includes = payload.get("includes", "**/*.jar")
    if step_log:
        step_log(f"ArchiveArtifacts: {workspace}")
    return {"artifact": archive_artifacts(workspace_path=workspace, includes=includes)}


def _publish_to_registry_handler(payload: dict) -> dict[str, Any]:
    """Publish an artifact to a registry (Maven, npm, etc.)."""
    step_log = payload.get("_step_log")
    registry_url = payload.get("registry_url", "https://registry.example.com")
    version = payload.get("version", "1.0.0")
    group_id = payload.get("group_id", "com.example")
    artifact_path = payload.get("artifact_path", "/target/app.jar")
    if step_log:
        step_log(f"PublishToRegistry: v{version} -> {registry_url}")
    return {
        "artifact": publish_to_registry(
            registry_url=registry_url,
            version=version,
            group_id=group_id,
            artifact_path=artifact_path,
        )
    }


def _docker_push_handler(payload: dict) -> dict[str, Any]:
    """Push a Docker image to a container registry."""
    step_log = payload.get("_step_log")
    image_tag = payload.get("image_tag", "app:latest")
    registry_url = payload.get("registry_url", "registry.example.com")
    if step_log:
        step_log(f"DockerPush: {image_tag}")
    return {"artifact": docker_push(image_tag=image_tag, registry_url=registry_url)}


# RegistryRunner dispatch adapter
_DISPATCH = {
    f"{NAMESPACE}.ArchiveArtifacts": _archive_artifacts_handler,
    f"{NAMESPACE}.PublishToRegistry": _publish_to_registry_handler,
    f"{NAMESPACE}.DockerPush": _docker_push_handler,
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


def register_artifact_handlers(poller) -> None:
    """Register all artifact event facet handlers with the poller."""
    for fqn, func in _DISPATCH.items():
        poller.register(fqn, func)
        log.debug("Registered artifact handler: %s", fqn)
