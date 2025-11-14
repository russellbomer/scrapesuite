# Modern Framework Support Guide

> **Complete guide to extracting data from React, Vue, Next.js, and other modern JavaScript frameworks**

---

## Table of Contents

1. [Quick Start (10 minutes)](#quick-start)
2. [The Dynamic CSS Problem](#the-problem)
3. [Solution Architecture](#solution-architecture)
4. [Framework Detection](#framework-detection)
5. [Selector Strategies](#selector-strategies)
6. [Testing & Validation](#testing-validation)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Techniques](#advanced-techniques)

---

## Quick Start

**Goal:** Extract articles from NYT US News (React + CSS-in-JS) in 10 minutes

### Step 1: Analyze the Site (2 min)

```bash
quarry scout https://www.nytimes.com/section/us --format json --output nyt_analysis.json
```

**What you'll see:**
- Framework detected: `React`
- Container pattern: `article`
- Field suggestions with dynamic CSS classes

### Step 2: Create Resilient Schema (3 min)

```yaml
# nyt_us_news.yml
version: "1"
job: nyt_us_news

source:
  kind: html
  entry: "https://www.nytimes.com/section/us"
  parser: generic
  rate_limit_rps: 1.0

selectors:
  item: article                    # Semantic HTML - stable ✅
  fields:
    title: h3 a                    # Tag hierarchy - resilient ✅
    url: a::attr(href)              # Attribute extraction - stable ✅
    description: p                  # Simple structural - works ✅
    date: time::attr(datetime)      # Semantic HTML - ideal ✅
    image: img::attr(src)           # Attribute - stable ✅

sink:
  kind: parquet
  path: data/cache/nyt_us_news/%Y%m%dT%H%M%SZ.parquet

policy:
  robots: allow
  allowlist: [nytimes.com]
```

### Step 3: Test Extraction (2 min)

```bash
# Extract sample
quarry excavate nyt_us_news.yml --max-items 5

# Verify output
python -c "import pandas as pd; df = pd.read_parquet('data/cache/nyt_us_news/*.parquet'); print(df.head())"
```

**Expected:** All fields populated, no None values ✅

---

## The Problem

### Why Traditional Selectors Fail

Modern websites use JavaScript frameworks (React, Vue, Angular) with CSS-in-JS that generate **dynamic class names**:

```html
<!-- Today's build -->
<article class="css-1jydbgl">
  <h3 class="css-17p10p8">
    <a href="/article">Title</a>
  </h3>
</article>

<!-- Tomorrow's build -->
<article class="css-9xk2mf">  <!-- ❌ Class changed! -->
  <h3 class="css-4gh7nq">      <!-- ❌ Class changed! -->
    <a href="/article">Title</a>
  </h3>
</article>
```

**Problems:**
1. **Dynamic Class Names**: `css-17p10p8` changes with each build
2. **CSS-in-JS Hashes**: `emotion-abc123` are build-time generated
3. **No Semantic Classes**: `.title` replaced by `.css-xxxxx`
4. **Deep Nesting**: React components wrap content in many layers

### Real-World Breakage

```yaml
# ❌ BRITTLE - Breaks on next deployment
selectors:
  item: article.css-1jydbgl
  fields:
    title: h3.css-17p10p8 a        # Class changes = selector fails
    author: span.emotion-abc123    # Hash changes = selector fails
```

**Result:** Schema works today, breaks tomorrow. High maintenance burden.

---

## Solution Architecture

### Three-Layer Defense

```
Layer 1: Structural Selectors (Primary)
         ↓ (if fails)
Layer 2: Semantic HTML (Fallback)
         ↓ (if fails)
Layer 3: Data Attributes (Last Resort)
```

### Layer 1: Structural Selectors

**Principle:** Use tag hierarchy, not classes

```yaml
# ✅ RESILIENT - Uses HTML structure
selectors:
  item: article               # Semantic HTML5 tag
  fields:
    title: h3 a               # Tag hierarchy (no classes)
    url: a::attr(href)         # Direct attribute access
    description: article > p   # Parent-child relationship
```

**Why it works:**
- HTML structure changes less frequently than CSS
- Browsers enforce semantic tag standards
- Frameworks generate predictable DOM trees

### Layer 2: Semantic HTML

**Principle:** Leverage HTML5 semantic elements

```yaml
# ✅ ROBUST - Uses semantic tags
selectors:
  fields:
    date: time::attr(datetime)      # <time> element (standard)
    nav_links: nav a                # <nav> element (standard)
    main_content: main article      # <main> element (standard)
    author: address a               # <address> for contact info
```

**Semantic tags that rarely change:**
- `<article>`, `<section>`, `<nav>`, `<header>`, `<footer>`
- `<time>`, `<address>`, `<figure>`, `<figcaption>`
- `<main>`, `<aside>`, `<mark>`

### Layer 3: Data Attributes

**Principle:** Use `data-*` attributes when available

```yaml
# ✅ STABLE - Data attributes are API-like
selectors:
  fields:
    title: '[data-testid="article-title"]'     # Test ID (stable)
    author: '[data-author-name]'                # Custom data attr
    category: '[data-section-name]'             # Section metadata
```

**When to use:**
- Sites with test automation (they need stable selectors too)
- Custom CMS platforms
- When structural selectors are too ambiguous

---

## Framework Detection

### Automatic Detection

Quarry automatically detects frameworks and suggests optimal extraction strategies:

```python
from quarry.framework_profiles import detect_framework, suggest_extraction_strategy
from bs4 import BeautifulSoup
import requests

# Fetch page
html = requests.get('https://www.nytimes.com/section/us').text
soup = BeautifulSoup(html, 'html.parser')
url = 'https://www.nytimes.com/section/us'

# Detect framework
framework = detect_framework(html, soup, url)
print(f"Framework: {framework.name}")
print(f"Confidence: {framework.confidence:.0%}")
print(f"Indicators: {', '.join(framework.indicators)}")

# Get extraction strategy
strategy = suggest_extraction_strategy(soup, url)
print(strategy)
```

**Output:**
```
Framework: React
Confidence: 85%
Indicators: __NEXT_DATA__, _next, CSS-in-JS patterns

STRUCTURAL SELECTORS (Recommended for React sites)
- Prefer tag hierarchy over class names
- Use data attributes if available
- Extract from semantic HTML elements
- Example: article h3 a (not .css-xyz a)
```

### Supported Frameworks

| Framework | Detection Method | Recommended Strategy |
|-----------|-----------------|----------------------|
| **React** | `__NEXT_DATA__`, `_react`, CSS-in-JS | Structural + data attrs |
| **Next.js** | `__NEXT_DATA__`, `_next/` paths | Structural + SSR hints |
| **Vue** | `v-cloak`, `data-v-` attrs | Structural + Vue directives |
| **Angular** | `ng-app`, `ng-controller` | Structural + ng attrs |
| **Svelte** | `.svelte-` classes, `s-` attrs | Structural selectors |
| **Gatsby** | `gatsby-` classes, GraphQL | Structural + data layer |
| **WordPress** | `wp-content`, `wp-includes` | Class-based (WP classes stable) |
| **Drupal** | `node-type-`, `field-name-` | Class-based (Drupal patterns) |
| **Shopify** | `shopify-section`, `.product` | Class-based (theme classes) |
| **Bootstrap** | `.container`, `.row`, `.col-` | Class-based (Bootstrap stable) |

### Framework Profiles (Modular Architecture)

```
quarry/framework_profiles/
├── __init__.py              # Registry & detection
├── base.py                  # FrameworkProfile base class
├── cms/
│   ├── drupal.py           # DrupalViewsProfile
│   └── wordpress.py        # WordPressProfile
├── frameworks/
│   ├── django.py           # DjangoAdminProfile
│   ├── nextjs.py           # NextJSProfile
│   ├── react.py            # ReactComponentProfile
│   └── vue.py              # VueJSProfile
├── css/
│   ├── bootstrap.py        # BootstrapProfile
│   └── tailwind.py         # TailwindProfile
└── ecommerce/
    └── shopify.py          # ShopifyProfile
```

**Benefits:**
- ✅ Easy to add new profiles
- ✅ Test categories independently
- ✅ Self-documenting structure
- ✅ Type-safe with mypy strict mode

---

## Selector Strategies

### DO ✅

```yaml
# Pure structural (excellent)
title: h3 a
description: article > p
links: nav a

# Semantic HTML (very good)
date: time::attr(datetime)
author: address a
image: figure img

# Data attributes (good)
category: '[data-category]'
test_id: '[data-testid="headline"]'

# Attribute extraction (stable)
url: a::attr(href)
src: img::attr(src)
alt: img::attr(alt)

# Shallow hierarchy (good)
headline: article h2        # 2 levels
byline: article header p    # 3 levels
```

### DON'T ❌

```yaml
# Dynamic CSS classes (brittle)
title: h3.css-17p10p8 a             # ❌ Hash changes
author: span.emotion-abc123         # ❌ CSS-in-JS generated

# Deep class chains (fragile)
content: .css-x > .css-y > .css-z   # ❌ Any break fails all

# Generated IDs (unstable)
article: '#article-12345'           # ❌ ID changes per item

# Over-specific (brittle)
link: 'div.container > div:nth-child(3) > article:first-child a'  # ❌ Layout changes break this

# Positional selectors (fragile)
first: article:first-child          # ❌ Order changes break
third: div:nth-of-type(3)           # ❌ New elements break position
```

### Pattern Decision Tree

```
START: Need to extract a field
│
├─ Is there a <time>, <nav>, <article>, <address> tag?
│  └─ YES → Use semantic HTML selector ✅
│  └─ NO  → Continue
│
├─ Is there a data-* attribute?
│  └─ YES → Use data attribute selector ✅
│  └─ NO  → Continue
│
├─ Can you use tag hierarchy (h3 a, article > p)?
│  └─ YES → Use structural selector ✅
│  └─ NO  → Continue
│
└─ Only classes available?
   ├─ Are classes semantic (.title, .author)?
   │  └─ YES → Use with caution ⚠️
   │  └─ NO  → Avoid, find alternative ❌
   │
   └─ Are classes from stable framework (Bootstrap, WP)?
      └─ YES → Safe to use ✅
      └─ NO  → Find structural alternative ❌
```

### Example Transformations

| Brittle ❌ | Resilient ✅ | Why Better |
|-----------|-------------|-----------|
| `h3.css-17p10p8 a` | `h3 a` | Removes dynamic class |
| `.emotion-abc123` | `article > p` | Uses structure, not hash |
| `#article-12345` | `article[data-id="12345"]` | Data attr more stable |
| `div:nth-child(3) a` | `nav a` | Semantic, not positional |
| `.headline.primary.featured` | `h1` | Simpler, more robust |

---

## Testing & Validation

### Audit Schemas

```bash
# Validate selector resilience
python scripts/audit_schema_selectors.py nyt_us_news.yml
```

**Output:**
```
📊 Summary: 5 selectors analyzed
   ✅ OK:     5
   ⚠️  Medium: 0
   🔴 High:   0

🎯 Item Selector
  ✅ article
    ✓ Uses semantic HTML5 tags

📝 Field Selectors
  Field: title
    ✅ h3 a
      ✓ Pure structural selector (excellent)

  Field: url
    ✅ a::attr(href)
      ✓ Uses attribute extraction (stable)

✅ SCHEMA LOOKS GOOD: All selectors use resilient patterns
```

### Manual Validation

```python
from quarry.lib.selectors import validate_selector, build_fallback_chain
from bs4 import BeautifulSoup
import requests

# Fetch page
url = 'https://www.nytimes.com/section/us'
html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
soup = BeautifulSoup(html, 'html.parser')

# Test selector
result = validate_selector(soup, 'h3 a')
print(f"Valid: {result['valid']}")
print(f"Count: {result['count']}")
print(f"Warnings: {result['warnings']}")

# Build fallback chain
chain = build_fallback_chain('h3.css-17p10p8 a', ['class', 'tag'])
print(f"Fallback chain: {chain.selectors}")
```

### Schema Health Metrics

```python
import pandas as pd
import glob

# Load extractions
files = glob.glob('data/cache/nyt_us_news/*.parquet')
df = pd.read_parquet(files[-1])

# Check extraction quality
null_pct = (df.isnull().sum() / len(df)) * 100
print("Null percentages by field:")
print(null_pct)

# Alert if >20% nulls
for field, pct in null_pct.items():
    if pct > 20:
        print(f"⚠️ WARNING: {field} has {pct:.1f}% nulls - selector may be broken")
```

**Thresholds:**
- **0-5% nulls**: ✅ Excellent
- **5-20% nulls**: ⚠️ Monitor closely
- **>20% nulls**: 🔴 Update selectors

---

## Troubleshooting

### Issue: "No items extracted"

**Symptom:** `df.empty == True`

**Diagnosis:**
```python
from bs4 import BeautifulSoup
import requests

html = requests.get('https://www.nytimes.com/section/us').text
soup = BeautifulSoup(html, 'html.parser')

# Test item selector
articles = soup.select('article')
print(f"Found {len(articles)} articles")

# If 0, inspect page structure
print("Available containers:")
for tag in ['article', 'div', 'section']:
    count = len(soup.select(tag))
    print(f"  {tag}: {count}")
```

**Solutions:**
1. Try broader selector: `div` instead of `article`
2. Check if content is client-rendered (view page source vs inspect element)
3. Use `quarry scout` to auto-detect containers

### Issue: "Fields extracting as None"

**Symptom:** `df['title'].isnull().sum() > 0`

**Diagnosis:**
```python
# Field selectors are relative to ITEM
item = soup.select_one('article')
if item:
    title = item.select_one('h3 a')
    print(f"Title found: {title is not None}")
    if not title:
        print("Item structure:")
        print(item.prettify()[:1000])
```

**Solutions:**
1. Verify field selector is relative to item, not page
2. Check if field is in nested component
3. Use browser DevTools to verify selector path

### Issue: "Selector broke after site update"

**Symptom:** Schema worked yesterday, failing today

**Diagnosis:**
```bash
# Re-analyze site
quarry scout https://www.nytimes.com/section/us --output fresh_analysis.json

# Compare old vs new
diff nyt_analysis.json fresh_analysis.json
```

**Solutions:**
1. Update selectors to match new structure
2. Build fallback chain for future-proofing
3. Switch to more stable semantic selectors

### Issue: "Slow extraction"

**Symptom:** Taking >5s per page

**Diagnosis:**
```python
import cProfile
import pstats

# Profile extraction
cProfile.run('run_job(job_dict)', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumtime')
stats.print_stats(10)
```

**Solutions:**
1. Reduce `rate_limit_rps` (may be throttling)
2. Optimize complex selectors (deep nesting)
3. Use attribute extraction instead of text parsing

---

## Advanced Techniques

### Fallback Chains

Build multi-tier selector fallbacks:

```python
from quarry.lib.selectors import SelectorChain, build_fallback_chain

# Auto-generate chain
chain = build_fallback_chain(
    'h3.css-17p10p8 a',  # Current working selector
    ['class', 'tag']      # Context hints
)

# Manual chain
chain = SelectorChain([
    'h3.headline a',          # Tier 1: Specific
    'h3 a',                   # Tier 2: Structural
    'article a:first-child'   # Tier 3: Fallback
])

# Extract with auto-fallback
value, used_selector = chain.extract(soup)
print(f"Extracted '{value}' using: {used_selector}")
```

### Framework-Specific Patterns

```python
from quarry.framework_profiles import get_framework_profile

# Get React-specific patterns
react = get_framework_profile('React')
patterns = react.get_extraction_patterns()

print(f"Typical item containers: {patterns['containers']}")
print(f"Common field patterns: {patterns['fields']}")
print(f"Avoid: {patterns['anti_patterns']}")
```

### Robust Selector Builder

```python
from quarry.lib.selectors import build_robust_selector

# Convert brittle to robust
brittle = 'h3.css-17p10p8.emotion-abc123 a'
robust = build_robust_selector(brittle, context=['class', 'tag'])

print(f"Original: {brittle}")
print(f"Robust:   {robust}")
# Output: "h3 a"
```

### Monitoring & Alerts

```python
import pandas as pd
from datetime import datetime, timedelta

def check_schema_health(job_name, threshold=0.8):
    """Alert if extraction quality drops"""
    
    # Load recent extractions
    files = glob.glob(f'data/cache/{job_name}/*.parquet')
    recent = [f for f in files if file_age(f) < timedelta(hours=24)]
    
    for file in recent:
        df = pd.read_parquet(file)
        
        # Calculate completeness
        completeness = 1 - (df.isnull().sum().sum() / df.size)
        
        if completeness < threshold:
            send_alert(
                f"Schema health degraded: {job_name}",
                f"Completeness: {completeness:.1%} (threshold: {threshold:.0%})"
            )
```

---

## Best Practices

### Schema Design

1. **Start structural, add specificity only if needed**
   ```yaml
   # Good progression
   title: h3 a                    # Try this first
   title: article h3 a            # If too broad
   title: article header h3 a     # If still ambiguous
   ```

2. **Use semantic HTML when available**
   ```yaml
   date: time::attr(datetime)     # Not: span.date
   author: address a              # Not: div.author a
   ```

3. **Extract attributes directly**
   ```yaml
   url: a::attr(href)             # Not: a (then parse text)
   image: img::attr(src)          # Not: img (then parse)
   ```

4. **Keep hierarchy shallow**
   ```yaml
   # Good: 2-3 levels
   title: article h3 a
   
   # Bad: >4 levels
   title: div > section > article > header > h3 > a
   ```

### Testing Workflow

```bash
# 1. Analyze
quarry scout <url> --output analysis.json

# 2. Create schema
nano schema.yml

# 3. Validate
python scripts/audit_schema_selectors.py schema.yml

# 4. Test extraction
quarry excavate schema.yml --max-items 5

# 5. Verify data quality
python -c "import pandas as pd; df = pd.read_parquet('<file>'); print(df.isnull().sum())"

# 6. Deploy
quarry excavate schema.yml --live
```

### Maintenance Schedule

- **Daily**: Monitor extraction completeness
- **Weekly**: Audit schemas for brittleness
- **Monthly**: Re-analyze sites for structure changes
- **Quarterly**: Update framework detection profiles

---

## Resources

### Tools

- **`quarry scout`**: Analyze page structure and detect frameworks
- **`scripts/audit_schema_selectors.py`**: Validate selector resilience
- **`quarry/lib/selectors.py`**: Selector utilities (validate, build fallbacks)
- **`quarry/framework_profiles/`**: Framework detection system

### Examples

- [`examples/schemas/nyt_resilient.yml`](../examples/schemas/nyt_resilient.yml) - NYT with resilient selectors
- [`examples/use_selector_utilities.py`](../examples/use_selector_utilities.py) - Selector API examples
- [`examples/jobs/`](../examples/jobs/) - Working extraction jobs

### Related Documentation

- [Selector Quick Reference](SELECTOR_QUICK_REFERENCE.md) - DO/DON'T patterns
- [Wizard Guide](WIZARD.md) - Interactive schema builder
- [Testing Guide](TESTING.md) - Comprehensive testing strategies
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues & solutions

---

## Contributing

### Adding New Framework Profiles

1. Create profile in appropriate category:
   ```python
   # quarry/framework_profiles/frameworks/my_framework.py
   from ..base import FrameworkProfile
   
   class MyFrameworkProfile(FrameworkProfile):
       name = "MyFramework"
       
       def detect(self, html: str, soup: BeautifulSoup, url: str) -> int:
           score = 0
           if 'my-framework-marker' in html:
               score += 50
           return score
   ```

2. Register in `__init__.py`:
   ```python
   from .frameworks.my_framework import MyFrameworkProfile
   PROFILES.append(MyFrameworkProfile())
   ```

3. Add tests:
   ```python
   def test_my_framework_detection():
       html = '<div id="my-framework-app">...</div>'
       soup = BeautifulSoup(html, 'html.parser')
       result = detect_framework(html, soup, url)
       assert result.name == "MyFramework"
   ```

### Improving Selector Utilities

1. Add new validator in `quarry/lib/selectors.py`
2. Update `audit_schema_selectors.py` to use new validator
3. Add examples to `examples/use_selector_utilities.py`
4. Update this guide with new patterns

---

## Summary

**Key Takeaways:**

1. ✅ **Use structural selectors** - `h3 a` not `h3.css-xyz a`
2. ✅ **Leverage semantic HTML** - `<time>`, `<article>`, `<nav>`
3. ✅ **Extract attributes directly** - `::attr(href)`, `::attr(src)`
4. ✅ **Validate before deploying** - `audit_schema_selectors.py`
5. ✅ **Monitor extraction quality** - Alert on >20% nulls
6. ✅ **Build fallback chains** - Multi-tier resilience
7. ✅ **Detect frameworks automatically** - Use `quarry scout`

**Time Investment:**
- Initial setup: 10 minutes
- Schema creation: 5-10 minutes per site
- Validation: 2 minutes
- Maintenance: ~5 minutes/month (if using resilient patterns)

**Expected Results:**
- ✅ 95%+ extraction completeness
- ✅ Low maintenance burden
- ✅ Resilient to CSS framework updates
- ✅ Works across build cycles

---

**Happy scraping modern sites!** 🚀

*Last updated: 2024-11-14*
