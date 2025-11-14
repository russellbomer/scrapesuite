# Quick Start - Extract Data in 5 Minutes

This guide shows you how to extract real data from a website in under 5 minutes.

## 1. Install Quarry

```bash
pip install -e .
```

## 2. Extract Weather Alerts (No Config Needed)

Use the pre-built weather alerts schema:

```bash
quarry excavate examples/schemas/weather_simple.yml
```

**Output**: Creates `output.jsonl` with 40+ current weather alerts!

**View the data**:
```bash
head -1 output.jsonl | python -m json.tool
```

## 3. Convert to CSV

```bash
quarry ship output.jsonl alerts.csv
```

**Done!** You now have a CSV file with weather alerts.

---

## Create Your Own Schema

### Option A: Use Survey Builder (Interactive)

```bash
quarry survey create --url https://example.com
```

Follow the prompts to:
1. Select item containers
2. Add/edit/preview fields
3. Save the schema

### Option B: Write YAML Manually

Create `my_schema.yml`:

```yaml
name: my_extraction
version: 1

url: https://example.com

item_selector: "article"  # CSS selector for items

fields:
  title:
    selector: "h2"
    required: true
  
  link:
    selector: "a"
    attribute: "href"
  
  date:
    selector: "time"
```

Then run:

```bash
quarry excavate my_schema.yml
```

---

## Full Workflow Example

Let's extract from a real government site:

```bash
# 1. Analyze the site (optional but recommended)
quarry scout https://data.cdc.gov/browse

# 2. Create a schema interactively
quarry survey create --url https://data.cdc.gov/browse

# 3. Or use this manual schema
cat > cdc_datasets.yml << 'EOF'
name: cdc_datasets
version: 1
url: https://data.cdc.gov/browse

item_selector: ".browse2-result"

fields:
  title:
    selector: ".browse2-result-name-link"
    required: true
  
  description:
    selector: ".browse2-result-description"
  
  category:
    selector: ".browse2-result-category"
  
  updated:
    selector: ".browse2-result-modified"
EOF

# 4. Extract the data
quarry excavate cdc_datasets.yml -o cdc_data.jsonl

# 5. Convert to CSV
quarry ship cdc_data.jsonl cdc_data.csv

# 6. Open in Excel/Numbers/LibreOffice
open cdc_data.csv
```

---

## What Each Command Does

| Command | Purpose | Example |
|---------|---------|---------|
| `scout` | Analyze site structure, detect frameworks | `quarry scout URL` |
| `survey create` | Interactive schema builder | `quarry survey create --url URL` |
| `excavate` | Extract data using schema | `quarry excavate schema.yml` |
| `polish` | Clean/transform data | `quarry polish input.jsonl -o cleaned.jsonl` |
| `ship` | Export to CSV/Parquet | `quarry ship input.jsonl output.csv` |

---

## Troubleshooting

**No data extracted?**
- Run `quarry scout URL` to see detected containers
- Try different `item_selector` values
- Check if site requires JavaScript (won't work with basic scraping)

**Empty fields?**
- Selectors might be wrong
- Use browser DevTools to find correct selectors
- Try relative selectors (e.g., `h2` instead of `.css-abc123`)

**Site blocks you?**
- Respect robots.txt
- Add delays between requests
- Consider if scraping is appropriate

---

## Next Steps

- Read [USAGE_GUIDE.md](USAGE_GUIDE.md) for advanced features
- Check [examples/schemas/](examples/schemas/) for more examples
- Learn about [pagination, transforms, and sinks](docs/)
