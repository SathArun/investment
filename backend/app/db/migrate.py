"""Database migration runner."""
import subprocess
import sys
from pathlib import Path


def run_migrations():
    backend_dir = Path(__file__).parent.parent.parent
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=backend_dir
    )
    return result.returncode == 0


if __name__ == "__main__":
    if run_migrations():
        print("Migrations complete.")
    else:
        print("Migration failed.")
        sys.exit(1)
