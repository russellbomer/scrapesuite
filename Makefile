.PHONY: fmt lint test init run-fda run-nws build-batches

fmt:
	ruff format .

lint:
	ruff check .

test:
	pytest -q

init:
	python -m scrapesuite.cli init

run-fda:
	python -m scrapesuite.cli run jobs/fda.yml --max-items 100 --offline true

run-nws:
	python -m scrapesuite.cli run jobs/nws.yml --max-items 100 --offline true

build-batches:
	python scripts/build_batches.py


