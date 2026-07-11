import subprocess
import pytest

@pytest.mark.advisory
def test_handles_invalid_model():
    """System should fail gracefully with an invalid model name"""
    result = subprocess.run(['ollama', 'run', 'nonexistent:model', 'test'],
                             capture_output=True, text=True, timeout=15)
    assert result.returncode != 0, "Should fail with invalid model"
    assert len(result.stderr) > 0, "Should provide an error message"

@pytest.mark.advisory
def test_handles_empty_prompt(model_name):
    """System should respond appropriately to empty input"""
    result = subprocess.run(['ollama', 'run', model_name, ""],
                             capture_output=True, text=True, timeout=30)
    assert result.returncode == 0 or len(result.stderr) > 0

@pytest.mark.advisory
def test_handles_timeout(model_name):
    """Verify a very short timeout raises the expected exception"""
    with pytest.raises(subprocess.TimeoutExpired):
        subprocess.run(['ollama', 'run', model_name, "Write a 2000 word essay"],
                        capture_output=True, text=True, timeout=0.1)

@pytest.mark.critical
def test_partial_failure_recovery():
    """A single failing check should not crash the whole test process"""
    try:
        subprocess.run(['ollama', 'run', 'nonexistent:model', 'test'],
                        capture_output=True, text=True, timeout=10)
    except Exception:
        pass
    result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
    assert result.returncode == 0, "System did not recover after prior failure"

@pytest.mark.advisory
def test_error_messages_helpful():
    """Error output should contain actionable information"""
    result = subprocess.run(['ollama', 'run', 'nonexistent:model', 'test'],
                             capture_output=True, text=True, timeout=15)
    assert len(result.stderr.strip()) > 0, "Error message was empty"
