.PHONY: test lint

PYTHON_MODULES := reposcore

VENV := .venv
VIRTUALENV := -m venv

DEFAULT_PYTHON := $(shell which python3)
PYTHON := env PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest

VERSION := $(shell grep '__version__' reposcore/__init__.py |cut -d'"' -f 2)

version:
	@echo $(VERSION)

venv:
	test -d $(VENV) || $(DEFAULT_PYTHON) $(VIRTUALENV) $(VENV)

requirements: venv
	$(PIP) install -r requirements.txt -r requirements-dev.txt

test: requirements
	$(PYTEST) tests

