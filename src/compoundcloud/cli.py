from __future__ import annotations

import argparse
import json
from pathlib import Path

from .compiler import compile_workload
from .models import Workload
from .render import write_artifacts
from .replay import load_scenario, replay, write_replay


def main() -> None:
    parser = argparse.ArgumentParser(prog="compoundcloud")
    parser.add_argument("workload", type=Path, help="JSON workload or transaction scenario")
    parser.add_argument("--output", type=Path, default=Path("generated/latest"))
    parser.add_argument("--replay", action="store_true", help="run an enterprise transaction replay")
    args = parser.parse_args()
    if args.replay:
        transactions, policy, failures = load_scenario(args.workload)
        report = replay(transactions, policy, failures)
        write_replay(report, args.output)
        print(json.dumps({"summary": report["summary"], "recovery": report["recovery"]}, indent=2))
        return
    workload = Workload.from_dict(json.loads(args.workload.read_text()))
    report = compile_workload(workload)
    write_artifacts(report, args.output)
    print(json.dumps(report["decision"], indent=2))


if __name__ == "__main__":
    main()
