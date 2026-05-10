"""SCM simulators — `git_checkout`, `git_merge`."""

from __future__ import annotations

from typing import Any


def git_checkout(*, repo: str, branch: str = "main") -> dict[str, Any]:
    """Simulate a git checkout/clone."""
    return {
        "repo": repo,
        "branch": branch,
        "commit_sha": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
        "commit_message": f"Latest commit on {branch}",
        "author": "jenkins-ci",
        "workspace_path": f"/var/jenkins/workspace/{repo.split('/')[-1]}",
        "clone_duration_ms": 4500,
    }


def git_merge(
    *,
    source_branch: str,
    target_branch: str = "main",
    workspace_path: str = "/var/jenkins/workspace/repo",
) -> dict[str, Any]:
    """Simulate a git merge of *source_branch* into *target_branch*."""
    return {
        "repo": workspace_path.split("/")[-1],
        "branch": target_branch,
        "commit_sha": "b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3",
        "commit_message": f"Merge {source_branch} into {target_branch}",
        "author": "jenkins-ci",
        "workspace_path": workspace_path,
        "clone_duration_ms": 0,
    }
