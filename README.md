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

Discovered by the Facetwork runner via the `facetwork.examples` entry point
declared in `pyproject.toml`. After `pip install -e .`, Facetwork's
`scripts/start-runner --example jenkins` and `scripts/seed-examples`
pick this package up automatically.

## Install

```bash
git clone https://github.com/rlemke/fwh_jenkins.git ~/fw_handlers/fwh_jenkins
cd ~/fw_handlers/fwh_jenkins
pip install -e .
```

This registers the package under the `facetwork.examples` entry-point group,
making it discoverable by any Facetwork installation in the same environment.

## Run from a Facetwork checkout

```bash
scripts/seed-examples --include jenkins                  # one-time, seeds FFL
scripts/start-runner --example jenkins -- --log-format text
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
├── pyproject.toml                  # facetwork.examples entry point
├── README.md
├── CLAUDE.md                       # guidance for Claude Code in this repo
├── USER_GUIDE.md                   # human-facing walkthrough
├── agent-spec/                     # tools-pattern, cache-layout specs
├── agent.py                        # standalone AgentPoller variant
├── tests/                          # mocked + real test trees
└── src/jenkins_pipeline/
    ├── __init__.py                 # exports `example: ExamplePackage`
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
