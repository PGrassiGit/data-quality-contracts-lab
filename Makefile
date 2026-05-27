.PHONY: test validate

test:
	python -m pytest

validate:
	python -m data_quality_contracts_lab.cli --contracts contracts --data data/sample --report reports/validation_report.md --quarantine quarantine
