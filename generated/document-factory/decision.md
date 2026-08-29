# Architecture decision: Sovereign insurance document-processing factory

**Selected:** `azure-premium-low-latency`  
**Production ready:** `True`  
**Decision basis:** highest feasible revenue-adjusted architecture score

| Candidate | SLO | Monthly cost | Gross profit | Margin | p95 ms | Score |
|---|---:|---:|---:|---:|---:|---:|
| azure-premium-low-latency | PASS | $43,707.99 | $316,256.01 | 87.9% | 720 | 93.93 |
| onprem-gpu-sovereign | FAIL | $8,500.34 | $351,139.66 | 97.6% | 980 | 66.93 |
| azure-serverless-balanced | FAIL | $10,142.99 | $349,677.01 | 97.2% | 1450 | 34.54 |
| gcp-global-balanced | FAIL | $9,317.92 | $350,502.08 | 97.4% | 1320 | 5.67 |
| aws-serverless-throughput | FAIL | $10,963.09 | $348,856.91 | 97.0% | 1380 | 4.87 |

## Decision contract

This report is a reproducible estimate, not a cloud-provider quote. Run the benchmark harness with representative traffic, replace catalog assumptions with contracted pricing, and require measured SLO evidence before production promotion.
