# CLAUDE.md — jenkins (jenkins-pipeline)

This repository is a **standalone Facetwork example package**. The Facetwork
platform (workflow compiler + runtime) lives at
`/Users/ralph_lemke/facetwork`; this repo only contains the Jenkins-specific
FFL, handlers, and tools. The two are wired together via the
`facetwork.examples` entry point in `pyproject.toml`.

## Quick orientation

```
fwh_jenkins/
├── pyproject.toml                       # declares the facetwork.examples entry point
├── src/jenkins_pipeline/__init__.py     # exports `example: ExamplePackage`
├── src/jenkins_pipeline/handlers/       # 6 event-facet modules + shared/ shim
├── src/jenkins_pipeline/ffl/            # FFL workflows + mixins
├── src/jenkins_pipeline/tools/          # CLI utilities + _lib/ (simulators)
├── tests/                               # mocked + real test trees
└── agent-spec/                          # cross-cutting design specs
```

## Common operations

```bash
# Register this package with Facetwork's runner
pip install -e .

# From a Facetwork checkout:
scripts/seed-examples --include jenkins
scripts/start-runner --example jenkins -- --log-format text

# Run as a standalone agent (skip the registry runner path):
PYTHONPATH=src python agent.py

# CLIs (call the same _lib/ as the handlers — see Tools pattern below):
src/jenkins_pipeline/tools/git-checkout.sh --repo github.com/example/app --branch main
src/jenkins_pipeline/tools/maven-build.sh --workspace /tmp/app --goals "clean package"
src/jenkins_pipeline/tools/run-tests.sh --framework junit --suite unit
src/jenkins_pipeline/tools/docker-push.sh --image-tag app:1.0.0 --registry registry.example.com

# Tests
pytest tests/ src/jenkins_pipeline/handlers/ -v
```

## Key concepts

### Tools / handlers / _lib pattern

Every facet has two surfaces — a CLI under `src/jenkins_pipeline/tools/`
and an FFL handler under `src/jenkins_pipeline/handlers/<domain>_handlers.py`
— and both call into the **same** simulator implementation in
`src/jenkins_pipeline/tools/_lib/`. This is the Facetwork canonical
pattern (see `agent-spec/tools-pattern.agent-spec.yaml`).

```
                       ┌─────────────────────────────┐
   CLI tool ───────────┤                             │
                       │   tools/_lib/<domain>.py    │ ← single source of truth
   FFL handler ────────┤   (deterministic simulator) │
   (via shared shim)   │                             │
                       └─────────────────────────────┘
```

The shim lives at `src/jenkins_pipeline/handlers/shared/jenkins_utils.py`.
It re-exports the per-domain modules via the **fully-qualified** package
path (`from jenkins_pipeline.tools._lib.scm import …`) — never the bare
`_lib` name — so this package coexists cleanly with sibling
`facetwork.examples` packages (osm-geocoder, noaa-weather) that also ship
their own `_lib` directories.

### Handler / domain map

| Domain | Facets | _lib module | Handler module |
|--------|--------|-------------|----------------|
| `jenkins.scm` | GitCheckout, GitMerge | `tools/_lib/scm.py` | `handlers/scm_handlers.py` |
| `jenkins.build` | MavenBuild, GradleBuild, NpmBuild, DockerBuild | `tools/_lib/build.py` | `handlers/build_handlers.py` |
| `jenkins.test` | RunTests, CodeQuality, SecurityScan | `tools/_lib/test.py` | `handlers/test_handlers.py` |
| `jenkins.artifact` | ArchiveArtifacts, PublishToRegistry, DockerPush | `tools/_lib/artifact.py` | `handlers/artifact_handlers.py` |
| `jenkins.deploy` | DeployToEnvironment, DeployToK8s, RollbackDeploy | `tools/_lib/deploy.py` | `handlers/deploy_handlers.py` |
| `jenkins.notify` | SlackNotify, EmailNotify | `tools/_lib/notify.py` | `handlers/notify_handlers.py` |

### CLI contract

Every CLI script in `tools/`:

- Uses argparse with `--help`
- Logs human-readable progress to **stderr**
- Prints a JSON dict with the simulated result to **stdout**
- Exits 0 on success, non-zero on bad input or simulated failure
- Never imports MongoDB or facetwork.runtime — `_lib/` stays standalone

This means the CLIs run with no Facetwork stack at all:

```bash
$ src/jenkins_pipeline/tools/maven-build.sh --workspace /tmp/app --goals "clean package"
MavenBuild: clean package in /tmp/app
{"artifact_path": "/tmp/app/target/app-1.0.0.jar", "build_tool": "maven-3.9.6/jdk-17", ...}
```

## Adding new facets

1. Add a simulator function to the right `tools/_lib/<domain>.py`
   (or create a new domain module; pick a short name).
2. Add a CLI wrapper at `tools/<verb>-<noun>.py` (and a thin
   `tools/<verb>-<noun>.sh` for ergonomics) that argparse-parses input,
   calls the `_lib` function, and prints JSON.
3. Re-export the simulator from `handlers/shared/jenkins_utils.py`.
4. Add a `_<facet_lower>_handler(payload)` to the matching
   `handlers/<domain>_handlers.py` and wire it into `_DISPATCH`.
5. Drop the FFL declaration into `src/jenkins_pipeline/ffl/`.
6. Re-run `scripts/seed-examples --include jenkins` so the new flow
   shows up in the dashboard.

## Code review checklist

- For every state transition: "what if this crashes halfway?" Design the recovery path.
- For every retry: max count and backoff. No infinite loops.
- For every shared resource (thread pool, connection, queue): consider isolation/bulkheads.
- For every error handler: never silently return empty defaults. Fail explicitly or re-raise.
- Keep `_lib/` free of `facetwork.runtime` / `pymongo` deps so CLIs stay runnable standalone.
