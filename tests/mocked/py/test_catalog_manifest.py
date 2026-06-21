"""Offline checks for the composability manifest (``src/jenkins_pipeline/catalog.yaml``).

Asserts the manifest loads, every workflow carries a non-empty intent summary +
tags + param_schema, every facet carries purpose/signature/effect/cost/namespace,
every listed qualified_name is plausibly real (its leaf name appears as a
`workflow`/`facet` declaration in the package's .ffl sources, under its declared
namespace), and that the effect/cost recorded in the manifest matches the
`with Effect(...) / with Cost(...)` mixins actually present on that event facet
in the FFL. No runner, DB, or network needed.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from jenkins_pipeline import catalog

# Repo root: tests/mocked/py/ -> repo root is parents[3].
_REPO_ROOT = Path(__file__).resolve().parents[3]
_FFL_ROOT = _REPO_ROOT / "src" / "jenkins_pipeline"


def _all_ffl_text() -> str:
    parts = [p.read_text(encoding="utf-8") for p in _FFL_ROOT.rglob("*.ffl")]
    assert parts, "no .ffl sources found under src/jenkins_pipeline"
    return "\n".join(parts)


@pytest.fixture(scope="module")
def ffl_text() -> str:
    return _all_ffl_text()


@pytest.fixture(scope="module")
def manifest():
    return catalog.load_manifest()


def test_manifest_loads(manifest):
    assert isinstance(manifest, dict)
    assert manifest.get("package") == "jenkins-pipeline"
    assert isinstance(catalog.workflows(), list) and catalog.workflows()
    assert isinstance(catalog.facets(), list) and catalog.facets()


def test_workflows_have_summary_and_tags():
    for wf in catalog.workflows():
        qn = wf.get("qualified_name", "<missing>")
        summary = wf.get("summary", "")
        assert isinstance(summary, str) and summary.strip(), f"empty summary for {qn}"
        tags = wf.get("tags")
        assert isinstance(tags, list) and tags, f"empty tags for {qn}"
        assert all(isinstance(t, str) and t.strip() for t in tags), f"bad tag in {qn}"
        assert wf.get("entry_point") is True, f"workflow {qn} not marked entry_point"
        assert isinstance(wf.get("param_schema"), dict), f"no param_schema for {qn}"


def test_facets_have_required_fields():
    valid_effects = {"pure", "external", "io"}
    valid_costs = {"free", "cheap", "moderate", "expensive"}
    for fc in catalog.facets():
        qn = fc.get("qualified_name", "<missing>")
        assert fc.get("purpose", "").strip(), f"empty purpose for {qn}"
        assert fc.get("signature", "").strip(), f"empty signature for {qn}"
        assert fc.get("effect") in valid_effects, f"bad effect for {qn}: {fc.get('effect')}"
        assert fc.get("cost") in valid_costs, f"bad cost for {qn}: {fc.get('cost')}"
        assert fc.get("namespace"), f"no namespace for {qn}"
        # The qualified name must live under its declared namespace.
        assert qn.startswith(fc["namespace"] + "."), f"{qn} not under namespace {fc['namespace']}"


def test_no_duplicate_entries():
    wf_names = [w["qualified_name"] for w in catalog.workflows()]
    fc_names = [f["qualified_name"] for f in catalog.facets()]
    assert len(wf_names) == len(set(wf_names)), "duplicate workflow qualified_names"
    assert len(fc_names) == len(set(fc_names)), "duplicate facet qualified_names"
    overlap = set(wf_names) & set(fc_names)
    assert not overlap, f"name listed as both workflow and facet: {overlap}"


def test_workflow_qualified_names_are_real(ffl_text):
    """Each workflow's leaf name must be declared as a `workflow <Leaf>` in the FFL."""
    for wf in catalog.workflows():
        qn = wf["qualified_name"]
        leaf = qn.rsplit(".", 1)[-1]
        pat = re.compile(rf"\bworkflow\s+{re.escape(leaf)}\b")
        assert pat.search(ffl_text), f"no `workflow {leaf}` found in FFL for {qn}"


def test_facet_qualified_names_are_real(ffl_text):
    """Each facet's leaf name must be declared as a `facet <Leaf>` in the FFL."""
    for fc in catalog.facets():
        qn = fc["qualified_name"]
        leaf = qn.rsplit(".", 1)[-1]
        pat = re.compile(rf"\bfacet\s+{re.escape(leaf)}\b")
        assert pat.search(ffl_text), f"no `facet {leaf}` found in FFL for {qn}"


def test_facet_namespaces_exist_in_ffl(ffl_text):
    """Each distinct facet namespace must be a declared `namespace` in the FFL."""
    namespaces = {f["namespace"] for f in catalog.facets()}
    for ns in namespaces:
        pat = re.compile(rf"\bnamespace\s+{re.escape(ns)}\b")
        assert pat.search(ffl_text), f"namespace {ns} not declared in any .ffl"


def _facet_decl_blocks(ffl_text: str) -> dict[str, str]:
    """Map each `event facet <Leaf>(...)` to the text from its name up to the
    next blank line / next facet decl (where its `with` mixin chain lives)."""
    blocks: dict[str, str] = {}
    pat = re.compile(r"event facet\s+(\w+)\b")
    matches = list(pat.finditer(ffl_text))
    for i, m in enumerate(matches):
        leaf = m.group(1)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(ffl_text)
        blocks[leaf] = ffl_text[start:end]
    return blocks


def test_facet_effect_cost_match_ffl_mixins(ffl_text):
    """The effect/cost in the manifest must match the `with Effect/Cost` mixins
    actually written on that event facet in the FFL — keeps the manifest honest."""
    blocks = _facet_decl_blocks(ffl_text)
    for fc in catalog.facets():
        leaf = fc["qualified_name"].rsplit(".", 1)[-1]
        block = blocks.get(leaf)
        assert block, f"no `event facet {leaf}` block found in FFL"
        eff = re.search(r'Effect\(\s*kind\s*=\s*"(\w+)"', block)
        cost = re.search(r'Cost\(\s*tier\s*=\s*"(\w+)"', block)
        assert eff, f"no `with Effect(kind=...)` on event facet {leaf}"
        assert cost, f"no `with Cost(tier=...)` on event facet {leaf}"
        assert eff.group(1) == fc["effect"], (
            f"effect mismatch for {leaf}: ffl={eff.group(1)} manifest={fc['effect']}"
        )
        assert cost.group(1) == fc["cost"], (
            f"cost mismatch for {leaf}: ffl={cost.group(1)} manifest={fc['cost']}"
        )


def test_all_event_facets_indexed(ffl_text):
    """Every `event facet` in the FFL is indexed in the manifest (full coverage)."""
    ffl_leaves = set(_facet_decl_blocks(ffl_text).keys())
    manifest_leaves = {f["qualified_name"].rsplit(".", 1)[-1] for f in catalog.facets()}
    missing = ffl_leaves - manifest_leaves
    assert not missing, f"event facets in FFL not indexed in catalog.yaml: {missing}"


def test_all_event_facets_have_effect_cost_in_ffl(ffl_text):
    """Every event facet declaration carries both Effect and Cost mixins."""
    for leaf, block in _facet_decl_blocks(ffl_text).items():
        assert re.search(r"with\s+Effect\(", block), f"event facet {leaf} missing with Effect(...)"
        assert re.search(r"with\s+Cost\(", block), f"event facet {leaf} missing with Cost(...)"
