from __future__ import annotations

import json
from pathlib import Path


def render_markdown(report: dict) -> str:
    workload = report["workload"]
    rows = []
    for item in report["evaluations"]:
        candidate = item["candidate"]
        rows.append(
            f"| {candidate['id']} | {'PASS' if item['feasible'] else 'FAIL'} | "
            f"${item['monthly_cloud_cost']:,.2f} | ${item['monthly_gross_profit']:,.2f} | "
            f"{item['gross_margin']:.1%} | {candidate['expected_p95_ms']} | {item['score']:.2f} |"
        )
    return f"""# Architecture decision: {workload['name']}

**Selected:** `{report['decision']['selected_candidate']}`  
**Production ready:** `{report['decision']['production_ready']}`  
**Decision basis:** {report['decision']['reason']}

| Candidate | SLO | Monthly cost | Gross profit | Margin | p95 ms | Score |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

## Decision contract

This report is a reproducible estimate, not a cloud-provider quote. Run the benchmark harness with representative traffic, replace catalog assumptions with contracted pricing, and require measured SLO evidence before production promotion.
"""


def render_terraform(report: dict) -> str:
    selected = next(e for e in report["evaluations"] if e["candidate"]["id"] == report["decision"]["selected_candidate"])
    c = selected["candidate"]
    return f'''terraform {{
  required_version = ">= 1.6.0"
}}

locals {{
  architecture_decision = {{
    candidate_id          = "{c['id']}"
    cloud                 = "{c['cloud']}"
    region                = "{c['region']}"
    compute               = "{c['compute']}"
    network_topology      = "{c['topology']}"
    estimated_monthly_usd = {selected['monthly_cloud_cost']}
    estimated_margin      = {selected['gross_margin']}
  }}
}}

output "architecture_decision" {{
  value = local.architecture_decision
}}
'''


def write_artifacts(report: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "decision.json").write_text(json.dumps(report, indent=2) + "\n")
    (output_dir / "decision.md").write_text(render_markdown(report))
    (output_dir / "main.tf").write_text(render_terraform(report))

