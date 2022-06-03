SHELL := /bin/bash -O extglob

.PHONY: all zip clean check check_format fix mypy pylint ankiweb run test

all: zip

zip:
	python -m ankibuild --type package --install --qt all --noconsts --forms-dir forms --install

ankiweb:
	python -m ankibuild --type ankiweb --install --qt all --noconsts --forms-dir forms --install

run: zip
	python -m ankirun

check: check_format mypy pylint

check_format:
	python -m black --exclude=forms --check --diff --color src tests
	python -m isort --check --diff --color src tests

fix:
	python -m black --exclude=forms src tests
	python -m isort src tests

mypy:
	python -m mypy src tests

pylint:
	python -m pylint src tests

test:
	python -m unittest

clean:
	rm -rf build/
