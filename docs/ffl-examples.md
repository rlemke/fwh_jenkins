# FFL Examples — `jenkins`

Every numbered scenario is a **complete, compilable FFL file**. Copy one into
`my.ffl` and run it:

```bash
fw ffl run --primary my.ffl \
  --library src/jenkins_pipeline/ffl/jenkins_types.ffl \
  --library src/jenkins_pipeline/ffl/jenkins_mixins.ffl \
  --library src/jenkins_pipeline/ffl/jenkins_scm.ffl \
  --library src/jenkins_pipeline/ffl/jenkins_build.ffl \
  --library src/jenkins_pipeline/ffl/jenkins_test.ffl \
  --workflow my.ci.<WorkflowName>
```

(Add a `--library` per FFL file your workflow touches, or `fw ffl seed --include
jenkins` once.) A runner serving the `jenkins` namespace must be up
(`fw runner start --domain jenkins`). Every block below is compile-checked
against `src/jenkins_pipeline/ffl/`.

All 17 handlers are **deterministic simulators** — nothing here actually invokes
Jenkins, Maven or kubectl — so these examples run offline and are a good way to
learn the language without waiting on real builds.

New to the language? Start with the
[FFL grammar](https://github.com/rlemke/facetwork/blob/main/docs/reference/language/grammar.md)
and the [canonical examples](https://github.com/rlemke/facetwork/tree/main/examples/canonical).

---

## The facets at a glance

| Namespace | Facets |
|---|---|
| `jenkins.scm` | `GitCheckout(repo, branch, depth, submodules) => (info: ScmInfo)`, `GitMerge` |
| `jenkins.build` | `MavenBuild`, `GradleBuild`, `NpmBuild`, `DockerBuild` → `(result: BuildResult)` |
| `jenkins.test` | `RunTests => (report: TestReport)`, `CodeQuality`, `SecurityScan` → `(report: QualityReport)` |
| `jenkins.artifact` | `ArchiveArtifacts`, `PublishToRegistry`, `DockerPush` → `(artifact: Artifact)` |
| `jenkins.deploy` | `DeployToEnvironment(artifact_path, environment, strategy, version)`, `DeployToK8s`, `RollbackDeploy` → `(result: DeployResult)` |
| `jenkins.notify` | `SlackNotify`, `EmailNotify` |
| `jenkins.mixins` | `Retry`, `Timeout`, `Credentials`, `Notification`, `AgentLabel`, `Stash` + three `implicit` defaults |
| `jenkins.pipeline` | `JavaMavenCI`, `DockerK8sDeploy`, `MultiModuleBuild`, `FullCIPipeline` |

The interesting part of this domain is **`jenkins.mixins`**: Jenkins concepts that
are *decorations* on a step (retry, timeout, credentials, agent label,
notification) are mixins, not parameters — so any step can be decorated at its
call site without changing the facet.

---

## 1. Run what ships — no FFL to write

```bash
fw ffl seed --include jenkins

fw ffl run --workflow jenkins.pipeline.JavaMavenCI \
  --inputs '{"repo": "github.com/example/app", "branch": "main", "environment": "staging"}'

fw ffl run --workflow jenkins.pipeline.FullCIPipeline \
  --inputs '{"repo": "github.com/example/app", "deploy_env": "prod", "notify_channel": "#releases"}'
```

Write FFL when you want a different *shape* — your own stage order, extra quality
gates, a matrix build, or different failure handling.

## 2. The smallest pipeline you can write

Every FFL workflow needs a `namespace`, a `use` per namespace it calls into, and a
`yield` back to itself.

```ffl
namespace my.ci {

    use jenkins.scm
    use jenkins.build
    use jenkins.test

    /** Checkout, build, and test a Maven project. */
    workflow QuickBuild(repo: String, branch: String = "main") => (version: String, passed: Long) andThen {

        src = jenkins.scm.GitCheckout(repo = $.repo, branch = $.branch)

        build = jenkins.build.MavenBuild(
            workspace_path = src.info.workspace_path,
            goals = "clean package")

        tests = jenkins.test.RunTests(
            workspace_path = src.info.workspace_path,
            framework = "junit",
            suite = "unit")

        yield QuickBuild(version = build.result.version, passed = tests.report.passed)
    }
}
```

Rules visible above: `=>` sits on the **same line** as the closing `)`; references
are always `step.field` and schema results nest one level
(`src.info.workspace_path`); `$.repo` reads the workflow's parameter.

## 3. Mixins are the Jenkins vocabulary

`with Credentials(...)`, `with Timeout(...)`, `with Retry(...)`,
`with AgentLabel(...)`, `with Notification(...)` — these are what a Jenkinsfile
expresses as `options`/`agent`/`credentials` blocks, attached per step.

```ffl
namespace my.ci {

    use jenkins.scm
    use jenkins.build
    use jenkins.deploy

    /** Credentials on checkout, retry on build, notification on deploy. */
    workflow DecoratedBuild(repo: String, branch: String = "main", target_env: String = "staging") => (deploy_url: String) andThen {

        src = jenkins.scm.GitCheckout(
            repo = $.repo,
            branch = $.branch) with Credentials(credentialId = "git-ssh-key", type = "ssh")

        build = jenkins.build.MavenBuild(
            workspace_path = src.info.workspace_path,
            goals = "clean package -DskipTests") with Timeout(minutes = 20) with Retry(maxAttempts = 2, backoffSeconds = 60)

        deploy = jenkins.deploy.DeployToEnvironment(
            artifact_path = build.result.artifact_path,
            environment = $.target_env,
            version = build.result.version) with Credentials(credentialId = "deploy-token") with Notification(channel = "#deployments")

        yield DecoratedBuild(deploy_url = deploy.result.url)
    }
}
```

Three `implicit` declarations in `jenkins.mixins` already apply default retry,
timeout and agent to every step — a call-site mixin **overrides** the default for
that step only.

## 4. Parallel stages come free

Tests, code quality and the security scan all reference only the checkout, never
each other, so the runtime dispatches them **concurrently** — the FFL equivalent
of a Jenkins `parallel` block, with no extra syntax.

```ffl
namespace my.ci {

    use jenkins.scm
    use jenkins.test

    /** Three quality gates at once. */
    workflow ParallelGates(repo: String, branch: String = "main") => (coverage: Double, issues: Long, critical: Long) andThen {

        src = jenkins.scm.GitCheckout(repo = $.repo, branch = $.branch)

        tests = jenkins.test.RunTests(workspace_path = src.info.workspace_path, framework = "junit")
        quality = jenkins.test.CodeQuality(workspace_path = src.info.workspace_path, tool = "sonarqube")
        security = jenkins.test.SecurityScan(workspace_path = src.info.workspace_path, scanner = "trivy")

        yield ParallelGates(
            coverage = tests.report.coverage_pct,
            issues = quality.report.issues,
            critical = security.report.critical)
    }
}
```

## 5. Gate the deploy — `when`

A `when` block hangs off the step it inspects: inside a case `$` is that step and
`$$` reaches the workflow. Every `when` needs a default case, last, and conditions
must be real `Boolean`s (no truthy coercion).

```ffl
namespace my.ci {

    use jenkins.scm
    use jenkins.build
    use jenkins.test
    use jenkins.deploy

    /** Deploy only when the test suite is green. */
    workflow GatedDeploy(repo: String, branch: String = "main", target_env: String = "staging") => (status: String, deploy_url: String) andThen {

        src = jenkins.scm.GitCheckout(repo = $.repo, branch = $.branch)

        build = jenkins.build.MavenBuild(workspace_path = src.info.workspace_path)

        tests = jenkins.test.RunTests(
            workspace_path = src.info.workspace_path, framework = "junit") andThen when {
            case $.report.failed == 0 => {
                deploy = jenkins.deploy.DeployToEnvironment(
                    artifact_path = "target/app.jar",
                    environment = $$.target_env)
                yield GatedDeploy(status = "deployed", deploy_url = deploy.result.url)
            }
            case _ => {
                yield GatedDeploy(status = "tests_failed", deploy_url = "")
            }
        }
    }
}
```

> Note the shape: the deploy has to live **inside** the `when` case, because a
> block may only reference steps in its own block (plus `$…` container
> attributes). To gate on several prior steps, pass them in as parameters instead
> of nesting deeper.

## 6. Roll back on a failed deploy — `catch`

`catch` fires when its step errors after retries are exhausted. This is the
Jenkins `post { failure { … } }` equivalent, scoped to one step.

```ffl
namespace my.ci {

    use jenkins.build
    use jenkins.deploy
    use jenkins.notify

    /** If the deploy fails, say so on Slack instead of failing silently. */
    workflow SafeDeploy(artifact_path: String, target_env: String = "prod", version: String = "1.0.0") => (status: String, url: String) andThen {

        deploy = jenkins.deploy.DeployToEnvironment(
            artifact_path = $.artifact_path,
            environment = $.target_env,
            strategy = "blue-green",
            version = $.version) with Retry(maxAttempts = 2, backoffSeconds = 30) catch {
            yield SafeDeploy(status = "deploy_failed", url = "")
        }

        notify = jenkins.notify.SlackNotify(
            channel = "#releases",
            message = "Deployed " ++ $.version ++ " to " ++ $.target_env,
            color = "good")

        yield SafeDeploy(status = "deployed", url = deploy.result.url)
    }
}
```

## 7. Matrix builds — `foreach`

`andThen foreach v in <list>` runs the body once per element, in parallel across
the fleet. Here the `foreach` hangs off the **workflow**, so the loop variable and
the workflow's parameters share one `$`. This is `MultiModuleBuild`'s shape.

```ffl
namespace my.ci {

    use jenkins.scm
    use jenkins.build
    use jenkins.artifact

    /** One build+archive per module, all modules in parallel. */
    workflow MatrixBuild(repo: String, modules: Json, branch: String = "main") => (artifacts: [String]) andThen foreach m in $.modules {

        src = jenkins.scm.GitCheckout(repo = $.repo, branch = $.branch)

        build = jenkins.build.MavenBuild(
            workspace_path = src.info.workspace_path,
            goals = "clean package -pl " ++ $.m)

        archived = jenkins.artifact.ArchiveArtifacts(
            workspace_path = src.info.workspace_path,
            includes = "target/*.jar")

        yield MatrixBuild(artifacts = [archived.artifact.path])
    }
}
```

```bash
fw ffl run --primary my.ffl --library … --workflow my.ci.MatrixBuild \
  --inputs '{"repo": "github.com/example/app", "modules": ["core", "api", "web"]}'
```

## 8. Container pipeline — build, scan, push, deploy

```ffl
namespace my.ci {

    use jenkins.scm
    use jenkins.build
    use jenkins.test
    use jenkins.artifact
    use jenkins.deploy

    /** Docker build → scan → push → k8s rollout. */
    workflow ContainerPipeline(repo: String, image_tag: String, registry_url: String,
        k8s_namespace: String = "default", replicas: Int = 2) => (deploy_url: String, healthy: Boolean) andThen {

        src = jenkins.scm.GitCheckout(repo = $.repo) with AgentLabel(label = "docker")

        build = jenkins.build.DockerBuild(
            workspace_path = src.info.workspace_path,
            image_tag = $.image_tag) with Timeout(minutes = 30) with AgentLabel(label = "docker")

        scan = jenkins.test.SecurityScan(
            workspace_path = src.info.workspace_path,
            scanner = "trivy",
            severity_threshold = "CRITICAL")

        push = jenkins.artifact.DockerPush(
            image_tag = $.image_tag,
            registry_url = $.registry_url) with Credentials(credentialId = "registry-creds") with Retry(maxAttempts = 3, backoffSeconds = 10)

        deploy = jenkins.deploy.DeployToK8s(
            artifact_path = push.artifact.path,
            k8s_namespace = $.k8s_namespace,
            cluster = "production",
            replicas = $.replicas,
            image_tag = $.image_tag) with Credentials(credentialId = "k8s-token") with Timeout(minutes = 10)

        yield ContainerPipeline(deploy_url = deploy.result.url, healthy = deploy.result.healthy)
    }
}
```

## 9. Reuse the shipped pipelines

Workflows compose like facets — wrap one instead of forking it.

```ffl
namespace my.ci {

    use jenkins.pipeline
    use jenkins.notify

    /** Run the shipped Java CI pipeline, then announce the result. */
    workflow CIWithAnnounce(repo: String, branch: String = "main") => (version: String, sent: Boolean) andThen {

        run = jenkins.pipeline.JavaMavenCI(repo = $.repo, branch = $.branch)

        notify = jenkins.notify.SlackNotify(
            channel = "#ci",
            message = "Built " ++ run.version ++ " → " ++ run.deploy_url,
            color = "good")

        yield CIWithAnnounce(version = run.version, sent = notify.sent)
    }
}
```

---

## Cheat sheet

| Jenkins concept | FFL |
|---|---|
| Stage | a step: `build = jenkins.build.MavenBuild(…)` |
| `parallel` block | steps that don't reference each other |
| Stage ordering | reference the earlier step: `workspace_path = src.info.workspace_path` |
| `options { retry(2) }` | `… with Retry(maxAttempts = 2, backoffSeconds = 60)` |
| `options { timeout(…) }` | `… with Timeout(minutes = 20)` |
| `agent { label 'docker' }` | `… with AgentLabel(label = "docker")` |
| `withCredentials { … }` | `… with Credentials(credentialId = "…", type = "ssh")` |
| `post { failure { … } }` | `step = Facet(…) catch { yield … }` |
| `when { expression { … } }` | `step = Facet(…) andThen when { case <bool> => { … } case _ => { … } }` |
| Matrix build | `workflow W(items: Json) … andThen foreach i in $.items { … }` |
| Read a parameter | `$.name` (`$$.name` one level out) |

**Validate before you run:** `afl my.ffl --check` or MCP `fw_validate`. Every error
carries a `rule_id` — fetch `fw://docs/rules/{rule_id}` for a wrong/right pair.

## See also

- [`docs/README.md`](README.md) — per-feature specs for this domain
- [`docs/pipelines.md`](pipelines.md) — the four shipped pipelines in detail ·
  [`docs/mixins.md`](mixins.md) — the mixin library and the `implicit` defaults
- [FFL grammar](https://github.com/rlemke/facetwork/blob/main/docs/reference/language/grammar.md) ·
  [canonical examples](https://github.com/rlemke/facetwork/tree/main/examples/canonical) ·
  [relative `$`-scoping](https://github.com/rlemke/facetwork/blob/main/docs/architecture/ffl-relative-scoping.md)
- `src/jenkins_pipeline/ffl/` — the source of truth for every signature above
