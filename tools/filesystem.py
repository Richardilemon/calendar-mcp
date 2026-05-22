import os
import json
from pathlib import Path

ALLOWED_DIR = Path(os.getenv("DATA_DIR", "./data")).resolve()

def safe_path(filename: str) -> Path:
    """Prevent path traversal attacks"""
    target = (ALLOWED_DIR / filename).resolve()
    if not str(target).startswith(str(ALLOWED_DIR)):
        raise ValueError(f"Access denied: {filename}")
    return target

async def handle_read_file(args: dict) -> str:
    path = safe_path(args["filename"])
    if not path.exists():
        return f"File not found: {args['filename']}"
    return path.read_text()

async def handle_write_file(args: dict) -> str:
    path = safe_path(args["filename"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(args["content"])
    return f"Written to {args['filename']}"

async def handle_list_files(args: dict) -> str:
    files = [f.name for f in ALLOWED_DIR.iterdir() if f.is_file()]
    return json.dumps(files)