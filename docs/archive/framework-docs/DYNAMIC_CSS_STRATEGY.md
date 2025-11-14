# Strategy for Handling Dynamic CSS & Modern Frameworks

## Problem Statement

Modern websites use JavaScript frameworks (React, Vue, Angular) with CSS-in-JS libraries that generate dynamic class names. This makes traditional CSS selector-based scraping brittle because:

1. **Dynamic Class Names**: `css-17p10p8`, `emotion-abc123` change with each build
2. **Deep Component Nesting**: Elements are wrapped in many layers of divs
3. **No Semantic Classes**: `.title` replaced by `.css-xxxxx`
4. **Client-Side Rendering**: Content may not exist in initial HTML

## Real-World Example: NYT

### Original Schema (Broken)
```yaml
item_selector: article
fields:
  title: {selector: "h1, h2, .title, .headline"}  # ❌ Returns None
  link: {selector: "a", attribute: "href"}  # ✅ Works
```

### Actual HTML Structure
```html
<article class="css-1jydbgl">
  <h3 class="css-17p10p8">
    <a href="/2025/...">Title is here</a>
  </h3>
  <p class="css-1jhf0lz">Description</p>
</article>
```

### Working Schema
```yaml
item_selector: article
fields:
  title: {selector: "h3 a"}  # ✅ Structural selector
  link: {selector: "a", attribute: "href"}
```

## Solutions Implemented

### 1. Selector Fallback Chain

**File**: `quarry/lib/selectors.py`

Creates multi-tier selectors that degrade gracefully:

```python
from quarry.lib.selectors import SelectorChain

chain = SelectorChain([
    "h3.css-17p10p8 a",       # Specific (brittle but fast if it works)
    "h3 a",                    # Structural (resilient)
    "article a:first-of-type"  # Semantic fallback (most resilient)
])

# Try selectors in order until one works
title_element = chain.select_one(item)
```

**Benefits**:
- Graceful degradation when CSS changes
- No need to update selectors frequently
- Works across site redesigns

### 2. Framework Detection

**File**: `quarry/framework_profiles.py`

Automatically detects frameworks and suggests appropriate selectors:

```python
from quarry.framework_profiles import detect_framework

framework = detect_framework(html)
# Returns: FrameworkProfile(name="React", confidence=0.9, ...)

# Get framework-specific hints
item_hints = framework.get_item_selector_hints()
# ['article', '[role="article"]', '[data-testid*="story"]', ...]

field_hints = framework.get_field_mappings()
# {'title': ['h1', 'h2', '[data-testid*="headline"]'], ...}
```

**Supported Frameworks**:
- React / Next.js
- Vue.js
- Angular
- Drupal CMS
- WordPress
- CSS-in-JS (Emotion, styled-components)

### 3. Robust Selector Builder

**File**: `quarry/lib/selectors.py`

Builds selectors that avoid dynamic identifiers:

```python
from quarry.lib.selectors import build_robust_selector

# Analyzes element and builds stable selector
selector = build_robust_selector(element, root=item_container)
# Returns: "article > div:nth-of-type(2) > h3"
# Avoids: "article.css-1jydbgl > div.css-abc123 > h3.css-xyz789"
```

**Features**:
- Skips dynamic classes (`css-*`, `emotion-*`, `_abc123`)
- Prefers semantic IDs and data attributes
- Falls back to structural selectors (`nth-of-type`)

### 4. Enhanced HTML Inspector

**File**: `quarry/inspector.py` (already enhanced)

Improvements:
- Framework-aware pattern detection
- Table row intelligence (FDA, government sites)
- Parent container detection (Drupal field patterns)
- URL pattern clustering
- Sample deduplication for clearer preview

### 5. Selector Validation

**File**: `quarry/lib/selectors.py`

Test selectors before using them:

```python
from quarry.lib.selectors import validate_selector

result = validate_selector(
    html=page_html,
    selector="h3 a",
    expected_count=14
)

print(result)
# {
#     "valid": True,
#     "count": 14,
#     "sample_texts": ["Title 1", "Title 2", "Title 3"],
#     "issues": []
# }
```

## Best Practices

### 1. Prefer Structural Selectors

❌ **Brittle (tied to specific classes)**:
```yaml
title: {selector: "h3.css-17p10p8 a"}
```

✅ **Resilient (structural relationship)**:
```yaml
title: {selector: "h3 a"}
```

✅ **Even Better (with fallback)**:
```yaml
title: {selector: ["h3 a", "h2 a", "article a:first-of-type"]}
```

### 2. Use Data Attributes When Available

✅ **Stable identifiers**:
```yaml
title: {selector: "[data-testid='headline']"}
author: {selector: "[itemprop='author']"}
date: {selector: "[datetime]"}
```

### 3. Leverage Semantic HTML

✅ **Framework-agnostic**:
```yaml
item_selector: article
fields:
  title: {selector: "h2"}  # Not h2.someClass
  date: {selector: "time"}
  image: {selector: "img"}
```

### 4. Build Selector Chains in YAML

Propose YAML extension for fallback selectors:

```yaml
fields:
  title:
    selectors:  # Try in order
      - "h3.css-17p10p8 a"     # Current specific
      - "h3 a"                  # Structural
      - "article a:first-of-type"  # Semantic fallback
```

## Usage in GenericConnector

The `GenericConnector` can be enhanced to use these strategies:

```python
# In quarry/connectors/generic.py

def _extract_field(self, element, selector: str) -> str:
    """Extract field with fallback support."""
    
    # If selector is a list/chain, try each
    if isinstance(selector, list):
        for sel in selector:
            value = self._extract_single_selector(element, sel)
            if value:
                return value
        return ""
    
    return self._extract_single_selector(element, selector)
```

## Interactive Wizard Enhancements

The wizard (`quarry/wizard.py`) already includes:

✅ Framework detection during HTML analysis
✅ Smart selector generation avoiding dynamic classes  
✅ Multiple sample previews for pattern verification
✅ Table-aware column mapping
✅ Fallback to manual entry when auto-detection fails

### Example Wizard Flow

```bash
$ scrapesuite wizard

# 1. Wizard fetches URL
# 2. Detects React framework
# 3. Suggests item_selector: "article"
# 4. For each field type:
#    - Tries framework-specific patterns first
#    - Falls back to structural analysis
#    - Shows preview: "Title 1 | Title 2 | Title 3"
#    - User confirms or edits

✓ Generated schema.yml with resilient selectors
```

## Migration Guide

### For Existing Schemas

1. **Test Current Schema**:
   ```bash
   python -c "
   from quarry.core import load_yaml, run_job
   job = load_yaml('jobs/my_job.yml')
   df, _ = run_job(job, max_items=10, offline=False)
   print(df[['title', 'url']])
   "
   ```

2. **If Fields Are Empty**:
   ```bash
   # Run wizard on the URL
   scrapesuite wizard
   # Select your URL
   # Let it auto-detect selectors
   # Compare with your existing schema
   ```

3. **Update Selectors**:
   - Replace class-specific selectors with structural ones
   - Add data-attribute selectors where available
   - Consider adding fallback chains

### For New Sites

1. **Always Run Wizard First**:
   ```bash
   scrapesuite wizard
   ```

2. **Review Framework Detection**:
   - Check what framework was detected
   - Use framework-specific patterns

3. **Validate with Small Sample**:
   ```bash
   scrapesuite run jobs/my_job.yml --max-items=5
   ```

4. **Inspect Results**:
   ```python
   import pandas as pd
   df = pd.read_parquet("data/cache/my_job/latest.parquet")
   print(df.head())
   
   # Check for None/empty values
   print(df.isnull().sum())
   ```

## Future Enhancements

### 1. Selector Health Monitoring

Track selector success rates over time:

```python
# In state.py
def log_selector_health(job_name, field_name, success_rate):
    """Track which selectors are degrading."""
    # If success_rate < 80%, alert user to update schema
```

### 2. Auto-Healing Selectors

Try alternative selectors when primary fails:

```python
class SelfHealingConnector(GenericConnector):
    """Automatically tries fallback selectors."""
    
    def _extract_field(self, element, selector):
        # Try primary
        value = super()._extract_field(element, selector)
        
        if not value:
            # Try framework-specific fallbacks
            framework = detect_framework(str(element))
            if framework:
                for fallback in framework.get_field_mappings().get(field_type, []):
                    value = self._try_selector(element, fallback)
                    if value:
                        # Log successful fallback for future use
                        return value
        
        return value
```

### 3. Visual Selector Builder

Browser extension that highlights elements and generates resilient selectors:

```
┌─────────────────────────────────┐
│ Quarry Selector Builder         │
└─────────────────────────────────┘
│ 1. Click element to select      │
│ 2. Tool generates selector      │
│ 3. Shows fallback chain         │
│ 4. Copy to clipboard            │
└─────────────────────────────────┘
```

### 4. Schema Version Control

Track schema changes and selector evolution:

```yaml
version: 2
job: nyt_us_news
selectors:
  v2:  # Current
    item: article
    title: "h3 a"
  v1:  # Deprecated
    item: article
    title: "h3.css-17p10p8 a"
migration_notes: "Updated to structural selector after CSS change"
```

## Testing

### Unit Tests for Selector Utilities

```python
# tests/test_selectors.py
from quarry.lib.selectors import (
    build_robust_selector,
    extract_structural_pattern,
    validate_selector,
)

def test_build_robust_selector_avoids_dynamic_classes():
    html = '<div class="css-abc123"><h2 class="emotion-xyz">Title</h2></div>'
    soup = BeautifulSoup(html, 'html.parser')
    h2 = soup.find('h2')
    
    selector = build_robust_selector(h2)
    
    assert 'css-' not in selector
    assert 'emotion-' not in selector
    assert selector == "h2"  # Simple structural selector

def test_extract_structural_pattern():
    assert extract_structural_pattern("h3.css-17p10p8 a") == "h3 a"
    assert extract_structural_pattern("div.emotion-abc > span") == "div > span"

def test_validate_selector():
    html = '<article><h2>Title 1</h2></article><article><h2>Title 2</h2></article>'
    
    result = validate_selector(html, "article h2", expected_count=2)
    
    assert result["valid"] is True
    assert result["count"] == 2
    assert len(result["sample_texts"]) == 2
```

### Integration Tests

```python
# tests/test_nyt_extraction.py
def test_nyt_extraction_with_resilient_selectors():
    """Test that NYT extraction works with structural selectors."""
    spec = {
        "version": "1",
        "job": "nyt_test",
        "source": {
            "kind": "html",
            "entry": "https://www.nytimes.com/section/us",
            "parser": "generic",
        },
        "selectors": {
            "item": "article",
            "fields": {
                "title": "h3 a",  # Structural, not class-based
                "link": "a::attr(href)",
            },
        },
        # ... rest of spec
    }
    
    df, _ = run_job(spec, max_items=5, offline=False)
    
    assert not df.empty
    assert df["title"].notna().all()  # No None values
    assert df["link"].notna().all()
```

## Summary

This strategy provides a robust foundation for handling modern websites:

1. ✅ **Selector Fallback Chains** - Graceful degradation
2. ✅ **Framework Detection** - Auto-adapt to site architecture  
3. ✅ **Robust Selector Builder** - Avoid dynamic identifiers
4. ✅ **Enhanced Inspector** - Better pattern detection
5. ✅ **Validation Tools** - Test before deploying

The key insight: **Stop fighting CSS-in-JS. Embrace structural selectors and semantic HTML.**

---

**Next Steps**:
1. Update `GenericConnector` to support selector chains
2. Add health monitoring for selector degradation
3. Build visual selector tool for complex sites
4. Document framework-specific patterns in cookbook
