# AI Prompt Notes

## Prompts I used
- Prompt 1: "Rate documentation quality Excellent/Good/Needs Improvement/Poor" (README analysis, Day 2 challenge)
- Prompt 2: "Explain CI in one sentence" / "Explain automation in one sentence" (parameterized pytest inputs)
- Prompt 3: "What is continuous integration?" (performance benchmarking prompt)

## What AI helped with
- Generated the caching pattern (binary cache + model cache with cache-hit
  outputs) and the pytest fixture/test structure across conftest.py,
  test_ollama_service.py, test_performance.py, and test_reliability.py.
- Accepted the critical/advisory marker split as written.
- Adjusted timeout values and threshold numbers to match my own runner's
  actual timing rather than blindly trusting the suggested 30s/15s defaults.

## My explanation of the workflow
- The binary cache saves the installed Ollama executable and its runtime
  files (like llama-server) so the install step can skip curl/install.sh
  on later runs.
- The model cache saves the downloaded llama3.2:1b model files under
  OLLAMA_MODELS so ollama pull can be skipped on a cache hit.
- The pytest step validates that Ollama installed correctly, the service
  responds, the model is available and loads, response times stay under
  threshold, and the system degrades gracefully on failure (bad model name,
  empty prompt, timeout).
- The workflow uploads test-results.xml, coverage.xml, and
  performance-report.txt as an artifact named with the run number.
- If the optional AI check fails, continue-on-error keeps the job running
  so critical tests and artifact upload still complete.

## Verification
- Two consecutive `gh run list` and `gh run view --log` checks proved the
  workflow worked: run 1 showed "Cache hit: false" and a fresh install;
  run 2 showed "Cache hit: true" for both binary and model caches, and
  total workflow time dropped from 2m15s to 1m18s.
- I can explain the caching logic, the critical vs advisory test split, and
  the artifact upload steps without looking at AI output -- those are
  straightforward file/cache mechanics I traced through the YAML myself.
