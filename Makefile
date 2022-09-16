.PHONY: all zip clean check check_format fix mypy pylint ankiweb test

all: zip

zip:
	python -m ankibuild --type package --qt all --noconsts --forms-dir forms --exclude user_files/**/

ankiweb:
	python -m ankibuild --type ankiweb --qt all --noconsts --forms-dir forms --exclude user_files/**/

check: check_format mypy pylint

check_format:
	python -m black --exclude="forms|ankidata|samples|user_files" --check --diff --color src tests
	python -m isort --check --diff --color src tests

fix:
	python -m black --exclude="forms|ankidata|samples|user_files" src tests
	python -m isort src tests

mypy:
	python -m mypy src tests

pylint:
	python -m pylint src tests

test:
	python -m unittest

clean:
	rm -rf build/
