"""Jenkins build event facet handlers.

Handles MavenBuild, GradleBuild, NpmBuild, and DockerBuild event facets
from the jenkins.build namespace. The actual build simulators live in
``jenkins_pipeline.tools._lib.build`` (also exposed as the
``maven-build``, ``gradle-build``, ``npm-build``, ``docker-build`` CLIs).
"""

import logging
import os
from typing import Any

from .shared.jenkins_utils import docker_build, gradle_build, maven_build, npm_build

log = logging.getLogger(__name__)

NAMESPACE = "jenkins.build"


def _maven_build_handler(payload: dict) -> dict[str, Any]:
    """Run a Maven build."""
    step_log = payload.get("_step_log")
    workspace = payload.get("workspace_path", "/var/jenkins/workspace/app")
    goals = payload.get("goals", "clean package")
    jdk = payload.get("jdk_version", "17")
    if step_log:
        step_log(f"MavenBuild: {goals} in {workspace}")
    return {"result": maven_build(workspace_path=workspace, goals=goals, jdk_version=jdk)}


def _gradle_build_handler(payload: dict) -> dict[str, Any]:
    """Run a Gradle build."""
    step_log = payload.get("_step_log")
    workspace = payload.get("workspace_path", "/var/jenkins/workspace/app")
    tasks = payload.get("tasks", "build")
    jdk = payload.get("jdk_version", "17")
    if step_log:
        step_log(f"GradleBuild: {tasks} in {workspace}")
    return {"result": gradle_build(workspace_path=workspace, tasks=tasks, jdk_version=jdk)}


def _npm_build_handler(payload: dict) -> dict[str, Any]:
    """Run an npm build."""
    step_log = payload.get("_step_log")
    workspace = payload.get("workspace_path", "/var/jenkins/workspace/app")
    script = payload.get("build_script", "build")
    node_version = payload.get("node_version", "20")
    if step_log:
        step_log(f"NpmBuild: {script} in {workspace}")
    return {
        "result": npm_build(
            workspace_path=workspace, build_script=script, node_version=node_version
        )
    }


def _docker_build_handler(payload: dict) -> dict[str, Any]:
    """Build a Docker image."""
    step_log = payload.get("_step_log")
    workspace = payload.get("workspace_path", "/var/jenkins/workspace/app")
    image_tag = payload.get("image_tag", "app:latest")
    dockerfile = payload.get("dockerfile", "Dockerfile")
    if step_log:
        step_log(f"DockerBuild: {image_tag}")
    return {
        "result": docker_build(
            image_tag=image_tag, dockerfile=dockerfile, workspace_path=workspace
        )
    }


# RegistryRunner dispatch adapter
_DISPATCH = {
    f"{NAMESPACE}.MavenBuild": _maven_build_handler,
    f"{NAMESPACE}.GradleBuild": _gradle_build_handler,
    f"{NAMESPACE}.NpmBuild": _npm_build_handler,
    f"{NAMESPACE}.DockerBuild": _docker_build_handler,
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


def register_build_handlers(poller) -> None:
    """Register all build event facet handlers with the poller."""
    for fqn, func in _DISPATCH.items():
        poller.register(fqn, func)
        log.debug("Registered build handler: %s", fqn)
