"""
Minimal plugin registry. Each pluggable stage discovers implementations via
standard Python package entry points -- the same mechanism pytest and flake8
use. A third party ships a plugin as its own pip-installable package; nothing
in this repo has to change for it to be discoverable.

    [project.entry-points."strata.plugins.world_readers"]
    my_format = "my_package.reader:MyWorldReader"
"""
from __future__ import annotations

from importlib.metadata import entry_points
from typing import Dict, Type


def discover(kind: str) -> Dict[str, Type]:
    """Returns {plugin_name: plugin_class} for group f"strata.plugins.{kind}"."""
    found: Dict[str, Type] = {}
    for ep in entry_points(group=f"strata.plugins.{kind}"):
        found[ep.name] = ep.load()
    return found
