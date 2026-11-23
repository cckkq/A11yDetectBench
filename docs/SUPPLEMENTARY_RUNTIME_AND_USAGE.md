# Supplementary Runtime and Usage Summary

This note summarizes runtime and language-model usage for representative A11yDetectBench runs. Token totals and invocation counts are read from each run's `usage.json`; runtime is measured from the first to the last recorded step in `history.json`. Runtime is reported as the median per completed run.

| Experiment group | Runs with usage | Runs with history | Total tokens | Model calls | Median runtime (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Keyboard page-evidence pack | 45 | 45 | 19,845,202 | 970 | 2,388.96 |
| Focus page-evidence pack | 39 | 39 | 18,688,126 | 824 | 3,179.95 |
| Focus, GPT-5.2 formal condition | 180 | 178 | 60,804,003 | 3,049 | 1,883.40 |
| Focus, GPT-5.5 formal condition | 180 | 180 | 53,178,466 | 2,733 | 826.87 |
| Focus, Kimi-K2.6 formal condition | 180 | 174 | 64,486,172 | 3,418 | 1,988.25 |

`Total tokens` is the recorded total-usage field; the underlying logs also retain prompt and completion counts. `Model calls` is the sum of invocation entries. Runtime is per run and should not be summed to estimate wall-clock experiment duration because runs were executed in parallel. Provider-side monetary cost was not recorded in the submitted logs.
