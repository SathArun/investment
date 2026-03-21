"""
PreToolUse hook: blocks direct edits to .env files (allow .env.example).
Exit code 2 = block + show message. Exit code 0 = allow.
"""
import sys
import json

data = sys.stdin.read().strip()
if not data:
    sys.exit(0)

try:
    payload = json.loads(data)
except json.JSONDecodeError:
    sys.exit(0)

file_path = payload.get("file_path", "")
filename = file_path.replace("\\", "/").split("/")[-1]

if filename.startswith(".env") and not filename.endswith(".example"):
    print("BLOCKED: Direct .env edits are prohibited. Edit .env.example instead.")
    sys.exit(2)

sys.exit(0)
