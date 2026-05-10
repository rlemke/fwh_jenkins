"""Shared shim layer for jenkins-pipeline handlers.

The handler modules in the parent package call into the simulators in
``jenkins_pipeline.tools._lib`` via this shim. The shim re-exports the
implementation under stable names so handlers don't need to track
module reorganizations under ``tools/_lib``.
"""
