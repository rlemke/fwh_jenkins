"""Deploy simulators — environment, k8s, rollback."""

from __future__ import annotations

from typing import Any


def deploy_to_environment(
    *,
    environment: str = "staging",
    version: str = "1.0.0",
    strategy: str = "rolling",
) -> dict[str, Any]:
    """Simulate deploying *version* to *environment* with *strategy*."""
    return {
        "environment": environment,
        "strategy": strategy,
        "version": version,
        "url": f"https://{environment}.example.com",
        "replicas": 3,
        "healthy": True,
        "deploy_id": f"deploy-{environment}-{version}-001",
    }


def deploy_to_k8s(
    *,
    cluster: str = "default",
    k8s_namespace: str = "default",
    image_tag: str = "app:latest",
    replicas: int = 2,
) -> dict[str, Any]:
    """Simulate a kubectl-style deploy to a Kubernetes cluster."""
    version = image_tag.split(":")[-1] if ":" in image_tag else "latest"
    return {
        "environment": f"k8s/{cluster}/{k8s_namespace}",
        "strategy": "rolling",
        "version": version,
        "url": f"https://{k8s_namespace}.{cluster}.k8s.example.com",
        "replicas": replicas,
        "healthy": True,
        "deploy_id": f"k8s-{cluster}-{k8s_namespace}-001",
    }


def rollback_deploy(
    *,
    deploy_id: str = "deploy-unknown-001",
    environment: str = "staging",
) -> dict[str, Any]:
    """Simulate rolling back a previous deploy."""
    return {
        "environment": environment,
        "strategy": "rollback",
        "version": "previous",
        "url": f"https://{environment}.example.com",
        "replicas": 3,
        "healthy": True,
        "deploy_id": f"{deploy_id}-rollback",
    }
