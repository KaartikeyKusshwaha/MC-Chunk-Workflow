"""Stage 5: Chunk Manager. Buckets the optimized block list into chunk
groups. The visibility-toggle UI itself (hide/show, nearest-chunk selection)
lives on the Blender side -- addon/chunk_workflow/ -- this stage only
produces the grouping data Stage 3 and the add-on both consume."""
from __future__ import annotations

from ..pipeline_state import PipelineState
from ..chunking import bucket_into_chunks


class ChunkManagerStage:
    def run(self, state: PipelineState) -> PipelineState:
        state.chunks = bucket_into_chunks(state.blocks, chunk_size=state.chunk_size)
        return state
