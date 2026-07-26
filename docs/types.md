# Shared Types (schema vocabulary)

**Namespace:** `jenkins.types` ·
**FFL:** `src/jenkins_pipeline/ffl/jenkins_types.ffl` ·
**Handlers:** none — schema declarations only ·
**Tests:** `tests/mocked/py/test_jenkins_compilation.py` (`TestJenkinsTypes`)

## Overview

`jenkins.types` is the shared **schema vocabulary** every operation namespace
`use`s. It declares seven schemas that are the return shapes of the event facets
and the data that flows between pipeline steps. Centralising them here is what
lets a `MavenBuild`'s `BuildResult.artifact_path` feed a
`DeployToEnvironment`'s `artifact_path` param without redefining the shape — the
[pipelines](pipelines.md) rely on this single vocabulary.

## How it works

Each schema is `schema <Name> { field: Type, … }` inside the namespace. Every
operation file begins with `use jenkins.types` and names these schemas in its
facet return clauses (e.g. `event facet MavenBuild(…) => (result: BuildResult)`).
The simulators in `tools/_lib/` return plain dicts whose keys match these fields;
the handlers wrap them under the FFL return key (`result`/`info`/`report`/
`artifact`) — so the schema field names and the `_lib` dict keys must stay in
sync.

## Fan-out

**N/A** — type declarations do not execute.

## Data & fields

The seven schemas and their fields (verbatim from the FFL):

| Schema | Fields |
|---|---|
| `ScmInfo` | `repo, branch, commit_sha, commit_message, author, workspace_path: String; clone_duration_ms: Long` |
| `BuildResult` | `artifact_path, build_tool, version: String; success: Boolean; duration_ms, warnings, errors: Long` |
| `TestReport` | `total, passed, failed, skipped, duration_ms: Long; report_path: String; coverage_pct: Double` |
| `QualityReport` | `tool: String; issues, critical, major, minor: Long; report_path: String; passed: Boolean` |
| `Artifact` | `name, path: String; size_bytes: Long; checksum, registry_url, tag: String` |
| `DeployResult` | `environment, strategy, version, url: String; replicas: Long; healthy: Boolean; deploy_id: String` |
| `PipelineStatus` | `pipeline_name: String; build_number: Long; status: String; duration_ms: Long; url: String` |

Which facet returns which: `ScmInfo` ← scm; `BuildResult` ← build; `TestReport`
← `RunTests`; `QualityReport` ← `CodeQuality`/`SecurityScan`; `Artifact` ←
artifact; `DeployResult` ← deploy. `PipelineStatus` is declared but **not
currently returned by any facet or workflow** — it is available vocabulary for a
pipeline-status facet that has not been added.

## External libraries / binaries

**None.** Pure FFL schema declarations.

## Facets & workflows

**None** — this namespace declares no facets or workflows, only schemas.

## Cache / output

**N/A** — no runtime footprint.

## Gotchas & notes

- **Field names are the contract between FFL and `_lib`.** A simulator dict key
  must match its schema field, or the value silently drops. The notify facets are
  the exception — they return `(sent, timestamp)` / `(sent, message_id)` tuples,
  not a schema (see [notify](notify.md)).
- **`PipelineStatus` is unused** — declared vocabulary with no producer. Do not
  assume a facet emits it.
- **Numeric widths:** counts/durations are `Long`, `coverage_pct` is `Double`.
  The Python simulators return plain ints/floats; the runtime coerces to the FFL
  types.

## Related specs

- Every operation spec consumes these: [scm](scm.md), [build](build.md),
  [test](test.md), [artifact](artifact.md), [deploy](deploy.md),
  [notify](notify.md).
- [pipelines](pipelines.md) — where the schemas flow step to step.
