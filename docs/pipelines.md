# CI/CD Pipelines (mixin composition)

**Namespace:** `jenkins.pipeline` ·
**FFL:** `src/jenkins_pipeline/ffl/jenkins_pipelines.ffl` ·
**Depends on:** `jenkins.types`, `jenkins.mixins`, and all six operation namespaces ·
**Handlers:** none of its own — the workflows compose the operation event facets ·
**Tests:** `tests/mocked/py/test_jenkins_compilation.py` (`TestJenkinsPipelines`)

## Overview

This is the **flagship** feature and the reason the package exists: four
end-to-end Jenkins-style pipelines that demonstrate **FFL mixin composition** —
attaching cross-cutting concerns (retry, timeout, credentials, notification,
agent selection, stash) to build/test/deploy steps at call time. The four
workflows are all `entry_point: true` in `catalog.yaml`:

| Workflow | Demonstrates |
|---|---|
| `JavaMavenCI` | Call-time mixin composition — `with Timeout()`, `with Retry()`, `with Credentials()`, `with Notification()` on a linear checkout→build→test→deploy chain |
| `DockerK8sDeploy` | `with AgentLabel()` node pinning + `with Credentials()` for a build→scan→push→deploy→notify container pipeline |
| `MultiModuleBuild` | `andThen foreach` fan-out with **per-iteration** `with Stash()` / `with Retry()` mixins |
| `FullCIPipeline` | Comprehensive composition: parallel quality gates (tests + code-quality + security scan with no inter-dependencies) then archive→deploy→notify |

The workflows do not add handlers of their own; they wire together the event
facets defined in [scm](scm.md), [build](build.md), [test](test.md),
[artifact](artifact.md), [deploy](deploy.md), and [notify](notify.md), every one
of which is a **deterministic simulator**. Running a pipeline therefore executes
the real Facetwork step state machine (dependency resolution, per-step tasks,
mixin attachment) over simulated CI work — the point is to exercise
*composition*, not to actually build anything.

## How it works

Each workflow is a `workflow <Name>(params) => (returns) andThen { … }` block. A
step is `name = jenkins.<ns>.<Facet>(args) with <Mixin>(…) with <Mixin>(…)`.
Dependencies are expressed by referencing a prior step's return field, e.g.
`build = jenkins.build.MavenBuild(workspace_path = src.info.workspace_path, …)`
reads `src`'s `ScmInfo.workspace_path`, so the runtime schedules `build` after
`src`. Relative `$`-scoping is used for workflow params (`$.repo`, `$.branch`,
`$.environment`) and, inside the `foreach`, for the loop variable (`$.mod.name`,
`$.mod.build_task`).

`JavaMavenCI` chain (linear):
`GitCheckout` → `MavenBuild` → `RunTests` → `DeployToEnvironment` → `yield`
(deploy_url, test_passed, test_total, version).

`FullCIPipeline` shows the **parallel quality gate** pattern — `tests`,
`quality`, and `security` all depend only on `build` (not on each other), so the
runtime can dispatch them concurrently; `archive`/`deploy` then depend on the
gate + `build`, and `notify` last. String outputs are assembled with the `++`
concatenation operator (e.g. the Slack message `"Pipeline complete: " ++
build.result.version ++ " deployed to " ++ $.deploy_env`).

Data shape at each hop is a `jenkins.types` schema (see [types](types.md)):
`ScmInfo → BuildResult → TestReport/QualityReport → Artifact → DeployResult`.

## Fan-out

**Only `MultiModuleBuild` fans out.** Its body is `andThen foreach mod in
$.modules { … }`, so it emits one iteration per element of the `modules: Json`
input, each running `GitCheckout → GradleBuild → RunTests → ArchiveArtifacts`
with per-iteration `with Stash(name = $.mod.name ++ "-build", …)` and
`with Retry(maxAttempts = 2)`. This is the canonical foreach-fan-out shape (one
distributed task per module) reused across the framework. The other three
workflows are **single linear/parallel DAGs — no fan-out**.

## Data & fields

Inputs are plain workflow params (`repo`, `branch`, `environment`,
`image_tag`, `registry_url`, `k8s_namespace`, `replicas`, `deploy_env`,
`notify_channel`, and `modules: Json` for the foreach). Outputs are `yield`ed
tuples of scalars pulled from the composed steps' schema fields — e.g.
`FullCIPipeline` yields `deploy_url`, `version`, `test_coverage`
(`tests.report.coverage_pct`), `quality_issues` (`quality.report.issues`),
`security_critical` (`security.report.critical`). Because the leaves are
simulators, these resolve to constant-ish values (coverage `87.3`, etc. — see
each operation spec).

## External libraries / binaries

**None.** The pipelines are pure FFL; execution needs only the Facetwork runtime
+ this package's simulators (themselves pure-stdlib). No Jenkins, Maven, Gradle,
Docker, kubectl, or Slack client is invoked or required.

## Facets & workflows

All four are `workflow` declarations (entry points), not event facets — they
need no handler:

| Workflow | Signature (params → returns) |
|---|---|
| `JavaMavenCI` | `(repo, branch="main", environment="staging") => (deploy_url, test_passed, test_total, version)` |
| `DockerK8sDeploy` | `(repo, branch="main", image_tag, registry_url, k8s_namespace="default", replicas=2) => (deploy_url, image, healthy)` |
| `MultiModuleBuild` | `(repo, branch="main", modules: Json) => (artifact_path, module_name, test_passed)` — `andThen foreach` |
| `FullCIPipeline` | `(repo, branch="main", deploy_env="staging", notify_channel="#ci") => (deploy_url, version, test_coverage, quality_issues, security_critical)` |

The **mixins** attached at call sites (`Retry`, `Timeout`, `Credentials`,
`Notification`, `AgentLabel`, `Stash`) are pure composition facets from
[jenkins.mixins](mixins.md) — not event facets, so they carry no handler and no
Effect/Cost.

## Cache / output

**No cache, no durable artifact.** The workflows produce a `yield`ed result
tuple that the runtime records as the run's output; nothing is written to
`$FW_CACHE_ROOT` or MinIO/S3. (These are simulator pipelines — contrast the
map-producing fwh_* domains whose workflows publish GeoJSON/HTML.)

## Gotchas & notes

- **Everything downstream is simulated.** A green `FullCIPipeline` run proves the
  *composition and scheduling* work, not that any code built, tested, or
  deployed. Do not treat the returned coverage/issue/health numbers as real —
  they are the simulators' constants (see [test](test.md), [deploy](deploy.md)).
- **`__init__.py` docstring overstates the feature set.** The package
  `__init__.py` claims the example showcases "`RequiresApproval`", "prompt +
  script blocks", and "`andThen when` branching". **None of these appear in the
  shipped FFL** — the mixins are exactly `Retry/Timeout/Credentials/Notification/
  AgentLabel/Stash` (see [mixins](mixins.md)), there are no `prompt {}`/`script
  {}` blocks, and no workflow uses `andThen when`. Treat that docstring as
  aspirational; the FFL is the source of truth.
- **Parallel gates are implicit, not a keyword.** `FullCIPipeline`'s "parallel"
  quality gates are parallel only because `tests`/`quality`/`security` share no
  data dependency — the runtime infers concurrency from the DAG. There is no
  `parallel {}` construct.
- **`MultiModuleBuild.modules` is untyped `Json`.** Each element must supply the
  fields the body reads: `name`, `build_task`, `output_pattern`, `test_suite`. A
  missing key surfaces at run time, not compile time.

## Related specs

- [mixins](mixins.md) — the six composition facets these workflows attach.
- [types](types.md) — the shared schemas that flow between steps.
- [scm](scm.md) · [build](build.md) · [test](test.md) · [artifact](artifact.md)
  · [deploy](deploy.md) · [notify](notify.md) — the composed operation facets.
- [catalog](catalog.md) — the reuse-first manifest that indexes these four
  workflows by intent.
