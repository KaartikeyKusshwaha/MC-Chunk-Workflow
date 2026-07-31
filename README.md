# MC Chunk Workflow

> A Blender addon for working efficiently with huge Minecraft worlds in the 3D Viewport.

![Blender](https://img.shields.io/badge/Blender-4.0%2B-orange?logo=blender)
![License](https://img.shields.io/badge/license-GPL--3.0-blue)
![Version](https://img.shields.io/badge/version-1.0.0-green)

---

## The Problem

Importing a full Minecraft world into Blender means **thousands of objects and millions of faces** loaded at once. This kills viewport performance and makes it nearly impossible to animate characters, position props, or do any fine editing work.

## The Solution

**MC Chunk Workflow** splits the world into 16 × 16 × 16 block chunks and gives you one-click controls to show only the chunks you need right now — while keeping every chunk render-enabled in the background. You work fast in a clean viewport; Blender renders the full world.

---

## Features

| Feature | Description |
|---|---|
| **Performance Mode** | Shows only the rig's chunk in Solid shading — minimal GPU load |
| **Lookdev Mode** | Material Preview for the currently visible chunks |
| **Rig Chunk / Rig + Neighbors** | Snap visible chunks to Steve's current position |
| **Selected Chunk** | Show only the chunk containing the selected block |
| **Selected + Neighbors** | Expand visibility by an adjustable radius around the selected chunk |
| **Origin Radius** | Show chunks within a radius of world origin |
| **Pick Block by Screen Box** | Click-select blocks using projected bounding boxes (great for dense leaves) |
| **Pick Block by Ray** | Geometry ray-cast picker for solid terrain |
| **Lock / Unlock Terrain** | Prevent terrain blocks from intercepting character/prop selection |
| **Select Steve Rig** | Jump-select the hero armature even when terrain is locked |
| **Hide All / Show All Viewport** | Bulk toggle all chunks without touching render flags |
| **Final Render State** | Enable render on every chunk in one click |
| **Print Stats** | Print chunk/object counts to the system console |

---

## Installation

### Method A — Install from `.zip` (recommended)

1. Download the latest `mc_chunk_workflow_v1.0.0.zip` from the [Releases](../../releases) page.
2. In Blender: **Edit → Preferences → Add-ons → Install…**
3. Select the downloaded `.zip` file.
4. Enable **MC Chunk Workflow** in the add-on list.

### Method B — Install from source

```bash
git clone https://github.com/YOUR_USERNAME/MC-Chunk-Workflow.git
```

Then zip the `mc_chunk_workflow/` folder and install via Blender Preferences as above,  
**or** copy the `mc_chunk_workflow/` folder directly into your Blender addons directory:

| Platform | Path |
|---|---|
| Windows | `%APPDATA%\Blender Foundation\Blender\4.x\scripts\addons\` |
| macOS | `~/Library/Application Support/Blender/4.x/scripts/addons/` |
| Linux | `~/.config/blender/4.x/scripts/addons/` |

---

## Quick Start

1. Install and enable the addon.
2. Open your Minecraft-imported `.blend` file.
3. In the **3D Viewport**, press **N** to open the N-sidebar.
4. Navigate to the **MC World** tab.

> **Requirement:** Your world must be organised into collections named  
> `MC_Chunks_16x16x16 > Chunk_x±NNN_y±NNN_z±NNN`.  
> Each chunk collection must have `mc_chunk_x`, `mc_chunk_y`, `mc_chunk_z` custom properties.  
> Block objects must have `block_id`, `mc_x`, `mc_y`, `mc_z` custom properties.  
> See [WORLD_FORMAT.md](docs/WORLD_FORMAT.md) for the full specification.

### Typical Workflow

```
1. Open Blender → load your world .blend
2. MC World panel → "Performance Mode"      (only rig chunk visible, Solid shading)
3. Select a block near your shot area
4. "Selected + Neighbors"                   (expand to nearby chunks)
5. Animate / edit freely in the clean viewport
6. "Final Render State"                     (re-enable render for all chunks)
7. Render!
```

---

## Panel Reference

```
MC Chunk Workflow
├── Chunks: 2181  |  Visible: 4
├── Visible objects: 599
│
├── Viewport Performance
│   ├── [Performance Mode]  [Lookdev Mode]
│   ├── [Rig Chunk]         [Rig + Neighbors]
│   ├── Terrain selection: LOCKED
│   ├── [Lock Terrain]      [Unlock Blocks]
│   └── [Select Steve Rig]
│
└── Block Edit Tools
    ├── [Pick Block by Screen Box]
    ├── [Pick Block by Ray]
    ├── [Selected Chunk]
    ├── [Selected + Neighbors]
    ├── [Origin Radius]
    ├── ─────────────────────
    ├── [Hide All Viewport]
    ├── [Show All Viewport]
    ├── [Final Render State]
    └── [Print Stats]
```

---

## Customisation

### Rename the hero rig

If your character armature is not called `A1_Steve_Rig`, open  
`mc_chunk_workflow/chunk_utils.py` and change:

```python
HERO_RIG_NAME = "A1_Steve_Rig"   # ← change to your armature's name
```

### Change the chunks parent collection name

```python
CHUNKS_PARENT_NAME = "MC_Chunks_16x16x16"   # ← change if needed
```

---

## Repository Structure

```
MC-Chunk-Workflow/
├── mc_chunk_workflow/          ← the installable addon package
│   ├── __init__.py             #   bl_info + register/unregister
│   ├── chunk_utils.py          #   core chunk/collection helpers
│   ├── pick_utils.py           #   block-picking (ray & screen box)
│   ├── operators.py            #   all Blender operator classes
│   └── panel.py                #   N-sidebar panel
├── docs/
│   └── WORLD_FORMAT.md         #   chunk collection format spec
├── scripts/
│   └── build_release.py        #   builds the installable .zip
├── .gitignore
├── CHANGELOG.md
├── LICENSE
└── README.md
```

---

## Contributing

Pull requests are welcome!  
Please open an issue first to discuss significant changes.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Open a pull request

---

## License

[GPL-3.0-or-later](LICENSE) — the same license as Blender itself.
