SHELL := /bin/bash -O extglob

.PHONY: all forms zip clean format check prebuild install

all: zip

PACKAGE_NAME := wiktionary

forms: src/form_qt5.py src/form_qt6.py src/import_dictionary_qt5.py src/import_dictionary_qt6.py

zip: forms $(PACKAGE_NAME).ankiaddon

src/form_qt5.py: designer/form.ui
	pyuic5 $^ > $@

src/form_qt6.py: designer/form.ui
	pyuic6 $^ > $@

src/import_dictionary_qt5.py: designer/import_dictionary.ui
	pyuic5 $^ > $@

src/import_dictionary_qt6.py: designer/import_dictionary.ui
	pyuic6 $^ > $@

$(PACKAGE_NAME).ankiaddon: src/*
	rm -f $@
	rm -rf src/__pycache__
	# 7z u -tzip src -w src/.
	( cd src/; 7z u -tzip ../$@ -w . )


# Install in test profile
ankiprofile/addons21/$(PACKAGE_NAME): src/* forms
	rm -rf src/__pycache__
	cp -r src/. ankiprofile/addons21/$(PACKAGE_NAME);

install: ankiprofile/addons21/$(PACKAGE_NAME)

format:
	python -m black src/

check:
	python -m mypy .

clean:
	rm -f $(PACKAGE_NAME).ankiaddon
