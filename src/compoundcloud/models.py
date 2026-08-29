from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Workload:
    name: str
    monthly_requests: int
    average_input_tokens: int
    average_output_tokens: int
    revenue_per_successful_request: float
    quality_target: float
    p95_latency_target_ms: int
    availability_target: float
    data_residency: list[str]
    peak_to_average_ratio: float = 3.0
    retrieval: bool = True
    regulated: bool = False
    max_monthly_cloud_cost: float | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Workload":
        required = {
            "name", "monthly_requests", "average_input_tokens",
            "average_output_tokens", "revenue_per_successful_request",
            "quality_target", "p95_latency_target_ms", "availability_target",
            "data_residency",
        }
        missing = required - raw.keys()
        if missing:
            raise ValueError(f"missing required fields: {', '.join(sorted(missing))}")
        workload = cls(**raw)
        if workload.monthly_requests <= 0 or workload.revenue_per_successful_request < 0:
            raise ValueError("volume must be positive and revenue cannot be negative")
        if not 0 < workload.quality_target <= 1 or not 0 < workload.availability_target <= 1:
            raise ValueError("quality and availability targets must be in (0, 1]")
        return workload


@dataclass(frozen=True)
class ArchitectureCandidate:
    id: str
    cloud: str
    region: str
    compute: str
    model: str
    model_class: str
    topology: str
    retrieval: str
    unit_input_per_million: float
    unit_output_per_million: float
    fixed_monthly_cost: float
    variable_platform_cost_per_request: float
    expected_quality: float
    expected_p95_ms: int
    expected_availability: float
    max_sustained_rps: float
    egress_cost_per_gb: float


@dataclass(frozen=True)
class Evaluation:
    candidate: ArchitectureCandidate
    feasible: bool
    violations: list[str]
    monthly_cloud_cost: float
    monthly_revenue: float
    monthly_gross_profit: float
    gross_margin: float
    cost_per_request: float
    break_even_requests: int
    peak_required_rps: float
    capacity_headroom: float
    score: float
    cost_breakdown: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["candidate"] = asdict(self.candidate)
        return value

