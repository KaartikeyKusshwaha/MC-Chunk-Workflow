"""
v2 stub. Not a second pipeline -- Stage 6 gaining a target that
exports/streams the already-built, already-chunked geometry (Nanite for
geometry streaming, Lumen for lighting) into an Unreal project instead of
configuring a Blender render engine. Stage 5's chunking already maps
naturally onto Unreal's own streaming units. See docs/ROADMAP.md.
"""
from __future__ import annotations

from .base import RenderTarget


class UnrealTarget(RenderTarget):
    def apply(self, scene) -> None:
        raise NotImplementedError(
            "unreal render target is a v2 stub -- see docs/ROADMAP.md. "
            "Use 'eevee_cycles' (the v1 default) for now."
        )
