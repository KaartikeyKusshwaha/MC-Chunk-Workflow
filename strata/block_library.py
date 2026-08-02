"""Stage 2 helper: Minecraft block id -> prototype object name resolution."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


def load_block_map(path: str) -> Dict[str, str]:
    """Loads a JSON file mapping block ids to prototype object names in the
    user's library .blend, e.g. {"oak_planks": "OakPlank_Proto"}."""
    data = json.loads(Path(path).read_text())
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object of block_id -> prototype_name")
    return data


def resolve_prototype_name(
    block_id: str, block_map: Dict[str, str], fallback_to_block_id: bool = True
) -> Optional[str]:
    """
    1. Exact match in block_map, else
    2. block_id itself, if fallback_to_block_id (covers users who named their
       library objects identically to the Minecraft block id).
    This is a *guess* in case 2 -- the caller (Stage 3 / addon side) confirms
    it actually exists as a linked object before treating it as resolved.
    """
    if block_id in block_map:
        return block_map[block_id]
    return block_id if fallback_to_block_id else None
