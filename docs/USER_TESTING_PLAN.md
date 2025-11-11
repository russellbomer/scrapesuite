# ScrapeSuite User Testing Plan

## Overview

This manual testing plan validates the 4 new framework profiles (Schema.org, Open Graph, Twitter Cards, WooCommerce) and verifies the overall system with real-world URLs.

**Testing Environment:** Git Bash on Windows  
**Total Test Time:** ~30-45 minutes  
**Prerequisites:** Python 3.12+, scrapesuite installed

---

## Pre-Testing Setup

### 1. Verify Installation

```bash
# Navigate to scrapesuite directory
cd /c/path/to/scrapesuite

# Verify Python version
python --version
# Expected: Python 3.12.x or higher

# Install/update dependencies
pip install -r requirements.txt

# Run test suite to ensure clean state
python -m pytest -q
# Expected: All tests passing (115/115)
```

### 2. Create Testing Directory

```bash
# Create a testing workspace
mkdir -p testing/session-$(date +%Y%m%d)
cd testing/session-$(date +%Y%m%d)

# Create logs directory
mkdir -p logs
mkdir -p results

# Set environment for testing
export PYTHONPATH=/c/path/to/scrapesuite
```

---

## Test Suite 1: Schema.org Microdata Detection

**Objective:** Verify Schema.org profile detects microdata and extracts structured data

### Test 1.1: Recipe Sites (Schema.org/Recipe)

**Test URLs:**
- https://www.allrecipes.com/recipe/10813/best-chocolate-chip-cookies/
- https://www.epicurious.com/recipes/food/views/chocolate-chip-cookies

**Steps:**

```bash
# Test detection
python -c "
from scrapesuite.http import get_html
from scrapesuite.framework_profiles import detect_framework, detect_all_frameworks

url = 'https://www.allrecipes.com/recipe/10813/best-chocolate-chip-cookies/'
html = get_html(url, offline=False)

# Single detection
framework = detect_framework(html)
print(f'Detected: {framework.name if framework else None}')

# All frameworks with scores
all_fw = detect_all_frameworks(html)
print('\\nAll detections:')
for fw, score in all_fw[:5]:
    print(f'  {fw.name}: {score}')
" 2>&1 | tee logs/test-1.1-recipe.log
```

**Expected Results:**
- ✅ `schema_org` detected with score ≥ 40
- ✅ May also detect `opengraph` and `twitter_cards`
- ✅ Output shows itemscope/itemprop detection

**Validation Checklist:**
- [ ] Schema.org appears in top 3 detections
- [ ] Score is reasonable (40-100)
- [ ] No errors in log

### Test 1.2: Article/News Sites (Schema.org/Article)

**Test URLs:**
- https://www.bbc.com/news (any article)
- https://www.theguardian.com (any article)
- https://techcrunch.com (any article)

**Steps:**

```bash
# Test with news article
python -c "
from scrapesuite.http import get_html
from scrapesuite.framework_profiles import SchemaOrgProfile, detect_framework
from bs4 import BeautifulSoup

url = 'https://techcrunch.com/2024/01/15/example-article/'  # Use actual URL
html = get_html(url, offline=False)

# Detect
framework = detect_framework(html)
print(f'Framework: {framework.name if framework else None}')

# Check for specific Schema.org patterns
score = SchemaOrgProfile.detect(html)
print(f'Schema.org score: {score}')

# Check field mappings
if framework == SchemaOrgProfile:
    mappings = SchemaOrgProfile.get_field_mappings()
    print(f'\\nSupported fields: {list(mappings.keys())}')
    
# Look for microdata
soup = BeautifulSoup(html, 'html.parser')
itemscope_count = len(soup.find_all(attrs={'itemscope': True}))
itemprop_count = len(soup.find_all(attrs={'itemprop': True}))
print(f'\\nMicrodata elements:')
print(f'  itemscope: {itemscope_count}')
print(f'  itemprop: {itemprop_count}')
" 2>&1 | tee logs/test-1.2-article.log
```

**Expected Results:**
- ✅ Schema.org detected if article has microdata
- ✅ Shows field mappings (title, date, author, description, etc.)
- ✅ itemscope/itemprop counts > 0

**Validation Checklist:**
- [ ] Detection works for news sites
- [ ] Field mappings shown correctly
- [ ] Microdata elements found

### Test 1.3: Product Pages (Schema.org/Product)

**Test URLs:**
- https://www.amazon.com/dp/[product-id]
- https://www.target.com/p/[product-slug]
- https://www.bestbuy.com/site/[product-slug]

**Steps:**

```bash
# Test product page
python -c "
from scrapesuite.http import get_html
from scrapesuite.framework_profiles import detect_all_frameworks

url = 'https://www.amazon.com/dp/B08N5WRWNW'  # Use actual product URL
html = get_html(url, offline=False)

# Get all frameworks
all_fw = detect_all_frameworks(html)
print('Framework detection results:')
for fw, score in all_fw:
    print(f'  {fw.name}: {score}')
    
# Check for product-specific patterns
if 'schema.org/Product' in html:
    print('\\n✅ Product microdata found')
if 'itemprop=\"price\"' in html:
    print('✅ Price microdata found')
if 'itemprop=\"name\"' in html:
    print('✅ Name microdata found')
" 2>&1 | tee logs/test-1.3-product.log
```

**Expected Results:**
- ✅ Multiple frameworks may be detected (Schema.org, OG, Twitter)
- ✅ Product-specific microdata found
- ✅ Price, name fields detected

**Validation Checklist:**
- [ ] Schema.org detected on product pages
- [ ] Product-specific fields found
- [ ] Multi-framework detection works

---

## Test Suite 2: Open Graph Meta Tags

**Objective:** Verify OpenGraph profile extracts social metadata

### Test 2.1: Social Media Optimized Sites

**Test URLs:**
- https://medium.com/@username/article-slug (any Medium article)
- https://dev.to/username/article-slug (any DEV article)
- https://github.com/username/repo (any GitHub repo)

**Steps:**

```bash
# Test Open Graph extraction
python -c "
from scrapesuite.http import get_html
from scrapesuite.framework_profiles import OpenGraphProfile, detect_framework

url = 'https://medium.com/@example/example-article'  # Use actual URL
html = get_html(url, offline=False)

# Detect
framework = detect_framework(html)
print(f'Detected framework: {framework.name if framework else None}')

# Extract all OG metadata
metadata = OpenGraphProfile.extract_metadata(html)
print(f'\\nOpen Graph metadata ({len(metadata)} tags):')
for key, value in sorted(metadata.items())[:10]:
    print(f'  {key}: {value[:100]}...' if len(value) > 100 else f'  {key}: {value}')

# Check detection score
score = OpenGraphProfile.detect(html)
print(f'\\nOpenGraph score: {score}')
" 2>&1 | tee logs/test-2.1-opengraph.log
```

**Expected Results:**
- ✅ OpenGraph detected with score ≥ 40
- ✅ Metadata extracted (title, description, image, url, type)
- ✅ At least 3-5 OG tags found

**Validation Checklist:**
- [ ] OpenGraph detected
- [ ] Metadata dictionary has ≥ 3 entries
- [ ] Standard fields present (title, description, image)

### Test 2.2: News Sites with OG Tags

**Test URLs:**
- https://www.nytimes.com (any article)
- https://www.washingtonpost.com (any article)
- https://www.reuters.com (any article)

**Steps:**

```bash
# Compare OG vs Schema.org detection
python -c "
from scrapesuite.http import get_html
from scrapesuite.framework_profiles import detect_all_frameworks, OpenGraphProfile, SchemaOrgProfile

url = 'https://www.nytimes.com/2024/01/15/world/example.html'  # Use actual URL
html = get_html(url, offline=False)

# All frameworks
all_fw = detect_all_frameworks(html)
print('Framework scores:')
for fw, score in all_fw[:5]:
    print(f'  {fw.name}: {score}')

# Check which metadata format is present
og_metadata = OpenGraphProfile.extract_metadata(html)
print(f'\\nOpen Graph tags: {len(og_metadata)}')

has_microdata = 'itemscope' in html
print(f'Has microdata: {has_microdata}')
" 2>&1 | tee logs/test-2.2-news-og.log
```

**Expected Results:**
- ✅ Both OG and Schema.org may be detected
- ✅ Higher scorer wins detection
- ✅ Shows which format site prefers

**Validation Checklist:**
- [ ] Multiple frameworks detected
- [ ] Scores reasonable
- [ ] Metadata extraction works

---

## Test Suite 3: Twitter Cards

**Objective:** Verify Twitter Cards profile extracts social metadata

### Test 3.1: Twitter-Optimized Sites

**Test URLs:**
- https://blog.twitter.com (any post)
- https://stackoverflow.com/questions/[id] (any question)
- https://www.youtube.com/watch?v=[id] (any video)

**Steps:**

```bash
# Test Twitter Cards extraction
python -c "
from scrapesuite.http import get_html
from scrapesuite.framework_profiles import TwitterCardsProfile, detect_framework

url = 'https://stackoverflow.com/questions/12345678/example'  # Use actual URL
html = get_html(url, offline=False)

# Detect
framework = detect_framework(html)
print(f'Detected: {framework.name if framework else None}')

# Extract Twitter metadata
metadata = TwitterCardsProfile.extract_metadata(html)
print(f'\\nTwitter Card metadata ({len(metadata)} tags):')
for key, value in sorted(metadata.items()):
    print(f'  {key}: {value[:100]}...' if len(value) > 100 else f'  {key}: {value}')

# Check detection score
score = TwitterCardsProfile.detect(html)
print(f'\\nTwitter Cards score: {score}')
" 2>&1 | tee logs/test-3.1-twitter-cards.log
```

**Expected Results:**
- ✅ Twitter Cards detected with score ≥ 40
- ✅ Metadata includes card type, title, description
- ✅ Site and/or creator fields present

**Validation Checklist:**
- [ ] Twitter Cards detected
- [ ] Card type present (summary, summary_large_image, etc.)
- [ ] Core fields extracted

### Test 3.2: Sites with Both OG and Twitter

**Test URLs:**
- https://www.producthunt.com/posts/[slug] (any product)
- https://substack.com (any newsletter post)
- https://hashnode.com (any blog post)

**Steps:**

```bash
# Compare OG and Twitter Cards
python -c "
from scrapesuite.http import get_html
from scrapesuite.framework_profiles import OpenGraphProfile, TwitterCardsProfile, detect_all_frameworks

url = 'https://www.producthunt.com/posts/example-product'  # Use actual URL
html = get_html(url, offline=False)

# All frameworks
all_fw = detect_all_frameworks(html)
print('Framework scores:')
for fw, score in all_fw[:7]:
    print(f'  {fw.name}: {score}')

# Compare metadata
og_meta = OpenGraphProfile.extract_metadata(html)
twitter_meta = TwitterCardsProfile.extract_metadata(html)

print(f'\\nOpen Graph tags: {len(og_meta)}')
print(f'Twitter Card tags: {len(twitter_meta)}')

# Show overlap
if og_meta and twitter_meta:
    print(f'\\nTitle comparison:')
    print(f'  OG: {og_meta.get(\"title\", \"N/A\")}')
    print(f'  Twitter: {twitter_meta.get(\"title\", \"N/A\")}')
" 2>&1 | tee logs/test-3.2-og-twitter.log
```

**Expected Results:**
- ✅ Both OG and Twitter detected
- ✅ Metadata from both sources extracted
- ✅ Titles usually match

**Validation Checklist:**
- [ ] Multiple universal profiles detected
- [ ] Both metadata sources work
- [ ] Data consistency between sources

---

## Test Suite 4: WooCommerce E-commerce

**Objective:** Verify WooCommerce profile detects WordPress e-commerce sites

### Test 4.1: Known WooCommerce Stores

**Test URLs:**
- https://www.themeforest.net (uses WooCommerce)
- Search "WooCommerce demo store" for live examples
- Your own WooCommerce store (if available)

**Steps:**

```bash
# Test WooCommerce detection
python -c "
from scrapesuite.http import get_html
from scrapesuite.framework_profiles import WooCommerceProfile, WordPressProfile, detect_all_frameworks

url = 'https://example-woocommerce-store.com/shop'  # Use actual URL
html = get_html(url, offline=False)

# All frameworks
all_fw = detect_all_frameworks(html)
print('Framework scores:')
for fw, score in all_fw[:5]:
    print(f'  {fw.name}: {score}')

# WooCommerce specific
wc_score = WooCommerceProfile.detect(html)
wp_score = WordPressProfile.detect(html)

print(f'\\nWooCommerce score: {wc_score}')
print(f'WordPress score: {wp_score}')

# Check for WooCommerce classes
if 'woocommerce' in html:
    print('✅ WooCommerce classes found')
if 'product-card' in html or 'wc-product' in html:
    print('✅ Product elements found')
if 'add_to_cart' in html or 'add-to-cart' in html:
    print('✅ Add to cart found')
" 2>&1 | tee logs/test-4.1-woocommerce.log
```

**Expected Results:**
- ✅ WooCommerce detected with score ≥ 40
- ✅ WordPress also detected (combination)
- ✅ WooCommerce-specific classes found

**Validation Checklist:**
- [ ] WooCommerce profile detects
- [ ] WordPress profile also present
- [ ] Product elements identified

### Test 4.2: WooCommerce Product Pages

**Test URLs:**
- Any WooCommerce store product page
- Check for /product/ in URL path

**Steps:**

```bash
# Test product page field mappings
python -c "
from scrapesuite.http import get_html
from scrapesuite.framework_profiles import WooCommerceProfile, detect_framework

url = 'https://example-store.com/product/example-product/'  # Use actual URL
html = get_html(url, offline=False)

# Detect
framework = detect_framework(html)
print(f'Detected: {framework.name if framework else None}')

# Field mappings
if framework == WooCommerceProfile:
    mappings = WooCommerceProfile.get_field_mappings()
    print(f'\\nWooCommerce field types: {list(mappings.keys())}')
    
# Check for product-specific fields
checks = {
    'price': 'woocommerce-Price-amount' in html or 'price' in html,
    'sku': 'sku' in html,
    'stock': 'in-stock' in html or 'out-of-stock' in html,
    'rating': 'star-rating' in html,
    'sale': 'onsale' in html,
}

print('\\nProduct elements:')
for field, found in checks.items():
    status = '✅' if found else '❌'
    print(f'  {status} {field}: {found}')
" 2>&1 | tee logs/test-4.2-woocommerce-product.log
```

**Expected Results:**
- ✅ WooCommerce detected
- ✅ Product-specific fields available
- ✅ Price, SKU, stock fields found

**Validation Checklist:**
- [ ] Product page detected
- [ ] Field mappings include e-commerce fields
- [ ] Product elements present

---

## Test Suite 5: Wizard Integration Testing

**Objective:** Test framework detection in the interactive wizard

### Test 5.1: Wizard with Schema.org Site

**Steps:**

```bash
# Run wizard interactively
python -m scrapesuite wizard

# When prompted:
# 1. Enter URL: https://www.allrecipes.com/recipes/
# 2. Watch for framework detection message
# 3. Review selector options (should prioritize Schema.org patterns)
# 4. Select an option and continue
# 5. Review field suggestions
```

**Manual Validation:**
- [ ] Wizard shows "✓ Framework detected: schema_org" message
- [ ] Selector table has Schema.org patterns in top 3
- [ ] Field detection uses itemprop selectors
- [ ] Generated YAML includes detected framework

**Save Output:**

```bash
# Copy wizard output
# Save to: results/test-5.1-wizard-schema.txt
```

### Test 5.2: Wizard with E-commerce Site

**Steps:**

```bash
# Run wizard with WooCommerce site
python -m scrapesuite wizard

# When prompted:
# 1. Enter URL: [WooCommerce store URL]
# 2. Watch for WooCommerce detection
# 3. Check if product selectors appear
# 4. Verify price/SKU fields suggested
```

**Manual Validation:**
- [ ] Framework detected (WooCommerce or WordPress)
- [ ] Product-specific selectors offered
- [ ] Price/SKU field types available
- [ ] Container hints include .product classes

**Save Output:**

```bash
# Save to: results/test-5.2-wizard-woocommerce.txt
```

### Test 5.3: Wizard with News Site (Multi-Framework)

**Steps:**

```bash
# Run wizard with modern news site
python -m scrapesuite wizard

# When prompted:
# 1. Enter URL: https://techcrunch.com/
# 2. Note all detected frameworks
# 3. Check which wins (highest score)
# 4. Verify field mappings are appropriate
```

**Manual Validation:**
- [ ] Multiple frameworks detected
- [ ] Best match selected (Schema.org, OG, or Twitter)
- [ ] Field selectors match detected framework
- [ ] No errors or conflicts

**Save Output:**

```bash
# Save to: results/test-5.3-wizard-news.txt
```

---

## Test Suite 6: End-to-End Job Execution

**Objective:** Create and run complete scraping jobs with new profiles

### Test 6.1: Schema.org Recipe Scraping

**Steps:**

```bash
# Create job file
cat > test-schema-recipes.yml << 'EOF'
job: test_schema_recipes
connector: custom
source:
  entry: https://www.allrecipes.com/recipes/
  item_selector: "[itemscope][itemtype*='Recipe']"
  
fields:
  title:
    selector: "[itemprop='name']"
  description:
    selector: "[itemprop='description']"
  date:
    selector: "time[itemprop='datePublished']"
  image:
    selector: "img[itemprop='image']"
    extract: src
    
transform: custom
sink:
  type: csv
  path: results/schema-recipes.csv
EOF

# Run job in offline mode (if you have test data)
# Or modify to use live mode with rate limiting
python -m scrapesuite run test-schema-recipes.yml --offline

# Check results
head -20 results/schema-recipes.csv
```

**Validation Checklist:**
- [ ] Job runs without errors
- [ ] CSV file created
- [ ] Data extracted correctly
- [ ] Schema.org selectors work

### Test 6.2: WooCommerce Product Scraping

**Steps:**

```bash
# Create WooCommerce job
cat > test-woocommerce-products.yml << 'EOF'
job: test_woocommerce_products
connector: custom
source:
  entry: https://example-store.com/shop/
  item_selector: ".product"
  
fields:
  title:
    selector: ".woocommerce-loop-product__title"
  price:
    selector: ".woocommerce-Price-amount"
  url:
    selector: "a.woocommerce-LoopProduct-link"
    extract: href
  image:
    selector: "img.attachment-woocommerce_thumbnail"
    extract: src
    
transform: custom
sink:
  type: csv
  path: results/woocommerce-products.csv
EOF

# Run job (adjust URL to real WooCommerce store)
python -m scrapesuite run test-woocommerce-products.yml

# Check results
cat results/woocommerce-products.csv | head -10
```

**Validation Checklist:**
- [ ] Job executes successfully
- [ ] Products extracted
- [ ] Prices formatted correctly
- [ ] URLs are absolute

---

## Test Suite 7: Performance & Regression Testing

**Objective:** Verify performance is still good with 13 profiles

### Test 7.1: Profile Detection Speed

**Steps:**

```bash
# Run performance profiler
python scripts/profile_framework_detection.py > results/performance-profile.txt 2>&1

# Check results
cat results/performance-profile.txt
```

**Expected Results:**
- ✅ Detection < 0.1ms per page
- ✅ All fixtures process successfully
- ✅ Per-profile overhead < 0.01ms

**Validation Checklist:**
- [ ] Performance is acceptable
- [ ] No significant slowdown from 9→13 profiles
- [ ] All recommendations are "excellent" or "good"

### Test 7.2: Regression Test Suite

**Steps:**

```bash
# Run full test suite
python -m pytest -v > results/test-results.txt 2>&1

# Check for failures
grep -E "(FAILED|ERROR)" results/test-results.txt
echo "Exit code: $?"
# Should be 1 (no matches found)

# Count passing tests
grep -c "PASSED" results/test-results.txt
# Should be 115
```

**Validation Checklist:**
- [ ] All 115 tests pass
- [ ] No new failures introduced
- [ ] No deprecation warnings

---

## Test Suite 8: Edge Cases & Error Handling

**Objective:** Test error handling and edge cases

### Test 8.1: Non-Framework Sites

**Test URLs:**
- Plain HTML page with no frameworks
- Government site with minimal markup
- Old-style HTML 4.0 site

**Steps:**

```bash
# Test with minimal HTML site
python -c "
from scrapesuite.http import get_html
from scrapesuite.framework_profiles import detect_framework, detect_all_frameworks

url = 'http://info.cern.ch/'  # Historic plain HTML site
html = get_html(url, offline=False)

framework = detect_framework(html)
print(f'Detected: {framework.name if framework else \"None (as expected)\"}')

all_fw = detect_all_frameworks(html)
print(f'\\nAll detections: {len(all_fw)}')
for fw, score in all_fw[:5]:
    print(f'  {fw.name}: {score}')
" 2>&1 | tee logs/test-8.1-plain-html.log
```

**Expected Results:**
- ✅ No framework detected (None) OR very low scores
- ✅ No errors thrown
- ✅ Graceful fallback behavior

**Validation Checklist:**
- [ ] No crashes on plain HTML
- [ ] Returns None or low scores
- [ ] System handles gracefully

### Test 8.2: Malformed HTML

**Steps:**

```bash
# Test with malformed HTML
python -c "
from scrapesuite.framework_profiles import detect_framework

html = '<div itemscope><p itemprop=\"title\">Test</div>'  # Missing closing tags
framework = detect_framework(html)
print(f'Detected: {framework.name if framework else \"None\"}')
print('✅ No crash on malformed HTML')
" 2>&1 | tee logs/test-8.2-malformed.log
```

**Expected Results:**
- ✅ No exceptions thrown
- ✅ BeautifulSoup handles parsing
- ✅ Detection still works or returns None

**Validation Checklist:**
- [ ] No crashes
- [ ] Graceful error handling
- [ ] Informative output

### Test 8.3: Very Large Pages

**Test URLs:**
- Wikipedia article with long content
- Documentation site with large HTML
- E-commerce page with many products

**Steps:**

```bash
# Test with large page
python -c "
import time
from scrapesuite.http import get_html
from scrapesuite.framework_profiles import detect_framework

url = 'https://en.wikipedia.org/wiki/Python_(programming_language)'
start = time.time()
html = get_html(url, offline=False)
fetch_time = time.time() - start

start = time.time()
framework = detect_framework(html)
detect_time = time.time() - start

print(f'Page size: {len(html):,} bytes')
print(f'Fetch time: {fetch_time:.2f}s')
print(f'Detection time: {detect_time:.4f}s')
print(f'Detected: {framework.name if framework else \"None\"}')
" 2>&1 | tee logs/test-8.3-large-page.log
```

**Expected Results:**
- ✅ Detection still < 1 second
- ✅ No memory issues
- ✅ Handles pages > 1MB

**Validation Checklist:**
- [ ] Large pages process successfully
- [ ] Performance acceptable
- [ ] No memory errors

---

## Test Suite 9: Real-World URLs Batch Test

**Objective:** Test against diverse real-world URLs

### Test 9.1: Mixed URL Batch

**Create test file:**

```bash
# Create URLs file
cat > test-urls.txt << 'EOF'
https://www.allrecipes.com/recipe/10813/best-chocolate-chip-cookies/
https://techcrunch.com/
https://www.nytimes.com/
https://medium.com/
https://stackoverflow.com/questions
https://github.com/
https://www.producthunt.com/
https://dev.to/
https://www.amazon.com/
https://www.target.com/
EOF

# Run batch test
while IFS= read -r url; do
    echo "Testing: $url"
    python -c "
from scrapesuite.http import get_html
from scrapesuite.framework_profiles import detect_all_frameworks

url = '$url'
try:
    html = get_html(url, offline=False)
    all_fw = detect_all_frameworks(html)
    
    if all_fw:
        top3 = all_fw[:3]
        print(f'{url}')
        for fw, score in top3:
            print(f'  {fw.name}: {score}')
    else:
        print(f'{url}: No frameworks detected')
except Exception as e:
    print(f'{url}: ERROR - {e}')
print()
" 2>&1 | tee -a logs/test-9.1-batch.log
    sleep 2  # Be polite
done < test-urls.txt
```

**Expected Results:**
- ✅ All URLs process successfully
- ✅ Appropriate frameworks detected
- ✅ Universal profiles (Schema.org, OG, Twitter) common

**Validation Checklist:**
- [ ] No crashes across diverse URLs
- [ ] Detection results make sense
- [ ] Performance consistent

---

## Test Suite 10: Documentation Validation

**Objective:** Verify examples in documentation work

### Test 10.1: CONTRIBUTING.md Examples

**Steps:**

```bash
# Test the example from CONTRIBUTING.md
# (Copy the AngularProfile example and run it)

# Verify type checking works
cd /c/path/to/scrapesuite
mypy scrapesuite/framework_profiles/ 2>&1 | tee logs/test-10.1-mypy.log

# Should show 0 errors for framework_profiles
```

**Validation Checklist:**
- [ ] Example code runs
- [ ] No type errors in profiles
- [ ] Documentation accurate

---

## Results Summary & Reporting

### Generate Test Report

```bash
# Collect all results
cat > results/TEST_REPORT.md << 'EOF'
# ScrapeSuite User Testing Report

**Date:** $(date +%Y-%m-%d)
**Tester:** [Your Name]
**Environment:** Git Bash on Windows

## Test Execution Summary

### Suite 1: Schema.org Microdata
- [ ] Test 1.1: Recipe sites - PASS/FAIL
- [ ] Test 1.2: Article sites - PASS/FAIL
- [ ] Test 1.3: Product pages - PASS/FAIL

### Suite 2: Open Graph
- [ ] Test 2.1: Social sites - PASS/FAIL
- [ ] Test 2.2: News sites - PASS/FAIL

### Suite 3: Twitter Cards
- [ ] Test 3.1: Twitter-optimized - PASS/FAIL
- [ ] Test 3.2: OG + Twitter - PASS/FAIL

### Suite 4: WooCommerce
- [ ] Test 4.1: Store detection - PASS/FAIL
- [ ] Test 4.2: Product pages - PASS/FAIL

### Suite 5: Wizard Integration
- [ ] Test 5.1: Schema.org wizard - PASS/FAIL
- [ ] Test 5.2: WooCommerce wizard - PASS/FAIL
- [ ] Test 5.3: Multi-framework - PASS/FAIL

### Suite 6: End-to-End Jobs
- [ ] Test 6.1: Recipe scraping - PASS/FAIL
- [ ] Test 6.2: Product scraping - PASS/FAIL

### Suite 7: Performance
- [ ] Test 7.1: Detection speed - PASS/FAIL
- [ ] Test 7.2: Regression tests - PASS/FAIL

### Suite 8: Edge Cases
- [ ] Test 8.1: Plain HTML - PASS/FAIL
- [ ] Test 8.2: Malformed HTML - PASS/FAIL
- [ ] Test 8.3: Large pages - PASS/FAIL

### Suite 9: Real-World Batch
- [ ] Test 9.1: Mixed URLs - PASS/FAIL

### Suite 10: Documentation
- [ ] Test 10.1: Examples work - PASS/FAIL

## Issues Found

[List any issues, unexpected behavior, or bugs]

## Performance Metrics

- Average detection time: _____ ms
- Successful detections: _____ / _____
- Frameworks coverage: _____ %

## Recommendations

[Any suggestions for improvement]

## Conclusion

Overall Status: ✅ PASS / ⚠️ NEEDS WORK / ❌ FAIL

EOF

# Open report for editing
code results/TEST_REPORT.md  # Or use notepad, vim, etc.
```

### Archive Test Session

```bash
# Create archive
cd /c/path/to/scrapesuite/testing
tar -czf session-$(date +%Y%m%d)-complete.tar.gz session-$(date +%Y%m%d)/

# List archive contents
tar -tzf session-$(date +%Y%m%d)-complete.tar.gz | head -20

echo "✅ Testing complete! Results archived."
```

---

## Quick Reference Commands

### Check Installation
```bash
python --version && python -m pytest -q
```

### Run Single Detection Test
```bash
python -c "from scrapesuite.framework_profiles import detect_framework; from scrapesuite.http import get_html; html = get_html('URL', offline=False); print(detect_framework(html).name if detect_framework(html) else 'None')"
```

### Run Performance Profiler
```bash
python scripts/profile_framework_detection.py
```

### Run Wizard
```bash
python -m scrapesuite wizard
```

### Check Logs
```bash
tail -f logs/*.log
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'scrapesuite'"

**Solution:**
```bash
export PYTHONPATH=/c/path/to/scrapesuite
# Or use absolute import path
```

### Issue: "Rate limiting errors"

**Solution:**
```bash
# Add delays between requests
sleep 2

# Or use offline mode for testing
python -m scrapesuite run job.yml --offline
```

### Issue: "BeautifulSoup parse warnings"

**Solution:**
```bash
# Install lxml parser
pip install lxml

# Or ignore warnings in test scripts
export PYTHONWARNINGS="ignore::UserWarning"
```

### Issue: "SSL certificate errors"

**Solution:**
```bash
# For testing only (not production)
export PYTHONHTTPSVERIFY=0
```

---

## Success Criteria

**Minimum passing criteria:**
- ✅ 90% of test suites pass
- ✅ All 115 regression tests pass
- ✅ Performance < 0.1ms per detection
- ✅ No critical bugs found
- ✅ New profiles detect on appropriate sites
- ✅ Wizard integration works
- ✅ End-to-end jobs complete successfully

**Nice to have:**
- All 10 test suites 100% pass
- Performance < 0.05ms
- Zero issues found
- Documentation examples all work

---

## Next Steps After Testing

1. **Review results** - Check TEST_REPORT.md
2. **File issues** - Create GitHub issues for bugs
3. **Update docs** - Fix any inaccurate documentation
4. **Performance tuning** - Optimize slow areas
5. **Add fixtures** - Create test fixtures for new profiles
6. **Expand coverage** - Add more URLs to batch test

---

**Good luck with testing! 🚀**
