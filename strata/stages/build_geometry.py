"""
Stage 3: Build Geometry. The one stage that reaches across the process
boundary into a live Blender instance, via strata/blender_io.py.

Sends the already-chunked block data plus a *plugin name string* across the
bridge -- this file must NOT import strata.plugins.geometry_backends (those
modules `import bpy`; see the boundary note in strata/stages/__init__.py).
The addon side does its own strata.plugins.geometry_backends lookup and
actually places geometry -- see addon/world_import/operators.py's
`build_geometry` bridge command.
"""
from __future__ import annotations

from ..pipeline_state import PipelineState
from ..block_library import resolve_prototype_name
from .. import blender_io


class BuildGeometryStage:
    def __init__(self, backend_name: str = "geometry_nodes"):
        self.backend_name = backend_name

    def run(self, state: PipelineState) -> PipelineState:
        groups = [
            {
                "chunk_key": f"{cx}:{cz}",
                "block_id": block_id,
                "prototype_name": resolve_prototype_name(block_id, state.block_map),
                "positions": positions,
            }
            for (cx, cz), block_groups in state.chunks.items()
            for block_id, positions in block_groups.items()
        ]
        result = blender_io.call(
            "build_geometry",
            library_blend_path=state.library_blend_path,
            groups=groups,
            backend_name=self.backend_name,
        )
        state.unmapped_block_ids = set(result.get("unmapped_block_ids", []))
        state.stats.update({k: v for k, v in result.items() if k != "unmapped_block_ids"})
        return state
