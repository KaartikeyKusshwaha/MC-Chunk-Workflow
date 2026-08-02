"""
Stage 4 helper: pure hidden-block culling. No bpy, no I/O.

Deliberately separate from strata/plugins/world_readers/ -- Stage 1 (Read
World) just reads every non-air block; Stage 4 (Optimize) decides what's
actually worth placing geometry for. Improving the culling algorithm, or
making it configurable per block category, never touches a world-reader
plugin.
"""
from __future__ import annotations

from typing import Dict, Iterable, Iterator, Tuple

from .pipeline_state import Block

# Blocks treated as "see-through" -- a block fully surrounded by blocks NOT in
# this set can never be seen and gets dropped. Deliberately conservative for
# v1: glass, leaves, slabs, stairs etc. aren't here yet, so they (correctly)
# never get culled, but solid neighbors of theirs also won't be, where they
# visually could be. Expand this set as v1.1 work -- see docs/ROADMAP.md.
NON_OPAQUE = {"air", "cave_air", "void_air"}

NEIGHBOR_OFFSETS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def cull_hidden_blocks(blocks: Iterable[Block]) -> Iterator[Block]:
    lookup: Dict[Tuple[int, int, int], str] = {(x, y, z): block_id for x, y, z, block_id in blocks}
    for (x, y, z), block_id in lookup.items():
        for dx, dy, dz in NEIGHBOR_OFFSETS:
            neighbor = lookup.get((x + dx, y + dy, z + dz))
            if neighbor is None or neighbor in NON_OPAQUE:
                yield x, y, z, block_id
                break
