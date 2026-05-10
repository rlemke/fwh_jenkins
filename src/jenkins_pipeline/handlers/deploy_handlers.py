"""Jenkins deploy event facet handlers.

Handles DeployToEnvironment, DeployToK8s, and RollbackDeploy event facets
from the jenkins.deploy namespace. Simulators live in
``jenkins_pipeline.tools._lib.deploy`` (also reachable via the
``deploy-to-environment``, ``deploy-to-k8s``, ``rollback-deploy`` CLIs).
"""

import logging
import os
from typing import Any

from .shared.jenkins_utils import deploy_to_environment, deploy_to_k8s, rollback_deploy

log = logging.getLogger(__name__)

NAMESPACE = "jenkins.deploy"


def _deploy_to_environment_handler(payload: dict) -> dict[str, Any]:
    """Deploy an artifact to a target environment."""
    step_log = payload.get("_step_log")
    environment = payload.get("environment", "staging")
    strategy = payload.get("strategy", "rolling")
    version = payload.get("version", "1.0.0")
    if step_log:
        step_log(f"Deploy: {version} -> {environment}")
    return {
        "result": deploy_to_environment(
            environment=environment, version=version, strategy=strategy
        )
    }


def _deploy_to_k8s_handler(payload: dict) -> dict[str, Any]:
    """Deploy to a Kubernetes cluster."""
    step_log = payload.get("_step_log")
    namespace = payload.get("k8s_namespace", "default")
    cluster = payload.get("cluster", "default")
    replicas = payload.get("replicas", 2)
    image_tag = payload.get("image_tag", "app:latest")
    if step_log:
        step_log(f"DeployToK8s: {cluster}/{namespace}")
    return {
        "result": deploy_to_k8s(
            cluster=cluster,
            k8s_namespace=namespace,
            image_tag=image_tag,
            replicas=replicas,
        )
    }


def _rollback_deploy_handler(payload: dict) -> dict[str, Any]:
    """Roll back a deployment."""
    step_log = payload.get("_step_log")
    deploy_id = payload.get("deploy_id", "deploy-unknown-001")
    environment = payload.get("environment", "staging")
    if step_log:
        step_log(f"RollbackDeploy: {deploy_id}")
    return {"result": rollback_deploy(deploy_id=deploy_id, environment=environment)}


# RegistryRunner dispatch adapter
_DISPATCH = {
    f"{NAMESPACE}.DeployToEnvironment": _deploy_to_environment_handler,
    f"{NAMESPACE}.DeployToK8s": _deploy_to_k8s_handler,
    f"{NAMESPACE}.RollbackDeploy": _rollback_deploy_handler,
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


def register_deploy_handlers(poller) -> None:
    """Register all deploy event facet handlers with the poller."""
    for fqn, func in _DISPATCH.items():
        poller.register(fqn, func)
        log.debug("Registered deploy handler: %s", fqn)
