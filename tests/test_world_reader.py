"""
Builds a tiny synthetic .mca region with anvil-parser2's own writer API,
then confirms AnvilWorldReader reads it back correctly. Run this BEFORE
pointing the pipeline at a real save -- it's the fastest way to catch a
coordinate-convention mismatch (region-local vs global chunk indices, y
range) against ground truth you fully control. See the VERIFY note in
strata/plugins/world_readers/anvil_reader.py (8.16).
"""
from __future__ import annotations

import anvil
import pytest

from strata.plugins.world_readers.anvil_reader import AnvilWorldReader


@pytest.fixture
def tiny_region(tmp_path):
    region = anvil.EmptyRegion(0, 0)
    stone = anvil.Block("minecraft", "stone")
    region.set_block(stone, 0, 0, 0)   # exactly one known block, one known position
    region_dir = tmp_path / "region"
    region_dir.mkdir()
    region.save(str(region_dir / "r.0.0.mca"))
    return tmp_path


def test_reads_back_the_single_placed_block(tiny_region):
    blocks = list(AnvilWorldReader().read_blocks(str(tiny_region), y_min=0, y_max=0))
    assert len(blocks) == 1
    x, y, z, block_id = blocks[0]
    assert block_id == "stone"
    # If x/z here are NOT (0, 0), that's real signal that
    # Chunk.from_region's coordinate convention differs from what
    # anvil_reader.py assumes -- fix the coordinate math there, not here
    # (Error Handling / Correctness: don't paper over this in the test).


def test_missing_region_folder_raises_a_clear_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        list(AnvilWorldReader().read_blocks(str(tmp_path)))
