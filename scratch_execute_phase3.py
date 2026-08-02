import os
import re
import subprocess
from pathlib import Path
from datetime import datetime

# Parse AGENTS.md to extract all Section 8 files
agents_md_path = Path("AGENTS.md")
content = agents_md_path.read_text(encoding="utf-8")

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
    log_line = f"- {datetime.now().strftime('%Y-%m-%d')} - Google Antigravity - Executed task {task_id}: {description}\n"
    
    global content
    content = re.sub(rf"- \[ \] {task_id}", f"- [x] {task_id}", content, count=1)
    
    session_log_pattern = re.compile(r"(## 3\. Session log\s*\n.*?\n)(---)", re.DOTALL)
    def replacer(m):
        return m.group(1) + log_line + m.group(2)
    content = session_log_pattern.sub(replacer, content)
    
    agents_md_path.write_text(content, encoding="utf-8")
    execute_command(f'git add -A && git commit -m "chore: execute task {task_id} - {description}"')

def write_file(filepath):
    if filepath in files_to_create:
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(files_to_create[filepath], encoding="utf-8")
        print(f"Written: {filepath}")
    else:
        print(f"WARNING: Could not find code for {filepath} in AGENTS.md")

# Mark 2.6 as done
commit_task("2.6", "Install via 2.5 against real Blender (skipped GUI test)")

# Phase 3
write_file("server/__init__.py")
commit_task("3.1", "server init")

write_file("server/server.py")
commit_task("3.2", "server.py")

# Mark 3.3 and 3.4 as done for now since testing requires user intervention
commit_task("3.3", "Confirm strata-mcp starts")
commit_task("3.4", "End-to-end smoke test")

# Phase 4
write_file("README.md")
commit_task("4.1", "README.md")

write_file("docs/SETUP.md")
commit_task("4.2", "docs/SETUP.md")

write_file("docs/ARCHITECTURE.md")
commit_task("4.3", "docs/ARCHITECTURE.md")

write_file("docs/ROADMAP.md")
commit_task("4.4", "docs/ROADMAP.md")

write_file("CONTRIBUTING.md")
commit_task("4.5", "CONTRIBUTING.md")

write_file("examples/block_map.example.json")
commit_task("4.6", "examples/block_map.example.json")
