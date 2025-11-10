#!/usr/bin/env python3
"""Test the wizard HTML analysis on Hacker News."""

import sys

# Fix Windows encoding issues
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from scrapesuite.http import get_html
from scrapesuite.inspector import find_item_selector, inspect_html, preview_extraction

# Test URL
url = "https://news.ycombinator.com/"

print("Fetching HTML from Hacker News...")
html = get_html(url)

print("\n=== HTML Inspection ===")
analysis = inspect_html(html)
print(f"Title: {analysis['title']}")
print(f"Total links: {analysis['total_links']}")

print("\n=== Repeated Classes ===")
for cls_info in analysis['repeated_classes'][:5]:
    sample_text = cls_info['sample_text'][:50]
    try:
        print(f"  .{cls_info['class']} - {cls_info['count']} items - {sample_text}")
    except UnicodeEncodeError:
        # Fallback to ASCII-safe output
        sample_text_safe = sample_text.encode('ascii', errors='ignore').decode('ascii')
        print(f"  .{cls_info['class']} - {cls_info['count']} items - {sample_text_safe}")

print("\n=== Containers ===")
for container in analysis['containers'][:3]:
    print(f"  {container['tag']}.{container['class']} - {container['child_count']} children of {container['child_tag']}")

print("\n=== Item Selector Detection ===")
candidates = find_item_selector(html, min_items=3)
for i, candidate in enumerate(candidates[:5], 1):
    print(f"{i}. {candidate['selector']}")
    print(f"   Count: {candidate['count']}")
    sample_title = candidate.get('sample_title', '')[:60]
    sample_url = candidate.get('sample_url', '')[:60]
    try:
        if sample_title:
            print(f"   Sample: {sample_title}")
        if sample_url:
            print(f"   URL: {sample_url}")
    except UnicodeEncodeError:
        # Fallback to ASCII-safe output
        if sample_title:
            sample_title_safe = sample_title.encode('ascii', errors='ignore').decode('ascii')
            print(f"   Sample: {sample_title_safe}")
        if sample_url:
            print(f"   URL: {sample_url}")
    print()

# Test extraction with .athing (HN story rows)
print("\n=== Testing Extraction ===")
item_selector = ".athing"
print(f"Using selector: {item_selector}")

# Manual field selectors for HN
field_selectors = {
    "title": "span.titleline a",
    "url": "span.titleline a::attr(href)",
}

previews = preview_extraction(html, item_selector, field_selectors)

print(f"\nExtracted {len(previews)} items:")
for i, item in enumerate(previews, 1):
    title = item.get('title', '')[:60]
    url = item.get('url', '')[:60]
    # Handle encoding issues gracefully
    try:
        print(f"\n{i}. {title}")
        print(f"   URL: {url}")
    except UnicodeEncodeError:
        # Fallback to ASCII-safe output
        print(f"\n{i}. {title.encode('ascii', errors='ignore').decode('ascii')}")
        print(f"   URL: {url}")

