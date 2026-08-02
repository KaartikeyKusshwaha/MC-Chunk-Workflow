from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Tuple


class GeometryBackend(ABC):
    """Every geometry-backend plugin (geometry_nodes, barebones, ...)
    implements this. Called once per (chunk, block_type) group by Stage 3."""

    @abstractmethod
    def place_instances(
        self,
        chunk_collection,               # a bpy.types.Collection
        prototype_obj,                  # a bpy.types.Object, already linked
        positions: List[Tuple[int, int, int]],
        name_hint: str,
    ) -> None:
        """Populates `chunk_collection` with `prototype_obj` instanced at
        every position in `positions`."""
        raise NotImplementedError
