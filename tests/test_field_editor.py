"""Tests for interactive field editor."""

from collections import OrderedDict

from quarry.lib.schemas import FieldSchema
from quarry.tools.survey.field_editor import (
    _display_fields_table,
    _get_selector_suggestions,
    _preview_extraction,
    _preview_single_field,
)


def test_display_fields_table_empty():
    """Test displaying empty fields table."""
    fields = OrderedDict()
    # Should not raise an exception
    _display_fields_table(fields)


def test_display_fields_table_with_fields():
    """Test displaying fields table with data."""
    fields = OrderedDict([
        ("title", FieldSchema(selector="h1", required=True)),
        ("url", FieldSchema(selector="a", attribute="href")),
        ("image", FieldSchema(selector="img", attribute="src", required=False)),
    ])
    # Should not raise an exception
    _display_fields_table(fields)


def test_get_selector_suggestions():
    """Test getting selector suggestions from HTML."""
    html = """
    <html>
        <div class="item">
            <h2 class="title">Test Item</h2>
            <a href="/test">Link</a>
            <p class="description">Description text</p>
            <span class="price">$9.99</span>
        </div>
    </html>
    """
    
    suggestions = _get_selector_suggestions(html, ".item", limit=10)
    
    # Should return list of (selector, preview) tuples
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0
    
    # Each suggestion should be a tuple
    for sel, preview in suggestions:
        assert isinstance(sel, str)
        assert isinstance(preview, str)
    
    # Should include common tags
    selectors = [s for s, _ in suggestions]
    assert "h2" in selectors or ".title" in selectors


def test_get_selector_suggestions_no_items():
    """Test selector suggestions with no matching items."""
    html = """
    <html>
        <div class="other">Not an item</div>
    </html>
    """
    
    suggestions = _get_selector_suggestions(html, ".item")
    assert suggestions == []


def test_preview_single_field():
    """Test previewing single field extraction."""
    html = """
    <html>
        <div class="item">
            <h2>Item 1</h2>
        </div>
        <div class="item">
            <h2>Item 2</h2>
        </div>
    </html>
    """
    
    field = FieldSchema(selector="h2")
    # Should not raise an exception
    _preview_single_field(html, ".item", "title", field, limit=2)


def test_preview_extraction():
    """Test previewing full extraction."""
    html = """
    <html>
        <div class="item">
            <h2>Item 1</h2>
            <a href="/item1">Link 1</a>
        </div>
        <div class="item">
            <h2>Item 2</h2>
            <a href="/item2">Link 2</a>
        </div>
    </html>
    """
    
    fields = {
        "title": FieldSchema(selector="h2"),
        "url": FieldSchema(selector="a", attribute="href"),
    }
    
    # Should not raise an exception
    _preview_extraction(html, ".item", fields, limit=2)


def test_preview_extraction_no_items():
    """Test preview with no matching items."""
    html = """
    <html>
        <div class="other">Not an item</div>
    </html>
    """
    
    fields = {
        "title": FieldSchema(selector="h2"),
    }
    
    # Should not raise an exception, should show error
    _preview_extraction(html, ".item", fields)
