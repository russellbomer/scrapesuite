.PHONY: setup fmt fix lint test init run-fda run-nws build-batches build-profiles run-sample

setup:
	pip install -e .
	pip install -r requirements.txt

fmt:
	ruff format .

fix:
	ruff check --fix .
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

build-profiles:
	python scripts/build_profiles.py

run-sample:
	python -m scrapesuite.cli run examples/jobs/fda.yml --offline true --max-items 10


