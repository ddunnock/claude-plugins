"""Shared I/O utilities for atomic file writes and path validation.

Provides crash-safe write operations and path traversal protection
for the system-dev Design Registry.
"""

import json
import os
from tempfile import NamedTemporaryFile


def _atomic_rename(filepath: str, write_fn) -> None:
    """Write content atomically via temp file + fsync + rename.

    Args:
        filepath: Target file path.
        write_fn: Callable that receives the open file handle and writes content.

    Raises:
        OSError: If the write or rename operation fails.
    """
    target_dir = os.path.dirname(os.path.abspath(filepath))
    fd = NamedTemporaryFile(
        mode="w", dir=target_dir, suffix=".tmp", delete=False
    )
    try:
        write_fn(fd)
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


def atomic_write(filepath: str, data: dict) -> None:
    """Write JSON data atomically via temp file + fsync + rename.

    Args:
        filepath: Absolute or relative path to the target JSON file.
        data: Dictionary to serialize as JSON.

    References:
        SCAF-03 (path safety), DREG-02 (atomic writes)
    """
    def _write(fd):
        json.dump(data, fd, indent=2)
        fd.write("\n")

    _atomic_rename(filepath, _write)


def atomic_write_text(filepath: str, text: str) -> None:
    """Write text atomically via temp file + fsync + rename.

    Args:
        filepath: Absolute or relative path to the target file.
        text: Text content to write.

    References:
        DREG-06 (change journal)
    """
    _atomic_rename(filepath, lambda fd: fd.write(text))


def cleanup_orphaned_temps(directory: str) -> list[str]:
    """Remove orphaned .tmp files left by interrupted atomic writes.

    Walks the directory tree and removes any files ending in .tmp,
    which are artifacts of atomic write operations that were
    interrupted before the rename completed.

    Args:
        directory: Root directory to scan for orphaned temp files.

    Returns:
        List of paths to removed .tmp files.

    References:
        DREG-02 (crash recovery)
    """
    cleaned = []
    for root, _dirs, files in os.walk(directory):
        for f in files:
            if f.endswith(".tmp"):
                path = os.path.join(root, f)
                os.unlink(path)
                cleaned.append(path)
    return cleaned


def validate_path(path: str, workspace_root: str) -> str:
    """Validate that a path resolves within the workspace root.

    Uses os.path.realpath() to resolve symlinks and relative components,
    then verifies the resolved path starts with the workspace root.
    Prevents path traversal attacks (e.g., ../../etc/passwd).

    Args:
        path: Path to validate (may be relative or contain symlinks).
        workspace_root: Absolute path to the workspace root directory.

    Returns:
        The resolved absolute path.

    Raises:
        ValueError: If the resolved path is outside the workspace root.

    References:
        SCAF-03 (path validation, security)
    """
    resolved = os.path.realpath(path)
    root = os.path.realpath(workspace_root)
    if not resolved.startswith(root + os.sep) and resolved != root:
        raise ValueError(
            f"Path traversal detected: '{path}' resolves to '{resolved}' "
            f"which is outside workspace root '{root}'"
        )
    return resolved


def ensure_directory(path: str) -> None:
    """Create a directory and all parent directories if they don't exist.

    Args:
        path: Directory path to create.

    References:
        SCAF-05 (workspace initialization)
    """
    os.makedirs(path, exist_ok=True)
