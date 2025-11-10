#!/usr/bin/env python3
"""Test the improved inspector on FDA recalls page."""

import sys
from pathlib import Path

# Fix Windows encoding issues
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from scrapesuite.inspector import find_item_selector

# Use test fixture instead of live fetch
fixture_path = Path("tests/fixtures/fda_list.html")
print(f"Loading HTML from {fixture_path}...")
with open(fixture_path, encoding="utf-8") as f:
    html = f.read()

print("\n=== Item Selector Detection (Improved) ===\n")
candidates = find_item_selector(html, min_items=3)

print(f"Found {len(candidates)} patterns:\n")

for i, candidate in enumerate(candidates[:15], 1):
    print(f"{i:2d}. {candidate['selector']:30s} - {candidate['count']:3d} items")
    sample = candidate.get('sample_title', '')
    if sample:
        # Truncate for display
        if len(sample) > 80:
            sample = sample[:77] + "..."
        try:
            print(f"    Sample: {sample}")
        except UnicodeEncodeError:
            sample_safe = sample.encode('ascii', errors='ignore').decode('ascii')
            print(f"    Sample: {sample_safe}")
    print()

print("\n=== Looking for recalls (10 items expected) ===")
for i, candidate in enumerate(candidates, 1):
    if 8 <= candidate['count'] <= 12:  # Looking for ~10 items
        print(f"✓ Candidate {i}: {candidate['selector']} ({candidate['count']} items)")
        sample = candidate.get('sample_title', '')[:80]
        try:
            print(f"  Sample: {sample}")
        except UnicodeEncodeError:
            sample_safe = sample.encode('ascii', errors='ignore').decode('ascii')
            print(f"  Sample: {sample_safe}")
