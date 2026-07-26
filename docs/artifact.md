# Artifact (archive / registry publish / Docker push)

**Namespace:** `jenkins.artifact` ·
**FFL:** `src/jenkins_pipeline/ffl/jenkins_artifacts.ffl` ·
**Handlers:** `src/jenkins_pipeline/handlers/artifact_handlers.py` ·
**Simulator:** `src/jenkins_pipeline/tools/_lib/artifact.py` ·
**CLIs:** `tools/{archive-artifacts,publish-to-registry,docker-push}.{py,sh}`

## Overview

`jenkins.artifact` is the **publish stage** — collecting build outputs and
pushing them to a registry. Three facets: archive workspace files, publish to a
Maven/npm-style registry, and push a Docker image to a container registry. Each
is a **deterministic simulator** returning an `Artifact` shape (name, path, size,
checksum, registry URL, tag) without moving any bytes.

## How it works

Handlers wrap simulator dicts under `{"artifact": …}`:

- `ArchiveArtifacts` → `archive_artifacts(workspace_path, includes)` → `Artifact`
  with `name "app-1.0.0.jar", size_bytes 15,728,640, checksum "sha256:a1b2…",
  registry_url ""` (local archival — no remote system, hence `registry_url`
  empty).
- `PublishToRegistry` → `publish_to_registry(registry_url, version, group_id,
  artifact_path)` → `Artifact` with a derived `registry_url
  "<base>/<group/as/path>/app/<version>"` and `name "<group_id>:app"`.
- `DockerPush` → `docker_push(image_tag, registry_url)` → `Artifact` with `path
  "<registry>/<image_tag>", size_bytes 256,000,000, tag` = the image tag suffix.

## Fan-out

**Single-task per call — no fan-out.** `MultiModuleBuild` calls
`ArchiveArtifacts` once per module through the workflow `foreach` (see
[pipelines](pipelines.md)).

## Data & fields

All three return `Artifact` (see [types](types.md)): `name, path, size_bytes,
checksum, registry_url, tag`. Checksums are hardcoded `sha256:` constants; sizes
are constants (`~15 MB` jar, `256 MB` image). `registry_url`/`path`/`tag` are
derived from inputs.

## External libraries / binaries

**None.** No `mvn deploy`, `npm publish`, `docker push`, or registry client —
pure-stdlib simulators.

## Facets & workflows

| Facet | Kind | Effect / Cost | Signature |
|---|---|---|---|
| `ArchiveArtifacts` | event | **io** / cheap | `ArchiveArtifacts(workspace_path, includes, excludes="") => (artifact: Artifact)` |
| `PublishToRegistry` | event | external / moderate | `PublishToRegistry(artifact_path, registry_url, group_id="", version="") => (artifact: Artifact)` |
| `DockerPush` | event | external / expensive | `DockerPush(image_tag, registry_url) => (artifact: Artifact)` |

`ArchiveArtifacts` is the **only `io`-effect, `cheap`-cost facet in the whole
package** — it represents workspace file collection with no remote system, which
`catalog.yaml` records explicitly. The other two drive external registries.

## Cache / output

**No cache, no durable output.** Despite representing archival/publishing, the
simulators write nothing — the returned `path`/`registry_url` are simulated
strings, not real locations. CLI prints JSON.

## Gotchas & notes

- **`ArchiveArtifacts` archives nothing** — `includes` is accepted for API parity
  and ignored (`# noqa: ARG001`); no files are copied. Its `io` effect labels the
  *represented* operation, not observable disk I/O.
- **Sizes/checksums are constants.** The `256 MB` Docker image size and every
  `sha256:` digest are fixed literals.
- **`ArchiveArtifacts.registry_url` is intentionally `""`** — local archival has
  no registry; `PublishToRegistry`/`DockerPush` fill it.

## Related specs

- [types](types.md) — `Artifact`. · [build](build.md) — supplies the artifact.
- [deploy](deploy.md) — consumes the published artifact. · [pipelines](pipelines.md).
