from __future__ import annotations

import argparse
from pathlib import Path

from data_quality_contracts_lab.contracts import load_contracts
from data_quality_contracts_lab.report import write_report
from data_quality_contracts_lab.validator import quarantine_failed_rows, read_csv, validate_dataset


def run(contracts_dir: Path, data_dir: Path, report_path: Path, quarantine_dir: Path) -> int:
    contracts = load_contracts(contracts_dir)
    results = []
    for contract in contracts:
        rows = read_csv(data_dir / f"{contract.dataset}.csv")
        result = validate_dataset(contract, data_dir)
        results.append(result)
        quarantine_failed_rows(contract, rows, result.issues, quarantine_dir)

    write_report(results, report_path)
    return 1 if any(not result.passed for result in results) else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate datasets against local contracts")
    parser.add_argument("--contracts", default="contracts")
    parser.add_argument("--data", default="data/sample")
    parser.add_argument("--report", default="reports/validation_report.md")
    parser.add_argument("--quarantine", default="quarantine")
    args = parser.parse_args()

    raise SystemExit(
        run(
            contracts_dir=Path(args.contracts),
            data_dir=Path(args.data),
            report_path=Path(args.report),
            quarantine_dir=Path(args.quarantine),
        )
    )


if __name__ == "__main__":
    main()
