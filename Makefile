SHELL := /bin/bash -O extglob

.PHONY: all zip clean check check_format fix mypy pylint ankiweb run

all: zip

zip:
	python -m ankibuild --type package --install --qt all --noconsts --forms-dir forms --install

ankiweb:
	python -m ankibuild --type ankiweb --install --qt all --noconsts --forms-dir forms --install

run: zip
	python -m ankirun

check: check_format mypy pylint

check_format:
	python -m black --exclude=forms --check --diff --color src
	python -m isort --check --diff --color src

fix:
	python -m black --exclude=forms src
	python -m isort src

mypy:
	python -m mypy src

pylint:
	python -m pylint src

clean:
	rm -rf build/
