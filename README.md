# ScrapeSuite

A production-quality Python toolkit for declarative web scraping with offline-first testing, interactive wizard, and framework-aware HTML inspection.

**New to ScrapeSuite?** Jump to [Quick Start](#quick-start) for a 60-second demo.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Interactive Wizard](#interactive-wizard)
- [Core Concepts](#core-concepts)
- [Usage Examples](#usage-examples)
- [Documentation](#documentation)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### 🧙 Interactive Wizard
- Generate custom scrapers for ANY website through guided prompts
- Automatic framework detection (WordPress, Drupal, React, Vue, Next.js, etc.)
- Smart HTML inspection with pattern-based selector suggestions
- Confidence scoring for framework matches
- No coding required - wizard handles everything

### 📋 YAML-Driven Architecture
- Declarative job definitions for repeatable scraping
- CSS selector-based extraction works with any site
- Multiple output formats (Parquet, CSV, JSONL)
- Modular connector/transform/sink pipeline

### 🔒 Offline-First Testing
- All tests run with local HTML fixtures
- No network required for test suite (115+ tests)
- Paste HTML directly into wizard for offline scraper building
- Perfect for CI/CD and development

### 🤝 Polite & Robust
- Built-in per-domain rate limiting with token bucket algorithm
- Automatic robots.txt parsing and caching (24-hour TTL)
- Exponential backoff with jitter for retries
- Adaptive throttling on 429/503 errors
- Failed URL tracking and recovery

### 📊 State Management
- SQLite-based cursor tracking for incremental scraping
- Idempotent deduplication by item ID
- Per-job state with automatic migration
- Batch tracking with timestamps

### 🎯 Framework-Aware Extraction
- Detects 9 frameworks with confidence scoring (0-100)
- 17+ field types (title, url, date, author, category, tags, rating, etc.)
- Framework-specific selector patterns
- Multi-framework site support

### 🛠️ Type-Safe & Modern
- Full type hints throughout codebase
- pyright-strict compatible
- Comprehensive error handling
- Structured logging

---

## Installation

```bash
# Clone repository
git clone https://github.com/russellbomer/scrapesuite.git
cd scrapesuite

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m scrapesuite.cli --version
```

**Requirements**: Python 3.12+

---

## Quick Start

### 1. Run a Pre-Built Example (60 seconds)

```bash
# Run FDA recalls scraper (offline mode)
python -m scrapesuite.cli run examples/jobs/fda.yml --offline --max-items 10
```

Output:
```
fda_recalls: 6 new, 3 in batch, next_cursor=acme-foods...
```

### 2. View the Results

```bash
# Check job state
python -m scrapesuite.cli state

# Find output file
ls -lh data/cache/fda/

# Peek at data with pandas
python -c "
import pandas as pd
import glob
file = sorted(glob.glob('data/cache/fda/*.parquet'))[-1]
df = pd.read_parquet(file)
print(df[['id', 'title', 'url']].head())
print(f'\nTotal: {len(df)} records')
"
```

### 3. Create Your Own Scraper

```bash
# Launch interactive wizard
python -m scrapesuite.cli init
```

The wizard will:
1. Ask for the URL to scrape
2. Fetch the HTML and detect framework (WordPress, Drupal, React, etc.)
3. Analyze HTML structure and suggest selectors
4. Let you pick item containers and field selectors
5. Generate a complete YAML job file
6. Save to `jobs/YOUR_JOB.yml`

### 4. Run Your Custom Job

```bash
# Test offline first (if you pasted HTML)
python -m scrapesuite.cli run jobs/YOUR_JOB.yml --offline

# Or run live (hits real URLs)
python -m scrapesuite.cli run jobs/YOUR_JOB.yml --live --max-items 5
```

---

## Interactive Wizard

The wizard is the fastest way to create custom scrapers:

```bash
python -m scrapesuite.cli init
```

### Example Session

```
╔══════════════════════════════════════════════════════════════╗
║            ScrapeSuite Wizard - Job Generator                ║
╚══════════════════════════════════════════════════════════════╝

Enter the URL to scrape: https://example.com/blog

🌐 Fetching HTML...
✓ Retrieved 45.2 KB

🔍 Detecting framework...
✓ Detected: WordPress (confidence: 85)

📊 Analyzing HTML structure...
Found 12 repeated patterns

Select item container:
 1. .post (12 items) ⭐ [WordPress pattern]
 2. article.hentry (12 items) ⭐ [WordPress pattern]
 3. .entry (12 items)
 ...

Choice: 1

Configure fields for each item:
 > title: .entry-title
 > url: .entry-title a::attr(href)
 > date: .entry-date
 > author: .author
...

✓ Job saved to jobs/example_blog.yml
```

### Wizard Features

- **Framework Detection**: Automatically detects WordPress, Drupal, Bootstrap, React, Vue, Next.js, Django, Shopify, Tailwind
- **Smart Suggestions**: Framework-matching patterns get boosted to top of selector list
- **Confidence Scoring**: See how confident the system is about each framework (0-100)
- **Paste HTML Mode**: Paste HTML directly instead of fetching from URL (perfect for offline work)
- **Pattern Analysis**: Finds repeated elements automatically
- **Field Mapping**: Maps common field types to appropriate selectors

**Full wizard documentation**: [docs/WIZARD.md](docs/WIZARD.md)

---

## Core Concepts

### Job YAML Structure

```yaml
id: my_job
connector:
  type: custom
  url: https://example.com/items
  item_selector: .item
  fields:
    - field: title
      selector: .title
    - field: url
      selector: a::attr(href)
    - field: date
      selector: .date

transform:
  type: custom
  # Optional custom transformation logic

sink:
  type: parquet
  path: data/cache/my_job
```

### Framework Profiles

ScrapeSuite uses **framework profiles** to boost scraping accuracy:

- **9 active profiles**: Drupal Views, WordPress, Bootstrap, Tailwind, Shopify, Django Admin, Next.js, React, Vue.js
- **Confidence scoring**: Each profile returns 0-100 based on HTML signals
- **17+ field types**: title, url, date, published_date, updated_date, author, excerpt, content, image, thumbnail, category, tags, rating, location, phone, email, vendor, status
- **Multi-framework detection**: Sites using multiple frameworks (e.g., WordPress + Bootstrap) are handled

**Supported Frameworks**:
| Framework | Detection Signals | Common Patterns |
|-----------|------------------|-----------------|
| **Drupal Views** | `.views-row`, `.views-field-*` | Government/enterprise sites |
| **WordPress** | `.hentry`, `.entry-*`, `/wp-content/` | 40%+ of web |
| **Bootstrap** | `.card`, `.list-group-item` | Component library |
| **Tailwind** | Utility classes (10+ matches) | Modern CSS framework |
| **Shopify** | `.product-*`, `.collection-*` | E-commerce sites |
| **Django Admin** | `.django-admin`, `.field-*` | Python admin interfaces |
| **Next.js** | `__NEXT_DATA__`, `/_next/` | React meta-framework |
| **React** | `data-reactroot`, `data-react-*` | React apps |
| **Vue.js** | `v-for=`, `v-bind:`, `@click=` | Vue.js apps |

**Framework documentation**: [docs/FRAMEWORK_PROFILES.md](docs/FRAMEWORK_PROFILES.md)

### State Management

ScrapeSuite tracks state in SQLite (`state.db`):

- **Cursors**: Pagination state for incremental scraping
- **Seen Items**: Deduplication by item ID
- **Failed URLs**: Track and retry failed requests
- **Batch Metadata**: Timestamps and record counts

```bash
# View state
python -m scrapesuite.cli state

# Reset state for a job
python -m scrapesuite.cli reset my_job
```

---

## Usage Examples

### Example 1: Simple List Scraping

```yaml
# jobs/blog.yml
id: blog_posts
connector:
  type: custom
  url: https://blog.example.com
  item_selector: article.post
  fields:
    - field: title
      selector: h2.entry-title
    - field: url
      selector: a.permalink::attr(href)
    - field: date
      selector: time.published::attr(datetime)
    - field: author
      selector: .author-name

sink:
  type: parquet
  path: data/cache/blog_posts
```

Run it:
```bash
python -m scrapesuite.cli run jobs/blog.yml --live --max-items 20
```

### Example 2: Paginated Scraping

```yaml
# jobs/products.yml
id: products
connector:
  type: custom
  url: https://shop.example.com/products
  item_selector: .product-card
  fields:
    - field: title
      selector: .product-title
    - field: price
      selector: .product-price
    - field: rating
      selector: .star-rating::attr(data-rating)
  pagination:
    next_selector: a.next-page::attr(href)
    max_pages: 10

sink:
  type: csv
  path: data/products.csv
```

### Example 3: Using Fixtures (Offline Testing)

```python
# tests/test_my_scraper.py
from scrapesuite.connectors.custom import CustomConnector

def test_blog_scraper():
    with open('tests/fixtures/blog_page.html') as f:
        html = f.read()
    
    connector = CustomConnector(
        url='https://example.com',
        item_selector='article.post',
        fields=[
            {'field': 'title', 'selector': 'h2'},
            {'field': 'url', 'selector': 'a::attr(href)'},
        ]
    )
    
    items = list(connector.extract_items(html))
    assert len(items) == 10
    assert items[0]['title']
```

### Example 4: Custom Transform

```python
# jobs/custom_transform.yml
id: enriched_data
connector:
  type: custom
  url: https://api.example.com/data
  item_selector: .item
  fields:
    - field: raw_date
      selector: .date

transform:
  type: custom
  script: |
    import datetime
    
    def transform(item):
        # Parse date
        item['parsed_date'] = datetime.datetime.fromisoformat(item['raw_date'])
        # Add computed field
        item['is_recent'] = (datetime.datetime.now() - item['parsed_date']).days < 7
        return item

sink:
  type: parquet
```

---

## Documentation

Comprehensive documentation is in the [`docs/`](docs/) directory:

### User Guides
- **[Wizard Guide](docs/WIZARD.md)** - Interactive scraper generator
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

### Developer Guides
- **[Framework Profiles](docs/FRAMEWORK_PROFILES.md)** - Understanding framework detection
- **[Testing Guide](docs/TESTING.md)** - Running and writing tests
- **[Architecture](docs/ARCHITECTURE.md)** - System design and limitations
- **[Security](docs/SECURITY.md)** - Bot evasion and best practices

### Quick Reference
- **[Examples](examples/jobs/)** - Pre-built job templates
- **[API Docs](docs/API.md)** *(coming soon)* - Python API reference
- **[CLI Docs](docs/CLI.md)** *(coming soon)* - Command-line reference

---

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scrapesuite --cov-report=html

# Run specific test file
pytest tests/test_framework_scoring.py -v

# Run with make
make test
```

### Code Quality

```bash
# Format code
make format

# Lint code
make check

# Run all checks
make all
```

### Project Structure

```
scrapesuite/
├── scrapesuite/          # Main package
│   ├── __init__.py
│   ├── cli.py           # Command-line interface
│   ├── core.py          # Job runner
│   ├── http.py          # HTTP client with rate limiting
│   ├── policy.py        # Robots.txt handling
│   ├── state.py         # State management
│   ├── wizard.py        # Interactive job generator
│   ├── inspector.py     # HTML analysis (1,579 lines)
│   ├── framework_profiles.py  # Framework detection (1,100+ lines)
│   ├── connectors/      # Data source connectors
│   ├── transforms/      # Data transformations
│   └── sinks/           # Output writers
├── tests/               # Test suite (115+ tests)
├── docs/                # Documentation
├── examples/            # Example job files
└── scripts/             # Utility scripts
```

---

## Contributing

Contributions are welcome! Here's how to help:

### Reporting Issues

Open an issue on GitHub with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- ScrapeSuite version and Python version

### Adding Framework Profiles

To add support for a new framework:

1. Study the framework's HTML patterns
2. Add profile class in `scrapesuite/framework_profiles.py`
3. Implement detection with confidence scoring (0-100)
4. Add field mappings for common field types
5. Write tests with real-world HTML samples
6. Update documentation

Example:
```python
class AngularProfile(FrameworkProfile):
    name = "angular"
    
    @classmethod
    def detect(cls, html: str, item_element: Tag | None = None) -> int:
        score = 0
        if "ng-app" in html:
            score += 40
        if "ng-controller" in html:
            score += 30
        if "[ng-repeat]" in html:
            score += 25
        return min(score, 100)
    
    @classmethod
    def get_field_mappings(cls) -> dict[str, list[str]]:
        return {
            "title": ["[ng-bind='title']", "h2"],
            "date": ["[ng-bind='date']", "time"],
        }
```

### Code Style

- Use type hints for all public functions
- Follow PEP 8 style guide
- Add docstrings to classes and functions
- Write tests for new features
- Keep functions focused and small

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run full test suite (`pytest`)
5. Run linting (`make check`)
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

---

## Roadmap

### Completed
- ✅ Confidence scoring system (0-100)
- ✅ Expanded field types (17+ types)
- ✅ Multi-framework detection
- ✅ Interactive wizard

### In Progress
- 🚧 Schema.org/JSON-LD extraction
- 🚧 Open Graph meta tag support
- 🚧 Performance optimization

### Planned
- 📋 WooCommerce profile (28% of e-commerce)
- 📋 Angular/AngularJS profile (20%+ of SPAs)
- 📋 Svelte/SvelteKit profile
- 📋 Playwright integration for JS-heavy sites
- 📋 API documentation
- 📋 PyPI packaging

See [CLEANUP_PLAN.md](CLEANUP_PLAN.md) for detailed roadmap.

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built with [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- Uses [Pyarrow](https://arrow.apache.org/docs/python/) for efficient Parquet output
- Rate limiting inspired by [aiohttp-client-cache](https://github.com/requests-cache/aiohttp-client-cache)

---

## Support

- **Documentation**: [docs/](docs/)
- **Examples**: [examples/jobs/](examples/jobs/)
- **Issues**: [GitHub Issues](https://github.com/russellbomer/scrapesuite/issues)
- **Discussions**: [GitHub Discussions](https://github.com/russellbomer/scrapesuite/discussions)

**Happy Scraping! 🎉**
