"""Model operations and routing for the Ollama pipeline."""

import subprocess
import time
import functools


class OllamaError(Exception):
    """Custom exception for Ollama operations."""

    def __init__(self, message, model=None, timeout=None):
        super().__init__(message)
        self.model = model
        self.timeout = timeout


def timed_operation(func):
    """Decorator that logs execution time for any model operation."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"{func.__name__} took {duration:.1f}s")
        return result
    return wrapper


@timed_operation
def run_model_query(model, prompt, timeout=60):
    """Execute Ollama query and return response text."""
    start = time.time()
    try:
        result = subprocess.run(
            ['ollama', 'run', model, prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
        duration = time.time() - start
        print(f"Model {model} responded in {duration:.1f}s")
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        raise OllamaError(f"Query timed out after {timeout}s", model=model, timeout=timeout)
    except subprocess.CalledProcessError as e:
        raise OllamaError(f"Query failed: {e.stderr}", model=model)


def is_model_available(model):
    """Check if a model is downloaded and available."""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=15)
        return result.returncode == 0 and model in result.stdout
    except Exception:
        return False


def ensure_model_available(model):
    """Check if a model is available; download it if missing."""
    if is_model_available(model):
        return True
    print(f"Model {model} not found locally, pulling...")
    try:
        subprocess.run(['ollama', 'pull', model], check=True, timeout=600)
        return True
    except subprocess.CalledProcessError as e:
        raise OllamaError(f"Failed to pull model: {e}", model=model)


class ModelRouter:
    """Classifies content and routes to the appropriate model."""

    def __init__(self, config):
        self.config = config
        self.assignments = config.get('model_assignments', {})
        self.classifier = config.get('models', {}).get('classifier', 'llama3.2:1b')
        self.default_model = config.get('models', {}).get('default', 'llama3.2:1b')
        self.valid_task_types = ['code_review', 'documentation', 'bug_analysis']

    def classify_task(self, content):
        """Use fast model to classify content type."""
        prompt_template = self.config.get('prompts', {}).get(
            'classify',
            'Classify this content as exactly one of: code_review, documentation, bug_analysis. '
            'Respond with only the classification.'
        )
        prompt = f"{prompt_template}\n\nContent:\n{content[:500]}"

        result = run_model_query(self.classifier, prompt, timeout=30)

        result_lower = result.lower()
        for task_type in self.valid_task_types:
            if task_type in result_lower:
                print(f"Classified as: {task_type}")
                return task_type

        print("Classification unclear, defaulting to documentation")
        return 'documentation'

    def select_model(self, task_type):
        """Select appropriate model for task type."""
        model = self.assignments.get(task_type, self.default_model)
        print(f"Selected model {model} for {task_type}")
        return model

    def analyze(self, content):
        """Classify content, select a model, and run analysis. Returns dict with metadata."""
        start = time.time()

        task_type = self.classify_task(content)
        model = self.select_model(task_type)

        prompt_template = self.config.get('prompts', {}).get(
            task_type, f"Analyze the following {task_type} content:"
        )
        prompt = f"{prompt_template}\n\nContent:\n{content[:2000]}"

        analysis_text = run_model_query(model, prompt, timeout=self.config.get('thresholds', {}).get('max_response_time', 60))

        duration = time.time() - start

        return {
            'task_type': task_type,
            'model': model,
            'analysis': analysis_text,
            'duration_seconds': round(duration, 1),
        }
