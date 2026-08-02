"""
Real Minecraft world reader, built on anvil-parser2 (pip install anvil-parser2),
which supports Minecraft 1.18+ saves.

**VERIFY before trusting this on a real save**: whether
`anvil.Chunk.from_region(region, x, z)` expects region-local (0-31) indices or
global chunk coordinates for your installed anvil-parser2 version, and whether
`Chunk` exposes `.x`/`.z` as global chunk coordinates. This module assumes
region-local indices in the loop and global `.x`/`.z` on the returned chunk.
`tests/test_world_reader.py` builds a tiny synthetic region with a single
block at a known position specifically to catch a wrong assumption here
empirically -- run it before pointing this at a real save, not after.

Known v1 limitation, intentionally not fixed yet: the triple-nested Python
loop over every (x, y, z) in every chunk is slow on a large world. Vectorizing
this with numpy is v1.1 work (docs/ROADMAP.md) -- the same bulk-extraction
approach already proven for this project's Blender-side vertex work, applied
here to the read side.

For broader version coverage (older saves, entities, biomes), a plugin built
on amulet-core is the natural v2 alternative -- nothing outside this file
needs to change, since every other stage only ever sees (x, y, z, block_id).
"""
from __future__ import annotations

import glob
import os
from typing import Dict, Iterator, Optional, Tuple

import anvil  # anvil-parser2

from ...pipeline_state import Block
from .base import WorldReader

DEFAULT_Y_MIN = -64   # Minecraft 1.18+ world floor -- pass y_min=0 explicitly for older saves
DEFAULT_Y_MAX = 319   # Minecraft 1.18+ build limit  -- pass y_max=255 explicitly for older saves


class AnvilWorldReader(WorldReader):
    """v1 default `world_readers` plugin -- vanilla Minecraft Anvil saves."""

    def read_blocks(
        self, world_path: str, y_min: Optional[int] = None, y_max: Optional[int] = None
    ) -> Iterator[Block]:
        all_blocks = self._load_all_blocks(
            world_path,
            DEFAULT_Y_MIN if y_min is None else y_min,
            DEFAULT_Y_MAX if y_max is None else y_max,
        )
        for (x, y, z), block_id in all_blocks.items():
            yield x, y, z, block_id

    # -- internals --------------------------------------------------------

    def _region_files(self, world_path: str) -> Iterator[str]:
        region_dir = os.path.join(world_path, "region")
        if not os.path.isdir(region_dir):
            raise FileNotFoundError(
                f"No 'region/' folder under {world_path} -- point world_path at "
                "the save folder that directly contains region/, not a parent "
                "folder or a specific .mca file."
            )
        yield from sorted(glob.glob(os.path.join(region_dir, "r.*.*.mca")))

    def _load_all_blocks(self, world_path: str, y_min: int, y_max: int) -> Dict[Tuple[int, int, int], str]:
        blocks: Dict[Tuple[int, int, int], str] = {}
        for region_path in self._region_files(world_path):
            region = anvil.Region.from_file(region_path)
            for local_x in range(32):
                for local_z in range(32):
                    try:
                        chunk = anvil.Chunk.from_region(region, local_x, local_z)
                    except Exception:
                        continue  # empty/ungenerated chunk in this region
                    for x in range(16):
                        for z in range(16):
                            for y in range(y_min, y_max + 1):
                                block = chunk.get_block(x, y, z)
                                if block.id == "air":
                                    continue
                                world_x = chunk.x * 16 + x
                                world_z = chunk.z * 16 + z
                                blocks[(world_x, y, world_z)] = block.id
        return blocks
