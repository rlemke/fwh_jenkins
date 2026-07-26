# Build (Maven / Gradle / npm / Docker)

**Namespace:** `jenkins.build` ·
**FFL:** `src/jenkins_pipeline/ffl/jenkins_build.ffl` ·
**Handlers:** `src/jenkins_pipeline/handlers/build_handlers.py` ·
**Simulator:** `src/jenkins_pipeline/tools/_lib/build.py` ·
**CLIs:** `tools/{maven-build,gradle-build,npm-build,docker-build}.{py,sh}`

## Overview

`jenkins.build` is the **compile/package stage** — it produces a build artifact
from a checked-out workspace. Four facets cover the common toolchains: Maven,
Gradle, npm, and Docker. Each is a **deterministic simulator** returning a
`BuildResult` (artifact path, tool/version banner, timing, warning/error counts)
without invoking the real tool.

## How it works

Each facet dispatches to a `_lib.build` function and the handler wraps it under
`{"result": …}`:

- `MavenBuild` → `maven_build(workspace_path, goals, jdk_version)` → artifact
  `…/target/app-1.0.0.jar`, `build_tool "maven-3.9.6/jdk-<v>"`, `duration_ms
  45000`, `warnings 3`.
- `GradleBuild` → `gradle_build(workspace_path, tasks, jdk_version)` → artifact
  `…/build/libs/app-1.0.0.jar`, `build_tool "gradle-8.5/jdk-<v>"`.
- `NpmBuild` → `npm_build(workspace_path, build_script, node_version)` → artifact
  `…/dist`, `build_tool "npm-10.2.0/node-<v>"`.
- `DockerBuild` → `docker_build(image_tag, dockerfile, workspace_path)` →
  artifact `docker://<image_tag>`, `version` = the image tag suffix,
  `build_tool "docker-24.0.7"`.

All return `success: True, errors: 0` — the simulators never fail.

## Fan-out

**Single-task per call.** `MultiModuleBuild` invokes `GradleBuild` once per
module via the workflow-level `foreach` (see [pipelines](pipelines.md)); the
facet itself does not fan out.

## Data & fields

All four return `BuildResult` (see [types](types.md)): `artifact_path,
build_tool, version ("1.0.0", or the tag for Docker), success, duration_ms,
warnings, errors`. `artifact_path` and `build_tool` reflect inputs; the rest are
constants.

## External libraries / binaries

**None.** No Maven, Gradle, npm, or Docker binary is invoked — pure-stdlib
simulators. This is what lets the example run fully offline.

## Facets & workflows

| Facet | Kind | Effect / Cost | Signature |
|---|---|---|---|
| `MavenBuild` | event | external / expensive | `MavenBuild(workspace_path, goals="clean package", profiles="", jdk_version="17", skip_tests=false) => (result: BuildResult)` |
| `GradleBuild` | event | external / expensive | `GradleBuild(workspace_path, tasks="build", jdk_version="17") => (result: BuildResult)` |
| `NpmBuild` | event | external / expensive | `NpmBuild(workspace_path, build_script="build", node_version="20") => (result: BuildResult)` |
| `DockerBuild` | event | external / expensive | `DockerBuild(workspace_path, dockerfile="Dockerfile", image_tag, build_args="") => (result: BuildResult)` |

All four are `Effect external / Cost expensive` — they represent the heaviest CI
step and, in a real deployment, the one you'd pin to a capable agent (the
pipelines attach `with AgentLabel("linux-large")` / `with Timeout(20–30m)`).

## Cache / output

**No cache, no durable output.** Dict in-process; CLI prints JSON.

## Gotchas & notes

- **Version is always `1.0.0`** (Maven/Gradle/npm) — a constant, not read from a
  POM/package.json. Docker's `version` is the tag suffix of `image_tag`.
- **`profiles`, `skip_tests`, `build_args` are declared but ignored** by the
  simulator (`docker_build` also ignores `dockerfile`/`workspace_path`, marked
  `# noqa: ARG001`). Shape parity, not behaviour.
- **The Maven handler forwards only `goals`/`jdk_version`** (not `profiles`/
  `skip_tests`) to the simulator — consistent with the shape-only design.

## Related specs

- [types](types.md) — `BuildResult`. · [scm](scm.md) — supplies `workspace_path`.
- [test](test.md) · [artifact](artifact.md) — the next stages. · [pipelines](pipelines.md).
