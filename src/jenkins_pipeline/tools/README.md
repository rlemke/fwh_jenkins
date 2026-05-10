# jenkins-pipeline tools

CLI utilities that simulate every Jenkins facet defined under
`src/jenkins_pipeline/ffl/`. Each operation has:

- a Python module under `_lib/<domain>.py` with the deterministic
  simulator (pure functions, no I/O, no MongoDB),
- a CLI script `<verb>_<noun>.py` that argparse-parses input and prints
  JSON,
- a thin shell wrapper `<verb>-<noun>.sh` so the CLI works from any
  shell session without remembering the underscore form.

The FFL handlers in `src/jenkins_pipeline/handlers/` call into the same
`_lib/` modules via `handlers/shared/jenkins_utils.py`, so both surfaces
share one implementation.

## CLI map

| Domain | Facet | CLI |
|--------|-------|-----|
| `jenkins.scm` | GitCheckout | `git-checkout.sh` |
| `jenkins.scm` | GitMerge | `git-merge.sh` |
| `jenkins.build` | MavenBuild | `maven-build.sh` |
| `jenkins.build` | GradleBuild | `gradle-build.sh` |
| `jenkins.build` | NpmBuild | `npm-build.sh` |
| `jenkins.build` | DockerBuild | `docker-build.sh` |
| `jenkins.test` | RunTests | `run-tests.sh` |
| `jenkins.test` | CodeQuality | `code-quality.sh` |
| `jenkins.test` | SecurityScan | `security-scan.sh` |
| `jenkins.artifact` | ArchiveArtifacts | `archive-artifacts.sh` |
| `jenkins.artifact` | PublishToRegistry | `publish-to-registry.sh` |
| `jenkins.artifact` | DockerPush | `docker-push.sh` |
| `jenkins.deploy` | DeployToEnvironment | `deploy-to-environment.sh` |
| `jenkins.deploy` | DeployToK8s | `deploy-to-k8s.sh` |
| `jenkins.deploy` | RollbackDeploy | `rollback-deploy.sh` |
| `jenkins.notify` | SlackNotify | `slack-notify.sh` |
| `jenkins.notify` | EmailNotify | `email-notify.sh` |

## Conventions

- Help: `<cli>.sh --help` — every CLI uses argparse.
- Stderr: one-line human summary (mirrors Jenkins step log).
- Stdout: pretty-printed JSON dict (the same shape the FFL handler emits).
- Exit code: 0 on success, non-zero on argparse error or simulated failure.
- Imports: every CLI imports its simulator via the fully-qualified
  package path (`from jenkins_pipeline.tools._lib.<domain> import …`),
  so the example coexists cleanly with sibling `_lib/` directories from
  other Facetwork example packages.

## Example

```bash
$ src/jenkins_pipeline/tools/maven-build.sh --workspace /tmp/app --goals "clean package"
MavenBuild: clean package in /tmp/app
{
  "artifact_path": "/tmp/app/target/app-1.0.0.jar",
  "build_tool": "maven-3.9.6/jdk-17",
  "version": "1.0.0",
  "success": true,
  "duration_ms": 45000,
  "warnings": 3,
  "errors": 0
}
```

## Adding a new tool

1. Add a pure simulator function to the right `_lib/<domain>.py` (or
   create a new domain module).
2. Copy an existing CLI as a template; adjust argparse, the function
   call, and the docstring.
3. Re-create the matching `.sh` wrapper:
   `printf '#!/usr/bin/env bash\nexec python3 "$(dirname "$0")/<name>.py" "$@"\n' > <name>.sh && chmod +x <name>.sh <name>.py`
4. Re-export the simulator from
   `src/jenkins_pipeline/handlers/shared/jenkins_utils.py`.
5. Wire up the matching FFL handler dispatch entry.
