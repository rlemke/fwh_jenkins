# Tools, Simulators & the Dual-Surface Pattern

**Simulators:** `src/jenkins_pipeline/tools/_lib/{scm,build,test,artifact,deploy,notify}.py` ·
**CLIs:** `src/jenkins_pipeline/tools/<verb>_<noun>.py` + `<verb>-<noun>.sh` (17 each) ·
**Shim:** `src/jenkins_pipeline/handlers/shared/jenkins_utils.py` ·
**Handlers:** `src/jenkins_pipeline/handlers/<domain>_handlers.py` ·
**Agent:** `agent.py` · **Docs:** `src/jenkins_pipeline/tools/README.md`,
`agent-spec/tools-pattern.agent-spec.yaml`

## Overview

This spec documents the *architecture* every operation facet shares, rather than a
CI/CD capability. The package implements the Facetwork **tools / handlers / `_lib`
pattern**: every facet has **two surfaces** — a standalone CLI and an FFL
event-facet handler — and both call into the **same** deterministic simulator in
`tools/_lib/<domain>.py`. One implementation, no drift. This is the reference
example the framework's `agent-spec/tools-pattern.agent-spec.yaml` describes.

The simulators are **pure-stdlib, side-effect-free functions**: they take
keyword args and return a constant-shaped dict. No MongoDB, no network, no
subprocess, no `facetwork.runtime` import. That standalone-ness is deliberate —
the CLIs run with no Facetwork stack at all.

## How it works

```
                     ┌─────────────────────────────────┐
   CLI tool  ────────┤  tools/_lib/<domain>.py         │
   (tools/*.py)      │  (deterministic simulator,      │ ← single source of truth
   FFL handler ──────┤   pure stdlib, returns a dict)  │
   (via shim)        └─────────────────────────────────┘
```

1. **`_lib/<domain>.py`** — the simulator functions (`git_checkout`,
   `maven_build`, `run_tests`, `deploy_to_k8s`, `slack_notify`, …). Keyword-only
   args, return a `dict[str, Any]`.
2. **CLI (`tools/<verb>_<noun>.py`)** — argparse over stdin flags, imports the
   simulator by its **fully-qualified** path
   (`from jenkins_pipeline.tools._lib.scm import git_checkout`), prints a
   one-line human summary to **stderr** and the pretty-printed JSON dict to
   **stdout**, exits 0 (non-zero on argparse/simulated failure). A thin
   `<verb>-<noun>.sh` `exec`s the `.py` so it works from any shell.
3. **Handler (`handlers/<domain>_handlers.py`)** — imports the same simulator via
   the `handlers/shared/jenkins_utils.py` shim, calls it with payload values, and
   wraps the dict under the FFL return key (`{"result": …}` / `{"info": …}` /
   `{"report": …}` / `{"artifact": …}`; notify handlers return the tuple fields
   flat). Dispatch is a `_DISPATCH` map keyed by fully-qualified facet name, with
   a `handle(payload)` entrypoint that raises `ValueError("Unknown facet: …")` on
   a miss.

### Handler registration (two runner models)

Each `<domain>_handlers.py` exposes both:
- `register_handlers(runner)` — RegistryRunner: registers each facet with
  `module_uri=file://…`, `entrypoint="handle"`.
- `register_<domain>_handlers(poller)` — AgentPoller: `poller.register(fqn,
  func)` per facet.

`handlers/__init__.py` aggregates them into `register_all_registry_handlers` and
`register_all_handlers`. `test_handler_dispatch_jenkins.py` asserts the total is
**17** (2 scm + 4 build + 3 test + 3 artifact + 3 deploy + 2 notify).

## Fan-out

**N/A** — this is infrastructure. Fan-out is a workflow property (see
[pipelines](pipelines.md) `MultiModuleBuild`).

## Data & fields

The 17 simulators and their return-dict shape map onto the `jenkins.types`
schemas (see [types](types.md)). The returns are **constant or lightly-derived**:
e.g. `git_checkout` always returns `commit_sha
"a1b2c3d4e5f6…"`, `author "jenkins-ci"`, `clone_duration_ms 4500`, with
`workspace_path` derived as `/var/jenkins/workspace/<repo-leaf>`; `run_tests`
always returns `total 342, passed 335, failed 2, coverage_pct 87.3`.

## External libraries / binaries

**None for the simulators or CLIs** — pure stdlib (`argparse`, `json`, `sys`).
The package's only runtime dep beyond `facetwork` is `PyYAML`, used solely by the
[catalog](catalog.md) loader, not by any tool. No Maven/Docker/kubectl/Slack
client is imported — that is the whole design.

## Facets & workflows

Not a facet itself — the plumbing behind all six operation namespaces. Per-domain
facet lists live in [scm](scm.md), [build](build.md), [test](test.md),
[artifact](artifact.md), [deploy](deploy.md), [notify](notify.md).

## Cache / output

**No cache; ephemeral output only.** Simulator returns are in-process dicts; CLIs
print JSON to stdout. Nothing is written to `$FW_CACHE_ROOT`, disk, or MinIO/S3.

## Gotchas & notes

- **Fully-qualified `_lib` imports are load-bearing.** The shim and every CLI
  import `jenkins_pipeline.tools._lib.<domain>` — never the bare `_lib` — so this
  package coexists with sibling Facetwork packages (osm-geocoder, noaa-weather)
  that also ship a `tools/_lib/`. A bare `import _lib` would fight for the name on
  `sys.modules`.
- **Keep `_lib/` free of `facetwork.runtime` / `pymongo`.** The CLI contract
  requires the simulators run with no Facetwork stack; adding a runtime import
  breaks that (and the CLAUDE.md code-review checklist calls it out).
- **Simulators drop some FFL params.** Several `_lib` functions accept fewer args
  than the FFL facet declares (e.g. `security_scan` ignores `severity_threshold`;
  `archive_artifacts` ignores `includes`; `docker_build` ignores `dockerfile`/
  `workspace_path` — all marked `# noqa: ARG001 — kept for API parity`). The
  handlers likewise pass only a subset of payload keys. The returns are
  shape-accurate, not input-faithful.
- **Two entry-point mismatches to know about.** (1) The repo `README.md`/`CLAUDE.md`
  refer to a `facetwork.examples` entry point and `ExamplePackage`, but the
  shipped `pyproject.toml` + `__init__.py` register under **`facetwork.domains`**
  as a `DomainPackage(name="jenkins", …)`. (2) `agent.py` sets
  `server_group="jenkins"`. Trust the code.

## Related specs

- [scm](scm.md) · [build](build.md) · [test](test.md) · [artifact](artifact.md)
  · [deploy](deploy.md) · [notify](notify.md) — the six domains built on this
  pattern.
- [catalog](catalog.md) — the machine-readable index over the same facets.
