# Test & Quality (tests / code-quality / security scan)

**Namespace:** `jenkins.test` ·
**FFL:** `src/jenkins_pipeline/ffl/jenkins_test.ffl` ·
**Handlers:** `src/jenkins_pipeline/handlers/test_handlers.py` ·
**Simulator:** `src/jenkins_pipeline/tools/_lib/test.py` ·
**CLIs:** `tools/{run-tests,code-quality,security-scan}.{py,sh}`

## Overview

`jenkins.test` is the **quality-gate stage** — running a test suite, static code
quality analysis, and a security vulnerability scan against a built workspace.
These three facets form the parallel gates in `FullCIPipeline`. Each is a
**deterministic simulator** returning a report shape (`TestReport` or
`QualityReport`) without running any real test/scan tool.

## How it works

Handlers wrap simulator dicts under `{"report": …}`:

- `RunTests` → `run_tests(framework, suite)` → `TestReport` with `total 342,
  passed 335, failed 2, skipped 5, duration_ms 28000, coverage_pct 87.3` and a
  derived `report_path …/surefire-reports/<suite>-report.xml`.
- `CodeQuality` → `code_quality(tool, workspace_path)` → `QualityReport` with
  `issues 42, critical 0, major 5, minor 37, passed True`.
- `SecurityScan` → `security_scan(scanner, severity_threshold, workspace_path)` →
  `QualityReport` with `issues 8, critical 0, major 2, minor 6, passed True`.

`RunTests` returns extra keys (`framework`, `suite`) beyond the schema — the
runtime keeps only the `TestReport` fields.

## Fan-out

**Single-task per call.** In `FullCIPipeline` the three run **concurrently** —
not because they fan out, but because they share no data dependency (each depends
only on `build`), so the runtime schedules them in parallel (see
[pipelines](pipelines.md) → "parallel quality gates").

## Data & fields

- `RunTests` → `TestReport`: `total, passed, failed, skipped, duration_ms,
  report_path, coverage_pct` (all constants except the input-derived `report_path`).
- `CodeQuality` / `SecurityScan` → `QualityReport`: `tool (= the tool/scanner
  input), issues, critical, major, minor, report_path, passed`.

Because `critical` is always `0` and `passed` always `True`, a simulated quality
gate never blocks a deploy.

## External libraries / binaries

**None.** No JUnit/pytest, SonarQube, or Trivy is invoked — pure-stdlib
simulators.

## Facets & workflows

| Facet | Kind | Effect / Cost | Signature |
|---|---|---|---|
| `RunTests` | event | external / expensive | `RunTests(workspace_path, framework="junit", suite="unit", parallel=true) => (report: TestReport)` |
| `CodeQuality` | event | external / expensive | `CodeQuality(workspace_path, tool="sonarqube", config_path="sonar-project.properties") => (report: QualityReport)` |
| `SecurityScan` | event | external / moderate | `SecurityScan(workspace_path, scanner="trivy", severity_threshold="HIGH") => (report: QualityReport)` |

`SecurityScan` is `moderate` cost (vs the other two `expensive`) — the one
distinction the FFL draws in this namespace.

## Cache / output

**No cache, no durable output.** Report dicts are in-process; the `report_path`
fields are simulated strings, not files that exist on disk. CLI prints JSON.

## Gotchas & notes

- **The numbers are constants** — `coverage_pct 87.3`, `issues 42`, `critical 0`.
  A pipeline can't fail its gate on simulated data; do not assert on these as
  real results.
- **`severity_threshold` / `config_path` / `parallel` are declared but ignored**
  by the simulators (shape parity). The `CodeQuality`/`SecurityScan` handlers pass
  only the tool/scanner name through.
- **Two facets share one schema** — `CodeQuality` and `SecurityScan` both return
  `QualityReport`, distinguished by the `tool` field.

## Related specs

- [types](types.md) — `TestReport`, `QualityReport`. · [build](build.md) — the
  upstream stage. · [pipelines](pipelines.md) — the parallel gate pattern.
