# Deploy (environment / Kubernetes / rollback)

**Namespace:** `jenkins.deploy` ·
**FFL:** `src/jenkins_pipeline/ffl/jenkins_deploy.ffl` ·
**Handlers:** `src/jenkins_pipeline/handlers/deploy_handlers.py` ·
**Simulator:** `src/jenkins_pipeline/tools/_lib/deploy.py` ·
**CLIs:** `tools/{deploy-to-environment,deploy-to-k8s,rollback-deploy}.{py,sh}`

## Overview

`jenkins.deploy` is the **release stage** — shipping a built artifact to a named
environment or a Kubernetes cluster, plus a rollback path. Three facets:
`DeployToEnvironment` (rolling / blue-green to a named env), `DeployToK8s`
(replica-scaled k8s deploy), and `RollbackDeploy` (revert by deploy ID). Each is
a **deterministic simulator** returning a `DeployResult` (env, strategy, version,
URL, replicas, health, deploy ID) — no real deploy occurs.

## How it works

Handlers wrap simulator dicts under `{"result": …}`:

- `DeployToEnvironment` → `deploy_to_environment(environment, version, strategy)`
  → `DeployResult` with `url "https://<env>.example.com", replicas 3, healthy
  True, deploy_id "deploy-<env>-<version>-001"`.
- `DeployToK8s` → `deploy_to_k8s(cluster, k8s_namespace, image_tag, replicas)` →
  `environment "k8s/<cluster>/<ns>", version` = image-tag suffix, `url
  "https://<ns>.<cluster>.k8s.example.com", replicas` = the input.
- `RollbackDeploy` → `rollback_deploy(deploy_id, environment)` → `strategy
  "rollback", version "previous", deploy_id "<id>-rollback"`.

All return `healthy: True` — deploys never fail in simulation.

## Fan-out

**Single-task per call — no fan-out.** A deploy is atomic per call.

## Data & fields

All three return `DeployResult` (see [types](types.md)): `environment, strategy,
version, url, replicas, healthy, deploy_id`. `replicas` is a constant `3` for
`DeployToEnvironment`/`RollbackDeploy` but reflects the input for `DeployToK8s`;
`url`/`environment`/`deploy_id` are input-derived; `healthy` is always `True`.

## External libraries / binaries

**None.** No `kubectl`, Helm, or cloud SDK — pure-stdlib simulators.

## Facets & workflows

| Facet | Kind | Effect / Cost | Signature |
|---|---|---|---|
| `DeployToEnvironment` | event | external / expensive | `DeployToEnvironment(artifact_path, environment="staging", strategy="rolling", version="") => (result: DeployResult)` |
| `DeployToK8s` | event | external / expensive | `DeployToK8s(artifact_path, k8s_namespace="default", cluster="default", replicas: Int = 2, image_tag="") => (result: DeployResult)` |
| `RollbackDeploy` | event | external / moderate | `RollbackDeploy(deploy_id: String, environment: String) => (result: DeployResult)` |

`RollbackDeploy` is `moderate` (vs the forward deploys' `expensive`) and is the
package's nod to failure-recovery patterns — though no workflow currently invokes
it (it is available for a catch/recovery composition).

## Cache / output

**No cache, no durable output.** The returned `url`/`deploy_id` are simulated
strings; nothing is deployed or written. CLI prints JSON.

## Gotchas & notes

- **`healthy` is always `True`, `version "previous"` for rollback** — constants.
  A simulated deploy can't be observed to fail, so downstream health checks
  always pass.
- **`DeployToK8s` derives `version` from `image_tag`** (suffix after `:`),
  defaulting to `"latest"` when the tag has no `:`.
- **`artifact_path` is declared on both forward-deploy facets but the simulators
  ignore it** — they don't read the artifact, only its metadata is threaded by
  the workflow.
- **`RollbackDeploy` is wired but unused** by the four shipped pipelines.

## Related specs

- [types](types.md) — `DeployResult`. · [artifact](artifact.md) — supplies the
  artifact. · [notify](notify.md) — the announce-the-release follow-up. ·
  [pipelines](pipelines.md).
