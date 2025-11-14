#!/usr/bin/env python3
"""
End-to-end workflow test for Quarry MVP.

Tests the full pipeline: Scout → Survey → Excavate → Polish → Ship → CSV

Usage:
    python scripts/test_workflow.py
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], check: bool = True) -> tuple[int, str]:
    """Run a command and return exit code and output."""
    print(f"\n{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    print('='*60)
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        print(f"\n❌ Command failed with exit code {result.returncode}")
        sys.exit(1)
    
    return result.returncode, result.stdout + result.stderr


def test_weather_workflow():
    """Test weather.gov alerts workflow."""
    print("\n" + "🌩️ " * 20)
    print("TEST 1: Weather.gov Alerts")
    print("🌩️ " * 20)
    
    # Step 1: Scout (optional but good to test)
    print("\n📍 Step 1: Scout analysis")
    run_command([
        "quarry", "scout",
        "https://alerts.weather.gov/cap/us.php?x=0",
        "--batch"
    ])
    
    # Step 2: Use pre-made schema (survey was already tested)
    schema_path = "examples/schemas/weather_simple.yml"
    
    # Step 3: Excavate
    print("\n📍 Step 3: Extract data")
    run_command([
        "quarry", "excavate",
        schema_path,
        "--batch",
        "-o", "test_weather.jsonl"
    ])
    
    # Step 4: Polish (optional - test basic functionality)
    print("\n📍 Step 4: Clean data")
    run_command([
        "quarry", "polish",
        "test_weather.jsonl",
        "-o", "test_weather_clean.jsonl",
        "--batch"
    ])
    
    # Step 5: Ship to CSV
    print("\n📍 Step 5: Export to CSV")
    run_command([
        "quarry", "ship",
        "test_weather_clean.jsonl",
        "test_weather.csv"
    ])
    
    # Verify output
    csv_path = Path("test_weather.csv")
    if csv_path.exists():
        lines = csv_path.read_text().split('\n')
        print(f"\n✅ SUCCESS: Created CSV with {len(lines)-1} rows")
        print(f"   First row: {lines[1][:100]}...")
        return True
    else:
        print(f"\n❌ FAILED: CSV not created")
        return False


def test_hackernews_workflow():
    """Test Hacker News workflow."""
    print("\n" + "📰 " * 20)
    print("TEST 2: Hacker News")
    print("📰 " * 20)
    
    # Step 1: Scout
    print("\n📍 Step 1: Scout analysis")
    run_command([
        "quarry", "scout",
        "https://news.ycombinator.com/",
        "--batch"
    ])
    
    # Step 2: Use pre-made schema
    schema_path = "examples/schemas/hackernews.yml"
    
    # Step 3: Excavate
    print("\n📍 Step 3: Extract data")
    run_command([
        "quarry", "excavate",
        schema_path,
        "--batch",
        "-o", "test_hn.jsonl"
    ])
    
    # Step 4: Ship directly (skip polish)
    print("\n📍 Step 4: Export to CSV")
    run_command([
        "quarry", "ship",
        "test_hn.jsonl",
        "test_hn.csv"
    ])
    
    # Verify output
    csv_path = Path("test_hn.csv")
    if csv_path.exists():
        lines = csv_path.read_text().split('\n')
        print(f"\n✅ SUCCESS: Created CSV with {len(lines)-1} rows")
        return True
    else:
        print(f"\n❌ FAILED: CSV not created")
        return False


def cleanup():
    """Remove test files."""
    test_files = [
        "test_weather.jsonl",
        "test_weather_clean.jsonl",
        "test_weather.csv",
        "test_hn.jsonl",
        "test_hn.csv"
    ]
    
    print("\n🧹 Cleaning up test files...")
    for f in test_files:
        path = Path(f)
        if path.exists():
            path.unlink()
            print(f"   Removed {f}")


def main():
    """Run all workflow tests."""
    print("\n" + "="*60)
    print("QUARRY MVP WORKFLOW TEST")
    print("="*60)
    print("\nThis tests: Scout → Excavate → Polish → Ship → CSV")
    
    results = []
    
    # Test 1: Weather
    try:
        results.append(("Weather.gov", test_weather_workflow()))
    except Exception as e:
        print(f"\n❌ Weather test crashed: {e}")
        results.append(("Weather.gov", False))
    
    # Test 2: Hacker News
    try:
        results.append(("Hacker News", test_hackernews_workflow()))
    except Exception as e:
        print(f"\n❌ Hacker News test crashed: {e}")
        results.append(("Hacker News", False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\n{passed_count}/{total_count} tests passed")
    
    # Cleanup
    cleanup()
    
    # Exit with error if any failed
    if passed_count < total_count:
        sys.exit(1)
    
    print("\n🎉 All workflows successful!")


if __name__ == "__main__":
    main()
