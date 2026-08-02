"""
Exercises Pipeline orchestration end-to-end with NO live Blender instance --
strata.blender_io.call is mocked at the point each stage imports it, so only
Stages 1, 2, 4 (all pure Python) actually run; Stage 3 and prepare_render()
are checked by asserting they sent the right command and params to the
(mocked) bridge, not by asserting real geometry got placed. This is the
Testing Philosophy principle made concrete: everything up to the bridge call
is bpy-free and testable here.
"""
from __future__ import annotations

import json
from unittest.mock import patch

import anvil
import pytest

from strata import Pipeline


@pytest.fixture
def tiny_world(tmp_path):
    region = anvil.EmptyRegion(0, 0)
    region.set_block(anvil.Block("minecraft", "oak_planks"), 0, 0, 0)
    region.set_block(anvil.Block("minecraft", "stone"), 1, 0, 0)
    region_dir = tmp_path / "region"
    region_dir.mkdir()
    region.save(str(region_dir / "r.0.0.mca"))
    return tmp_path


@pytest.fixture
def block_map_file(tmp_path):
    path = tmp_path / "block_map.json"
    path.write_text(json.dumps({"oak_planks": "OakPlank_Proto"}))
    return str(path)


def test_load_world_and_optimize_without_blender(tiny_world):
    pipeline = Pipeline(chunk_size=16)
    pipeline.load_world(str(tiny_world), y_min=0, y_max=0)
    assert len(pipeline.state.blocks) == 2

    pipeline.optimize()
    # both blocks are adjacent to "nothing" (air by omission) in this tiny
    # fixture, so neither should get culled
    assert len(pipeline.state.blocks) == 2


def test_build_chunks_sends_resolved_prototype_names_not_classes(tiny_world, block_map_file):
    pipeline = Pipeline(chunk_size=16)
    pipeline.load_world(str(tiny_world), y_min=0, y_max=0)
    pipeline.use_library("blocks.blend")
    pipeline.use_block_map(block_map_file)
    pipeline.optimize()

    with patch("strata.stages.build_geometry.blender_io") as mock_io:
        mock_io.call.return_value = {"chunks": 1, "blocks_placed": 2, "unmapped_block_ids": ["stone"]}
        pipeline.build_chunks()

    assert mock_io.call.called
    command = mock_io.call.call_args[0][0]
    kwargs = mock_io.call.call_args[1]
    assert command == "build_geometry"
    sent_names = {g["prototype_name"] for g in kwargs["groups"]}
    assert "OakPlank_Proto" in sent_names   # resolved via the block map
    assert "stone" in sent_names            # fell back to the raw block id, as documented
    assert pipeline.state.unmapped_block_ids == {"stone"}


def test_prepare_render_sends_a_target_name_string_not_a_class():
    pipeline = Pipeline()
    with patch("strata.stages.render_prep.blender_io") as mock_io:
        mock_io.call.return_value = {}
        pipeline.prepare_render(target="eevee_cycles")
    mock_io.call.assert_called_once_with("apply_render_target", target_name="eevee_cycles")
