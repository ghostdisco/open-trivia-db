.PHONY: build test clean

PYTHON ?= python3
DIST   := dist

build:
	$(PYTHON) -m pip install --quiet build
	$(PYTHON) -m build --outdir $(DIST)
	@echo "Artefacts written to $(DIST)/"

test:
	PYTHONPATH=$(CURDIR) $(PYTHON) tests/test_sanity.py

clean:
	rm -rf $(DIST) build *.egg-info opentriviadb/__pycache__ __pycache__
