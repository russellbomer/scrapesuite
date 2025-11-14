# Quick Start: Scraping Modern JavaScript Sites

**Goal:** Extract articles from NYT US News section (React + CSS-in-JS)

**Time:** 10 minutes

---

## Step 1: Analyze the Site (2 min)

```bash
# Use probe to analyze HTML structure
quarry scout https://www.nytimes.com/section/us --format json --output nyt_analysis.json
```

**What you'll see:**
- Framework detected: `React`
- Container pattern: `article`
- Field suggestions with dynamic CSS classes

**Key Insight:** NYT uses CSS-in-JS with classes like `css-17p10p8` that change with every build.

---

## Step 2: Create Resilient Schema (3 min)

Create `nyt_us_news.yml`:

```yaml
version: "1"
job: nyt_us_news

source:
  kind: html
  entry: "https://www.nytimes.com/section/us"
  parser: generic
  rate_limit_rps: 1.0
  cursor:
    field: url
    stop_when_seen: true

# Use structural selectors, NOT dynamic CSS classes
selectors:
  item: article                    # Semantic HTML - stable
  fields:
    title: h3 a                    # Tag hierarchy - resilient
    url: a::attr(href)              # Attribute extraction - stable
    description: p                  # Simple structural - works
    date: time::attr(datetime)      # Semantic HTML - ideal
    image: img::attr(src)           # Attribute - stable

transform:
  pipeline:
    - normalize: generic

sink:
  kind: parquet
  path: data/cache/nyt_us_news/%Y%m%dT%H%M%SZ.parquet

policy:
  robots: allow
  allowlist:
    - nytimes.com
```

**Why these selectors work:**
- `article` - Semantic HTML5, unlikely to change
- `h3 a` - Structural hierarchy, not class-dependent
- `::attr()` - Direct attribute access, very stable
- `time` - Semantic element for dates

**What to avoid:**
- ❌ `h3.css-17p10p8 a` - Dynamic class, breaks on rebuild
- ❌ `.headline.emotion-xyz` - CSS-in-JS hash, unstable
- ❌ `#article-12345` - Generated ID, changes

---

## Step 3: Validate Selectors (2 min)

```bash
# Audit your schema
python scripts/audit_schema_selectors.py nyt_us_news.yml
```

**Expected output:**
```
================================================================================
Schema: nyt_us_news.yml
Job: nyt_us_news
================================================================================

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

  Field: description
    ✅ p
      ✓ Pure structural selector (excellent)

✅ SCHEMA LOOKS GOOD: All selectors use resilient patterns
```

---

## Step 4: Extract Data (2 min)

```bash
# Test with small sample
quarry excavate nyt_us_news.yml --url https://www.nytimes.com/section/us --max-items 5

# Check output
ls -lh data/cache/nyt_us_news/
```

**Expected result:**
- Parquet file with 5 articles
- All fields populated (no None values)
- URLs are absolute paths
- Dates in ISO format

---

## Step 5: Verify & Polish (1 min)

```python
import pandas as pd
import glob

# Load latest extraction
files = glob.glob('data/cache/nyt_us_news/*.parquet')
df = pd.read_parquet(files[-1])

# Verify extraction
print(f"Extracted {len(df)} items")
print(f"\nFields: {df.columns.tolist()}")
print(f"\nNull counts:\n{df.isnull().sum()}")
print(f"\nSample:\n{df.head()}")
```

**What to check:**
- Zero nulls in title, url fields
- Dates are valid ISO format
- URLs are complete (start with https://)
- No duplicate titles

---

## Troubleshooting

### "No items extracted"

**Problem:** Item selector not finding containers

**Solution:**
```python
from bs4 import BeautifulSoup
import requests

html = requests.get('https://www.nytimes.com/section/us').text
soup = BeautifulSoup(html, 'html.parser')

# Test item selector
articles = soup.select('article')
print(f"Found {len(articles)} articles")

# If 0, try broader selector
divs = soup.select('div')
print(f"Found {len(divs)} divs")

# Inspect first few
for i, article in enumerate(articles[:3]):
    print(f"\n=== Article {i+1} ===")
    print(article.prettify()[:500])
```

### "Fields extracting as None"

**Problem:** Field selectors relative to wrong context

**Solution:**
```python
# Field selectors are relative to ITEM, not page
item = soup.select_one('article')

# Test field selector within item context
title = item.select_one('h3 a')
print(f"Title: {title.text if title else 'NOT FOUND'}")

# If not found, inspect item structure
print(item.prettify()[:1000])
```

### "Selector broke after site update"

**Problem:** NYT changed HTML structure

**Solution:**
```bash
# Re-analyze site
quarry scout https://www.nytimes.com/section/us

# Look for new patterns
# Update selectors to match new structure
# Run audit again
python scripts/audit_schema_selectors.py nyt_us_news.yml
```

---

## Advanced: Framework-Specific Extraction

```python
from quarry.framework_profiles import detect_framework, suggest_extraction_strategy
from bs4 import BeautifulSoup
import requests

# Fetch page
html = requests.get('https://www.nytimes.com/section/us').text
soup = BeautifulSoup(html, 'html.parser')

# Detect framework
framework = detect_framework(html, soup, url)
print(f"Framework: {framework.name}")
print(f"Confidence: {framework.confidence:.0%}")

# Get extraction strategy
strategy = suggest_extraction_strategy(soup, url)
print(f"\nStrategy:\n{strategy}")
```

**Expected output:**
```
Framework: React
Confidence: 85%

Strategy:
STRUCTURAL SELECTORS (Recommended for React sites)
- Prefer tag hierarchy over class names
- Use data attributes if available
- Extract from semantic HTML elements
- Example: article h3 a (not .css-xyz a)
```

---

## Production Deployment

```bash
# Full extraction with pagination
quarry excavate nyt_us_news.yml --url https://www.nytimes.com/section/us --live

# Export to CSV
quarry ship data/cache/nyt_us_news/*.parquet nyt_articles.csv

# Schedule with cron
0 */6 * * * cd /path/to/quarry && quarry excavate nyt_us_news.yml --live
```

---

## Summary

**What you learned:**
1. ✅ Modern sites use dynamic CSS (React, Vue, CSS-in-JS)
2. ✅ Use structural selectors, not class names
3. ✅ Validate selectors before deploying
4. ✅ Audit schemas for brittleness
5. ✅ Test with small samples first

**Best practices:**
- Prefer `h3 a` over `h3.css-xyz a`
- Use semantic HTML: `article`, `time`, `nav`
- Extract attributes: `::attr(href)`, `::attr(src)`
- Keep hierarchy shallow: 2-3 levels max

**Resources:**
- [Dynamic CSS Strategy](../docs/DYNAMIC_CSS_STRATEGY.md) - Complete guide
- [Selector Quick Reference](../docs/SELECTOR_QUICK_REFERENCE.md) - DO/DON'T patterns
- [Example Schemas](../examples/schemas/) - Working examples
- [Audit Tool](../scripts/audit_schema_selectors.py) - Schema validator

**Next steps:**
- Try other modern sites (Guardian, BBC, TechCrunch)
- Create fallback chains for maximum resilience
- Set up monitoring for selector health
- Contribute framework profiles for new platforms

---

**Time to production:** 10 minutes ✅  
**Maintenance effort:** Low (structural selectors are stable)  
**Recommended for:** React, Vue, Angular, Next.js, Gatsby, any CSS-in-JS site

Happy scraping! 🎉
