# SPDX-License-Identifier: GPL-3.0-or-later
# MC Chunk Workflow — Blender addon
# https://github.com/YOUR_USERNAME/MC-Chunk-Workflow

bl_info = {
    "name": "MC Chunk Workflow",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "3D Viewport > N-sidebar > MC World",
    "description": (
        "Chunk-based viewport management for large Minecraft worlds. "
        "Toggle chunk visibility while keeping all chunks render-ready, "
        "pick blocks by ray or screen box, lock terrain selection, "
        "and snap the view to the nearest chunk."
    ),
    "category": "3D View",
    "doc_url": "https://github.com/YOUR_USERNAME/MC-Chunk-Workflow#readme",
    "tracker_url": "https://github.com/YOUR_USERNAME/MC-Chunk-Workflow/issues",
}

from . import operators, panel, chunk_utils  # noqa: E402 – imported after bl_info


def register() -> None:
    chunk_utils.register()
    operators.register()
    panel.register()


def unregister() -> None:
    panel.unregister()
    operators.unregister()
    chunk_utils.unregister()
