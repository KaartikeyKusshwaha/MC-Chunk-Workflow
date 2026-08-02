"""Stage 5 helper: pure grouping math. No bpy, no I/O, no third-party deps."""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable

from .pipeline_state import Block, ChunkContents, ChunkKey


def bucket_into_chunks(blocks: Iterable[Block], chunk_size: int = 16) -> Dict[ChunkKey, ChunkContents]:
    """Groups (x, y, z, block_id) tuples by chunk (x // chunk_size, z // chunk_size),
    then by block_id within each chunk."""
    chunks: Dict[ChunkKey, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for x, y, z, block_id in blocks:
        key = (x // chunk_size, z // chunk_size)
        chunks[key][block_id].append((x, y, z))
    return {k: dict(v) for k, v in chunks.items()}
