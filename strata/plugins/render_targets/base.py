from __future__ import annotations

from abc import ABC, abstractmethod


class RenderTarget(ABC):
    """Every render-target plugin (eevee_cycles, unreal, a future stylization
    preset, ...) implements this. Called once by Stage 6 against the whole
    scene, after Stage 3/5 have already built and chunked the geometry."""

    @abstractmethod
    def apply(self, scene) -> None:  # scene: bpy.types.Scene
        raise NotImplementedError
