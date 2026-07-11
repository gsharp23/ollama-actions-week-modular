# ollama-actions-week-modular

A production-shaped CI pipeline that runs a **multi-model AI analysis pass over
the repository on every push**, driven by a modular, unit-tested Python package
rather than inline shell. It classifies content, routes each piece to a
configured model, persists timestamped results back into git, and publishes a
rolling historical report.

This is the "graduated" version of
[`ollama-actions-week`](https://github.com/gsharp23/ollama-actions-week):
the same AI-in-CI idea, rebuilt as real, maintainable software. Runs are visible
under the [Actions tab](../../actions), and each run auto-commits its report to
[`historical_report.md`](historical_report.md).

## What the pipeline does

Defined in [`.github/workflows/ollama-basic.yml`](.github/workflows/ollama-basic.yml),
triggered on push to `main` or manual dispatch:

1. **Cache & install Ollama** — the Ollama binary + runtime and the pulled model
   files are cached (`actions/cache`), so repeat runs skip the slow install and
   multi-hundred-MB model downloads.
2. **Set up Python & run tests** — installs the package, runs a `pytest` suite
   split into **critical** (must pass) and **advisory** (`continue-on-error`)
   markers, with coverage and JUnit XML output.
3. **Run the analysis pipeline** — loads [`config.yaml`](config.yaml), classifies
   repo content, routes each task (code review / documentation / bug analysis) to
   its assigned model, and stores structured results in a per-run directory.
4. **Persist & report** — commits results and a regenerated historical trend
   report back to `main`, benchmarks response time, writes a
   `$GITHUB_STEP_SUMMARY` dashboard, and uploads results/coverage as artifacts.

## Package layout

```
ollama_pipeline/        Installable package — the core logic
  config.py             Load/merge config.yaml with safe defaults
  models.py             ModelRouter + query execution, retries, OllamaError
  analysis.py           Classify → route → analyze, returns AnalysisResult
  storage.py            Timestamped run dirs + git-based result persistence
scripts/                CLI wrappers: test runner, report generator, result mgr
tests/                  pytest suite (service, reliability, performance)
config.yaml             Models, per-task model assignments, prompts, thresholds
```

## Concepts demonstrated

- Dependency caching for expensive CI setup (binary + model weights)
- Config-driven model routing and content classification
- A tiered test strategy (critical vs. advisory) with coverage and JUnit reports
- Machine-generated results committed back to the repo by the workflow itself
- Trend/historical reporting across runs
- Clean separation of an installable package from thin CLI/workflow glue
