# Composability Catalog (machine-readable capability index)

**Manifest:** `src/jenkins_pipeline/catalog.yaml` ·
**Loader:** `src/jenkins_pipeline/catalog.py` ·
**Tests:** `tests/mocked/py/test_catalog_manifest.py`

## Overview

`catalog.yaml` is a **machine-readable index** of this package's reusable
capabilities, so an LLM (or the framework) can **discover and reuse** the CI/CD
workflows/facets by *intent* instead of grepping the FFL. It is the in-repo
analogue of the platform's two MCP discovery tools:

- **`workflows`** ↔ `fw_catalog_match` (workflow-level, reuse-first) — each
  entry-point pipeline with a natural-language `summary`, `tags`, and a
  `param_schema`.
- **`facets`** ↔ `fw_capabilities` (facet-level capability index) — each event
  facet with `purpose`, `signature`, and `effect`/`cost` taken verbatim from its
  `with Effect(...)` / `with Cost(...)` mixins.

`catalog.py` loads it (`load_manifest()`, `workflows()`, `facets()`), cached via
`lru_cache`.

## How it works

The YAML has `version`, `package: jenkins-pipeline`, a `workflows` list (4
entries, all `entry_point: true`), and a `facets` list (17 entries). The header
comment states the accuracy contract: qualified names + signatures are sourced
from the `.ffl`; effect/cost mirror the FFL mixins. Mixin facets from
[jenkins.mixins](mixins.md) are **deliberately excluded** (they are not event
facets).

## Fan-out

**N/A** — a static manifest, not an executable facet.

## Data & fields

- **Workflows (4):** `jenkins.pipeline.{JavaMavenCI, DockerK8sDeploy,
  MultiModuleBuild, FullCIPipeline}` — each with `qualified_name`, `summary`,
  `tags`, `entry_point: true`, `param_schema`.
- **Facets (17):** every event facet across `jenkins.{scm,build,test,artifact,
  deploy,notify}` — each with `qualified_name`, `namespace`, `purpose`,
  `signature`, `effect`, `cost`.

## External libraries / binaries

**`PyYAML`** (pip, declared in `pyproject.toml`) — the loader's only dependency,
and the package's only non-`facetwork` runtime dep. Nothing else.

## Facets & workflows

Not a facet — the index *over* the facets. See the per-domain specs for the
authoritative signatures; the manifest restates them for machine consumption.

## Cache / output

`load_manifest()` caches the parsed dict in-process (`lru_cache(maxsize=1)`). No
external cache or output.

## Gotchas & notes

- **The manifest is tested for honesty, not just presence.**
  `test_catalog_manifest.py` asserts: every workflow leaf name is a real
  `workflow <Leaf>` in the FFL; every facet leaf is a real `event facet <Leaf>`;
  every facet namespace is a declared `namespace`; and — critically —
  `test_facet_effect_cost_match_ffl_mixins` re-reads each `event facet`'s `with
  Effect(kind=…)`/`with Cost(tier=…)` and asserts the manifest matches. It also
  asserts **full coverage** (`test_all_event_facets_indexed`): every event facet
  in the FFL must appear in the manifest. So adding a facet without a matching,
  accurate manifest entry fails CI.
- **Keep effect/cost in sync in two places** — the FFL mixin and the manifest —
  or the honesty test breaks.
- **Valid values** (from the tests): effect ∈ {`pure`, `external`, `io`}, cost ∈
  {`free`, `cheap`, `moderate`, `expensive`}. In this package only `external`/`io`
  and `cheap`/`moderate`/`expensive` are used.

## Related specs

- [pipelines](pipelines.md) — the 4 indexed workflows. · [mixins](mixins.md) —
  the facets deliberately *not* indexed. · every operation spec ([scm](scm.md),
  [build](build.md), [test](test.md), [artifact](artifact.md), [deploy](deploy.md),
  [notify](notify.md)) — the 17 indexed facets and their effect/cost.
