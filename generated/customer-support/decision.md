# Architecture decision: B2B customer-support resolution copilot

**Selected:** `gcp-global-balanced`  
**Production ready:** `True`  
**Decision basis:** highest feasible revenue-adjusted architecture score

| Candidate | SLO | Monthly cost | Gross profit | Margin | p95 ms | Score |
|---|---:|---:|---:|---:|---:|---:|
| gcp-global-balanced | PASS | $28,448.35 | $187,443.65 | 86.8% | 1320 | 92.27 |
| azure-serverless-balanced | PASS | $31,163.90 | $184,728.10 | 85.6% | 1450 | 91.90 |
| aws-serverless-throughput | PASS | $33,034.72 | $182,857.28 | 84.7% | 1380 | 91.31 |
| azure-premium-low-latency | FAIL | $121,113.90 | $94,864.50 | 43.9% | 720 | 44.16 |
| onprem-gpu-sovereign | FAIL | $12,702.75 | $203,081.25 | 94.1% | 980 | 35.34 |

## Decision contract

This report is a reproducible estimate, not a cloud-provider quote. Run the benchmark harness with representative traffic, replace catalog assumptions with contracted pricing, and require measured SLO evidence before production promotion.
