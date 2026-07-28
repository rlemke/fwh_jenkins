# jenkins (jenkins-pipeline)

A standalone [Facetwork](https://github.com/rlemke/facetwork) example package
demonstrating Jenkins-style CI/CD pipelines as composable FFL workflows:

- **SCM** — `GitCheckout`, `GitMerge`
- **Build** — `MavenBuild`, `GradleBuild`, `NpmBuild`, `DockerBuild`
- **Test** — `RunTests`, `CodeQuality`, `SecurityScan`
- **Artifact** — `ArchiveArtifacts`, `PublishToRegistry`, `DockerPush`
- **Deploy** — `DeployToEnvironment`, `DeployToK8s`, `RollbackDeploy`
- **Notify** — `SlackNotify`, `EmailNotify`

The 17 handlers are deterministic simulators — they return realistic
shapes without actually invoking Jenkins, Maven, npm, kubectl, etc. — so
the example can run fully offline.

## FFL at a glance

Pipelines here are written in [FFL](https://github.com/rlemke/facetwork/blob/main/docs/reference/language/grammar.md),
Facetwork's workflow language. A stage is a step (`name = Facet(args)`), ordering
comes from references, and Jenkins' `options`/`agent`/`credentials` decorations
are **mixins** applied at the call site:

```ffl
namespace my.ci {

    use jenkins.scm
    use jenkins.build
    use jenkins.test

    /** Checkout, build, and test a Maven project. */
    workflow QuickBuild(repo: String, branch: String = "main") => (version: String, passed: Long) andThen {

        src = jenkins.scm.GitCheckout(
            repo = $.repo,
            branch = $.branch) with Credentials(credentialId = "git-ssh-key", type = "ssh")

        build = jenkins.build.MavenBuild(
            workspace_path = src.info.workspace_path,
            goals = "clean package") with Timeout(minutes = 20) with Retry(maxAttempts = 2, backoffSeconds = 60)

        tests = jenkins.test.RunTests(
            workspace_path = src.info.workspace_path,
            framework = "junit",
            suite = "unit")

        yield QuickBuild(version = build.result.version, passed = tests.report.passed)
    }
}
```

```bash
fw ffl run --primary my.ffl \
  --library src/jenkins_pipeline/ffl/jenkins_types.ffl \
  --library src/jenkins_pipeline/ffl/jenkins_mixins.ffl \
  --library src/jenkins_pipeline/ffl/jenkins_scm.ffl \
  --library src/jenkins_pipeline/ffl/jenkins_build.ffl \
  --library src/jenkins_pipeline/ffl/jenkins_test.ffl \
  --workflow my.ci.QuickBuild --inputs '{"repo": "github.com/example/app"}'
```

📖 **[docs/ffl-examples.md](docs/ffl-examples.md)** — the full example gallery,
with a Jenkins→FFL translation table: parallel stages, `when` deploy gates,
`catch` as `post { failure }`, matrix builds with `foreach`, a container
pipeline, and reusing the shipped pipelines. Every snippet there is
compile-checked, and the simulators mean they all run offline.

## Feature specifications

Every feature has a spec in [**`docs/`**](docs/README.md) — how it works,
whether/how it **fans out**, the **data & fields** it produces, the
**external libraries/binaries** it uses, its **facets & workflows** (with
`Effect`/`Cost`), and its **cache/output**. Start with the flagship
[**CI/CD Pipelines**](docs/pipelines.md) (the four composed workflows that
demonstrate mixin composition); the full index is in
[`docs/README.md`](docs/README.md).

| Area | Specs |
|------|-------|
| **Flagship & cross-cutting** | [pipelines](docs/pipelines.md) · [mixins](docs/mixins.md) · [types](docs/types.md) · [tools-and-simulators](docs/tools-and-simulators.md) · [catalog](docs/catalog.md) |
| **CI/CD operations** | [scm](docs/scm.md) · [build](docs/build.md) · [test](docs/test.md) · [artifact](docs/artifact.md) · [deploy](docs/deploy.md) · [notify](docs/notify.md) |

Discovered by the Facetwork runner via the `facetwork.domains` entry point
declared in `pyproject.toml`. After `pip install -e .`, Facetwork's
`fw runner start --domain jenkins` and `fw ffl seed`
pick this package up automatically.

## Install

```bash
git clone https://github.com/rlemke/fwh_jenkins.git ~/fw_handlers/fwh_jenkins
cd ~/fw_handlers/fwh_jenkins
pip install -e .
```

This registers the package under the `facetwork.domains` entry-point group,
making it discoverable by any Facetwork installation in the same environment.

## Run from a Facetwork checkout

```bash
fw ffl seed --include jenkins                  # one-time, seeds FFL
fw runner start --domain jenkins -- --log-format text
```

## Run a single CI/CD operation from the command line

Every facet has a matching CLI tool under `src/jenkins_pipeline/tools/`,
so you can exercise the same simulator without going through FFL:

```bash
src/jenkins_pipeline/tools/git-checkout.sh --repo github.com/example/app --branch main
src/jenkins_pipeline/tools/maven-build.sh --workspace /tmp/app --goals "clean package"
src/jenkins_pipeline/tools/run-tests.sh --framework junit --suite unit
src/jenkins_pipeline/tools/deploy-to-k8s.sh --cluster prod --namespace default --replicas 3
src/jenkins_pipeline/tools/slack-notify.sh --channel '#deploys' --message 'shipping v1.0.0'
```

The CLIs print the JSON result that the FFL handler would emit, plus a
human-readable summary on stderr. They exit non-zero if the simulator
detects an invalid configuration.

## Layout

```
fwh_jenkins/
├── pyproject.toml                  # facetwork.domains entry point
├── README.md
├── CLAUDE.md                       # guidance for Claude Code in this repo
├── USER_GUIDE.md                   # human-facing walkthrough
├── agent-spec/                     # tools-pattern, cache-layout specs
├── agent.py                        # standalone AgentPoller variant
├── tests/                          # mocked + real test trees
└── src/jenkins_pipeline/
    ├── __init__.py                 # exports `domain: DomainPackage`
    ├── handlers/                   # 6 event-facet modules + shared/ shim
    │   ├── scm_handlers.py
    │   ├── build_handlers.py
    │   ├── test_handlers.py
    │   ├── artifact_handlers.py
    │   ├── deploy_handlers.py
    │   ├── notify_handlers.py
    │   └── shared/jenkins_utils.py # imports the real impl from tools/_lib
    ├── ffl/                        # 9 FFL files
    └── tools/
        ├── _lib/                   # the real simulator (one .py per domain)
        │   ├── scm.py
        │   ├── build.py
        │   ├── test.py
        │   ├── artifact.py
        │   ├── deploy.py
        │   └── notify.py
        ├── *.py                    # one CLI per facet (17 total)
        └── *.sh                    # shell wrappers
```

The `tools/` dir gives every facet a CLI; the FFL handlers call into the
**same** `tools/_lib/` modules via the `handlers/shared/jenkins_utils.py`
shim. Both surfaces share one implementation, no drift.

## License

Apache 2.0 — see `LICENSE`.
