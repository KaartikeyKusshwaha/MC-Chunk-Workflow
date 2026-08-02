"""Stage 6: Render Prep. Same boundary rule as Stage 3 -- sends a render-
target *name* across the bridge, never imports a RenderTarget class here."""
from __future__ import annotations

from ..pipeline_state import PipelineState
from .. import blender_io


class RenderPrepStage:
    def __init__(self, target: str = "eevee_cycles"):
        self.target = target

    def run(self, state: PipelineState) -> PipelineState:
        state.render_target = self.target
        blender_io.call("apply_render_target", target_name=self.target)
        return state
