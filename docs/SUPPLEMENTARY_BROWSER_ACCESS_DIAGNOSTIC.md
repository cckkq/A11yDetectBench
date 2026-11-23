# Supplementary Browser-Access Diagnostic

This supplementary note reports a Keyboard-only browser-access diagnostic that runs the same task definitions and evaluation rules with Codex+CLI instead of browser-use. Codex+CLI uses a coding shell and Playwright/DOM probes to obtain page and interaction observations, so its action interface and step budget are not matched to the standard browser-use condition. The table is therefore a diagnostic, not a matched baseline or an overall model ranking. Metrics use the same definitions as the main results: Selected-L1 Hit and No-issue verdict are run-level rates, and Issue-list values are element-level repeat-macro recall/precision.

| Condition | Model | Steps | Selected-L1 Hit | No-issue Accuracy | Issue-list L2 Recall | Issue-list L2 Precision | Issue-list L3 Recall | Issue-list L3 Precision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| browser-use | GPT-5.2 | 25 | 0.82 | 0.93 | 0.15 | 0.55 | 0.10 | 0.51 |
| browser-use | GPT-5.5 | 25 | 0.85 | 0.92 | 0.44 | 0.35 | 0.38 | 0.31 |
| Codex+CLI | GPT-5.2 | n/a | 0.80 | 0.92 | 0.19 | 0.40 | 0.17 | 0.45 |
| Codex+CLI | GPT-5.5 | n/a | 0.82 | 0.99 | 0.49 | 0.34 | 0.56 | 0.35 |

The Codex+CLI rows are broadly similar to the standard Keyboard rows rather than changing the qualitative conclusion. GPT-5.5 with Codex+CLI has higher Issue-list L3 recall than browser-use, but precision remains low. These results support treating A11yDetectBench as a report-evaluation benchmark that can also diagnose different browser-access conditions, while keeping the main conclusions tied to the standard browser-use setting.
