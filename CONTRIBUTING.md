# Contributing

The core pipeline (`strata/stages/`, `strata/pipeline.py`) is intentionally
small and shouldn't need to change often. The easy, encouraged way to extend
Strata is a new plugin — it ships as ordinary Python, registered under one of
three entry-point groups, with zero changes to this repo required:

- `strata.plugins.world_readers` — read some other world/schematic format into
  `(x, y, z, block_id)` tuples. See `strata/plugins/world_readers/base.py`.
- `strata.plugins.geometry_backends` — a different way to turn a block-position
  list into Blender geometry. See `strata/plugins/geometry_backends/base.py`.
- `strata.plugins.render_targets` — a different Stage 6 target (a stylization
  preset, an Unreal exporter, ...). See `strata/plugins/render_targets/base.py`.

To contribute a plugin that ships *in* this repo (rather than as your own pip
package): implement the base class, register it in `pyproject.toml` under the
matching group, add a test, open a PR. To build one entirely on your own: same
first three steps, just in your own package — Strata will discover it once it's
`pip install`-ed alongside this one.

For core-pipeline changes: open an issue first describing the stage/interface
change before the PR — the seven-stage contract is deliberately stable so
plugins don't break across versions.
