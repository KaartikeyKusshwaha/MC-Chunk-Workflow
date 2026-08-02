"""Minecraft world-data inspection and conservative Java Anvil decoding."""

from __future__ import annotations

import gzip
import io
import json
import math
import re
import struct
import zlib
from pathlib import Path
from typing import Any

import nbtlib


CANONICAL_FORMAT = "minecraft-world-blender/v1"
REGION_NAME = re.compile(r"^r\.(-?\d+)\.(-?\d+)\.mca$")
AIR_BLOCKS = {"minecraft:air", "minecraft:cave_air", "minecraft:void_air"}


def _path(value: str, *, expected: str | None = None) -> Path:
    path = Path(value).expanduser().resolve()
    if expected == "file" and not path.is_file():
        raise ValueError(f"File not found: {path}")
    if expected == "dir" and not path.is_dir():
        raise ValueError(f"Directory not found: {path}")
    return path


def _region_files(world: Path) -> list[Path]:
    region_dir = world / "region"
    if not region_dir.is_dir():
        return []
    return sorted(path for path in region_dir.glob("r.*.*.mca") if REGION_NAME.fullmatch(path.name))


def _canonical_summary(data: dict[str, Any]) -> dict[str, Any]:
    blocks = data.get("blocks")
    if not isinstance(blocks, list):
        raise ValueError("Canonical JSON requires a 'blocks' array")
    ids = sorted({str(block.get("id", "")) for block in blocks if isinstance(block, dict)})
    return {
        "format": data.get("format"),
        "block_count": len(blocks),
        "block_ids": ids[:100],
        "block_id_count": len(ids),
        "chunk_size": int(data.get("chunk_size", 16)),
    }


def inspect_world_data(world_path: str) -> dict[str, Any]:
    """Identify supported world data without modifying it."""
    path = _path(world_path)
    if path.is_file() and path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        summary = _canonical_summary(data)
        return {
            "path": str(path),
            "kind": "canonical-json",
            "supported_for_generation": data.get("format") == CANONICAL_FORMAT,
            **summary,
        }

    if path.is_dir():
        regions = _region_files(path)
        return {
            "path": str(path),
            "kind": "java-anvil-world" if regions else "directory",
            "supported_for_generation": bool(regions),
            "has_level_dat": (path / "level.dat").is_file(),
            "region_file_count": len(regions),
            "region_samples": [item.name for item in regions[:12]],
            "notes": (
                "Generation reads Java Anvil terrain palettes. Supply a region limit and block cap; "
                "large worlds must be generated in passes."
                if regions
                else "No Java Anvil region files found. Supply canonical JSON or a Java world directory."
            ),
        }
    raise ValueError("World data must be a canonical .json file or a Java world directory")


def _unsigned(value: int) -> int:
    return int(value) & ((1 << 64) - 1)


def _packed_index(data: list[Any], index: int, bits: int) -> int:
    if not data:
        return 0
    bit_index = index * bits
    word_index, offset = divmod(bit_index, 64)
    if word_index >= len(data):
        return 0
    mask = (1 << bits) - 1
    value = _unsigned(data[word_index]) >> offset
    if offset + bits > 64 and word_index + 1 < len(data):
        value |= _unsigned(data[word_index + 1]) << (64 - offset)
    return value & mask


def _block_name(entry: Any) -> str:
    if isinstance(entry, dict):
        return str(entry.get("Name", entry.get("name", "minecraft:air")))
    return "minecraft:air"


def _section_blocks(section: Any, chunk_x: int, chunk_z: int):
    if not isinstance(section, dict):
        return
    section_y = int(section.get("Y", section.get("y", 0)))
    states = section.get("block_states", section)
    palette = states.get("palette", states.get("Palette", [])) if isinstance(states, dict) else []
    data = states.get("data", states.get("BlockStates", [])) if isinstance(states, dict) else []
    if not palette:
        return
    bits = max(4, math.ceil(math.log2(len(palette))))
    for index in range(4096):
        palette_index = _packed_index(list(data), index, bits) if len(palette) > 1 else 0
        if palette_index >= len(palette):
            continue
        block_id = _block_name(palette[palette_index])
        if block_id in AIR_BLOCKS:
            continue
        local_x = index & 15
        local_z = (index >> 4) & 15
        local_y = (index >> 8) & 15
        yield {
            "id": block_id,
            "x": chunk_x * 16 + local_x,
            "y": section_y * 16 + local_y,
            "z": chunk_z * 16 + local_z,
        }


def _decompress_chunk(payload: bytes, compression: int) -> bytes:
    if compression == 1:
        return gzip.decompress(payload)
    if compression == 2:
        return zlib.decompress(payload)
    if compression == 3:
        return payload
    raise ValueError(f"Unsupported Anvil chunk compression type: {compression}")


def _read_region(path: Path, max_blocks: int):
    match = REGION_NAME.fullmatch(path.name)
    if match is None:
        return
    region_x, region_z = (int(match.group(1)), int(match.group(2)))
    raw = path.read_bytes()
    if len(raw) < 8192:
        raise ValueError(f"Invalid Anvil region header: {path}")
    for slot in range(1024):
        entry = raw[slot * 4 : slot * 4 + 4]
        sector_offset = (entry[0] << 16) | (entry[1] << 8) | entry[2]
        if sector_offset == 0:
            continue
        start = sector_offset * 4096
        if start + 5 > len(raw):
            continue
        length = struct.unpack(">I", raw[start : start + 4])[0]
        if length < 2 or start + 4 + length > len(raw):
            continue
        compression = raw[start + 4]
        nbt_bytes = _decompress_chunk(raw[start + 5 : start + 4 + length], compression)
        root = nbtlib.File.parse(io.BytesIO(nbt_bytes))
        level = root.get("Level", root)
        chunk_x = int(level.get("xPos", region_x * 32 + slot % 32))
        chunk_z = int(level.get("zPos", region_z * 32 + slot // 32))
        sections = level.get("sections", level.get("Sections", []))
        for section in sections:
            for block in _section_blocks(section, chunk_x, chunk_z):
                yield block
                max_blocks -= 1
                if max_blocks <= 0:
                    return


def load_world_blocks(
    world_path: str,
    *,
    max_blocks: int = 50_000,
    region_limit: int = 1,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return canonical blocks from canonical JSON or a bounded Java Anvil read."""
    if max_blocks < 1:
        raise ValueError("max_blocks must be at least 1")
    report = inspect_world_data(world_path)
    path = Path(report["path"])
    if report["kind"] == "canonical-json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("format") != CANONICAL_FORMAT:
            raise ValueError(f"Unsupported canonical format: {data.get('format')!r}")
        blocks = data["blocks"][:max_blocks]
        report["truncated"] = len(data["blocks"]) > len(blocks)
        return report, [dict(block) for block in blocks]

    if report["kind"] != "java-anvil-world":
        raise ValueError(report["notes"])
    if region_limit < 1:
        raise ValueError("region_limit must be at least 1")
    blocks: list[dict[str, Any]] = []
    for region in _region_files(path)[:region_limit]:
        remaining = max_blocks - len(blocks)
        blocks.extend(_read_region(region, remaining))
        if len(blocks) >= max_blocks:
            break
    report.update(
        {
            "decoded_block_count": len(blocks),
            "region_limit": region_limit,
            "max_blocks": max_blocks,
            "truncated": len(blocks) >= max_blocks,
        }
    )
    return report, blocks
