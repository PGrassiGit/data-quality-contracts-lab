from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from data_quality_contracts_lab.contracts import DatasetContract, cast_value


@dataclass(frozen=True)
class ValidationIssue:
    dataset: str
    row_number: int
    field: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    dataset: str
    rows_read: int
    issues: list[ValidationIssue]

    @property
    def passed(self) -> bool:
        return not self.issues


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def validate_rows(contract: DatasetContract, rows: list[dict[str, str]]) -> ValidationResult:
    issues: list[ValidationIssue] = []
    seen_keys: set[tuple[str, ...]] = set()

    for index, row in enumerate(rows, start=2):
        for field in contract.fields:
            value = row.get(field.name, "")
            if field.required and value == "":
                issues.append(ValidationIssue(contract.dataset, index, field.name, "required value is missing"))
                continue
            if value != "":
                try:
                    cast_value(value, field.type)
                except ValueError:
                    issues.append(ValidationIssue(contract.dataset, index, field.name, f"expected {field.type}"))

        if contract.primary_key:
            key = tuple(row.get(field, "") for field in contract.primary_key)
            if key in seen_keys:
                issues.append(ValidationIssue(contract.dataset, index, ",".join(contract.primary_key), "duplicate key"))
            seen_keys.add(key)

    return ValidationResult(contract.dataset, len(rows), issues)


def validate_references(
    contract: DatasetContract,
    rows: list[dict[str, str]],
    datasets: dict[str, list[dict[str, str]]],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not contract.references:
        return issues

    for field, target in contract.references.items():
        target_dataset, target_field = target.split(".", maxsplit=1)
        allowed_values = {row.get(target_field, "") for row in datasets.get(target_dataset, [])}
        for index, row in enumerate(rows, start=2):
            value = row.get(field, "")
            if value and value not in allowed_values:
                issues.append(
                    ValidationIssue(
                        dataset=contract.dataset,
                        row_number=index,
                        field=field,
                        message=f"missing reference: {target}",
                    )
                )
    return issues


def validate_dataset(contract: DatasetContract, data_dir: Path) -> ValidationResult:
    rows = read_csv(data_dir / f"{contract.dataset}.csv")
    return validate_rows(contract, rows)


def quarantine_failed_rows(contract: DatasetContract, rows: list[dict[str, str]], issues: list[ValidationIssue], output_dir: Path) -> Path | None:
    failed_rows = {issue.row_number for issue in issues}
    if not failed_rows:
        return None

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{contract.dataset}_failed.csv"
    fieldnames = rows[0].keys() if rows else [field.name for field in contract.fields]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for index, row in enumerate(rows, start=2):
            if index in failed_rows:
                writer.writerow(row)

    return output_path
