import time
import subprocess
import pytest

@pytest.mark.critical
def test_ai_response_time(model_name, sample_prompt):
    """AI queries should complete within the maximum acceptable time"""
    start = time.time()
    result = subprocess.run(['ollama', 'run', model_name, sample_prompt],
                             capture_output=True, text=True, timeout=45)
    duration = time.time() - start
    assert result.returncode == 0, f"Query failed: {result.stderr}"
    assert duration < 30, f"Query took {duration:.1f}s, exceeds 30s threshold"
    print(f"Query completed in {duration:.1f}s")

@pytest.mark.advisory
def test_ai_response_time_warning(model_name, sample_prompt):
    """Warn if query is slower than the optimal 15s threshold"""
    start = time.time()
    subprocess.run(['ollama', 'run', model_name, sample_prompt],
                    capture_output=True, text=True, timeout=45)
    duration = time.time() - start
    assert duration < 15, f"Query took {duration:.1f}s, slower than 15s optimal"

@pytest.mark.critical
def test_model_load_time(model_name):
    """Cold start query must complete within 45s"""
    start = time.time()
    result = subprocess.run(['ollama', 'run', model_name, "Say hello"],
                             capture_output=True, text=True, timeout=60)
    duration = time.time() - start
    assert result.returncode == 0
    assert duration < 45, f"Cold start took {duration:.1f}s, exceeds 45s max"

@pytest.mark.advisory
def test_cache_improves_performance(model_name, sample_prompt):
    """Second query should usually be faster than the first (advisory, noisy signal)"""
    start1 = time.time()
    subprocess.run(['ollama', 'run', model_name, sample_prompt], capture_output=True, text=True, timeout=45)
    first = time.time() - start1

    start2 = time.time()
    subprocess.run(['ollama', 'run', model_name, sample_prompt], capture_output=True, text=True, timeout=45)
    second = time.time() - start2

    print(f"First: {first:.1f}s, Second: {second:.1f}s")
    assert second <= first * 1.5, "Second query unexpectedly much slower"

@pytest.mark.critical
def test_response_not_empty(model_name, sample_prompt):
    """AI response must contain actual content"""
    result = subprocess.run(['ollama', 'run', model_name, sample_prompt],
                             capture_output=True, text=True, timeout=45)
    assert len(result.stdout.strip()) > 0, "AI response was empty"
