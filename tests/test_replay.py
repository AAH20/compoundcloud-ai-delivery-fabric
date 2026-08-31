import unittest

from compoundcloud.loop import evaluate_promotion
from compoundcloud.replay import ReplayPolicy, Transaction, replay


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.transactions = [
            Transaction("one", 100, 0.1, True), Transaction("two", 50, 0.9, True),
            Transaction("three", 70, 0.1, False), Transaction("one", 100, 0.1, True),
        ]

    def test_idempotency_and_business_gates(self):
        report = replay(self.transactions, ReplayPolicy(), {})
        self.assertEqual(report["summary"]["committed"], 1)
        self.assertEqual(report["summary"]["rejected"], 2)
        self.assertTrue(any(e["status"] == "duplicate_suppressed" for e in report["events"]))

    def test_transient_failure_recovers(self):
        report = replay([self.transactions[0]], ReplayPolicy(), {"ai_inference": 1})
        self.assertEqual(report["summary"]["recovered_failures"], 1)
        self.assertEqual(report["summary"]["committed"], 1)
        self.assertTrue(report["recovery"]["passed"])

    def test_retry_exhaustion_fails_rpo_gate(self):
        report = replay([self.transactions[0]], ReplayPolicy(retry_limit=1), {"event_commit": 2})
        self.assertEqual(report["summary"]["committed"], 0)
        self.assertEqual(report["recovery"]["observed_rpo_events"], 1)
        self.assertFalse(report["recovery"]["passed"])

    def test_loop_blocks_regression(self):
        baseline = replay([self.transactions[0]], ReplayPolicy(), {})
        candidate = replay([Transaction("one", 90, 0.95, True)], ReplayPolicy(), {})
        decision = evaluate_promotion(baseline, candidate)
        self.assertEqual(decision["decision"], "hold")
        self.assertFalse(decision["gates"]["committed_not_regressed"])


if __name__ == "__main__":
    unittest.main()
