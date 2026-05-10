"""Handler-side compatibility shim for the jenkins-pipeline simulators.

The real implementation lives in ``jenkins_pipeline.tools._lib``. It is
shared verbatim by:

- the ``maven-build`` / ``run-tests`` / ``deploy-to-k8s`` / … CLI tools
  under ``src/jenkins_pipeline/tools/``, and
- the FFL build / test / deploy / scm / artifact / notify handlers in
  this package.

Both entry points return the **same** dicts; the FFL-handler layer just
re-wraps them in the per-domain outer key (``result`` / ``info`` /
``report`` / ``artifact``) that the FFL schemas expect.

Imports use the fully-qualified ``jenkins_pipeline.tools._lib.<domain>``
path so this package coexists cleanly with sibling Facetwork example
packages (osm-geocoder, noaa-weather) that also ship a ``tools/_lib/``
directory — there is no fight for the bare ``_lib`` name on
``sys.modules``.
"""

from __future__ import annotations

from jenkins_pipeline.tools._lib import (  # noqa: F401
    artifact,
    build,
    deploy,
    notify,
    scm,
    test,
)
from jenkins_pipeline.tools._lib.artifact import (  # noqa: F401
    archive_artifacts,
    docker_push,
    publish_to_registry,
)
from jenkins_pipeline.tools._lib.build import (  # noqa: F401
    docker_build,
    gradle_build,
    maven_build,
    npm_build,
)
from jenkins_pipeline.tools._lib.deploy import (  # noqa: F401
    deploy_to_environment,
    deploy_to_k8s,
    rollback_deploy,
)
from jenkins_pipeline.tools._lib.notify import email_notify, slack_notify  # noqa: F401
from jenkins_pipeline.tools._lib.scm import git_checkout, git_merge  # noqa: F401
from jenkins_pipeline.tools._lib.test import (  # noqa: F401
    code_quality,
    run_tests,
    security_scan,
)

__all__ = [
    "artifact",
    "build",
    "deploy",
    "notify",
    "scm",
    "test",
    "archive_artifacts",
    "code_quality",
    "deploy_to_environment",
    "deploy_to_k8s",
    "docker_build",
    "docker_push",
    "email_notify",
    "git_checkout",
    "git_merge",
    "gradle_build",
    "maven_build",
    "npm_build",
    "publish_to_registry",
    "rollback_deploy",
    "run_tests",
    "security_scan",
    "slack_notify",
]
