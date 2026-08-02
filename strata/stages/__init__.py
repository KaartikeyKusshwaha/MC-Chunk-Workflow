"""
Re-exports so `strata/pipeline.py` can do `from .stages import ReadWorldStage`
etc. A Stage is a convention, not an enforced ABC: a small class, constructor
takes whatever config it needs, `.run(state, **kwargs) -> state` mutates and
returns the shared PipelineState. The interesting extension point is the
plugins (strata/plugins/), not the stages themselves -- keep these thin.

IMPORTANT boundary: nothing imported here (or anywhere under strata/stages/,
strata/pipeline.py, strata/blender_io.py) may `import bpy` at module scope.
Only strata/plugins/geometry_backends/*.py and strata/plugins/render_targets/*.py
do that, and only the Blender-side addon code ever imports THOSE directly (see
addon/world_import/operators.py). Stages reach Blender exclusively through
strata/blender_io.py's socket client, passing plugin *names* as strings, never
plugin classes. Breaking this boundary means `strata.Pipeline` stops being
importable/usable from an external process (an MCP server, a plain script)
with no Blender installed -- which defeats the "two doors, one pipeline" point
of the whole design.
"""
from .read_world import ReadWorldStage
from .resolve_assets import ResolveAssetsStage
from .optimize import OptimizeStage
from .chunk_manager import ChunkManagerStage
from .build_geometry import BuildGeometryStage
from .render_prep import RenderPrepStage
from .animation_prep import AnimationPrepStage

__all__ = [
    "ReadWorldStage", "ResolveAssetsStage", "OptimizeStage", "ChunkManagerStage",
    "BuildGeometryStage", "RenderPrepStage", "AnimationPrepStage",
]
