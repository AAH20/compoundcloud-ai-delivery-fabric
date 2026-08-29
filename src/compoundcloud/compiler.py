from __future__ import annotations

import math
from dataclasses import asdict
from typing import Iterable

from .catalog import default_catalog
from .models import ArchitectureCandidate, Evaluation, Workload

SECONDS_PER_MONTH = 30 * 24 * 60 * 60


def evaluate(workload: Workload, candidate: ArchitectureCandidate) -> Evaluation:
    model_cost = workload.monthly_requests * (
        workload.average_input_tokens * candidate.unit_input_per_million
        + workload.average_output_tokens * candidate.unit_output_per_million
    ) / 1_000_000
    platform_variable = workload.monthly_requests * candidate.variable_platform_cost_per_request
    # Payload assumption is deliberately explicit and deterministic: 24 KiB/request.
    egress_gb = workload.monthly_requests * 24 / (1024 * 1024)
    network_egress = egress_gb * candidate.egress_cost_per_gb
    retrieval_cost = workload.monthly_requests * 0.00022 if workload.retrieval else 0
    cloud_cost = candidate.fixed_monthly_cost + model_cost + platform_variable + network_egress + retrieval_cost

    peak_rps = workload.monthly_requests / SECONDS_PER_MONTH * workload.peak_to_average_ratio
    headroom = candidate.max_sustained_rps / peak_rps if peak_rps else math.inf
    successful_requests = workload.monthly_requests * candidate.expected_availability
    revenue = successful_requests * workload.revenue_per_successful_request
    profit = revenue - cloud_cost
    margin = profit / revenue if revenue else -math.inf
    variable_cost = (model_cost + platform_variable + network_egress + retrieval_cost) / workload.monthly_requests
    contribution = workload.revenue_per_successful_request * candidate.expected_availability - variable_cost
    break_even = math.ceil(candidate.fixed_monthly_cost / contribution) if contribution > 0 else -1

    violations: list[str] = []
    if candidate.expected_quality < workload.quality_target:
        violations.append("quality_target")
    if candidate.expected_p95_ms > workload.p95_latency_target_ms:
        violations.append("p95_latency_target_ms")
    if candidate.expected_availability < workload.availability_target:
        violations.append("availability_target")
    if headroom < 1.25:
        violations.append("capacity_headroom")
    if workload.max_monthly_cloud_cost is not None and cloud_cost > workload.max_monthly_cloud_cost:
        violations.append("max_monthly_cloud_cost")
    if candidate.region not in workload.data_residency and candidate.cloud != "on-premises":
        violations.append("data_residency")

    # Profitability dominates; quality, latency, resilience and headroom prevent cheap-but-bad winning.
    margin_component = max(-1, min(1, margin)) * 45
    quality_component = candidate.expected_quality * 20
    latency_component = min(1, workload.p95_latency_target_ms / candidate.expected_p95_ms) * 15
    resilience_component = candidate.expected_availability * 10
    capacity_component = min(1, headroom / 2) * 10
    score = margin_component + quality_component + latency_component + resilience_component + capacity_component
    score -= len(violations) * 30

    return Evaluation(
        candidate=candidate, feasible=not violations, violations=violations,
        monthly_cloud_cost=round(cloud_cost, 2), monthly_revenue=round(revenue, 2),
        monthly_gross_profit=round(profit, 2), gross_margin=round(margin, 4),
        cost_per_request=round(cloud_cost / workload.monthly_requests, 6),
        break_even_requests=break_even, peak_required_rps=round(peak_rps, 3),
        capacity_headroom=round(headroom, 2), score=round(score, 2),
        cost_breakdown={
            "fixed_platform": round(candidate.fixed_monthly_cost, 2),
            "model_inference": round(model_cost, 2),
            "variable_platform": round(platform_variable, 2),
            "retrieval": round(retrieval_cost, 2),
            "network_egress": round(network_egress, 2),
        },
    )


def compile_workload(
    workload: Workload, candidates: Iterable[ArchitectureCandidate] | None = None
) -> dict:
    evaluations = [evaluate(workload, c) for c in (candidates or default_catalog())]
    evaluations.sort(key=lambda item: (item.feasible, item.score), reverse=True)
    winner = evaluations[0]
    return {
        "schema_version": "1.0",
        "workload": asdict(workload),
        "decision": {
            "selected_candidate": winner.candidate.id,
            "production_ready": winner.feasible,
            "reason": "highest feasible revenue-adjusted architecture score" if winner.feasible else "no candidate satisfies every SLO; selected least-bad candidate",
        },
        "evaluations": [item.to_dict() for item in evaluations],
        "assumptions": {
            "month_days": 30,
            "payload_kib_per_request": 24,
            "minimum_capacity_headroom": 1.25,
            "pricing": "versioned reference catalog; validate against provider quotes before commitment",
        },
    }

