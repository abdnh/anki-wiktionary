.PHONY: all zip clean check check_format fix mypy pylint ankiweb test vendor

all: zip

zip:
	python -m ankibuild --type package --qt all --noconsts --forms-dir forms --exclude user_files/**/

ankiweb:
	python -m ankibuild --type ankiweb --qt all --noconsts --forms-dir forms --exclude user_files/**/

check: check_format mypy pylint

check_format:
	python -m black --exclude="forms|ankidata|samples|user_files|vendor" --check --diff --color src tests
	python -m isort --check --diff --color src tests

fix:
	python -m black --exclude="forms|ankidata|samples|user_files|vendor" src tests
	python -m isort src tests

mypy:
	python -m mypy src tests

pylint:
	python -m pylint src tests

test:
	python -m unittest

vendor:
	./vendor.sh

clean:
	rm -rf build/
