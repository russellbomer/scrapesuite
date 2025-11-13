# ScrapeSuite Manual Testing Plan

**Version**: 2.0  
**Date**: November 13, 2025  
**Purpose**: Comprehensive CLI testing for both Foundry Suite and Legacy Wizard

---

## Prerequisites

```bash
# Ensure you're in the scrapesuite directory
cd /workspaces/scrapesuite

# Verify installation
python --version  # Should be 3.12+
pip list | grep -E "beautifulsoup4|pydantic|click|rich"

# Clean test environment
rm -rf /tmp/test_output
mkdir -p /tmp/test_output
```

---

## Part 1: Foundry Suite Testing (5 Tools)

### 1.1 Probe - HTML Analysis

**Test 1: Analyze Live URL**
```bash
# Test probe on real website
python -m scrapesuite.foundry probe https://news.ycombinator.com

# Expected Output:
# - Framework detection (likely "None" or generic)
# - List of repeated patterns
# - Field suggestions
# - Statistics (links, forms, etc.)
```

**Test 2: Analyze Local File**
```bash
# Test with fixture file
python -m scrapesuite.foundry probe \
  --file tests/fixtures/fda_list.html

# Expected Output:
# - Should detect patterns
# - Show .views-row or similar containers
# - Suggest title, date, link fields
```

**Test 3: JSON Output**
```bash
# Test JSON format
python -m scrapesuite.foundry probe \
  --file tests/fixtures/fda_list.html \
  --format json \
  --output /tmp/test_output/probe_result.json

# Verify:
cat /tmp/test_output/probe_result.json | python -m json.tool | head -20

# Expected: Valid JSON with frameworks, patterns, fields
```

**Test 4: Framework Detection**
```bash
# Test WordPress detection
python -m scrapesuite.foundry probe \
  --file tests/fixtures/fda_list.html

# Should show framework(s) detected with confidence scores
```

---

### 1.2 Blueprint - Schema Designer

**Test 5: Create Schema Interactively**
```bash
# Interactive schema creation (will prompt for input)
python -m scrapesuite.foundry blueprint create /tmp/test_output/test_schema.yml

# When prompted, enter:
# - URL: https://example.com
# - Container selector: .article
# - Fields: title (h2), url (a::attr(href)), date (.date)
# - Pagination: (press Enter to skip)

# Verify file created:
cat /tmp/test_output/test_schema.yml
```

**Test 6: Validate Schema**
```bash
# Create a test schema first
cat > /tmp/test_output/valid_schema.yml << 'EOF'
url: https://example.com
container: .article
fields:
  - name: title
    selector: h2
  - name: url
    selector: a::attr(href)
  - name: date
    selector: .date
EOF

# Validate it
python -m scrapesuite.foundry blueprint validate /tmp/test_output/valid_schema.yml

# Expected: "✓ Schema is valid"
```

**Test 7: Preview Extraction**
```bash
# Test preview with actual HTML
python -m scrapesuite.foundry blueprint preview \
  examples/jobs/fda.yml \
  --file tests/fixtures/fda_list.html

# Expected: Shows extracted items in table format
```

**Test 8: Invalid Schema**
```bash
# Test validation with bad schema
cat > /tmp/test_output/bad_schema.yml << 'EOF'
url: not-a-url
fields: "this should be a list"
EOF

python -m scrapesuite.foundry blueprint validate /tmp/test_output/bad_schema.yml

# Expected: Validation errors shown
```

---

### 1.3 Forge - Data Extraction

**Test 9: Extract from File**
```bash
# Basic extraction
python -m scrapesuite.foundry forge \
  examples/jobs/fda.yml \
  --file tests/fixtures/fda_list.html \
  --output /tmp/test_output/extracted.jsonl

# Verify output:
cat /tmp/test_output/extracted.jsonl | wc -l  # Should show number of records
head -1 /tmp/test_output/extracted.jsonl | python -m json.tool
```

**Test 10: Extract from URL (with rate limiting)**
```bash
# Extract from live URL
python -m scrapesuite.foundry forge \
  examples/jobs/fda.yml \
  --url https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts \
  --output /tmp/test_output/live_extracted.jsonl \
  --max-pages 1

# Verify:
wc -l /tmp/test_output/live_extracted.jsonl
```

**Test 11: Pagination Test**
```bash
# Test with max pages limit
python -m scrapesuite.foundry forge \
  examples/jobs/fda.yml \
  --file tests/fixtures/fda_list.html \
  --max-pages 2 \
  --output /tmp/test_output/paginated.jsonl

# Should stop after 2 pages (or when pagination fails with fixture)
```

**Test 12: Metadata Test**
```bash
# Extract and check metadata
python -m scrapesuite.foundry forge \
  examples/jobs/fda.yml \
  --file tests/fixtures/fda_list.html \
  --output /tmp/test_output/with_meta.jsonl

# Check for _metadata fields:
head -1 /tmp/test_output/with_meta.jsonl | python -c "
import sys, json
data = json.load(sys.stdin)
print('Metadata fields:', [k for k in data.keys() if k.startswith('_')])
"
```

---

### 1.4 Polish - Data Transformation

**Test 13: Basic Deduplication**
```bash
# Create test data with duplicates
cat > /tmp/test_output/dupes.jsonl << 'EOF'
{"id": "1", "title": "Article A", "url": "http://example.com/a"}
{"id": "2", "title": "Article B", "url": "http://example.com/b"}
{"id": "1", "title": "Article A", "url": "http://example.com/a"}
{"id": "3", "title": "Article C", "url": "http://example.com/c"}
EOF

# Deduplicate
python -m scrapesuite.foundry polish \
  /tmp/test_output/dupes.jsonl \
  --dedupe \
  --dedupe-keys id \
  --output /tmp/test_output/deduped.jsonl

# Verify: should have 3 lines instead of 4
wc -l /tmp/test_output/deduped.jsonl
```

**Test 14: Field Transformations**
```bash
# Create test data
cat > /tmp/test_output/transform_test.jsonl << 'EOF'
{"title": "  ARTICLE TITLE  ", "url": "https://example.com/page?utm_source=test", "date": "2024-01-15"}
{"title": "another title", "url": "https://subdomain.example.org/article", "date": "2024-02-20"}
EOF

# Apply transformations
python -m scrapesuite.foundry polish \
  /tmp/test_output/transform_test.jsonl \
  --transform title:normalize_text \
  --transform url:extract_domain \
  --transform date:parse_date \
  --output /tmp/test_output/transformed.jsonl

# Check results:
cat /tmp/test_output/transformed.jsonl | python -m json.tool
```

**Test 15: Validation**
```bash
# Create data with invalid emails
cat > /tmp/test_output/validate_test.jsonl << 'EOF'
{"email": "valid@example.com", "url": "https://example.com"}
{"email": "invalid-email", "url": "not-a-url"}
{"email": "another@test.org", "url": "https://test.org"}
EOF

# Validate and filter
python -m scrapesuite.foundry polish \
  /tmp/test_output/validate_test.jsonl \
  --validate email:email \
  --validate url:url \
  --skip-invalid \
  --output /tmp/test_output/validated.jsonl

# Should keep only valid records (2 records)
wc -l /tmp/test_output/validated.jsonl
```

**Test 16: Statistics**
```bash
# Get statistics
python -m scrapesuite.foundry polish \
  /tmp/test_output/dupes.jsonl \
  --dedupe \
  --dedupe-keys id \
  --stats

# Expected: Shows input count, duplicates removed, output count
```

---

### 1.5 Crate - Data Export

**Test 17: Export to CSV**
```bash
# Create test data
cat > /tmp/test_output/export_test.jsonl << 'EOF'
{"title": "Article 1", "author": "John Doe", "date": "2024-01-15"}
{"title": "Article 2", "author": "Jane Smith", "date": "2024-02-20"}
{"title": "Article 3", "author": "Bob Jones", "date": "2024-03-10"}
EOF

# Export to CSV
python -m scrapesuite.foundry crate \
  /tmp/test_output/export_test.jsonl \
  /tmp/test_output/output.csv

# Verify:
cat /tmp/test_output/output.csv
```

**Test 18: Export to JSON**
```bash
# Export to pretty JSON
python -m scrapesuite.foundry crate \
  /tmp/test_output/export_test.jsonl \
  /tmp/test_output/output.json \
  --pretty

# Verify:
cat /tmp/test_output/output.json
```

**Test 19: Export to SQLite**
```bash
# Export to SQLite
python -m scrapesuite.foundry crate \
  /tmp/test_output/export_test.jsonl \
  /tmp/test_output/output.db \
  --table articles

# Verify:
sqlite3 /tmp/test_output/output.db "SELECT * FROM articles;"
sqlite3 /tmp/test_output/output.db ".schema articles"
```

**Test 20: Export with Metadata Exclusion**
```bash
# Create data with metadata
cat > /tmp/test_output/with_metadata.jsonl << 'EOF'
{"title": "Article", "_source": "web", "_timestamp": "2024-01-01"}
EOF

# Export excluding metadata
python -m scrapesuite.foundry crate \
  /tmp/test_output/with_metadata.jsonl \
  /tmp/test_output/no_meta.csv \
  --exclude-meta

# Verify metadata fields are excluded:
cat /tmp/test_output/no_meta.csv
```

**Test 21: SQLite Replace/Append Modes**
```bash
# Create initial export
python -m scrapesuite.foundry crate \
  /tmp/test_output/export_test.jsonl \
  /tmp/test_output/mode_test.db \
  --table items

# Check count:
sqlite3 /tmp/test_output/mode_test.db "SELECT COUNT(*) FROM items;"

# Append more data
python -m scrapesuite.foundry crate \
  /tmp/test_output/export_test.jsonl \
  /tmp/test_output/mode_test.db \
  --table items \
  --if-exists append

# Should have 6 records now:
sqlite3 /tmp/test_output/mode_test.db "SELECT COUNT(*) FROM items;"

# Replace all data
python -m scrapesuite.foundry crate \
  /tmp/test_output/export_test.jsonl \
  /tmp/test_output/mode_test.db \
  --table items \
  --if-exists replace

# Back to 3 records:
sqlite3 /tmp/test_output/mode_test.db "SELECT COUNT(*) FROM items;"
```

---

### 1.6 Complete Pipeline Test

**Test 22: End-to-End Foundry Pipeline**
```bash
# Step 1: Analyze
python -m scrapesuite.foundry probe \
  --file tests/fixtures/fda_list.html \
  --format json \
  --output /tmp/test_output/pipeline_analysis.json

# Step 2: Extract (using existing schema)
python -m scrapesuite.foundry forge \
  examples/jobs/fda.yml \
  --file tests/fixtures/fda_list.html \
  --output /tmp/test_output/pipeline_raw.jsonl

# Step 3: Clean and deduplicate
python -m scrapesuite.foundry polish \
  /tmp/test_output/pipeline_raw.jsonl \
  --dedupe \
  --dedupe-keys title \
  --transform title:normalize_text \
  --output /tmp/test_output/pipeline_clean.jsonl

# Step 4: Export to CSV
python -m scrapesuite.foundry crate \
  /tmp/test_output/pipeline_clean.jsonl \
  /tmp/test_output/pipeline_final.csv

# Step 5: Export to SQLite
python -m scrapesuite.foundry crate \
  /tmp/test_output/pipeline_clean.jsonl \
  /tmp/test_output/pipeline_final.db \
  --table fda_recalls

# Verify all outputs exist:
ls -lh /tmp/test_output/pipeline_*

# Check CSV content:
cat /tmp/test_output/pipeline_final.csv

# Check SQLite content:
sqlite3 /tmp/test_output/pipeline_final.db "SELECT title FROM fda_recalls LIMIT 3;"
```

---

## Part 2: Legacy Wizard Testing

### 2.1 Interactive Wizard

**Test 23: Run Wizard (Manual)**
```bash
# Launch interactive wizard
python -m scrapesuite.cli init

# Follow prompts:
# 1. Choose template or paste HTML
# 2. Enter job details
# 3. Configure selectors
# 4. Save job file

# Verify job was created:
ls -l jobs/
```

**Test 24: Run Generated Job**
```bash
# Run a job created by wizard (use actual filename)
python -m scrapesuite.cli run jobs/YOUR_JOB.yml --offline --max-items 5

# Expected: Extracts data using configured selectors
```

---

### 2.2 Job Execution

**Test 25: Run Example Job (Offline)**
```bash
# Run FDA example offline
python -m scrapesuite.cli run examples/jobs/fda.yml --offline --max-items 10

# Expected: Runs without network, uses cached/fixture data
```

**Test 26: Run Job (Live)**
```bash
# Run live job with limits
python -m scrapesuite.cli run examples/jobs/fda.yml --live --max-items 5

# Expected: 
# - Fetches from actual URL
# - Respects rate limiting
# - Saves to data/cache/
```

**Test 27: Job with Rate Limiting**
```bash
# Run with custom rate limit
python -m scrapesuite.cli run examples/jobs/fda.yml \
  --live \
  --max-items 10 \
  --rps 0.5

# Expected: Slower execution due to rate limit
```

---

### 2.3 State Management

**Test 28: View State**
```bash
# Check state database
python -m scrapesuite.cli state

# Expected: Shows jobs, cursor positions, item counts
```

**Test 29: Reset Job State**
```bash
# Reset state for specific job
python -m scrapesuite.cli reset fda_recalls

# Verify state was cleared:
python -m scrapesuite.cli state
```

---

### 2.4 Robots.txt Testing

**Test 30: Check Robots.txt**
```bash
# Check if URL is allowed by robots.txt
python -c "
from scrapesuite import check_robots

url = 'https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts'
allowed = check_robots(url, 'ScrapeSuite')
print(f'Allowed: {allowed}')
"

# Expected: True or False based on robots.txt
```

---

## Part 3: Error Handling & Edge Cases

### 3.1 Invalid Input Tests

**Test 31: Invalid Schema File**
```bash
# Try to use non-existent schema
python -m scrapesuite.foundry forge /tmp/nonexistent.yml \
  --file tests/fixtures/fda_list.html

# Expected: Clear error message
```

**Test 32: Invalid HTML File**
```bash
# Try with non-existent HTML
python -m scrapesuite.foundry probe --file /tmp/nonexistent.html

# Expected: File not found error
```

**Test 33: Malformed JSONL**
```bash
# Create malformed JSONL
echo "not valid json" > /tmp/test_output/bad.jsonl

# Try to process it
python -m scrapesuite.foundry polish /tmp/test_output/bad.jsonl \
  --dedupe \
  --output /tmp/test_output/out.jsonl

# Expected: Error with line number
```

**Test 34: Empty Input**
```bash
# Create empty file
touch /tmp/test_output/empty.jsonl

# Try to export it
python -m scrapesuite.foundry crate \
  /tmp/test_output/empty.jsonl \
  /tmp/test_output/empty.csv

# Expected: Handles gracefully (empty CSV or error message)
```

---

### 3.2 Network Error Handling

**Test 35: Invalid URL**
```bash
# Try invalid URL
python -m scrapesuite.foundry probe https://this-domain-does-not-exist-12345.com

# Expected: Network error handling
```

**Test 36: Timeout Handling**
```bash
# Try URL that times out (example)
python -m scrapesuite.foundry forge examples/jobs/fda.yml \
  --url https://httpbin.org/delay/30 \
  --max-pages 1

# Expected: Should timeout gracefully
```

---

## Part 4: Performance & Load Testing

### 4.1 Large File Handling

**Test 37: Large JSONL File**
```bash
# Create large JSONL file (1000 records)
python -c "
import json
with open('/tmp/test_output/large.jsonl', 'w') as f:
    for i in range(1000):
        f.write(json.dumps({'id': i, 'title': f'Article {i}', 'content': 'Lorem ipsum ' * 50}) + '\n')
"

# Process it
time python -m scrapesuite.foundry polish \
  /tmp/test_output/large.jsonl \
  --dedupe \
  --dedupe-keys id \
  --output /tmp/test_output/large_clean.jsonl

# Export to database
time python -m scrapesuite.foundry crate \
  /tmp/test_output/large_clean.jsonl \
  /tmp/test_output/large.db \
  --table records

# Verify count:
sqlite3 /tmp/test_output/large.db "SELECT COUNT(*) FROM records;"
```

**Test 38: Memory Usage**
```bash
# Monitor memory while processing large file
/usr/bin/time -v python -m scrapesuite.foundry crate \
  /tmp/test_output/large.jsonl \
  /tmp/test_output/large_export.csv 2>&1 | grep "Maximum resident"
```

---

## Part 5: Integration Tests

### 5.1 Foundry + Legacy Integration

**Test 39: Export Legacy Job Output with Foundry**
```bash
# Run legacy job to create output
python -m scrapesuite.cli run examples/jobs/fda.yml --offline --max-items 10

# Find the output file
OUTPUT_FILE=$(ls -t data/cache/fda/*.parquet 2>/dev/null | head -1)

# Convert parquet to JSONL (if needed, using pandas)
python -c "
import pandas as pd
import sys
try:
    df = pd.read_parquet('$OUTPUT_FILE')
    df.to_json('/tmp/test_output/legacy_output.jsonl', orient='records', lines=True)
    print('Converted successfully')
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
"

# Process with Foundry tools
python -m scrapesuite.foundry polish \
  /tmp/test_output/legacy_output.jsonl \
  --dedupe \
  --stats \
  --output /tmp/test_output/polished_legacy.jsonl

# Export
python -m scrapesuite.foundry crate \
  /tmp/test_output/polished_legacy.jsonl \
  /tmp/test_output/legacy_final.csv
```

---

## Part 6: Help & Documentation

**Test 40: Help Commands**
```bash
# Main help
python -m scrapesuite.foundry --help

# Tool-specific help
python -m scrapesuite.foundry probe --help
python -m scrapesuite.foundry blueprint --help
python -m scrapesuite.foundry forge --help
python -m scrapesuite.foundry polish --help
python -m scrapesuite.foundry crate --help

# Legacy CLI help
python -m scrapesuite.cli --help
python -m scrapesuite.cli run --help
python -m scrapesuite.cli state --help
```

---

## Verification Checklist

After completing all tests, verify:

- [ ] All Foundry tools execute without errors
- [ ] Pipeline works end-to-end (probe → blueprint → forge → polish → crate)
- [ ] CSV, JSON, and SQLite exports work correctly
- [ ] Deduplication and transformations work as expected
- [ ] Legacy wizard still functional
- [ ] State management works
- [ ] Rate limiting is respected
- [ ] Error messages are clear and helpful
- [ ] Help commands display properly
- [ ] Large files are handled efficiently
- [ ] All output files are created correctly

---

## Cleanup

```bash
# Clean up test outputs
rm -rf /tmp/test_output

# Optional: Reset test state
python -m scrapesuite.cli reset fda_recalls
python -m scrapesuite.cli reset test_job

# Remove test job files if created
rm -f jobs/test_*.yml
```

---

## Quick Smoke Test (30 seconds)

For rapid validation, run these 5 tests:

```bash
# 1. Probe
python -m scrapesuite.foundry probe --file tests/fixtures/fda_list.html

# 2. Blueprint validate
python -m scrapesuite.foundry blueprint validate examples/jobs/fda.yml

# 3. Forge extract
python -m scrapesuite.foundry forge examples/jobs/fda.yml \
  --file tests/fixtures/fda_list.html --output /tmp/quick.jsonl

# 4. Polish dedupe
python -m scrapesuite.foundry polish /tmp/quick.jsonl \
  --dedupe --output /tmp/quick_clean.jsonl

# 5. Crate export
python -m scrapesuite.foundry crate /tmp/quick_clean.jsonl /tmp/quick.csv

# Verify: All 5 commands succeed and files are created
ls -lh /tmp/quick*
```

---

## Troubleshooting

**Issue**: `ModuleNotFoundError`
- **Fix**: Ensure you're in the scrapesuite directory and have installed requirements

**Issue**: `Permission denied` errors
- **Fix**: Use `/tmp` for test outputs or check directory permissions

**Issue**: Tests timeout or hang
- **Fix**: Check network connectivity, use `--max-pages 1` for URL tests

**Issue**: SQLite errors
- **Fix**: Ensure sqlite3 is installed: `sqlite3 --version`

**Issue**: Import errors after cleanup
- **Fix**: Run `python -m pytest -q` to verify all imports still work

---

## Summary

This test plan covers:
- ✅ All 5 Foundry tools
- ✅ Complete end-to-end pipeline
- ✅ Legacy wizard functionality
- ✅ Error handling
- ✅ Performance considerations
- ✅ Integration between old and new systems

**Total Tests**: 40+ manual test scenarios  
**Estimated Time**: 
- Quick smoke test: 1 minute
- Part 1 (Foundry): 20 minutes
- Part 2 (Legacy): 10 minutes
- Parts 3-5 (Edge cases): 15 minutes
- **Full suite**: ~45 minutes
