# ScrapeSuite

A reusable Python toolkit for web/data collection with offline-first testing.

ScrapeSuite is a production-quality library and CLI for defining scraping jobs in YAML, running connectors with retry/backoff and rate limits, transforming raw records into normalized tables, and writing outputs to sinks (Parquet/CSV). It maintains idempotent state in SQLite for per-job cursors and deduplication.

## Features

- **YAML job definitions**: Declarative job specs with source, transform, and sink configuration
- **Offline-first testing**: All tests run with local HTML fixtures (no network required)
- **Polite HTTP**: Built-in rate limiting, retry/backoff, and allowlist enforcement
- **State management**: SQLite-based cursor tracking and idempotent item deduplication
- **Interactive wizard**: Generate job YAML specs with guided prompts
- **Type-safe**: Full type hints, pyright-strict compatible

## Installation

```bash
pip install -r requirements.txt
```

## Quickstart

### 1. Create a job with the wizard

```bash
make init
# Or: python -m scrapesuite.cli init
```

Follow the prompts to generate a job YAML file in `jobs/`.

### 2. Run a job offline (with fixtures)

```bash
make run-fda
# Or: python -m scrapesuite.cli run jobs/fda.yml --offline true --max-items 100
```

### 3. Run all jobs

```bash
python -m scrapesuite.cli run-all --offline true
```

### 4. Check job state

```bash
python -m scrapesuite.cli state
```

## Example Job YAML

```yaml
version: "1"
job: fda_recalls
source:
  kind: html
  entry: https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts
  parser: fda_list
  detail_parser: fda_detail
  rate_limit_rps: 1
  cursor:
    field: id
    stop_when_seen: true
transform:
  pipeline:
    - normalize: fda_recalls
sink:
  kind: parquet
  path: data/cache/fda/%Y%m%dT%H%M%SZ.parquet
policy:
  robots: allow
  allowlist: ["fda.gov"]
```

## Development

```bash
# Format code
make fmt

# Lint
make lint

# Run tests
make test

# Build batches (offline)
make build-batches
```

## Policy and Live Mode

When running in live mode (`--offline false`), ScrapeSuite enforces:

- **Allowlist**: All outbound URLs must be in the `policy.allowlist` (required)
- **Rate limiting**: Respects `rate_limit_rps` with 1 RPS default and exponential backoff
- **Robots.txt**: Stub implementation (TODO: full parsing)

**Important**: Always test jobs offline first using fixtures. Live mode should only be used after careful review of the allowlist and rate limits.

## License

[Add your license here]


