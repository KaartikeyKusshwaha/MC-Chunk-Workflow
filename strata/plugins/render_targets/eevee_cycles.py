"""
v1 default `render_targets` plugin. Deliberately minimal -- sets the active
render engine and leaves lighting/shading to the user's library-.blend
materials. This is the plugin point v2's one-prompt stylization work (Arcane /
Spider-Verse / anime / cinematic-trailer looks) extends -- see docs/ROADMAP.md.
"""
from __future__ import annotations

from .base import RenderTarget

VALID_ENGINES = {"eevee": "BLENDER_EEVEE_NEXT", "cycles": "CYCLES"}


class EeveeCyclesTarget(RenderTarget):
    def __init__(self, engine: str = "eevee"):
        if engine not in VALID_ENGINES:
            raise ValueError(f"engine must be one of {sorted(VALID_ENGINES)}, got {engine!r}")
        self.engine = engine

    def apply(self, scene) -> None:
        scene.render.engine = VALID_ENGINES[self.engine]
