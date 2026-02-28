default: zip

set windows-shell := ["pwsh", "-c"]

UV_RUN := "uv run --"

# Package add-on for AnkiWeb
ankiweb args='':
	{{UV_RUN}} python -m ankiscripts.build --type ankiweb --qt all --exclude user_files/**/* {{args}}

# Package add-on for distribution outside of AnkiWeb
zip args='':
	{{UV_RUN}} python -m ankiscripts.build --type package --qt all --exclude user_files/**/* {{args}}

# Install dependencies to src/vendor
vendor:
	{{UV_RUN}} python -m ankiscripts.vendor

# Run protobuf generation
proto:
	{{UV_RUN}} python -m ankiscripts.protobuf

# Format using Ruff
ruff *files:
	{{UV_RUN}} ruff format --force-exclude {{files}}

# Check formatting and lints using Ruff
ruff-check *files:
	{{UV_RUN}} ruff check --force-exclude --fix {{files}}

# Format using dprint
dprint *files:
	dprint fmt --allow-no-files {{files}}

# Check formatting using dprint
dprint-check *files:
	dprint check --allow-no-files {{files}}

# Check type hints using mypy
mypy *files:
	{{UV_RUN}} mypy {{files}}

# Run ts+svelte checks
ts-check:
  {{ if path_exists("ts") == "true" { "cd ts && npm run check && npm run lint" } else { "" } }}

# Check proto files for formatting issues
proto-check:
  {{ if path_exists("ts") == "true" { "cd ts && npm run check_proto" } else { "" } }}

# Format proto files
proto-format:
  {{ if path_exists("ts") == "true" { "cd ts && npm run format_proto" } else { "" } }}

# Fix formatting issues
fix: ruff dprint proto-format

# Run mypy+formatting+ts+proto checks
lint: mypy ruff-check proto-check dprint-check ts-check

# Run pytest
pytest:
  {{UV_RUN}} python -m  pytest

# Run ts tests
ts-test:
  {{ if path_exists("ts") == "true" { "cd ts && npm run test" } else { "" } }}


# Run pytest+ts tests
test: pytest ts-test

# Build mdBook docs
build-docs:
  {{ if path_exists("docs") == "true" { "cd docs && mdbook build" } else { "" } }}

# Serve mdBook docs
serve-docs:
  {{ if path_exists("docs") == "true" { "cd docs && mdbook serve" } else { "" } }}


# Package source distribution
sourcedist:
	{{UV_RUN}} python -m ankiscripts.sourcedist

# Clean up build files
clean:
	rm -rf build/
