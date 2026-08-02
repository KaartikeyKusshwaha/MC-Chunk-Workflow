# SPDX-License-Identifier: GPL-3.0-or-later
"""
pick_utils.py
~~~~~~~~~~~~~
Block-picking helpers — screen-box projection and scene ray-cast.
Kept separate so they can be tested and extended without touching operators.
"""

from __future__ import annotations

from typing import Optional, Tuple

import bpy
from bpy_extras import view3d_utils
from mathutils import Vector

from . import chunk_utils


# ---------------------------------------------------------------------------
# Geometry ray-cast picker
# ---------------------------------------------------------------------------

def pick_block_by_ray(
    context: bpy.types.Context,
    mouse_x: float,
    mouse_y: float,
) -> Optional[bpy.types.Object]:
    """Return the first world-block object hit by a viewport ray under the
    cursor, or *None* on miss / non-block hit."""
    region = context.region
    space = context.space_data
    rv3d = getattr(space, "region_3d", None)
    if region is None or rv3d is None:
        return None

    coord = (mouse_x, mouse_y)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
    ray_direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    depsgraph = context.evaluated_depsgraph_get()

    hit, _loc, _normal, _face_index, obj, _matrix = context.scene.ray_cast(
        depsgraph,
        ray_origin,
        ray_direction,
        distance=10_000.0,
    )
    if not hit or obj is None:
        return None

    original = getattr(obj, "original", obj)
    if original and original.get("block_id"):
        return original
    if obj.get("block_id"):
        return obj
    return None


# ---------------------------------------------------------------------------
# Screen-box projection picker
# ---------------------------------------------------------------------------

def _iter_visible_block_objects(context: bpy.types.Context):
    """Yield every block object that is visible in the current view layer."""
    view_layer = context.view_layer
    parent = chunk_utils.chunks_parent()
    if parent:
        for col in parent.children:
            if not col.name.startswith("Chunk_") or col.hide_viewport:
                continue
            for obj in col.objects:
                if not obj.get("block_id"):
                    continue
                try:
                    if not obj.visible_get(view_layer=view_layer):
                        continue
                except TypeError:
                    if obj.hide_get() or obj.hide_viewport:
                        continue
                yield obj
    else:
        for obj in bpy.data.objects:
            if obj.get("block_id"):
                yield obj


def pick_block_by_screen_box(
    context: bpy.types.Context,
    mouse_x: float,
    mouse_y: float,
) -> Tuple[Optional[bpy.types.Object], str]:
    """Return ``(object, detail_str)`` for the block whose projected
    bounding box contains the cursor.  Falls back to the nearest block
    when multiple boxes overlap at the cursor position.

    The second element of the tuple is a human-readable diagnostic string
    suitable for ``self.report()``.
    """
    region = context.region
    rv3d = getattr(context.space_data, "region_3d", None)
    if region is None or rv3d is None:
        return None, "No 3D viewport region."

    context.view_layer.update()
    mx, my = float(mouse_x), float(mouse_y)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, (mx, my))
    ray_direction = (
        view3d_utils.region_2d_to_vector_3d(region, rv3d, (mx, my)).normalized()
    )

    candidates = []
    checked = 0
    for obj in _iter_visible_block_objects(context):
        checked += 1
        projected = []
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            screen = view3d_utils.location_3d_to_region_2d(region, rv3d, world)
            if screen is not None:
                projected.append(screen)
        if not projected:
            continue

        min_x = min(p.x for p in projected)
        max_x = max(p.x for p in projected)
        min_y = min(p.y for p in projected)
        max_y = max(p.y for p in projected)

        # Small padding because distant Minecraft blocks produce tiny screen
        # rectangles.
        pad = 5.0
        if not (min_x - pad <= mx <= max_x + pad and min_y - pad <= my <= max_y + pad):
            continue

        center = obj.matrix_world.translation
        depth = (center - ray_origin).dot(ray_direction)
        if depth < 0:
            continue

        center_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, center)
        center_dist = (
            (center_2d.x - mx) ** 2 + (center_2d.y - my) ** 2
            if center_2d is not None
            else 999_999.0
        )
        candidates.append((depth, center_dist, obj))

    if not candidates:
        return None, f"No visible block hit. Checked {checked} objects."

    candidates.sort(key=lambda item: (item[0], item[1]))
    best = candidates[0][2]
    return best, f"Checked {checked} objects; {len(candidates)} candidate(s)."


# ---------------------------------------------------------------------------
# Selection helper (handles Shift / Ctrl modifiers)
# ---------------------------------------------------------------------------

def select_block_object(
    context: bpy.types.Context,
    obj: Optional[bpy.types.Object],
    event: Optional[bpy.types.Event] = None,
) -> bool:
    """Select *obj*, honouring Shift (extend) and Ctrl (deselect) modifiers."""
    if obj is None:
        return False

    if event and event.shift:
        obj.select_set(not obj.select_get())
        if obj.select_get():
            context.view_layer.objects.active = obj
        return True

    if event and event.ctrl:
        obj.select_set(False)
        if context.view_layer.objects.active == obj:
            context.view_layer.objects.active = None
        return True

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    context.view_layer.objects.active = obj
    return True
