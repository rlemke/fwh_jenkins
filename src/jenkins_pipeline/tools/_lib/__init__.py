"""Simulator implementation for the jenkins-pipeline example.

Each module exposes pure functions that accept typed keyword arguments
and return a deterministic dict shaped like the corresponding facet's
output schema in the FFL. Both the CLIs (``tools/*.py``) and the FFL
handlers call into these functions; they never touch MongoDB, the
network, or facetwork.runtime, so they're trivially testable and
runnable standalone.
"""
