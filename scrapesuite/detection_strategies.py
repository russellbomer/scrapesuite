"""Advanced detection strategies for extracting structured data."""

from bs4 import BeautifulSoup, Tag


def detect_by_table_headers(html: str, item_selector: str) -> dict[str, str]:
    """
    Strategy: Use table header row to map columns to field types.
    
    Best for: Drupal Views tables, generic HTML tables, data grids
    Confidence: Very High (when headers exist)
    
    Returns: {field_type: selector} mapping
    """
    soup = BeautifulSoup(html, "html.parser")
    field_selectors = {}
    
    # Find the table containing our items
    sample_item = soup.select_one(item_selector)
    if not sample_item or sample_item.name != "tr":
        return {}
    
    # Find the table
    table = sample_item.find_parent("table")
    if not table:
        return {}
    
    # Find header row
    header_row = None
    
    # Strategy 1: Look in <thead>
    thead = table.find("thead")
    if thead:
        header_row = thead.find("tr")
    
    # Strategy 2: First row with <th> elements
    if not header_row:
        for tr in table.find_all("tr"):
            if tr.find("th"):
                header_row = tr
                break
    
    # Strategy 3: First row that looks like a header (short text in all cells)
    if not header_row:
        first_rows = table.find_all("tr", limit=3)
        for tr in first_rows:
            cells = tr.find_all(["td", "th"])
            if cells and all(
                cell.get_text(strip=True) and len(cell.get_text(strip=True)) < 30
                for cell in cells
            ):
                # Check if it's not a data row (no links or complex structure)
                if not tr.find("a") or len(tr.find_all("a")) <= 1:
                    header_row = tr
                    break
    
    if not header_row:
        return {}
    
    # Parse header cells
    header_cells = header_row.find_all(["th", "td"])
    
    # Get a sample data row to find corresponding cells
    data_rows = [r for r in table.find_all("tr") if r != header_row and r.find_parent("tbody")]
    if not data_rows:
        return {}
    
    sample_row = data_rows[0]
    data_cells = sample_row.find_all("td")
    
    if len(data_cells) != len(header_cells):
        # Mismatch - might have rowspan/colspan
        return {}
    
    # Map headers to field types
    field_keywords = {
        "title": ["title", "name", "product", "description", "subject", "heading"],
        "url": ["url", "link", "href", "permalink"],
        "date": ["date", "time", "posted", "published", "created", "updated", "modified"],
        "author": ["author", "by", "user", "company", "brand", "vendor", "publisher"],
        "price": ["price", "cost", "amount"],
        "category": ["category", "type", "class", "tag"],
        "status": ["status", "state"],
        "id": ["id", "number", "#"],
    }
    
    for idx, header_cell in enumerate(header_cells):
        header_text = header_cell.get_text(strip=True).lower()
        
        if not header_text:
            continue
        
        # Try to match to a field type
        for field_type, keywords in field_keywords.items():
            if any(keyword in header_text for keyword in keywords):
                # Generate selector for this column
                data_cell = data_cells[idx]
                
                # Prefer class-based selector if available
                if data_cell.get("class"):
                    selector = f"td.{data_cell['class'][0]}"
                else:
                    # Fall back to nth-child
                    selector = f"td:nth-child({idx + 1})"
                
                # For title and URL, look for <a> within the cell
                if field_type in ("title", "url"):
                    link = data_cell.find("a")
                    if link:
                        if field_type == "title":
                            field_selectors["title"] = f"{selector} a"
                        else:  # url
                            field_selectors["url"] = f"{selector} a::attr(href)"
                    else:
                        # No link, use cell text for title
                        if field_type == "title":
                            field_selectors["title"] = selector
                elif field_type == "date":
                    # Look for <time> element
                    time_elem = data_cell.find("time")
                    if time_elem:
                        field_selectors["date"] = f"{selector} time"
                    else:
                        field_selectors["date"] = selector
                else:
                    field_selectors[field_type] = selector
                
                break  # Found a match, move to next header
    
    return field_selectors


def detect_by_semantic_structure(html: str, item_selector: str) -> dict[str, str]:
    """
    Strategy: Use semantic HTML5 elements and microdata.
    
    Best for: Modern blogs, news sites using <article>, <header>, <time>
    Confidence: High
    
    Returns: {field_type: selector} mapping
    """
    soup = BeautifulSoup(html, "html.parser")
    sample_item = soup.select_one(item_selector)
    
    if not sample_item:
        return {}
    
    field_selectors = {}
    
    # Title: h1, h2, h3 in header or main heading
    for tag in ["h1", "h2", "h3"]:
        heading = sample_item.find(tag)
        if heading:
            link = heading.find("a")
            if link:
                field_selectors["title"] = f"{tag} a"
                field_selectors["url"] = f"{tag} a::attr(href)"
            else:
                field_selectors["title"] = tag
            break
    
    # Date: <time> element or datetime attribute
    time_elem = sample_item.find("time")
    if time_elem:
        field_selectors["date"] = "time"
    
    # Author: rel="author" or itemprop="author"
    author = sample_item.find("a", rel="author")
    if not author:
        author = sample_item.find(attrs={"itemprop": "author"})
    if author:
        field_selectors["author"] = "[rel='author']" if author.get("rel") else "[itemprop='author']"
    
    # Image: first <img> in <figure> or with itemprop="image"
    img = sample_item.find("img", attrs={"itemprop": "image"})
    if img:
        field_selectors["image"] = "img[itemprop='image']::attr(src)"
    else:
        figure = sample_item.find("figure")
        if figure and figure.find("img"):
            field_selectors["image"] = "figure img::attr(src)"
        elif sample_item.find("img"):
            field_selectors["image"] = "img::attr(src)"
    
    return field_selectors


def apply_all_strategies(html: str, item_selector: str) -> dict[str, str]:
    """
    Apply all detection strategies and merge results.
    
    Priority order:
    1. Table headers (very high for tables)
    2. Semantic HTML (high)
    
    Returns merged field selectors with highest-confidence results.
    """
    strategies = [
        ("table_headers", detect_by_table_headers),
        ("semantic", detect_by_semantic_structure),
    ]
    
    merged = {}
    
    for strategy_name, strategy_func in strategies:
        result = strategy_func(html, item_selector)
        
        # Merge, preferring earlier (higher confidence) strategies
        for field_type, selector in result.items():
            if field_type not in merged:
                merged[field_type] = selector
    
    return merged
