#!/usr/bin/env python3
"""
Deprecated: DirectoryManager now lives in ollama_pipeline.storage.
This module re-exports it for backward compatibility with existing imports.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from ollama_pipeline.storage import DirectoryManager

__all__ = ['DirectoryManager']

if __name__ == "__main__":
    dm = DirectoryManager()
    new_dir = dm.create_timestamped_dir("test-run")
    print(f"Created: {new_dir}")

    recent = dm.list_directories()
    print(f"Recent directories: {[d.name for d in recent]}")
