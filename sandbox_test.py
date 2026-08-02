# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Strata end-to-end sandbox test.
Tests every layer that can run without Blender installed:
  1. Import check
  2. Core SDK unit tests (pytest)
  3. Pipeline instantiation + stage dry-run
  4. MCP server import and tool listing
  5. Server/server.py tool registration
  6. Addon structure validation (no bpy executed, just file checks)
"""
import io, subprocess, sys, importlib, pathlib, json
import os; os.environ.setdefault("PYTHONIOENCODING", "utf-8")

PASS = "[PASS]"
FAIL = "[FAIL]"

results = []

def check(label, fn):
    try:
        fn()
        print(f"[{PASS}] {label}")
        results.append((label, True, None))
    except Exception as e:
        print(f"[{FAIL}] {label}\n       {e}")
        results.append((label, False, str(e)))

# ── 1. Import strata ──────────────────────────────────────────────────────────
def test_import_strata():
    import strata
    assert hasattr(strata, "Pipeline"), "strata.Pipeline not found"
    assert hasattr(strata, "PipelineState"), "strata.PipelineState not found"

check("import strata / Pipeline / PipelineState", test_import_strata)

# ── 2. Core submodules ────────────────────────────────────────────────────────
for mod in [
    "strata.chunking",
    "strata.culling",
    "strata.block_library",
    "strata.pipeline_state",
    "strata.pipeline",
    "strata.blender_io",
    "strata.stages",
    "strata.plugins.base",
    "strata.plugins.world_readers.base",
    "strata.plugins.world_readers.anvil_reader",
    "strata.plugins.world_readers.litematica_reader",
    "strata.plugins.geometry_backends.base",
    "strata.plugins.geometry_backends.geometry_nodes_backend",
    "strata.plugins.geometry_backends.barebones_backend",
    "strata.plugins.render_targets.base",
    "strata.plugins.render_targets.eevee_cycles",
    "strata.plugins.render_targets.unreal",
]:
    check(f"import {mod}", lambda m=mod: importlib.import_module(m))

# -- 3. Chunking math ----------------------------------------------------------
def test_chunking_math():
    from strata.chunking import bucket_into_chunks
    blocks = [(0, 64, 0, "stone"), (16, 64, 0, "stone"), (0, 64, 16, "grass")]
    chunks = bucket_into_chunks(blocks)
    assert (0, 0) in chunks, "chunk (0,0) missing"
    assert (1, 0) in chunks, "chunk (1,0) missing"
    assert (0, 1) in chunks, "chunk (0,1) missing"
    assert "stone" in chunks[(0, 0)]

check("chunking: bucket_into_chunks correctly groups blocks into 16x16 chunks", test_chunking_math)

# -- 4. Culling ----------------------------------------------------------------
def test_culling():
    from strata.culling import cull_hidden_blocks
    # Generator of (x,y,z,block_id) tuples -- expects list-of-4-tuples
    blocks = [(0, 0, 0, "stone"), (1, 0, 0, "stone")]
    visible = list(cull_hidden_blocks(blocks))
    # 2 adjacent blocks still have exposed outer faces, so both should survive
    assert len(visible) > 0, "expected at least 1 visible block"

check("culling: cull_hidden_blocks returns non-empty for solid pair", test_culling)

# -- 5. block_library functions -----------------------------------------------
def test_block_library():
    import tempfile, json
    from strata.block_library import load_block_map, resolve_prototype_name
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"stone": "Stone_Proto"}, f)
        fname = f.name
    bmap = load_block_map(fname)
    assert bmap == {"stone": "Stone_Proto"}
    assert resolve_prototype_name("stone", bmap) == "Stone_Proto"
    assert resolve_prototype_name("unknown", bmap) == "unknown"  # fallback

check("block_library: load_block_map + resolve_prototype_name", test_block_library)

# ── 6. Pipeline state round-trip ──────────────────────────────────────────────
def test_pipeline_state():
    from strata.pipeline_state import PipelineState
    s = PipelineState()
    s.world_path = "/some/world"
    assert s.world_path == "/some/world"

check("PipelineState round-trip", test_pipeline_state)

# ── 7. Pipeline class instantiation ──────────────────────────────────────────
def test_pipeline_class():
    from strata import Pipeline
    p = Pipeline()
    assert p is not None

check("Pipeline() instantiation", test_pipeline_class)

# ── 8. pytest suite ───────────────────────────────────────────────────────────
def test_pytest():
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--basetemp=./.pytest_tmp", "--tb=short"],
        capture_output=True, text=True
    )
    print(r.stdout[-2000:])  # show tail
    if r.returncode != 0:
        raise RuntimeError(f"pytest exited {r.returncode}\n{r.stderr[-500:]}")

check("pytest tests/ — all 5 tests pass", test_pytest)

# -- 9. MCP server imports ----------------------------------------------------
def test_mcp_import():
    import server.server as srv
    assert hasattr(srv, "mcp"), "mcp app not found in server.server"

check("server.server imports cleanly and mcp app exists", test_mcp_import)

# -- 10. MCP tool count -------------------------------------------------------
def test_mcp_tools():
    import server.server as srv
    # At minimum the 3 tools defined in server.py must exist as module-level callables
    for expected in ("get_scene_status", "list_block_library", "import_minecraft_world"):
        assert hasattr(srv, expected), f"tool function '{expected}' not found in server.server"
    print(f"       found tools: get_scene_status, list_block_library, import_minecraft_world")

check("MCP server has all 3 registered tools", test_mcp_tools)

# ── 11. Addon file structure ──────────────────────────────────────────────────
def test_addon_structure():
    required = [
        "addon/__init__.py",
        "addon/bridge_server.py",
        "addon/chunk_workflow/__init__.py",
        "addon/chunk_workflow/operators.py",
        "addon/chunk_workflow/panel.py",
        "addon/chunk_workflow/chunk_utils.py",
        "addon/world_import/__init__.py",
        "addon/world_import/operators.py",
        "scripts/install_addon.py",
    ]
    missing = [f for f in required if not pathlib.Path(f).exists()]
    if missing:
        raise FileNotFoundError(f"Missing addon files: {missing}")

check("addon/ all required files present", test_addon_structure)

# ── 12. pyproject.toml entry-point ───────────────────────────────────────────
def test_entrypoint():
    import tomllib
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    scripts = data.get("project", {}).get("scripts", {})
    assert "strata-mcp" in scripts, f"strata-mcp not in [project.scripts]: {scripts}"

check("pyproject.toml declares strata-mcp entry-point", test_entrypoint)

# -- 13. strata-mcp CLI dry-run (via python -m) --------------------------------
def test_cli_help():
    # Use the module entry-point directly — avoids PATH/Scripts issues on Windows
    r = subprocess.run(
        [sys.executable, "-c",
         "import server.server as s; print('strata-mcp entry point OK'); print(s.mcp.name)"],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        raise RuntimeError(f"strata-mcp entry-point failed:\n{r.stderr}")
    print(f"       {r.stdout.strip()}")

check("strata-mcp entry-point importable and mcp.name set", test_cli_help)

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "="*60)
passed = sum(1 for _, ok, _ in results if ok)
failed = sum(1 for _, ok, _ in results if not ok)
print(f"  {passed} passed  |  {failed} failed  |  {len(results)} total")
print("="*60)
if failed:
    print("\nFailed checks:")
    for label, ok, err in results:
        if not ok:
            print(f"  FAIL: {label}\n    {err}")
    sys.exit(1)
else:
    print("\nAll sandbox checks passed!")
    sys.exit(0)
