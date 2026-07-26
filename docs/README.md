# Jenkins CI/CD — Feature Specifications

This directory holds one **spec per feature** of the `jenkins-pipeline` example.
Each document follows a common shape ([`SPEC_TEMPLATE.md`](SPEC_TEMPLATE.md)) and
states, for that feature: how it works, whether and how it **fans out**, the
**data & fields** it produces, the **external libraries/binaries** it relies on,
its **facets & workflows** (with `Effect`/`Cost`), and its **cache/output**.
Claims are grounded in the FFL `/** … */` docstrings, the handler code, the
`tools/_lib/` simulators, and the tests.

**The one caveat that colours every spec:** this package is a **CI/CD
*simulator*** — the 17 event-facet handlers return realistic, deterministic
shapes without invoking Jenkins, Maven, Docker, kubectl, or Slack. It exists to
demonstrate **FFL mixin composition**, not to actually build or ship software.
Nothing is written to any cache or object store.

**Start here:** [**CI/CD Pipelines**](pipelines.md) — the flagship feature: the
four composed workflows that show `with Retry/Timeout/Credentials/Notification/
AgentLabel/Stash` composition and `andThen foreach` fan-out over the operation
facets.

## Cross-cutting

| Spec | What it covers |
|------|----------------|
| [pipelines.md](pipelines.md) | **Flagship.** Four end-to-end pipelines (`JavaMavenCI`, `DockerK8sDeploy`, `MultiModuleBuild`, `FullCIPipeline`) demonstrating call-time mixin composition, parallel quality gates, and foreach fan-out. |
| [mixins.md](mixins.md) | The six cross-cutting composition facets (`Retry`, `Timeout`, `Credentials`, `Notification`, `AgentLabel`, `Stash`) + namespace-level `implicit` defaults — the point of the demo. |
| [types.md](types.md) | The seven shared schemas (`ScmInfo`, `BuildResult`, `TestReport`, `QualityReport`, `Artifact`, `DeployResult`, `PipelineStatus`) that flow between steps. |
| [tools-and-simulators.md](tools-and-simulators.md) | The dual-surface tools/handlers/`_lib` pattern — 17 CLIs + 17 handlers over one set of pure-stdlib deterministic simulators; registration, dispatch, coexistence rules. |
| [catalog.md](catalog.md) | The machine-readable `catalog.yaml` capability index (4 workflows + 17 facets) and its honesty tests. |

## CI/CD operation namespaces

| Spec | What it covers |
|------|----------------|
| [scm.md](scm.md) | `jenkins.scm` — `GitCheckout` (auto 10-min timeout) / `GitMerge`; produces `ScmInfo` + the workspace path that threads the pipeline. |
| [build.md](build.md) | `jenkins.build` — `MavenBuild` / `GradleBuild` / `NpmBuild` / `DockerBuild`; produces `BuildResult` (all `external`/`expensive`). |
| [test.md](test.md) | `jenkins.test` — `RunTests` / `CodeQuality` / `SecurityScan`; the parallel quality gates producing `TestReport` / `QualityReport`. |
| [artifact.md](artifact.md) | `jenkins.artifact` — `ArchiveArtifacts` (the lone `io`/`cheap` facet) / `PublishToRegistry` / `DockerPush`; produces `Artifact`. |
| [deploy.md](deploy.md) | `jenkins.deploy` — `DeployToEnvironment` / `DeployToK8s` / `RollbackDeploy`; produces `DeployResult`. |
| [notify.md](notify.md) | `jenkins.notify` — `SlackNotify` / `EmailNotify`; the only facets returning a flat tuple instead of a schema. |

---

*See also the repo [`CLAUDE.md`](../CLAUDE.md) (domain contract + tools pattern),
the [`README.md`](../README.md) and [`USER_GUIDE.md`](../USER_GUIDE.md), the
machine-readable [`catalog.yaml`](../src/jenkins_pipeline/catalog.yaml), and the
cross-cutting design specs under [`agent-spec/`](../agent-spec/). The
live/queryable interface is the MCP `fw_capabilities` / `fw_catalog_search` /
`fw_describe_handler` tools.*
