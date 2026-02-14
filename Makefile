.PHONY: run mypy

all: run

run:
	uv run -m subsplease.main

mypy:
	uvx mypy subsplease/

build:
	uv build

install: build
	uv tool install --editable . --force

uninstall:
	uv tool uninstall subsplease
