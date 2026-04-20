.PHONY: run mypy types test build install uninstall

all: run

run:
	uv run -m subsplease.main

types:
	uv run pyrefly check

build:
	uv build

install: build
	uv tool install --editable . --force

uninstall:
	uv tool uninstall subsplease

test:
	uv run pytest
