SHELL = /bin/bash

VENV_PATH = venv
VERSIONING_FILES =  setup.py makefile docs/source/conf.py df_slots/__init__.py
CURRENT_VERSION = 0.1.0 

help:
	@echo "Thanks for your interest in Dialog Flow My Addon!"
	@echo
	@echo "make lint: Run linters"
	@echo "make test: Run basic tests (not testing most integrations)"
	@echo "make test-all: Run ALL tests (slow, closest to CI)"
	@echo "make format: Run code formatters (destructive)"
	@echo "make build_doc: Build Sphinx docs; activate your virtual environment before execution"
	@echo "make pre_commit: Register a git hook to lint the code on each commit"
	@echo "make version_major: increment version major in metadata files 8.8.1 -> 9.0.0"
	@echo "make version_minor: increment version minor in metadata files 9.1.1 -> 9.2.0"
	@echo "make version_patch: increment patch number in metadata files 9.9.1 -> 9.9.2"
	@echo

venv:
	@if [ "`which python`" != "venv/bin/python" ] ; 	then \
		echo "Start creating virtual environment";\
		python3 -m venv $(VENV_PATH);\
	fi

	$(VENV_PATH)/bin/pip install -e . ;
	$(VENV_PATH)/bin/pip install -r requirements_dev.txt ;
	$(VENV_PATH)/bin/pip install -r requirements_test.txt ;
	

format: venv
	$(VENV_PATH)/bin/python -m black --exclude="setup\.py" --line-length=120 .
.PHONY: format

lint: venv
	@set -e && $(VENV_PATH)/bin/python -m black --exclude="setup\.py" --line-length=120 --check . || ( \
		echo "================================"; \
		echo "Bad formatting? Run: make format"; \
		echo "================================"; \
		false)

.PHONY: lint

test: venv
	$(VENV_PATH)/bin/python -m pytest --cov-report html --cov-report term --cov=df_slots tests/
.PHONY: test

test_all: venv test lint
.PHONY: test_all

build_doc:
	if [ "`which python`" != "venv/bin/python" ]; then exit 1; fi 
	sphinx-apidoc -e -f -o docs/source/apiref dialog_flow_slots
	sphinx-build -M clean docs/source docs/build
	sphinx-build -M html docs/source docs/build
.PHONY: build_doc

pre_commit: venv
	echo -e "#!/bin/sh\n\nmake test_all" > .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
.PHONY: pre_commit

version_patch: venv
	bump2version --current-version $(CURRENT_VERSION) patch $(VERSIONING_FILES)
.PHONY: version_patch

version_minor: venv
	bump2version --current-version $(CURRENT_VERSION) minor $(VERSIONING_FILES)
.PHONY: version_minor

version_major: venv
	bump2version --current-version $(CURRENT_VERSION) major $(VERSIONING_FILES)
.PHONY: version_major
