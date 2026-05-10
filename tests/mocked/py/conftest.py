"""Conftest for jenkins mocked tests.

The package is installed editable (``pip install -e .``) so handler
modules resolve via ``jenkins_pipeline.handlers.*`` — no ``sys.path``
gymnastics required.
"""

from __future__ import annotations
