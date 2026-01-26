.PHONY: run mypy

all: run

run:
	uv run subsplease/main.py

mypy:
	uvx mypy subsplease/
