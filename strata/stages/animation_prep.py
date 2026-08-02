"""Stage 7: Animation Prep. v2 -- see docs/ROADMAP.md. A documented no-op for
now so Pipeline.prepare_animation() is safe to call in a v1 script even
though it doesn't do anything yet."""
from __future__ import annotations

from ..pipeline_state import PipelineState


class AnimationPrepStage:
    def run(self, state: PipelineState) -> PipelineState:
        state.stats.setdefault("animation_prep", "not implemented yet -- v2, see docs/ROADMAP.md")
        return state
