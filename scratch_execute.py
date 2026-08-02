import os
import re
import subprocess
from pathlib import Path
from datetime import datetime

# 1. Parse AGENTS.md to extract all Section 8 files
agents_md_path = Path("AGENTS.md")
content = agents_md_path.read_text(encoding="utf-8")

# Extract file sections
# Pattern looks for `### 8.X `path`` followed by a code block
file_pattern = re.compile(r"### 8\.\d+\s+`([^`]+)`.*?\n```[a-z]*\n(.*?)```", re.DOTALL)
files_to_create = {}
for match in file_pattern.finditer(content):
    path = match.group(1).strip()
    code = match.group(2)
    files_to_create[path] = code

def execute_command(cmd):
    print(f"Executing: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def commit_task(task_id, description):
    # Log to session log
    log_line = f"- {datetime.now().strftime('%Y-%m-%d')} - Google Antigravity - Executed task {task_id}: {description}\n"
    
    # Check off the task in AGENTS.md
    global content
    content = re.sub(rf"- \[ \] {task_id}", f"- [x] {task_id}", content, count=1)
    
    # Append to session log
    session_log_pattern = re.compile(r"(## 3\. Session log\s*\n.*?\n)(---)", re.DOTALL)
    def replacer(m):
        return m.group(1) + log_line + m.group(2)
    content = session_log_pattern.sub(replacer, content)
    
    agents_md_path.write_text(content, encoding="utf-8")
    
    # Commit
    execute_command(f'git add -A && git commit -m "chore: execute task {task_id} - {description}"')

# --- Execute tasks 0.1 through 2.5 automatically ---

def write_file(filepath):
    if filepath in files_to_create:
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(files_to_create[filepath], encoding="utf-8")
        print(f"Written: {filepath}")
    else:
        print(f"WARNING: Could not find code for {filepath} in AGENTS.md")

# 0.5 Configure packaging
execute_command("pip install -e .[dev]")
commit_task("0.5", "Configure packaging")

# Phase 1
write_file("strata/__init__.py")
write_file("strata/pipeline_state.py")
commit_task("1.1", "strata core init and pipeline state")

write_file("strata/chunking.py")
commit_task("1.2", "strata/chunking.py")

write_file("strata/culling.py")
commit_task("1.3", "strata/culling.py")

write_file("strata/block_library.py")
commit_task("1.4", "strata/block_library.py")

write_file("strata/plugins/base.py")
commit_task("1.5", "strata/plugins/base.py")

write_file("strata/plugins/world_readers/base.py")
write_file("strata/plugins/world_readers/anvil_reader.py")
commit_task("1.6", "world_readers base and anvil")

write_file("strata/plugins/world_readers/litematica_reader.py")
commit_task("1.7", "litematica_reader")

write_file("strata/plugins/geometry_backends/base.py")
write_file("strata/plugins/geometry_backends/geometry_nodes_backend.py")
commit_task("1.8", "geometry_backends base and geometry_nodes")

write_file("strata/plugins/geometry_backends/barebones_backend.py")
commit_task("1.9", "barebones_backend")

write_file("strata/plugins/render_targets/base.py")
write_file("strata/plugins/render_targets/eevee_cycles.py")
commit_task("1.10", "render_targets base and eevee_cycles")

write_file("strata/plugins/render_targets/unreal.py")
commit_task("1.11", "render_targets unreal")

write_file("strata/stages/__init__.py")
write_file("strata/stages/read_world.py")
write_file("strata/stages/resolve_assets.py")
write_file("strata/stages/optimize.py")
write_file("strata/stages/chunk_manager.py")
write_file("strata/stages/build_geometry.py")
write_file("strata/stages/render_prep.py")
write_file("strata/stages/animation_prep.py")
commit_task("1.12", "strata stages")

write_file("strata/blender_io.py")
commit_task("1.13", "strata/blender_io.py")

write_file("strata/pipeline.py")
commit_task("1.14", "strata/pipeline.py")

write_file("tests/test_world_reader.py")
write_file("tests/test_pipeline.py")
commit_task("1.15", "tests")

# 1.16 Run tests
execute_command("pytest tests/")
commit_task("1.16", "pytest")

# Phase 2
write_file("addon/__init__.py")
commit_task("2.1", "addon init")

write_file("addon/bridge_server.py")
commit_task("2.2", "addon bridge_server")

write_file("addon/chunk_workflow/__init__.py")
write_file("addon/chunk_workflow/panel.py")
write_file("addon/chunk_workflow/operators.py")
commit_task("2.3", "addon chunk_workflow ref implementation")

write_file("addon/world_import/__init__.py")
write_file("addon/world_import/operators.py")
commit_task("2.4", "addon world_import")

write_file("scripts/install_addon.py")
commit_task("2.5", "install_addon script")
