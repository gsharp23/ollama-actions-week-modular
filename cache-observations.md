# Cache Timing Observations

## First run
- Binary cache hit: false
- Model cache hit: false (not directly logged, but install/pull ran from scratch)
- Install Ollama step time: full fresh install (curl install.sh)
- AI Response Time: 16 seconds
- Total workflow time: 2m15s

## Second run
- Binary cache hit: true (ollama-install-Linux-v2)
- Model cache hit: true (ollama-models-Linux-llama3.2-1b-v1)
- Install Ollama step time: skipped install script, restored from cache
- AI Response Time: 23 seconds
- Total workflow time: 1m18s

## What changed?
- Total workflow time dropped from 2m15s to 1m18s (~42% faster) once both
  caches hit. The install step went from downloading and installing Ollama
  fresh to a simple file copy from the cache.
- Both binary caching and model caching contributed to the speedup, since
  both caches showed "Cache hit for:" on the second run.
- The AI Response Time itself (16s vs 23s) didn't improve, which makes sense
  since the model inference speed isn't affected by caching -- caching only
  avoids re-downloading/reinstalling. This was the interesting part: AI
  response time is noisy and unrelated to cache state, while setup time is
  the metric caching actually improves.
