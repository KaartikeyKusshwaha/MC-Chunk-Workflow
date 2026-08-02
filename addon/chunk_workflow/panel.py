import bpy

from . import operators as ops


class STRATA_PT_chunk_workflow(bpy.types.Panel):
    bl_idname = "STRATA_PT_chunk_workflow"
    bl_label = "Strata"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Strata"

    def draw(self, context):
        layout = self.layout
        stats = ops.get_scene_status()
        layout.label(text=f"Chunks: {stats['chunks']} | Visible: {stats['visible_chunks']}")
        layout.label(text=f"Visible objects: {stats['visible_objects']}")

        layout.separator()
        row = layout.row(align=True)
        row.operator("strata.start_server", text="Start Strata Bridge")
        row.operator("strata.stop_server", text="Stop")

        layout.separator()
        layout.label(text="Block Edit Tools")
        layout.operator(ops.STRATA_OT_select_nearest_chunk.bl_idname, text="Selected Chunk")
        layout.operator(ops.STRATA_OT_select_chunk_and_neighbors.bl_idname, text="Selected + Neighbors")

        layout.separator()
        layout.operator(ops.STRATA_OT_hide_all_viewport.bl_idname, text="Hide All Viewport")
        layout.operator(ops.STRATA_OT_show_all_viewport.bl_idname, text="Show All Viewport")
        layout.operator(ops.STRATA_OT_final_render_state.bl_idname, text="Final Render State")
        layout.operator(ops.STRATA_OT_print_stats.bl_idname, text="Print Stats")


CLASSES = (STRATA_PT_chunk_workflow,)
