from __future__ import annotations

import argparse
import json
from pathlib import Path

from .compiler import compile_workload
from .models import Workload
from .render import write_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(prog="compoundcloud")
    parser.add_argument("workload", type=Path, help="JSON workload contract")
    parser.add_argument("--output", type=Path, default=Path("generated/latest"))
    args = parser.parse_args()
    workload = Workload.from_dict(json.loads(args.workload.read_text()))
    report = compile_workload(workload)
    write_artifacts(report, args.output)
    print(json.dumps(report["decision"], indent=2))


if __name__ == "__main__":
    main()

