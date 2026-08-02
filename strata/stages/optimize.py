"""Stage 4: Optimize. Hidden-block culling today; the natural home for greedy
meshing or other geometry-reduction passes later -- see docs/ROADMAP.md."""
from __future__ import annotations

from ..pipeline_state import PipelineState
from ..culling import cull_hidden_blocks


class OptimizeStage:
    def run(self, state: PipelineState) -> PipelineState:
        state.blocks = list(cull_hidden_blocks(state.blocks))
        return state
