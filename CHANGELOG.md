# Changelog

All notable changes to **MC Chunk Workflow** are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).  
Versions follow [Semantic Versioning](https://semver.org/).

---

## [1.0.0] — 2026-07-31

### Added
- Initial public release extracted from `A1New.blend`.
- **Performance Mode** — Solid shading + rig chunk only.
- **Lookdev Mode** — Material Preview for visible chunks.
- **Rig Chunk / Rig + Neighbors** — rig-relative chunk focus.
- **Selected Chunk / Selected + Neighbors** — focus on active block's chunk.
- **Origin Radius** — show chunks within radius of world origin.
- **Pick Block by Screen Box** — bounding-box projected block picker.
- **Pick Block by Ray** — geometry ray-cast block picker.
- **Lock / Unlock Terrain** — prevent terrain from blocking prop selection.
- **Select Steve Rig** — one-click hero armature selection.
- **Hide All / Show All Viewport** — bulk chunk viewport toggle.
- **Final Render State** — enable render on all chunks with one click.
- **Print Stats** — console output of chunk and object counts.
- Refactored from monolithic text blocks into a proper multi-module addon package:
  `chunk_utils.py`, `pick_utils.py`, `operators.py`, `panel.py`.
- `docs/WORLD_FORMAT.md` — chunk collection format specification.
- `scripts/build_release.py` — automated `.zip` release builder.
