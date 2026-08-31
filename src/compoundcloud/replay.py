from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


STAGES = ("payment_fraud", "order_orchestration", "inventory_twin", "ai_inference", "event_commit")


@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    revenue: float
    fraud_score: float
    inventory_available: bool
    input_tokens: int = 800
    output_tokens: int = 180


@dataclass(frozen=True)
class ReplayPolicy:
    fraud_threshold: float = 0.82
    retry_limit: int = 2
    rto_target_ms: int = 250
    rpo_target_events: int = 0
    cost_per_stage: float = 0.00012
    inference_cost_per_1k_tokens: float = 0.0018


def load_scenario(path: Path) -> tuple[list[Transaction], ReplayPolicy, dict[str, int]]:
    raw = json.loads(path.read_text())
    transactions = [Transaction(**item) for item in raw["transactions"]]
    return transactions, ReplayPolicy(**raw.get("policy", {})), raw.get("failures", {})


def replay(transactions: list[Transaction], policy: ReplayPolicy, failures: dict[str, int]) -> dict[str, Any]:
    started = time.perf_counter()
    events: list[dict[str, Any]] = []
    committed: set[str] = set()
    injected = dict(failures)
    recovered = 0
    rejected = 0
    gross_revenue = 0.0
    variable_cost = 0.0
    lost_events = 0

    for tx in transactions:
        if tx.transaction_id in committed:
            events.append({"transaction_id": tx.transaction_id, "stage": "deduplication", "status": "duplicate_suppressed"})
            continue
        outcome = "committed"
        for stage in STAGES:
            attempts = 0
            while injected.get(stage, 0) > 0:
                injected[stage] -= 1
                attempts += 1
                events.append({"transaction_id": tx.transaction_id, "stage": stage, "status": "injected_failure", "attempt": attempts})
                if attempts > policy.retry_limit:
                    outcome = "retry_exhausted"
                    break
                recovered += 1
            if outcome != "committed":
                break
            variable_cost += policy.cost_per_stage
            if stage == "payment_fraud" and tx.fraud_score >= policy.fraud_threshold:
                outcome = "fraud_rejected"
            elif stage == "inventory_twin" and not tx.inventory_available:
                outcome = "inventory_rejected"
            elif stage == "ai_inference":
                variable_cost += (tx.input_tokens + tx.output_tokens) / 1000 * policy.inference_cost_per_1k_tokens
            events.append({"transaction_id": tx.transaction_id, "stage": stage, "status": outcome if outcome != "committed" else "passed"})
            if outcome != "committed":
                break
        if outcome == "committed":
            committed.add(tx.transaction_id)
            gross_revenue += tx.revenue
        else:
            rejected += 1
            if outcome == "retry_exhausted":
                lost_events += 1

    elapsed_ms = (time.perf_counter() - started) * 1000
    digest = hashlib.sha256(json.dumps(events, sort_keys=True).encode()).hexdigest()
    return {
        "schema_version": "1.0",
        "scope": "deterministic in-process transaction replay; not a live cloud benchmark",
        "summary": {
            "submitted": len(transactions), "committed": len(committed), "rejected": rejected,
            "recovered_failures": recovered, "elapsed_ms": round(elapsed_ms, 3),
            "gross_revenue": round(gross_revenue, 2), "variable_cost": round(variable_cost, 6),
            "contribution_profit": round(gross_revenue - variable_cost, 6),
            "event_digest_sha256": digest,
        },
        "recovery": {
            "observed_rto_ms": round(elapsed_ms, 3), "observed_rpo_events": lost_events,
            "rto_target_ms": policy.rto_target_ms, "rpo_target_events": policy.rpo_target_events,
            "passed": elapsed_ms <= policy.rto_target_ms and lost_events <= policy.rpo_target_events,
        },
        "events": events,
    }


def write_replay(report: dict[str, Any], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "replay.json").write_text(json.dumps(report, indent=2) + "\n")
    s, r = report["summary"], report["recovery"]
    lines = [
        "# Enterprise AI transaction replay", "", f"> {report['scope']}", "",
        "## Outcome", "", "| Metric | Result |", "|---|---:|",
        f"| Submitted | {s['submitted']} |", f"| Committed | {s['committed']} |",
        f"| Rejected | {s['rejected']} |", f"| Recovered failures | {s['recovered_failures']} |",
        f"| Gross revenue | ${s['gross_revenue']:.2f} |", f"| Variable cost | ${s['variable_cost']:.6f} |",
        f"| Contribution profit | ${s['contribution_profit']:.6f} |", "",
        "## Recovery gate", "", f"**{'PASS' if r['passed'] else 'FAIL'}** — RTO {r['observed_rto_ms']} ms / {r['rto_target_ms']} ms; RPO {r['observed_rpo_events']} / {r['rpo_target_events']} events.", "",
        f"Event digest: `{s['event_digest_sha256']}`", "",
    ]
    (output / "replay.md").write_text("\n".join(lines))
