"""
Chunk visibility / toggle system -- REFERENCE implementation.

Matches the behavior described for the existing 'MC Chunk Workflow' addon
panel (Selected Chunk, Selected + Neighbors, Hide/Show All Viewport, Final
Render State, Print Stats). Per Build Checklist item 2.7: if KK's real,
already-built operator code is available, replace the bodies of these
operators with it -- the bl_idname / panel wiring can stay as-is.

Deliberately NOT reference-implemented here, left for that real source
instead: Origin Radius, Lock/Unlock Terrain, Performance/Lookdev Mode --
their exact semantics weren't specified precisely enough to guess at safely.
(Error Handling: no silent fallbacks -- guessing wrong here would be worse
than leaving it undone.)
"""
from __future__ import annotations

import bpy

from .. import bridge_server


def _chunk_collections():
    root = bpy.data.collections.get("Strata_World")
    return list(root.children) if root else []


def _chunk_of_object(obj):
    for coll in obj.users_collection:
        if coll.name.startswith("Chunk_"):
            return coll
    return None


class STRATA_OT_select_nearest_chunk(bpy.types.Operator):
    bl_idname = "strata.select_nearest_chunk"
    bl_label = "Selected Chunk"
    bl_description = "Show only the chunk containing the active object"

    def execute(self, context):
        obj = context.active_object
        if obj is None:
            self.report({"WARNING"}, "No active object")
            return {"CANCELLED"}
        target = _chunk_of_object(obj)
        if target is None:
            self.report({"WARNING"}, "Active object isn't inside a chunk collection")
            return {"CANCELLED"}
        for coll in _chunk_collections():
            coll.hide_viewport = coll is not target
        return {"FINISHED"}


class STRATA_OT_select_chunk_and_neighbors(bpy.types.Operator):
    bl_idname = "strata.select_chunk_and_neighbors"
    bl_label = "Selected + Neighbors"
    bl_description = "Show the active object's chunk plus its 8 neighbors"

    def execute(self, context):
        obj = context.active_object
        target = _chunk_of_object(obj) if obj else None
        if target is None:
            self.report({"WARNING"}, "Active object isn't inside a chunk collection")
            return {"CANCELLED"}
        try:
            _, cx, cz = target.name.split("_")
            cx, cz = int(cx), int(cz)
        except ValueError:
            self.report({"WARNING"}, f"Unexpected chunk collection name: {target.name}")
            return {"CANCELLED"}
        wanted = {f"Chunk_{cx + dx}_{cz + dz}" for dx in (-1, 0, 1) for dz in (-1, 0, 1)}
        for coll in _chunk_collections():
            coll.hide_viewport = coll.name not in wanted
        return {"FINISHED"}


class STRATA_OT_hide_all_viewport(bpy.types.Operator):
    bl_idname = "strata.hide_all_viewport"
    bl_label = "Hide All Viewport"

    def execute(self, context):
        for coll in _chunk_collections():
            coll.hide_viewport = True
        return {"FINISHED"}


class STRATA_OT_show_all_viewport(bpy.types.Operator):
    bl_idname = "strata.show_all_viewport"
    bl_label = "Show All Viewport"

    def execute(self, context):
        for coll in _chunk_collections():
            coll.hide_viewport = False
        return {"FINISHED"}


class STRATA_OT_final_render_state(bpy.types.Operator):
    bl_idname = "strata.final_render_state"
    bl_label = "Final Render State"
    bl_description = "Confirms every chunk is set to render regardless of current viewport toggles"

    def execute(self, context):
        for coll in _chunk_collections():
            coll.hide_render = False
        return {"FINISHED"}


class STRATA_OT_print_stats(bpy.types.Operator):
    bl_idname = "strata.print_stats"
    bl_label = "Print Stats"

    def execute(self, context):
        stats = get_scene_status()
        self.report({"INFO"}, f"Chunks: {stats['chunks']} | Visible: {stats['visible_chunks']}")
        return {"FINISHED"}


@bridge_server.register_command("get_scene_status")
def get_scene_status():
    chunks = _chunk_collections()
    visible = [c for c in chunks if not c.hide_viewport]
    visible_objects = sum(len(c.objects) for c in visible)
    return {
        "chunks": len(chunks),
        "visible_chunks": len(visible),
        "visible_objects": visible_objects,
    }


@bridge_server.register_command("generate_chunk_system")
def generate_chunk_system(chunk_size=16):
    """
    Separate bridge entry point from world_import's build_geometry, so an
    agent can inspect/repair the chunk system without re-running a full
    import. v1 just reports current state -- Chunk_X_Z collections are
    created at build_geometry time; this doesn't yet re-bucket loose objects
    a user added by hand. Extend here when that's needed, not by duplicating
    chunk logic elsewhere (Reuse Before Reimplementation).
    """
    root = bpy.data.collections.get("Strata_World")
    if root is None:
        return {"chunks": 0, "note": "No Strata_World collection yet -- run import_minecraft_world first"}
    return get_scene_status()


CLASSES = (
    STRATA_OT_select_nearest_chunk,
    STRATA_OT_select_chunk_and_neighbors,
    STRATA_OT_hide_all_viewport,
    STRATA_OT_show_all_viewport,
    STRATA_OT_final_render_state,
    STRATA_OT_print_stats,
)
