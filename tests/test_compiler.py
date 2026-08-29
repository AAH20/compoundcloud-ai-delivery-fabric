import json
import tempfile
import unittest
from pathlib import Path

from compoundcloud.catalog import default_catalog
from compoundcloud.compiler import compile_workload, evaluate
from compoundcloud.models import Workload
from compoundcloud.render import write_artifacts


def sample(**overrides):
    raw = {
        "name": "test", "monthly_requests": 1_000_000,
        "average_input_tokens": 1000, "average_output_tokens": 250,
        "revenue_per_successful_request": 0.02, "quality_target": 0.90,
        "p95_latency_target_ms": 1600, "availability_target": 0.999,
        "data_residency": ["eastus2", "us-east-1", "us-central1"],
    }
    raw.update(overrides)
    return Workload.from_dict(raw)


class CompilerTests(unittest.TestCase):
    def test_rejects_invalid_workload(self):
        with self.assertRaises(ValueError):
            sample(quality_target=1.2)

    def test_cost_breakdown_reconciles(self):
        result = evaluate(sample(), default_catalog()[0])
        self.assertAlmostEqual(result.monthly_cloud_cost, sum(result.cost_breakdown.values()), places=2)

    def test_latency_violation_is_explicit(self):
        result = evaluate(sample(p95_latency_target_ms=500), default_catalog()[0])
        self.assertIn("p95_latency_target_ms", result.violations)
        self.assertFalse(result.feasible)

    def test_residency_violation_is_explicit(self):
        result = evaluate(sample(data_residency=["westeurope"]), default_catalog()[0])
        self.assertIn("data_residency", result.violations)

    def test_compiler_prefers_feasible_candidate(self):
        report = compile_workload(sample())
        selected = next(x for x in report["evaluations"] if x["candidate"]["id"] == report["decision"]["selected_candidate"])
        self.assertTrue(selected["feasible"])

    def test_artifacts_are_machine_and_human_readable(self):
        report = compile_workload(sample())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            write_artifacts(report, path)
            self.assertEqual(json.loads((path / "decision.json").read_text())["schema_version"], "1.0")
            self.assertIn("Architecture decision", (path / "decision.md").read_text())
            self.assertIn("architecture_decision", (path / "main.tf").read_text())


if __name__ == "__main__":
    unittest.main()

