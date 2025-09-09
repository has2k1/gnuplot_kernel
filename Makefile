.PHONY: clean-pyc clean-build docs clean
BROWSER := python -mwebbrowser

# NOTE: Take care not to use tabs in any programming flow outside the
# make target

# Use uv (if it is installed) to run all python related commands,
# and prefere the active environment over .venv in a parent folder
ifeq ($(OS),Windows_NT)
  HAS_UV := $(if $(shell where uv 2>NUL),true,false)
else
  HAS_UV := $(if $(shell command -v uv 2>/dev/null),true,false)
endif

ifeq ($(HAS_UV),true)
  PYTHON ?= uv run --active python
  PIP ?= uv pip
  UVRUN ?= uv run --active
else
  PYTHON ?= python
  PIP ?= pip
  UVRUN ?=
endif

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "release - package and upload a release"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"
	@echo "develop - install the package in development mode"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	find . -name '*.egg-info' -exec rm -fr {} +

clean-cache:
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	$(UVRUN) coverage erase
	rm -f coverage.xml
	rm -f .coverage
	rm -fr htmlcov/

format:
	$(UVRUN) ruff format --check .

format-fix:
	$(UVRUN) ruff format .

lint:
	$(UVRUN) ruff check .

lint-fix:
	$(UVRUN) ruff check --fix .

fix: format-fix lint-fix

test: clean-test
	$(UVRUN) pytest

coverage:
	$(UVRUN) coverage report -m
	$(UVRUN) coverage html
	$(BROWSER) htmlcov/index.html

dist: clean-build
	$(PYTHON) -m build
	ls -l dist

release-major:
	@$(PYTHON) ./tools/release-checklist.py major

release-minor:
	@$(PYTHON) ./tools/release-checklist.py minor

release-patch:
	@$(PYTHON) ./tools/release-checklist.py patch

install: clean
	$(PIP) install ".[extra]"

develop: clean-cache
	$(PIP) install -e ".[dev]"
