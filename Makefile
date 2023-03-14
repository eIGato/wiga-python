SHELL := /bin/bash

SOURCES := $(shell find wiga -name "*.py")
TESTS := $(shell find tests -name "*.py")

.PHONY: setup

setup: | .venv
	.venv/bin/pip install -r requirements-dev.txt

.venv:
	virtualenv -p python310 .venv

.venv/bin/autoflake: setup
.venv/bin/black: setup
.venv/bin/coverage: setup
.venv/bin/flake8: setup
.venv/bin/isort: setup
.venv/bin/mypy: setup
.venv/bin/pytest: setup

## Test

.PHONY: test coverage

test .coverage: $(SOURCES) $(TESTS) | .venv/bin/pytest
	.venv/bin/python -m pytest

coverage: .coverage | .venv/bin/coverage
	.venv/bin/coverage report --rcfile=setup.cfg

coverage.xml: .coverage | .venv/bin/coverage
	.venv/bin/coverage xml --rcfile=setup.cfg

## Code style

.PHONY: autoformat setup-git-hooks static-check

autoformat: | .venv/bin/autoflake .venv/bin/black .venv/bin/isort
	.venv/bin/autoflake \
		--in-place \
		--recursive \
		--remove-all-unused-imports \
		--ignore-init-module-imports \
		--remove-unused-variables \
		.
	.venv/bin/isort .
	.venv/bin/black .

static-check: | .venv/bin/black .venv/bin/flake8 .venv/bin/mypy
	.venv/bin/flake8
	.venv/bin/mypy

setup-git-hooks:
	src/hooks/setup-git-hooks.sh
