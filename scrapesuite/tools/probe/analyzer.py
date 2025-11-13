"""Core analysis engine for Probe tool."""

from collections import Counter
from typing import Any

from bs4 import BeautifulSoup, Tag

from scrapesuite.framework_profiles import detect_all_frameworks, _get_element_classes
from scrapesuite.lib.selectors import build_robust_selector


def analyze_page(html: str, url: str | None = None) -> dict[str, Any]:
    """
    Analyze a web page and return comprehensive structural analysis.
    
    Args:
        html: HTML content to analyze
        url: Optional URL for context
    
    Returns:
        Dictionary with analysis results:
        {
            "url": str,
            "frameworks": [...],      # Detected frameworks
            "containers": [...],      # Potential item containers
            "metadata": {...},        # Title, description, etc.
            "statistics": {...},      # Page stats
            "suggestions": {...}      # Extraction hints
        }
    """
    if not html or not html.strip():
        return {
            "url": url,
            "frameworks": [],
            "containers": [],
            "metadata": {},
            "statistics": {},
            "suggestions": {},
        }
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Detect frameworks
    frameworks = _detect_all_frameworks(html)
    
    # Find containers (repeated item patterns)
    containers = _find_containers(soup)
    
    # Extract metadata
    metadata = _extract_metadata(soup)
    
    # Calculate statistics
    statistics = _calculate_statistics(soup)
    
    # Generate suggestions
    suggestions = _generate_suggestions(soup, containers, frameworks)
    
    return {
        "url": url,
        "frameworks": frameworks,
        "containers": containers,
        "metadata": metadata,
        "statistics": statistics,
        "suggestions": suggestions,
    }


def _detect_all_frameworks(html: str) -> list[dict[str, Any]]:
    """Detect all frameworks in the HTML."""
    frameworks = []
    
    # Parse HTML once for framework detection
    soup = BeautifulSoup(html, "html.parser")
    
    # Use existing framework detection
    body = soup.find("body") or soup
    detected = detect_all_frameworks(html, item_element=body)
    
    for profile_class, score in detected:
        # Get framework name from class
        framework_name = profile_class.__name__.replace("Profile", "").lower()
        
        # Get version if available
        version = None
        if hasattr(profile_class, "get_version"):
            try:
                version = profile_class.get_version(html)
            except Exception:
                pass
        
        # Calculate confidence (score is 0-100)
        confidence = min(score / 100.0, 1.0)
        
        frameworks.append({
            "name": framework_name,
            "confidence": confidence,
            "version": version,
            "score": score,
        })
    
    # Sort by confidence (already sorted by detect_all_frameworks)
    frameworks.sort(key=lambda x: x["confidence"], reverse=True)
    
    return frameworks


def _find_containers(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """Find container elements with repeated children (likely item lists)."""
    containers = []
    
    for container_tag in ["div", "section", "article", "ul", "ol", "table", "tbody"]:
        for container in soup.find_all(container_tag):
            children = list(container.find_all(recursive=False))
            
            if len(children) >= 3:  # At least 3 items
                # Check if children are similar (same tag)
                child_tags = [c.name for c in children if hasattr(c, 'name')]
                if not child_tags:
                    continue
                    
                tag_counts = Counter(child_tags)
                most_common_tag, count = tag_counts.most_common(1)[0]
                
                # If most children share same tag, it's a good container
                if count >= 3:
                    selector = build_robust_selector(container)
                    child_selector = f"{selector} > {most_common_tag}"
                    
                    # Get sample text from first child
                    sample_child = next((c for c in children if hasattr(c, 'name') and c.name == most_common_tag), None)
                    sample_text = sample_child.get_text(strip=True)[:100] if sample_child else ""
                    
                    containers.append({
                        "selector": selector,
                        "child_selector": child_selector,
                        "container_tag": container.name,
                        "child_tag": most_common_tag,
                        "item_count": count,
                        "sample_text": sample_text,
                        "container_class": _get_element_classes(container),
                        "container_id": container.get("id"),
                    })
    
    # Sort by item count (most items first)
    containers.sort(key=lambda x: x["item_count"], reverse=True)
    
    # Return top 10
    return containers[:10]


def _extract_metadata(soup: BeautifulSoup) -> dict[str, Any]:
    """Extract page metadata (title, description, etc.)."""
    metadata = {}
    
    # Title
    title_tag = soup.find("title")
    metadata["title"] = title_tag.get_text(strip=True) if title_tag else ""
    
    # Meta description
    desc_tag = soup.find("meta", attrs={"name": "description"})
    if not desc_tag:
        desc_tag = soup.find("meta", property="og:description")
    metadata["description"] = desc_tag.get("content", "") if desc_tag else ""
    
    # Open Graph
    og_title = soup.find("meta", property="og:title")
    og_image = soup.find("meta", property="og:image")
    og_type = soup.find("meta", property="og:type")
    
    metadata["og"] = {
        "title": og_title.get("content") if og_title else None,
        "image": og_image.get("content") if og_image else None,
        "type": og_type.get("content") if og_type else None,
    }
    
    # Twitter Card
    twitter_card = soup.find("meta", attrs={"name": "twitter:card"})
    twitter_title = soup.find("meta", attrs={"name": "twitter:title"})
    
    metadata["twitter"] = {
        "card": twitter_card.get("content") if twitter_card else None,
        "title": twitter_title.get("content") if twitter_title else None,
    }
    
    # Language
    html_tag = soup.find("html")
    metadata["language"] = html_tag.get("lang") if html_tag else None
    
    # Canonical URL
    canonical = soup.find("link", rel="canonical")
    metadata["canonical"] = canonical.get("href") if canonical else None
    
    return metadata


def _calculate_statistics(soup: BeautifulSoup) -> dict[str, Any]:
    """Calculate page statistics."""
    stats = {}
    
    # Count elements
    stats["total_elements"] = len(soup.find_all(True))
    stats["total_links"] = len(soup.find_all("a", href=True))
    stats["total_images"] = len(soup.find_all("img"))
    stats["total_forms"] = len(soup.find_all("form"))
    stats["total_tables"] = len(soup.find_all("table"))
    stats["total_lists"] = len(soup.find_all(["ul", "ol"]))
    
    # Count headings
    stats["headings"] = {
        f"h{i}": len(soup.find_all(f"h{i}"))
        for i in range(1, 7)
    }
    
    # Text length
    text = soup.get_text(strip=True)
    stats["text_length"] = len(text)
    stats["text_words"] = len(text.split())
    
    # Most common tags
    tag_counter = Counter(tag.name for tag in soup.find_all(True))
    stats["most_common_tags"] = tag_counter.most_common(10)
    
    # Most common classes
    class_counter: Counter[str] = Counter()
    for tag in soup.find_all(True):
        classes = _get_element_classes(tag)
        for cls in classes.split():
            if cls:
                class_counter[cls] += 1
    stats["most_common_classes"] = class_counter.most_common(10)
    
    return stats


def _generate_suggestions(soup: BeautifulSoup, containers: list[dict], frameworks: list[dict]) -> dict[str, Any]:
    """Generate extraction suggestions based on analysis."""
    suggestions = {}
    
    # Best container guess
    if containers:
        suggestions["best_container"] = containers[0]
        suggestions["item_selector"] = containers[0]["child_selector"]
    else:
        suggestions["best_container"] = None
        suggestions["item_selector"] = None
    
    # Field suggestions based on first container
    if containers and containers[0]:
        best = containers[0]
        # Parse the selector to get actual elements
        try:
            items = soup.select(best["child_selector"])
            if items:
                first_item = items[0]
                suggestions["field_candidates"] = _suggest_fields(first_item)
            else:
                suggestions["field_candidates"] = []
        except Exception:
            suggestions["field_candidates"] = []
    else:
        suggestions["field_candidates"] = []
    
    # Framework-specific suggestions
    if frameworks:
        top_framework = frameworks[0]
        suggestions["framework_hint"] = {
            "name": top_framework["name"],
            "confidence": top_framework["confidence"],
            "recommendation": _get_framework_recommendation(top_framework["name"]),
        }
    else:
        suggestions["framework_hint"] = None
    
    return suggestions


def _suggest_fields(item: Tag) -> list[dict[str, str]]:
    """Suggest field selectors within an item."""
    fields = []
    
    # Find common field patterns
    patterns = [
        ("title", ["h1", "h2", "h3", "h4", ".title", ".heading", ".name"]),
        ("link", ["a[href]"]),
        ("image", ["img[src]"]),
        ("description", [".description", ".summary", ".excerpt", "p"]),
        ("date", ["time", ".date", ".published", ".timestamp"]),
        ("author", [".author", ".by", ".username"]),
        ("price", [".price", ".cost", ".amount"]),
        ("category", [".category", ".tag", ".label"]),
    ]
    
    for field_name, selectors in patterns:
        for selector in selectors:
            try:
                elements = item.select(selector)
                if elements:
                    # Found a match
                    elem = elements[0]
                    sample = elem.get_text(strip=True)[:50]
                    fields.append({
                        "name": field_name,
                        "selector": selector,
                        "sample": sample,
                        "count": len(elements),
                    })
                    break  # Only one match per field type
            except Exception:
                continue
    
    return fields


def _get_framework_recommendation(framework_name: str) -> str:
    """Get extraction recommendation based on framework."""
    recommendations = {
        "schema_org": "Use structured data extractors - JSON-LD is already available",
        "opengraph": "Extract Open Graph meta tags for rich previews",
        "twitter_cards": "Extract Twitter Card meta tags for social sharing data",
        "bootstrap": "Look for .card, .list-group-item, .row patterns",
        "tailwind": "Classes are utility-based, rely on semantic HTML structure",
        "react": "May be client-side rendered - check for data-reactid or __NEXT_DATA__",
        "vue": "May use v- directives, look for Vue-specific patterns",
        "nextjs": "Check __NEXT_DATA__ script tag for pre-rendered data",
        "wordpress": "Look for .post, .entry, WP-specific classes",
        "drupal": "Check for .node, .field patterns",
        "shopify": "Product data often in JSON scripts or meta tags",
        "woocommerce": "Products use .product, .woocommerce patterns",
    }
    return recommendations.get(framework_name, "No specific recommendation")
