from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FieldRule:
    name: str
    type: str
    required: bool = True


@dataclass(frozen=True)
class DatasetContract:
    dataset: str
    primary_key: list[str]
    fields: list[FieldRule]
    freshness_field: str | None = None
    references: dict[str, str] | None = None


def load_contract(path: Path) -> DatasetContract:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return DatasetContract(
        dataset=payload["dataset"],
        primary_key=list(payload.get("primary_key", [])),
        fields=[FieldRule(**field) for field in payload["fields"]],
        freshness_field=payload.get("freshness_field"),
        references=payload.get("references"),
    )


def load_contracts(directory: Path) -> list[DatasetContract]:
    return [load_contract(path) for path in sorted(directory.glob("*.json"))]


def cast_value(value: str, expected_type: str) -> Any:
    if expected_type == "string":
        return value
    if expected_type == "integer":
        return int(value)
    if expected_type == "number":
        return float(value)
    if expected_type == "date":
        parts = value.split("-")
        if len(parts) != 3:
            raise ValueError("invalid date")
        return value
    raise ValueError(f"unsupported type: {expected_type}")
