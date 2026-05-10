"""Jenkins CI/CD pipeline example package — Facetwork workflows + handlers
that simulate a complete Jenkins build/test/deploy pipeline.

The example showcases:

- Mixin composition (Retry, Timeout, Credentials, RequiresApproval, …)
- Prompt + script blocks for build glue
- `andThen when` branching for environment-aware deploys
- Rollback / failure-recovery patterns
- 17 simulator handlers across scm / build / test / artifact / deploy / notify

Discovered by the Facetwork runner via the ``facetwork.examples`` entry
point declared in ``pyproject.toml``::

    [project.entry-points."facetwork.examples"]
    jenkins = "jenkins_pipeline:example"

Once ``pip install -e .`` has been run from this repository, Facetwork's
``scripts/start-runner --example jenkins`` and ``scripts/seed-examples``
will pick this package up automatically — no edits to the Facetwork
repository required.
"""

from __future__ import annotations

from pathlib import Path

from facetwork.examples import ExamplePackage

from .handlers import register_all_registry_handlers

example = ExamplePackage(
    name="jenkins",
    ffl_dir=Path(__file__).parent / "ffl",
    register_handlers=register_all_registry_handlers,
)
