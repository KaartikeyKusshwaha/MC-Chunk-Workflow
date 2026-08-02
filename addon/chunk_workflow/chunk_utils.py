# SPDX-License-Identifier: GPL-3.0-or-later
"""
chunk_utils.py
~~~~~~~~~~~~~~
Pure-Python helpers for chunk/collection management.
No Blender operators or UI classes here — only functions that can be
imported by operators, the panel, and external scripts alike.
"""

from __future__ import annotations

import math
import re
from typing import Optional

import bpy
from mathutils import Vector

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CHUNKS_PARENT_NAME = "MC_Chunks_16x16x16"
HERO_RIG_NAME = "A1_Steve_Rig"

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _decode_signed(prefix: str, value: str) -> int:
    """Convert a signed-prefix string like 'm7' or 'p3' to an integer."""
    number = int(value)
    return -number if prefix == "m" else number


# ---------------------------------------------------------------------------
# Chunk name parsing
# ---------------------------------------------------------------------------

def parse_chunk_name(name: str) -> Optional[tuple[int, int, int]]:
    """Return (chunk_x, chunk_y, chunk_z) from a collection name like
    ``Chunk_xm001_yp002_zp003``, or *None* if the name does not match."""
    match = re.match(r"^Chunk_x([mp])(\d+)_y([mp])(\d+)_z([mp])(\d+)$", name)
    if not match:
        return None
    xs, xv, ys, yv, zs, zv = match.groups()
    return (
        _decode_signed(xs, xv),
        _decode_signed(ys, yv),
        _decode_signed(zs, zv),
    )


# ---------------------------------------------------------------------------
# Collection accessors
# ---------------------------------------------------------------------------

def chunks_parent() -> Optional[bpy.types.Collection]:
    """Return the ``MC_Chunks_16x16x16`` collection, or *None*."""
    return bpy.data.collections.get(CHUNKS_PARENT_NAME)


def chunk_collections() -> list[bpy.types.Collection]:
    """Return all ``Chunk_*`` child collections, sorted by coordinate."""
    parent = chunks_parent()
    if not parent:
        return []
    chunks = [c for c in parent.children if c.name.startswith("Chunk_")]
    return sorted(
        chunks,
        key=lambda c: (
            int(c.get("mc_chunk_x", 999_999)),
            int(c.get("mc_chunk_y", 999_999)),
            int(c.get("mc_chunk_z", 999_999)),
            c.name,
        ),
    )


def chunk_layer_collections(
    view_layer: Optional[bpy.types.ViewLayer] = None,
) -> dict[str, bpy.types.LayerCollection]:
    """Return a mapping of chunk-collection name → LayerCollection."""
    view_layer = view_layer or bpy.context.view_layer
    result: dict[str, bpy.types.LayerCollection] = {}
    stack = [view_layer.layer_collection]
    while stack:
        lc = stack.pop()
        if lc.collection.name.startswith("Chunk_"):
            result[lc.collection.name] = lc
        stack.extend(lc.children)
    return result


# ---------------------------------------------------------------------------
# Visibility synchronisation
# ---------------------------------------------------------------------------

def sync_chunk_layer_visibility() -> int:
    """Propagate ``hide_viewport`` from each chunk *collection* to every
    ViewLayer's *LayerCollection*.  Returns the number of chunks processed."""
    chunks = {col.name: col for col in chunk_collections()}
    for view_layer in bpy.context.scene.view_layers:
        layer_chunks = chunk_layer_collections(view_layer)
        for name, col in chunks.items():
            lc = layer_chunks.get(name)
            if lc is None:
                continue
            if lc.exclude:
                lc.exclude = False
            if lc.hide_viewport != col.hide_viewport:
                lc.hide_viewport = col.hide_viewport
    return len(chunks)


# ---------------------------------------------------------------------------
# Rig / hero helpers
# ---------------------------------------------------------------------------

def rig_chunk_coords() -> tuple[int, int]:
    """Return the (chunk_x, chunk_z) coordinates of the Steve rig.

    Raises ``RuntimeError`` when the rig object is absent.
    """
    rig = bpy.data.objects.get(HERO_RIG_NAME)
    if rig is None:
        raise RuntimeError(
            f"Hero rig '{HERO_RIG_NAME}' not found. "
            "Rename your character armature to match, or update HERO_RIG_NAME."
        )
    loc = rig.matrix_world.translation
    return math.floor(loc.x / 16.0), math.floor(loc.y / 16.0)


# ---------------------------------------------------------------------------
# Viewport configuration
# ---------------------------------------------------------------------------

def configure_viewports(mode: str = "SOLID") -> int:
    """Set shading mode and sensible overlays on every 3-D viewport.
    Returns the number of viewports changed."""
    changed = 0
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type != "VIEW_3D":
                continue
            space = area.spaces.active
            space.shading.type = mode
            space.overlay.show_overlays = True
            space.overlay.show_relationship_lines = False
            space.overlay.show_outline_selected = True
            if mode == "SOLID":
                space.overlay.show_extras = False
                space.overlay.show_floor = False
            else:
                space.overlay.show_extras = True
                space.overlay.show_floor = True
            changed += 1
    return changed


# ---------------------------------------------------------------------------
# Bulk chunk show / hide
# ---------------------------------------------------------------------------

def show_all_chunks_viewport() -> int:
    """Make every chunk visible in the viewport. Returns chunk count."""
    parent = chunks_parent()
    if parent:
        parent.hide_viewport = False
    cols = chunk_collections()
    for col in cols:
        if col.hide_viewport:
            col.hide_viewport = False
    sync_chunk_layer_visibility()
    return len(cols)


def hide_all_chunks_viewport() -> int:
    """Hide every chunk in the viewport. Returns chunk count."""
    parent = chunks_parent()
    if parent:
        parent.hide_viewport = False
    cols = chunk_collections()
    for col in cols:
        if not col.hide_viewport:
            col.hide_viewport = True
    sync_chunk_layer_visibility()
    return len(cols)


def set_all_chunks_render(enabled: bool = True) -> int:
    """Enable or disable render for every chunk. Returns chunk count."""
    parent = chunks_parent()
    if parent:
        parent.hide_render = False
    cols = chunk_collections()
    for col in cols:
        should_hide = not enabled
        if col.hide_render != should_hide:
            col.hide_render = should_hide
    return len(cols)


# ---------------------------------------------------------------------------
# Radius-based chunk visibility
# ---------------------------------------------------------------------------

def show_chunk_radius(
    center_x: int = 0,
    center_y: int = 0,
    center_z: int = 0,
    radius_x: int = 1,
    radius_y: int = 999,
    radius_z: int = 1,
) -> dict[str, int]:
    """Show only the chunks within *radius* steps of *center* in each axis.

    ``radius_y=999`` (default) keeps all vertical slices visible, which is
    the recommended setting for most workflows.

    Returns ``{"shown": n, "hidden": n}``.
    """
    parent = chunks_parent()
    if parent:
        parent.hide_viewport = False
    shown = hidden = 0
    for col in chunk_collections():
        cx = int(col.get("mc_chunk_x", 999_999))
        cy = int(col.get("mc_chunk_y", 999_999))
        cz = int(col.get("mc_chunk_z", 999_999))
        visible = (
            abs(cx - int(center_x)) <= int(radius_x)
            and abs(cy - int(center_y)) <= int(radius_y)
            and abs(cz - int(center_z)) <= int(radius_z)
        )
        should_hide = not visible
        if col.hide_viewport != should_hide:
            col.hide_viewport = should_hide
        if visible:
            shown += 1
        else:
            hidden += 1
    sync_chunk_layer_visibility()
    set_all_chunks_render(True)
    return {"shown": shown, "hidden": hidden}


def show_rig_area(radius: int = 0) -> dict[str, int]:
    """Show the chunk column (and optional ring) around the hero rig."""
    center_x, center_z = rig_chunk_coords()
    return show_chunk_radius(
        center_x=center_x,
        center_y=0,
        center_z=center_z,
        radius_x=radius,
        radius_y=999,
        radius_z=radius,
    )


# ---------------------------------------------------------------------------
# Selected-object chunk helpers
# ---------------------------------------------------------------------------

def selected_chunk_coords(
    context: Optional[bpy.types.Context] = None,
) -> Optional[tuple[int, int, int]]:
    """Return chunk coordinates for the active object, or *None*."""
    context = context or bpy.context
    obj = context.object
    if obj is None:
        return None
    # Try collection membership first (fastest path).
    for col in obj.users_collection:
        if col.name.startswith("Chunk_"):
            parsed = parse_chunk_name(col.name)
            if parsed:
                return parsed
    # Fall back to custom mc_x / mc_y / mc_z properties.
    if all(k in obj for k in ("mc_x", "mc_y", "mc_z")):
        return (
            int(obj["mc_x"]) // 16,
            int(obj["mc_y"]) // 16,
            int(obj["mc_z"]) // 16,
        )
    return None


def show_selected_chunk(
    radius_x: int = 0,
    radius_y: int = 999,
    radius_z: int = 0,
    context: Optional[bpy.types.Context] = None,
) -> dict[str, int]:
    """Show the chunk that contains the active object (± optional radius).

    Raises ``RuntimeError`` if no valid block object is active.
    """
    coords = selected_chunk_coords(context)
    if coords is None:
        raise RuntimeError("Select a world block object first.")
    return show_chunk_radius(coords[0], coords[1], coords[2], radius_x, radius_y, radius_z)


# ---------------------------------------------------------------------------
# Final render state
# ---------------------------------------------------------------------------

def final_render_state(show_in_viewport: bool = False) -> dict:
    """Enable render on all chunks, optionally also show them in the viewport."""
    set_all_chunks_render(True)
    if show_in_viewport:
        show_all_chunks_viewport()
    return world_stats()


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def world_stats() -> dict:
    """Return a summary dict of chunk / object counts."""
    cols = chunk_collections()
    return {
        "chunks": len(cols),
        "objects": sum(int(c.get("mc_object_count", len(c.objects))) for c in cols),
        "visible_chunks": sum(1 for c in cols if not c.hide_viewport),
        "visible_objects": sum(
            int(c.get("mc_object_count", len(c.objects)))
            for c in cols
            if not c.hide_viewport
        ),
        "render_disabled_chunks": sum(1 for c in cols if c.hide_render),
    }


# ---------------------------------------------------------------------------
# Terrain selection lock
# ---------------------------------------------------------------------------

def terrain_selection_locked() -> bool:
    parent = chunks_parent()
    return bool(parent and parent.hide_select)


def set_terrain_selection_locked(locked: bool = True) -> bool:
    """Lock (or unlock) the parent chunk collection against selection.

    Raises ``RuntimeError`` when the parent collection is missing.
    """
    parent = chunks_parent()
    if parent is None:
        raise RuntimeError(
            f"'{CHUNKS_PARENT_NAME}' collection not found. "
            "Is this a MC Chunk Workflow scene?"
        )
    parent.hide_select = bool(locked)
    # Always keep individual chunks unlocked so they can be toggled freely.
    for col in chunk_collections():
        if col.hide_select:
            col.hide_select = False
    return bool(parent.hide_select)


# ---------------------------------------------------------------------------
# Hero rig selection
# ---------------------------------------------------------------------------

def select_hero_rig(
    context: Optional[bpy.types.Context] = None,
) -> bpy.types.Object:
    """Select the hero rig, switch to Object Mode if needed.

    Raises ``RuntimeError`` when the rig is missing.
    """
    context = context or bpy.context
    rig = bpy.data.objects.get(HERO_RIG_NAME)
    if rig is None:
        raise RuntimeError(
            f"Rig '{HERO_RIG_NAME}' not found. "
            "Rename your armature or update HERO_RIG_NAME in chunk_utils.py."
        )
    try:
        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
    except Exception:
        pass
    bpy.ops.object.select_all(action="DESELECT")
    rig.hide_select = False
    rig.hide_viewport = False
    rig.show_in_front = True
    rig.select_set(True)
    context.view_layer.objects.active = rig
    return rig


# ---------------------------------------------------------------------------
# Addon register / unregister (nothing to register for a utils module)
# ---------------------------------------------------------------------------

def register() -> None:
    pass


def unregister() -> None:
    pass
