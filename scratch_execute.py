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

# 1.16 Run tests
execute_command(r"python -m pytest tests/ --basetemp=./.pytest_tmp")
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
