"""Storage operations: timestamped directories and git-based result persistence."""

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


class DirectoryManager:
    """Manages timestamped directories for workflow results."""

    def __init__(self, base_dir="results"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def create_timestamped_dir(self, prefix="workflow"):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        dir_name = f"{prefix}-{timestamp}"
        dir_path = self.base_dir / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"Created directory: {dir_path}")
        return dir_path

    def get_latest_dir(self, prefix="workflow"):
        pattern = f"{prefix}-*"
        matching_dirs = list(self.base_dir.glob(pattern))
        if not matching_dirs:
            return None
        return max(matching_dirs, key=lambda p: p.stat().st_mtime)

    def list_directories(self, prefix="workflow", limit=10):
        pattern = f"{prefix}-*"
        matching_dirs = list(self.base_dir.glob(pattern))
        sorted_dirs = sorted(matching_dirs, key=lambda p: p.stat().st_mtime, reverse=True)
        return sorted_dirs[:limit]

    def cleanup_old_directories(self, prefix="workflow", keep=5):
        all_dirs = self.list_directories(prefix, limit=100)
        if len(all_dirs) <= keep:
            print(f"Only {len(all_dirs)} directories found, no cleanup needed")
            return 0
        to_remove = all_dirs[keep:]
        for dir_path in to_remove:
            print(f"Removing old directory: {dir_path}")
            shutil.rmtree(dir_path)
        print(f"Cleaned up {len(to_remove)} old directories")
        return len(to_remove)


def run_git_command(command):
    """Execute git command and return stdout, or None on failure."""
    try:
        result = subprocess.run(
            ['git'] + command,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e.stderr}")
        return None


def commit_results(result_dir, metadata):
    """Write a metadata summary into result_dir and commit it to git."""
    result_dir = Path(result_dir)
    summary_file = result_dir / "workflow_summary.json"

    with open(summary_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Created summary: {summary_file}")

    run_git_command(['add', str(result_dir)])
    workflow_run = metadata.get('workflow_run', 'unknown')
    commit_msg = f"Results from workflow run #{workflow_run}"
    result = run_git_command(['commit', '-m', commit_msg])

    if result is not None:
        print(f"Committed results for run #{workflow_run}")
        return True
    else:
        print("No changes to commit or commit failed")
        return False


def checkout_results_branch(branch="main"):
    """Ensure we're on the given branch before committing results."""
    return run_git_command(['checkout', branch])


class ResultStorage:
    """Combines directory management and git-based result persistence."""

    def __init__(self, base_dir="results"):
        self.dir_manager = DirectoryManager(base_dir)

    def create_run_directory(self, run_number):
        return self.dir_manager.create_timestamped_dir(f"run-{run_number}")

    def save_analysis(self, result_dir, filename, content):
        result_dir = Path(result_dir)
        file_path = result_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Saved analysis to {file_path}")
        return file_path

    def commit_all(self, result_dir, workflow_run, commit_sha, extra_metadata=None):
        result_dir = Path(result_dir)
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "workflow_run": workflow_run,
            "commit_sha": commit_sha,
            "result_directory": str(result_dir),
            "files_created": [],
        }
        if extra_metadata:
            metadata.update(extra_metadata)

        if result_dir.exists():
            for file_path in result_dir.rglob("*"):
                if file_path.is_file():
                    metadata["files_created"].append(str(file_path.relative_to(result_dir)))

        return commit_results(result_dir, metadata)
