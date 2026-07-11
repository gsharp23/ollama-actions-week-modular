# Team Testing Notes

## Critical vs Advisory
Critical tests: ollama installed, service responding, model available,
model loads, AI response time under 30s, response not empty, and recovery
after a failure. These block the workflow because if any of them fail,
the AI functionality genuinely doesn't work.

Advisory tests: cache directory exists, response time under the 15s
optimal target, cache improves performance on the second call, and the
reliability edge cases (invalid model, empty prompt, timeout, helpful
error messages). These are noisy or environment-dependent -- runner
load and cache state vary run to run -- so they warn without blocking.

## Performance baseline choices
30s max / 15s optimal for a single query on a small model (1b params)
on a GitHub-hosted runner felt like a reasonable ceiling based on the
lab's suggested starting point. Actual observed times (16s and 23s)
stayed under 30s on both runs, so the threshold held up in practice
without needing adjustment yet.

## What I learned about testing AI workflows vs traditional software
Traditional software tests are deterministic -- same input, same output,
every time. AI workflow tests have to tolerate timing variance and
non-deterministic model output, so the critical/advisory split matters
more here than in typical unit testing. You end up testing infrastructure
health (is the service up, is the model there) more than exact output
correctness, since the model's actual response text isn't something you
can assert on reliably.
