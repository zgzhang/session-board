.PHONY: index test publish check

PYTHON ?= $(shell command -v python3 2>/dev/null || command -v python || echo python3)
export PYTHONPATH := src:tools

index:
	$(PYTHON) tools/index_export_folder.py

test: index
	@if $(PYTHON) -c "import pytest" >/dev/null 2>&1; then \
		$(PYTHON) -m pytest -q; \
	else \
		$(PYTHON) tools/run_tests.py; \
	fi

publish:
	$(PYTHON) tools/publish_session.py

check: test publish
