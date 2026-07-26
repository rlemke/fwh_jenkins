<!-- SPEC TEMPLATE — every docs/<feature>.md follows this shape so the set reads
consistently. Delete this comment in real specs. Keep sections in this order;
omit a section only if it genuinely does not apply (say so in one line rather
than dropping the heading silently). Ground every claim in the actual FFL
docstrings / handler code / _lib simulators / CLIs — do not invent behaviour.
This is a CI/CD *simulator* package: nearly everything worth documenting is the
gap between what a facet *represents* (a Maven build, a k8s deploy) and what it
*does* (return a constant-shaped dict). Say so wherever it matters. -->

# <Feature Name>

**Namespace(s):** `jenkins.<ns>` · **FFL:** `src/jenkins_pipeline/ffl/<file>.ffl` ·
**Handlers:** `src/jenkins_pipeline/handlers/<domain>_handlers.py` ·
**Simulator:** `src/jenkins_pipeline/tools/_lib/<domain>.py` ·
**CLIs:** `src/jenkins_pipeline/tools/<verb>-<noun>.{py,sh}`

## Overview
One or two paragraphs: what CI/CD step this feature represents, the request it
answers, and where it sits in a pipeline (checkout → build → test → artifact →
deploy → notify). State up front that the handlers are **deterministic
simulators** — they return realistic shapes without invoking Jenkins, Maven,
kubectl, Slack, etc. — if that is the case.

## How it works
The data flow, step by step. Name the concrete facet(s), the `_lib` simulator
function each dispatches to, the outer key the handler wraps the result in
(`result` / `info` / `report` / `artifact`, or flat for tuple-returns), and the
constant-ish shape returned. If a handler drops FFL params before calling the
simulator (shape-only parity), say so.

## Fan-out
Does it fan out across the fleet? For per-facet features the answer is almost
always "single-task — no fan-out" (one facet, one task). The one fan-out in this
package is `jenkins.pipeline.MultiModuleBuild` (`andThen foreach mod in
$.modules`). Name the fan-out unit if any.

## Data & fields
The schema(s) this feature produces (from `jenkins.types`) and the concrete
field names + the constant values the simulator fills them with (e.g.
`coverage_pct: 87.3`, `total: 342`). Note fields that are hardcoded vs derived
from inputs. (Rename from the OSM template's "Filtering & attributes" — this
domain does not tag/geo-filter.)

## External libraries / binaries
Every non-stdlib dependency this feature relies on. For most facets here the
honest answer is **none** — the `_lib` simulators are pure-stdlib functions with
no I/O, no MongoDB, no subprocess. Say so explicitly; that standalone-ness is a
deliberate design property (CLIs run with no Facetwork stack). Note `PyYAML`
only where it actually applies (the catalog loader).

## Facets & workflows
The key event facets / workflows, with signatures and a one-line purpose taken
from the FFL `/** … */` docstrings. Mark event facets (need a handler) vs pure
composition facets (mixins), and note the `with Effect(...)` / `with Cost(...)`
mixins present on each.

## Cache / output
For simulator facets the honest answer is **no cache namespace, no durable
output** — the handler returns a dict in-process; the CLI prints JSON to stdout
and a human summary to stderr. Say so. (Contrast the real fwh_* domains that
write GeoJSON/HTML to `$FW_CACHE_ROOT`/MinIO — this package writes nothing.)

## Gotchas & notes
Known pitfalls: constant return values (don't assert on them as if real),
params the simulator ignores, stale docstrings, entry-point naming, coexistence
with sibling `_lib/` packages, etc.

## Related specs
Links to the specs this feature composes with or depends on.
