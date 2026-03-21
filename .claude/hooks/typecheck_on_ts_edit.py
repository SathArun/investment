"""
PostToolUse hook: runs TypeScript typecheck after editing a frontend .ts/.tsx file.
Only triggers for files inside the frontend/ directory.
"""
import sys
import json
import subprocess
import os

data = sys.stdin.read().strip()
if not data:
    sys.exit(0)

try:
    payload = json.loads(data)
except json.JSONDecodeError:
    sys.exit(0)

file_path = payload.get("file_path", "").replace("\\", "/")

if "frontend" not in file_path:
    sys.exit(0)
if not (file_path.endswith(".ts") or file_path.endswith(".tsx")):
    sys.exit(0)

print("Running TypeScript typecheck...")
frontend_dir = os.path.join("C:\\", "Arun", "investment", "frontend")
result = subprocess.run(
    ["npm", "run", "typecheck"],
    cwd=frontend_dir,
    capture_output=True,
    text=True,
)

output = (result.stdout + result.stderr).strip()
lines = output.splitlines()
if lines:
    print("".join(lines[-30:]))

if result.returncode != 0:
    print(f"Typecheck failed (exit {result.returncode})")

sys.exit(0)
