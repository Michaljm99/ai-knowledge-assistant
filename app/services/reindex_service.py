import subprocess
import sys
from pathlib import Path


def rebuild_knowledge_base():

    app_dir = Path(__file__).resolve().parent.parent

    result = subprocess.run(
        [sys.executable, "build_database.py"],
        cwd=app_dir,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return {
            "status": "success",
            "message": "Knowledge base rebuilt successfully"
        }

    return {
        "status": "error",
        "message": result.stderr
    }
