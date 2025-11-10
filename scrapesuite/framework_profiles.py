"""Framework-specific HTML structure profiles for better field detection."""

from typing import Any

from bs4 import Tag


class FrameworkProfile:
    """Base class for framework-specific detection profiles."""
    
    name: str = "generic"
    
    @classmethod
    def detect(cls, html: str, item_element: Tag | None = None) -> bool:
        """
        Detect if this framework is being used.
        
        Args:
            html: Full page HTML
            item_element: Optional item container element
        
        Returns:
            True if framework detected
        """
        raise NotImplementedError
    
    @classmethod
    def get_item_selector_hints(cls) -> list[str]:
        """
        Get CSS selector patterns likely to match item containers.
        
        Returns:
            List of selector patterns to try
        """
        return []
    
    @classmethod
    def get_field_mappings(cls) -> dict[str, list[str]]:
        """
        Get field type to CSS selector/class pattern mappings.
        
        Returns:
            Dict mapping field types to list of selector patterns
        """
        return {}
    
    @classmethod
    def generate_field_selector(cls, item_element: Tag, field_type: str) -> str | None:
        """
        Generate field selector using framework-specific knowledge.
        
        Args:
            item_element: Item container element
            field_type: Field type to detect
        
        Returns:
            CSS selector string or None
        """
        mappings = cls.get_field_mappings()
        patterns = mappings.get(field_type, [])
        
        for pattern in patterns:
            # Handle ::attr() syntax for attribute extraction
            has_attr = "::attr(" in pattern
            if has_attr:
                # Split pattern and attr
                base_pattern = pattern.split("::attr(")[0].strip()
                # attr_name = pattern.split("::attr(")[1].rstrip(")")
            else:
                base_pattern = pattern
            
            # Try to find element matching pattern
            if base_pattern.startswith("."):
                # Class selector
                class_name = base_pattern[1:].split()[0]  # Get first class if pattern has spaces
                
                # Handle patterns like ".class a" (selector with descendant)
                if " " in base_pattern:
                    # Split into parent and child
                    parent_class = base_pattern.split()[0][1:]  # Remove leading dot
                    child_selector = " ".join(base_pattern.split()[1:])
                    
                    # Find parent element
                    parent = item_element.find(class_=parent_class)
                    if parent:
                        # Check if child exists
                        if child_selector == "a":
                            if parent.find("a", href=True):
                                return pattern  # Return original with ::attr if present
                        elif child_selector.startswith("img"):
                            if parent.find("img"):
                                return pattern
                else:
                    # Simple class selector
                    elem = item_element.find(class_=class_name)
                    if elem:
                        return pattern
            elif base_pattern.startswith("["):
                # Attribute selector - parse it
                # Simple implementation for common cases
                if "=" in base_pattern:
                    attr_name = base_pattern.split("=")[0].replace("[", "").strip()
                    elem = item_element.find(attrs={attr_name: True})
                    if elem:
                        return pattern
            else:
                # Tag selector
                elem = item_element.find(base_pattern)
                if elem:
                    return pattern
        
        return None


class DrupalViewsProfile(FrameworkProfile):
    """Drupal Views module - very common for listing pages."""
    
    name = "drupal_views"
    
    @classmethod
    def detect(cls, html: str, item_element: Tag | None = None) -> bool:
        """Detect Drupal Views by looking for characteristic classes."""
        if "views-row" in html or "views-field" in html:
            return True
        if item_element:
            classes = " ".join(item_element.get("class", []))
            if "views-row" in classes:
                return True
        return False
    
    @classmethod
    def get_item_selector_hints(cls) -> list[str]:
        """Drupal Views typically uses .views-row or table rows."""
        return [
            ".views-row",
            "tr.views-row-first",
            "tr.even",
            "tr.odd",
            "tbody > tr",
            ".view-content .views-row",
        ]
    
    @classmethod
    def get_field_mappings(cls) -> dict[str, list[str]]:
        """Common Drupal Views field classes."""
        return {
            "title": [
                ".views-field-field-product-description",
                ".views-field-title",
                ".views-field-name",
                ".views-field-field-title",
                ".field-content",
            ],
            "url": [
                ".views-field-field-product-description a::attr(href)",
                ".views-field-title a::attr(href)",
                ".views-field-name a::attr(href)",
                ".views-field-path a::attr(href)",
            ],
            "date": [
                ".views-field-field-date",
                ".views-field-created",
                ".views-field-changed",
                ".views-field-post-date",
            ],
            "author": [
                ".views-field-company-name",
                ".views-field-brand-name",
                ".views-field-name",  # User name field
                ".views-field-uid",
                ".views-field-author",
                ".views-field-field-author",
            ],
            "body": [
                ".views-field-field-recall-reason-description",
                ".views-field-body",
                ".views-field-field-body",
                ".views-field-description",
            ],
            "image": [
                ".views-field-field-image img",
                ".views-field-field-photo img",
            ],
        }


class WordPressProfile(FrameworkProfile):
    """WordPress - extremely common CMS."""
    
    name = "wordpress"
    
    @classmethod
    def detect(cls, html: str, item_element: Tag | None = None) -> bool:
        """Detect WordPress by looking for characteristic classes."""
        wp_indicators = ["wp-content", "post-", "entry-", "hentry"]
        if any(indicator in html for indicator in wp_indicators):
            return True
        if item_element:
            classes = " ".join(item_element.get("class", []))
            if any(indicator in classes for indicator in ["post", "entry", "hentry", "article"]):
                return True
        return False
    
    @classmethod
    def get_item_selector_hints(cls) -> list[str]:
        """WordPress post/article selectors."""
        return [
            "article.post",
            ".post",
            ".hentry",
            "article.hentry",
            ".entry",
            ".type-post",
        ]
    
    @classmethod
    def get_field_mappings(cls) -> dict[str, list[str]]:
        """Common WordPress classes."""
        return {
            "title": [
                ".entry-title",
                ".post-title",
                "h2.entry-title",
                "h1.entry-title",
            ],
            "url": [
                ".entry-title a",
                ".post-title a",
            ],
            "date": [
                ".entry-date",
                ".post-date",
                ".published",
                "time.entry-date",
            ],
            "author": [
                ".author",
                ".entry-author",
                ".post-author",
                ".by-author",
            ],
            "body": [
                ".entry-content",
                ".entry-summary",
                ".post-content",
            ],
            "image": [
                ".post-thumbnail img",
                ".entry-image img",
            ],
        }


class BootstrapProfile(FrameworkProfile):
    """Bootstrap framework - very common for cards/listings."""
    
    name = "bootstrap"
    
    @classmethod
    def detect(cls, html: str, item_element: Tag | None = None) -> bool:
        """Detect Bootstrap by looking for characteristic classes."""
        if "card" in html or "list-group-item" in html or "media" in html:
            return True
        if item_element:
            classes = " ".join(item_element.get("class", []))
            if any(indicator in classes for indicator in ["card", "list-group-item", "media"]):
                return True
        return False
    
    @classmethod
    def get_item_selector_hints(cls) -> list[str]:
        """Bootstrap component selectors."""
        return [
            ".card",
            ".list-group-item",
            ".media",
            ".row .col",
        ]
    
    @classmethod
    def get_field_mappings(cls) -> dict[str, list[str]]:
        """Common Bootstrap patterns."""
        return {
            "title": [
                ".card-title",
                ".media-heading",
                "h5.card-title",
            ],
            "url": [
                ".card-title a",
                ".card-link",
            ],
            "date": [
                ".card-subtitle",
                ".text-muted",
            ],
            "body": [
                ".card-text",
                ".card-body",
                ".media-body",
            ],
            "image": [
                ".card-img-top",
                ".media-object",
            ],
        }


class TailwindProfile(FrameworkProfile):
    """Tailwind CSS - increasingly popular utility-first framework."""
    
    name = "tailwind"
    
    @classmethod
    def detect(cls, html: str, item_element: Tag | None = None) -> bool:
        """
        Tailwind is harder to detect as it uses utility classes.
        Look for common patterns like flex, grid, space-y, etc.
        """
        tailwind_patterns = [
            "flex", "grid", "space-y", "gap-", "p-", "m-", 
            "text-", "bg-", "rounded", "shadow"
        ]
        # Need multiple matches since these are generic
        matches = sum(1 for pattern in tailwind_patterns if pattern in html)
        return matches >= 5
    
    @classmethod
    def get_item_selector_hints(cls) -> list[str]:
        """Tailwind often uses semantic tags with utility classes."""
        return [
            "article",
            "li",
            "div[class*='flex']",
            "div[class*='grid']",
        ]
    
    @classmethod
    def get_field_mappings(cls) -> dict[str, list[str]]:
        """Tailwind uses semantic HTML, so defer to generic detection."""
        return {}


class ShopifyProfile(FrameworkProfile):
    """Shopify e-commerce platform."""
    
    name = "shopify"
    
    @classmethod
    def detect(cls, html: str, item_element: Tag | None = None) -> bool:
        """Detect Shopify by looking for product/collection classes."""
        shopify_indicators = ["product-", "collection-", "shopify"]
        return any(indicator in html for indicator in shopify_indicators)
    
    @classmethod
    def get_item_selector_hints(cls) -> list[str]:
        """Shopify product selectors."""
        return [
            ".product-card",
            ".product-item",
            ".grid-product",
            ".collection-item",
        ]
    
    @classmethod
    def get_field_mappings(cls) -> dict[str, list[str]]:
        """Common Shopify product fields."""
        return {
            "title": [
                ".product-card__title",
                ".product-title",
                ".grid-product__title",
            ],
            "url": [
                ".product-card__title a",
                ".product-link",
            ],
            "price": [
                ".product-price",
                ".price",
                ".grid-product__price",
            ],
            "image": [
                ".product-card__image img",
                ".grid-product__image img",
            ],
        }


# Registry of all available profiles
FRAMEWORK_PROFILES: list[type[FrameworkProfile]] = [
    DrupalViewsProfile,
    WordPressProfile,
    BootstrapProfile,
    ShopifyProfile,
    TailwindProfile,
]


def detect_framework(html: str, item_element: Tag | None = None) -> type[FrameworkProfile] | None:
    """
    Detect which framework is being used.
    
    Args:
        html: Full page HTML
        item_element: Optional item container element
    
    Returns:
        Detected framework profile class or None
    """
    for profile_class in FRAMEWORK_PROFILES:
        if profile_class.detect(html, item_element):
            return profile_class
    
    return None


def get_framework_field_selector(
    framework: type[FrameworkProfile],
    item_element: Tag,
    field_type: str,
) -> str | None:
    """
    Get field selector using framework-specific knowledge.
    
    Args:
        framework: Framework profile class
        item_element: Item container element
        field_type: Field type to detect
    
    Returns:
        CSS selector string or None
    """
    return framework.generate_field_selector(item_element, field_type)
