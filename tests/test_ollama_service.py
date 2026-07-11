import subprocess
import pytest

@pytest.mark.critical
def test_ollama_installed():
    """Verify Ollama CLI is installed and accessible"""
    result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
    assert result.returncode == 0, "Ollama not installed or not in PATH"

@pytest.mark.critical
def test_ollama_service_responding(ollama_available):
    """Verify the Ollama service responds to requests"""
    assert ollama_available, "Ollama service is not responding"

@pytest.mark.critical
def test_model_available(model_name):
    """Verify the target model appears in ollama list"""
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
    assert result.returncode == 0
    assert model_name in result.stdout, f"{model_name} not found in ollama list"

@pytest.mark.critical
def test_model_loads_successfully(model_name, sample_prompt):
    """Verify the model can process a simple prompt"""
    result = subprocess.run(['ollama', 'run', model_name, sample_prompt],
                             capture_output=True, text=True, timeout=45)
    assert result.returncode == 0
    assert len(result.stdout.strip()) > 0

@pytest.mark.advisory
def test_cache_directory_exists(ollama_models_dir):
    """Verify the configured OLLAMA_MODELS directory exists"""
    assert ollama_models_dir.exists(), f"{ollama_models_dir} does not exist"
