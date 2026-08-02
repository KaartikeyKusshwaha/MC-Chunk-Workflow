"""
Shared state threaded through the seven stages. Each stage's `run(state, ...)`
mutates and returns this same object -- see strata/stages/__init__.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

Block = Tuple[int, int, int, str]                        # (x, y, z, block_id)
ChunkKey = Tuple[int, int]                                # (chunk_x, chunk_z)
ChunkContents = Dict[str, List[Tuple[int, int, int]]]     # block_id -> positions


@dataclass
class PipelineState:
    chunk_size: int = 16
    world_path: str | None = None
    library_blend_path: str | None = None
    block_map: Dict[str, str] = field(default_factory=dict)
    blocks: List[Block] = field(default_factory=list)
    chunks: Dict[ChunkKey, ChunkContents] = field(default_factory=dict)
    unmapped_block_ids: Set[str] = field(default_factory=set)
    render_target: str = "eevee_cycles"
    stats: Dict[str, object] = field(default_factory=dict)
