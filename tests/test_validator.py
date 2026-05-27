from pathlib import Path

from data_quality_contracts_lab.contracts import DatasetContract, FieldRule, load_contract
from data_quality_contracts_lab.report import render_report
from data_quality_contracts_lab.validator import quarantine_failed_rows, validate_references, validate_rows


def test_load_contract_reads_fields() -> None:
    contract = load_contract(Path("contracts/invoices.json"))

    assert contract.dataset == "invoices"
    assert contract.primary_key == ["invoice_id"]


def test_validate_rows_passes_valid_dataset() -> None:
    contract = DatasetContract(
        dataset="customers",
        primary_key=["customer_id"],
        fields=[
            FieldRule("customer_id", "string"),
            FieldRule("created_at", "date"),
        ],
    )

    result = validate_rows(contract, [{"customer_id": "C001", "created_at": "2026-01-01"}])

    assert result.passed


def test_validate_rows_reports_missing_and_duplicate_values() -> None:
    contract = DatasetContract(
        dataset="customers",
        primary_key=["customer_id"],
        fields=[
            FieldRule("customer_id", "string"),
            FieldRule("created_at", "date"),
        ],
    )

    result = validate_rows(
        contract,
        [
            {"customer_id": "C001", "created_at": "2026-01-01"},
            {"customer_id": "C001", "created_at": ""},
        ],
    )

    assert not result.passed
    assert len(result.issues) == 2


def test_quarantine_failed_rows_writes_only_failed_rows(tmp_path: Path) -> None:
    contract = DatasetContract(
        dataset="customers",
        primary_key=["customer_id"],
        fields=[FieldRule("customer_id", "string"), FieldRule("created_at", "date")],
    )
    rows = [{"customer_id": "C001", "created_at": ""}]
    result = validate_rows(contract, rows)

    output_path = quarantine_failed_rows(contract, rows, result.issues, tmp_path)

    assert output_path is not None
    assert "C001" in output_path.read_text(encoding="utf-8")


def test_render_report_marks_failures() -> None:
    contract = DatasetContract(
        dataset="customers",
        primary_key=["customer_id"],
        fields=[FieldRule("customer_id", "string")],
    )
    result = validate_rows(contract, [{"customer_id": ""}])

    report = render_report([result])

    assert "status: fail" in report
    assert "required value is missing" in report


def test_validate_references_reports_missing_target() -> None:
    contract = DatasetContract(
        dataset="invoices",
        primary_key=["invoice_id"],
        fields=[FieldRule("invoice_id", "string"), FieldRule("customer_id", "string")],
        references={"customer_id": "customers.customer_id"},
    )

    issues = validate_references(
        contract,
        [{"invoice_id": "I001", "customer_id": "C999"}],
        {"customers": [{"customer_id": "C001"}]},
    )

    assert issues[0].message == "missing reference: customers.customer_id"
