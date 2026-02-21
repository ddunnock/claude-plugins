"""Shared I/O utilities for requirements-dev scripts."""
import json
import os
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile


def _atomic_write(filepath: str, data: dict) -> None:
    """Write JSON data atomically using temp-file-then-rename pattern.

    Creates a temporary file in the same directory as the target (ensuring
    same filesystem for atomic rename), writes JSON, fsyncs, then renames.
    """
    target_dir = os.path.dirname(os.path.abspath(filepath))
    fd = NamedTemporaryFile(
        mode="w",
        dir=target_dir,
        suffix=".tmp",
        delete=False,
    )
    try:
        json.dump(data, fd, indent=2)
        fd.write("\n")
        fd.flush()
        os.fsync(fd.fileno())
        fd.close()
        os.rename(fd.name, filepath)
    except Exception:
        fd.close()
        try:
            os.unlink(fd.name)
        except OSError:
            pass
        raise


def _validate_path(path: str, allowed_extensions: list[str] | None = None) -> str:
    """Validate and resolve a path argument. Reject '..' traversal.

    Returns os.path.realpath() resolved path.
    """
    if ".." in Path(path).parts:
        print(f"Error: Path contains '..' traversal: {path}", file=sys.stderr)
        sys.exit(1)
    resolved = os.path.realpath(path)
    if allowed_extensions:
        ext = os.path.splitext(resolved)[1].lower()
        if ext not in allowed_extensions:
            print(f"Error: Extension '{ext}' not in {allowed_extensions}", file=sys.stderr)
            sys.exit(1)
    return resolved


def _validate_dir_path(path: str) -> str:
    """Validate and resolve a directory path argument. Reject '..' traversal.

    Returns os.path.realpath() resolved path.
    """
    if ".." in Path(path).parts:
        print(f"Error: Path contains '..' traversal: {path}", file=sys.stderr)
        sys.exit(1)
    return os.path.realpath(path)
