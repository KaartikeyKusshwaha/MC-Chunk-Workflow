"""
v2 stub. Litematica schematics are single-file, self-contained block
palettes -- a much smaller surface than a full world save, and a good first
"prove the plugin system works for a real third party" candidate. Not
implemented in v1: raises immediately so a misconfigured Pipeline fails loudly
instead of silently returning nothing.
"""
from __future__ import annotations

from typing import Iterator, Optional

from ...pipeline_state import Block
from .base import WorldReader


class LitematicaWorldReader(WorldReader):
    def read_blocks(
        self, world_path: str, y_min: Optional[int] = None, y_max: Optional[int] = None
    ) -> Iterator[Block]:
        raise NotImplementedError(
            "litematica world reader is a v2 stub -- see docs/ROADMAP.md. "
            "Use the 'anvil' reader (the v1 default) for now."
        )
        yield  # pragma: no cover -- keeps this a generator function
