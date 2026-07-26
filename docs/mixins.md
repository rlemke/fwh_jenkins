# Mixins (cross-cutting composition facets)

**Namespace:** `jenkins.mixins` ·
**FFL:** `src/jenkins_pipeline/ffl/jenkins_mixins.ffl` ·
**Handlers:** none — these are **pure composition facets**, not event facets ·
**Tests:** `tests/mocked/py/test_jenkins_compilation.py` (`TestJenkinsMixins`)

## Overview

`jenkins.mixins` defines the six reusable cross-cutting concerns that the
[pipelines](pipelines.md) attach to steps with the `with <Mixin>(…)` syntax. They
model Jenkins pipeline decorators — retry, timeout, credentials, notification,
agent-node selection, and workspace stashing. This namespace is the *whole point*
of the demo: it shows how orthogonal concerns are declared once and composed onto
any step at call time, rather than baked into each operation facet.

They are **plain `facet` declarations, not `event facet`** — they carry no
handler, no simulator, and no `Effect`/`Cost`. `catalog.yaml` deliberately does
**not** index them (only event facets are capability-indexed). At runtime they
attach metadata to the step they decorate; the runtime honours `Timeout` as a
real per-step execution bound (the framework's `with Timeout(minutes=…)` also
feeds cost inference elsewhere), while `Retry`, `Credentials`, `Notification`,
`AgentLabel`, and `Stash` are demonstrated as composition surface in this example
rather than being enforced by the simulators.

## How it works

Each mixin is a parameterised facet with defaults. A pipeline step names it after
`with`:

```
build = jenkins.build.MavenBuild(workspace_path = src.info.workspace_path,
    goals = "clean package -DskipTests") with Timeout(minutes = 20) with Retry(maxAttempts = 2, backoffSeconds = 60)
```

Multiple `with` clauses chain on one step. The mixin arguments can be literals or
`$`/step references (e.g. `with Stash(name = $.mod.name ++ "-build", includes =
$.mod.output_pattern)` in the `foreach`, or `with Notification(channel =
$.notify_channel)` in `FullCIPipeline`).

### Namespace-level implicit defaults

The file also declares three `implicit` defaults that apply namespace-wide unless
a step overrides them:

```
implicit defaultRetry   = Retry(maxAttempts = 3, backoffSeconds = 30)
implicit defaultTimeout = Timeout(minutes = 30)
implicit defaultAgent   = AgentLabel(label = "linux")
```

These demonstrate the `implicit` mechanism — a mixin that is composed onto every
applicable step in scope without being written at each call site.

## Fan-out

**N/A — mixins do not execute.** They decorate steps; fan-out (if any) is a
property of the workflow body, not the mixin. `Stash` is the mixin most
associated with fan-out because `MultiModuleBuild` attaches a per-module stash
inside its `foreach` (see [pipelines](pipelines.md)).

## Data & fields

The six facets and their parameters (all from the FFL docstrings):

| Facet | Parameters | Purpose |
|---|---|---|
| `Retry` | `maxAttempts: Int = 3, backoffSeconds: Int = 30` | Retry a failed step with backoff |
| `Timeout` | `minutes: Int = 30` | Enforce a max execution time on a step |
| `Credentials` | `credentialId: String, type: String = "token"` | Attach auth (SSH key / token / password) |
| `Notification` | `channel: String, onSuccess: Boolean = true, onFailure: Boolean = true` | Notify a channel on success/failure |
| `AgentLabel` | `label: String = "any"` | Pin the step to a Jenkins agent node label |
| `Stash` | `name: String, includes: String = "**/*", excludes: String = ""` | Stash workspace files between stages |

## External libraries / binaries

**None.** Pure FFL declarations.

## Facets & workflows

All six are pure composition facets (no return clause, no `event`, no handler).
Usage across the pipelines:

- `Timeout` — every pipeline (per-step bounds, e.g. checkout 5m, build 20–30m).
- `Retry` — Maven/Gradle builds, the Docker push, per-module tests.
- `Credentials` — checkout (`git-ssh-key`), deploy (`deploy-token`), registry
  (`registry-creds`), k8s (`k8s-token`), SonarQube (`sonar-token`).
- `AgentLabel` — `DockerK8sDeploy` (`docker`), `FullCIPipeline` (`linux-large`).
- `Notification` — `JavaMavenCI` / `FullCIPipeline` deploy steps.
- `Stash` — `MultiModuleBuild` (per-module) and `FullCIPipeline` (`build-artifacts`).

## Cache / output

**N/A** — mixins produce no output.

## Gotchas & notes

- **Not event facets — no handler will ever be dispatched for a mixin.** If you
  add a mixin, do **not** add it to `catalog.yaml`'s `facets` list (that index is
  for event facets only, and `test_catalog_manifest.py` asserts each indexed
  facet is a real `facet <Leaf>` *and* has `with Effect/Cost` — a mixin has
  neither).
- **`RequiresApproval` does not exist.** The package `__init__.py` docstring
  lists it among the mixins; the shipped set is exactly the six above. See the
  [pipelines](pipelines.md) note on that stale docstring.
- **Only `Timeout` has enforced runtime semantics in this example.** The others
  are composition demonstrations — the deterministic simulators never fail, so
  `Retry`/`Credentials` are exercised as syntax/attachment, not as behaviour you
  can observe in a run.

## Related specs

- [pipelines](pipelines.md) — every `with <Mixin>` call site.
- [types](types.md) — the schemas the decorated steps return.
