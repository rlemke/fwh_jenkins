# SCM (source control)

**Namespace:** `jenkins.scm` ·
**FFL:** `src/jenkins_pipeline/ffl/jenkins_scm.ffl` ·
**Handlers:** `src/jenkins_pipeline/handlers/scm_handlers.py` ·
**Simulator:** `src/jenkins_pipeline/tools/_lib/scm.py` ·
**CLIs:** `tools/git-checkout.{py,sh}`, `tools/git-merge.{py,sh}`

## Overview

`jenkins.scm` is the **first stage of every pipeline** — cloning a repository and
merging branches. It answers "check out this repo at this branch into a
workspace" and returns the workspace path + commit metadata the build stage needs.
Both facets are **deterministic simulators**: they return realistic
`ScmInfo` shapes without touching Git.

## How it works

- `GitCheckout` → `_lib.scm.git_checkout(repo, branch)` → handler wraps as
  `{"info": …}`. Returns constant commit metadata with `workspace_path` derived
  as `/var/jenkins/workspace/<repo-leaf>` (last path segment of `repo`) and
  `clone_duration_ms 4500`.
- `GitMerge` → `_lib.scm.git_merge(source_branch, target_branch, workspace_path)`
  → `{"info": …}`. Returns a merge commit (`commit_message "Merge <src> into
  <tgt>"`, `clone_duration_ms 0`) on the existing workspace.

The handler reads payload keys (`repo`, `branch` / `source_branch`,
`target_branch`, `workspace_path`) with defaults and logs a one-line step summary
via `_step_log` when present.

## Fan-out

**Single-task per call — no fan-out.** One checkout/merge = one task. (In
`MultiModuleBuild` the *workflow* fans out and calls `GitCheckout` once per
module — the fan-out is the workflow's, not this facet's; see
[pipelines](pipelines.md).)

## Data & fields

Both facets return `ScmInfo` (see [types](types.md)): `repo, branch, commit_sha,
commit_message, author ("jenkins-ci"), workspace_path, clone_duration_ms`.
`commit_sha` is a hardcoded 40-hex constant; only `repo`/`branch`/`workspace_path`
reflect inputs.

## External libraries / binaries

**None.** No `git` binary, no `GitPython` — pure-stdlib simulator.

## Facets & workflows

| Facet | Kind | Effect / Cost | Signature |
|---|---|---|---|
| `GitCheckout` | event | external / moderate | `GitCheckout(repo: String, branch="main", depth: Int = 0, submodules: Boolean = false) => (info: ScmInfo)` — also carries `with jenkins.mixins.Timeout(minutes = 10)` |
| `GitMerge` | event | external / moderate | `GitMerge(workspace_path: String, source_branch: String, target_branch="main") => (info: ScmInfo)` |

`GitCheckout` is the one facet that declares a **built-in mixin in its own
declaration** (`with Timeout(minutes = 10)`) — an automatic 10-minute checkout
bound, on top of any `with` mixins a caller adds.

## Cache / output

**No cache, no durable output.** Handler returns a dict; CLI prints JSON to
stdout (`git-checkout.sh --repo … --branch …`).

## Gotchas & notes

- **`commit_sha`/`author` are constants** — never assert on them as if real.
- **`depth`/`submodules` are declared but the simulator ignores them** (shape
  parity only; see [tools-and-simulators](tools-and-simulators.md)).
- **`workspace_path` is the load-bearing output** — downstream build/test steps
  read `src.info.workspace_path`, so the derived `/var/jenkins/workspace/<leaf>`
  path is what threads the pipeline together.

## Related specs

- [types](types.md) — `ScmInfo`. · [pipelines](pipelines.md) — always step 1.
- [tools-and-simulators](tools-and-simulators.md) — the dual-surface pattern.
