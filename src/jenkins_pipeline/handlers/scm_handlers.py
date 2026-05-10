"""Jenkins SCM event facet handlers.

Handles GitCheckout and GitMerge event facets from jenkins.scm namespace.
The actual simulator lives in ``jenkins_pipeline.tools._lib.scm`` and is
called via the ``handlers.shared.jenkins_utils`` shim — the same code path
the CLIs (``tools/git-checkout.sh``, ``tools/git-merge.sh``) take.
"""

import logging
import os
from typing import Any

from .shared.jenkins_utils import git_checkout, git_merge

log = logging.getLogger(__name__)

NAMESPACE = "jenkins.scm"


def _git_checkout_handler(payload: dict) -> dict[str, Any]:
    """Clone/checkout a git repository."""
    step_log = payload.get("_step_log")
    repo = payload.get("repo", "unknown")
    branch = payload.get("branch", "main")
    if step_log:
        step_log(f"GitCheckout: {repo}@{branch}")
    return {"info": git_checkout(repo=repo, branch=branch)}


def _git_merge_handler(payload: dict) -> dict[str, Any]:
    """Merge a source branch into a target branch."""
    step_log = payload.get("_step_log")
    source = payload.get("source_branch", "feature")
    target = payload.get("target_branch", "main")
    workspace = payload.get("workspace_path", "/var/jenkins/workspace/repo")
    if step_log:
        step_log(f"GitMerge: {source} -> {target}")
    return {
        "info": git_merge(
            source_branch=source,
            target_branch=target,
            workspace_path=workspace,
        )
    }


# RegistryRunner dispatch adapter
_DISPATCH = {
    f"{NAMESPACE}.GitCheckout": _git_checkout_handler,
    f"{NAMESPACE}.GitMerge": _git_merge_handler,
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


def register_scm_handlers(poller) -> None:
    """Register all SCM event facet handlers with the poller."""
    for fqn, func in _DISPATCH.items():
        poller.register(fqn, func)
        log.debug("Registered SCM handler: %s", fqn)
