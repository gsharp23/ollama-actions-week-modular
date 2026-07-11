"""Orchestrates classification, routing, and storage for content analysis."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .models import ModelRouter
from .storage import ResultStorage


@dataclass
class AnalysisResult:
    """Structured result of a single content analysis."""
    content_preview: str
    task_type: str
    model: str
    analysis: str
    duration_seconds: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


def analyze_content(content, config, storage=None, result_dir=None):
    """Classify, route, analyze, and optionally save a single piece of content."""
    router = ModelRouter(config)
    routed = router.analyze(content)

    result = AnalysisResult(
        content_preview=content[:200],
        task_type=routed['task_type'],
        model=routed['model'],
        analysis=routed['analysis'],
        duration_seconds=routed['duration_seconds'],
    )

    if storage and result_dir:
        filename = f"analysis-{result.task_type}.txt"
        storage.save_analysis(result_dir, filename, result.analysis)

    return result


def analyze_repository(repo_path, config, storage=None, result_dir=None):
    """Analyze relevant files across a repository. Returns a list of AnalysisResult."""
    repo_path = Path(repo_path)
    results = []

    targets = []
    readme = repo_path / "README.md"
    if readme.exists():
        targets.append(readme)

    targets.extend(repo_path.glob("*.py"))
    targets.extend((repo_path / ".github" / "workflows").glob("*.yml")) if (repo_path / ".github" / "workflows").exists() else None

    for file_path in targets:
        if file_path is None or not file_path.exists():
            continue
        try:
            content = file_path.read_text()
        except Exception as e:
            print(f"Could not read {file_path}: {e}")
            continue

        print(f"Analyzing {file_path.name}...")
        result = analyze_content(content, config, storage=storage, result_dir=result_dir)
        results.append(result)

    return results
