# Setup

## Prerequisites
- Blender 4.0+
- Python 3.10+ (separate from Blender's bundled interpreter — this runs the MCP
  server and the pure-Python `strata` package on your system Python)
- A Minecraft world save (a folder that directly contains `region/`)
- A "block library" `.blend`: a file you've already built, containing one object
  per Minecraft block type you want rendered, textured/shaded however you like.
  Object names should either match Minecraft's block ids (e.g. an object named
  `oak_planks`) or be listed in a block-map JSON — see `examples/block_map.example.json`.

## Install

