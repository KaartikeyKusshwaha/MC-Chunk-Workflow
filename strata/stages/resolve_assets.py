"""Stage 2: Resolve Assets. Loads the (optional) block-id -> prototype-name
map. Actual verification that a named prototype exists happens in Stage 3,
once a real library .blend is in the loop -- this stage stays pure Python."""
from __future__ import annotations

from ..pipeline_state import PipelineState
from ..block_library import load_block_map


class ResolveAssetsStage:
    def run(self, state: PipelineState, block_map_path: str) -> PipelineState:
        state.block_map = load_block_map(block_map_path)
        return state
