import pytest
import subprocess
import os
from pathlib import Path

def pytest_configure(config):
    config.addinivalue_line("markers", "critical: mark test as critical (must pass)")
    config.addinivalue_line("markers", "advisory: mark test as advisory (can warn)")

@pytest.fixture
def ollama_available():
    """Checks if Ollama service is responding"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except Exception:
        return False

@pytest.fixture
def model_name():
    """Default model for testing"""
    return "llama3.2:1b"

@pytest.fixture
def ollama_models_dir():
    """Configured Ollama model cache directory"""
    return Path(os.environ.get("OLLAMA_MODELS", os.path.expanduser("~/.ollama/models")))

@pytest.fixture
def test_output_dir(tmp_path):
    """Temporary directory for test outputs"""
    output_dir = tmp_path / "test_outputs"
    output_dir.mkdir()
    return output_dir

@pytest.fixture
def sample_prompt():
    """Standard prompt for consistent testing"""
    return "Respond with exactly: TEST_PASSED"
