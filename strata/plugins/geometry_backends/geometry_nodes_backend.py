"""
v1 default `geometry_backends` plugin. Scatters a prototype object onto a
point cloud (one vertex per block position) using Geometry Nodes, instead of
creating one Blender Object per block -- necessary at the scale this project
targets (thousands of chunks, easily 10s of millions of block instances).

Mirrors the instancing configuration validated for this project elsewhere:
Object Info (Transform Space = ORIGINAL, As Instance = False) feeding
Instance on Points, followed by Realize Instances. If your actual working
node graph differs from this reconstruction, this is the file to fix --
nothing else in the pipeline needs to know how instancing works internally.

Assumes Blender 4.0+ (node-group interface via `.interface.new_socket`,
Blender 3.x used a different API on `node_group.inputs`/`.outputs` directly).
This file is the only place in the repo that assumption lives.
"""
from __future__ import annotations

from typing import List, Tuple

import bpy

from .base import GeometryBackend


class GeometryNodesBackend(GeometryBackend):
    def place_instances(self, chunk_collection, prototype_obj, positions: List[Tuple[int, int, int]], name_hint: str) -> None:
        mesh = bpy.data.meshes.new(f"{name_hint}_pts")
        mesh.from_pydata(positions, [], [])
        mesh.update()
        point_obj = bpy.data.objects.new(f"{name_hint}_pts", mesh)
        chunk_collection.objects.link(point_obj)

        modifier = point_obj.modifiers.new(name="Strata_Instance", type="NODES")
        modifier.node_group = self._instancer_node_group(prototype_obj)

    def _instancer_node_group(self, prototype_obj):
        group_name = f"Strata_Instancer_{prototype_obj.name}"
        existing = bpy.data.node_groups.get(group_name)
        if existing:
            return existing

        ng = bpy.data.node_groups.new(group_name, "GeometryNodeTree")
        ng.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
        ng.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")

        nodes, links = ng.nodes, ng.links
        n_in = nodes.new("NodeGroupInput"); n_in.location = (-600, 0)
        n_out = nodes.new("NodeGroupOutput"); n_out.location = (400, 0)

        obj_info = nodes.new("GeometryNodeObjectInfo")
        obj_info.location = (-600, -220)
        obj_info.transform_space = "ORIGINAL"
        obj_info.inputs["Object"].default_value = prototype_obj
        obj_info.inputs["As Instance"].default_value = False

        inst = nodes.new("GeometryNodeInstanceOnPoints"); inst.location = (-200, 0)
        realize = nodes.new("GeometryNodeRealizeInstances"); realize.location = (100, 0)

        links.new(n_in.outputs["Geometry"], inst.inputs["Points"])
        links.new(obj_info.outputs["Geometry"], inst.inputs["Instance"])
        links.new(inst.outputs["Instances"], realize.inputs["Geometry"])
        links.new(realize.outputs["Geometry"], n_out.inputs["Geometry"])
        return ng
