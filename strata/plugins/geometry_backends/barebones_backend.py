"""
v2 stub. Literal per-block mesh-duplication fallback (objects sharing one
mesh datablock, no Geometry Nodes) -- for Blender versions where the GN
interface differs, or worlds small enough that per-object overhead doesn't
matter and simplicity is worth more than instancing performance.
"""
from __future__ import annotations

from typing import List, Tuple

from .base import GeometryBackend


class BarebonesBackend(GeometryBackend):
    def place_instances(self, chunk_collection, prototype_obj, positions: List[Tuple[int, int, int]], name_hint: str) -> None:
        raise NotImplementedError(
            "barebones geometry backend is a v2 stub -- see docs/ROADMAP.md. "
            "Use the 'geometry_nodes' backend (the v1 default) for now."
        )
