from __future__ import annotations

from typing import Any


def evaluate_promotion(baseline: dict[str, Any], candidate: dict[str, Any], max_cost_increase: float = 0.05) -> dict[str, Any]:
    """Gate a candidate using revenue, recovery, success, and cost—not model preference."""
    b, c = baseline["summary"], candidate["summary"]
    gates = {
        "recovery_passed": bool(candidate["recovery"]["passed"]),
        "committed_not_regressed": c["committed"] >= b["committed"],
        "contribution_not_regressed": c["contribution_profit"] >= b["contribution_profit"],
        "cost_within_tolerance": c["variable_cost"] <= b["variable_cost"] * (1 + max_cost_increase),
    }
    return {
        "schema_version": "1.0", "decision": "promote" if all(gates.values()) else "hold",
        "gates": gates, "policy": {"max_cost_increase": max_cost_increase},
        "explanation": "all business, reliability, and cost gates passed" if all(gates.values()) else "one or more measurable gates failed",
    }
