#!/usr/bin/env python3
"""
Result management script for git-based workflow result storage.
Thin CLI wrapper around ollama_pipeline.storage.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from ollama_pipeline.storage import commit_results


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Manage workflow results")
    parser.add_argument("--workflow-run", required=True, help="Workflow run number")
    parser.add_argument("--commit-sha", required=True, help="Commit SHA")
    parser.add_argument("--result-dir", required=True, help="Result directory path")

    args = parser.parse_args()

    result_dir = Path(args.result_dir)
    if not result_dir.exists():
        print(f"Result directory does not exist: {result_dir}")
        sys.exit(1)

    metadata = {
        "workflow_run": args.workflow_run,
        "commit_sha": args.commit_sha,
    }

    success = commit_results(result_dir, metadata)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
