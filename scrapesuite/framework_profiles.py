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
                    parts = base_pattern.split()
                    parent_selector = parts[0][1:]  # Remove leading dot from first part
                    child_selector = " ".join(parts[1:])
                    
                    # Find parent element
                    parent = item_element.find(class_=parent_selector)
                    if parent:
                        # Check if child exists
                        if child_selector == "a":
                            if parent.find("a", href=True):
                                return pattern  # Return original with ::attr if present
                        elif child_selector.startswith("img"):
                            if parent.find("img"):
                                return pattern
                        elif child_selector.startswith("time"):
                            if parent.find("time"):
                                return pattern
                        else:
                            # Try generic tag search
                            if parent.find(child_selector.split()[0]):
                                return pattern
                else:
                    # Simple class selector
                    elem = item_element.find(class_=class_name)
                    if elem:
                        return pattern
            elif base_pattern.count(".") > 0 and not base_pattern.startswith("["):
                # Handle tag.class patterns like "th.field-__str__"
                if " " in base_pattern:
                    # Complex selector with descendants
                    parts = base_pattern.split()
                    first_part = parts[0]
                    
                    # Parse tag.class
                    if "." in first_part:
                        tag_name, class_name = first_part.split(".", 1)
                        parent = item_element.find(tag_name, class_=class_name)
                    else:
                        parent = item_element.find(class_=first_part)
                    
                    if parent:
                        # Check for descendant
                        child_selector = " ".join(parts[1:])
                        if child_selector == "a":
                            if parent.find("a", href=True):
                                return pattern
                        elif parent.find(child_selector.split()[0]):
                            return pattern
                else:
                    # Simple tag.class pattern
                    tag_name, class_name = base_pattern.split(".", 1)
                    elem = item_element.find(tag_name, class_=class_name)
                    if elem:
                        return pattern
            elif base_pattern.startswith("["):
                # Attribute selector - parse it
                # Simple implementation for common cases
                if "*=" in base_pattern:
                    # Partial match selector like [class*='title']
                    attr_name = base_pattern.split("*=")[0].replace("[", "").strip()
                    search_value = base_pattern.split("*=")[1].replace("]", "").replace("'", "").replace('"', "").strip()
                    
                    # Find element with attribute containing value
                    for elem in item_element.find_all():
                        attr_val = elem.get(attr_name, "")
                        if isinstance(attr_val, list):
                            attr_val = " ".join(attr_val)
                        if search_value.lower() in str(attr_val).lower():
                            return pattern
                elif "=" in base_pattern:
                    attr_name = base_pattern.split("=")[0].replace("[", "").strip()
                    elem = item_element.find(attrs={attr_name: True})
                    if elem:
                        return pattern
            else:
                # Tag selector or more complex selector
                # Try to find element by tag name
                elem = item_element.find(base_pattern.split()[0])  # Get first part for tag selectors
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


class DjangoAdminProfile(FrameworkProfile):
    """Django Admin interface detection."""
    
    name = "django_admin"
    
    @classmethod
    def detect(cls, html: str, item_element: Tag | None = None) -> bool:
        """Detect Django Admin by looking for admin-specific classes and meta tags."""
        django_indicators = [
            "django-admin",
            "grp-",  # Django Grappelli
            "suit-",  # Django Suit
            "/admin/",
            "djdt",  # Django Debug Toolbar
        ]
        return any(indicator in html for indicator in django_indicators)
    
    @classmethod
    def get_item_selector_hints(cls) -> list[str]:
        """Django Admin list view selectors."""
        return [
            "tbody tr",
            ".result",
            ".grp-row",
            "tr.row1, tr.row2",
        ]
    
    @classmethod
    def get_field_mappings(cls) -> dict[str, list[str]]:
        """Django Admin field mappings."""
        return {
            "title": [
                "th.field-__str__ a",
                ".field-title a",
                ".field-name a",
            ],
            "url": [
                "th.field-__str__ a::attr(href)",
                ".field-title a::attr(href)",
            ],
            "date": [
                ".field-created",
                ".field-modified",
                ".field-date",
                ".field-published",
            ],
            "author": [
                ".field-author",
                ".field-user",
                ".field-created_by",
            ],
        }


class NextJSProfile(FrameworkProfile):
    """Next.js application detection."""
    
    name = "nextjs"
    
    @classmethod
    def detect(cls, html: str, item_element: Tag | None = None) -> bool:
        """Detect Next.js by looking for __NEXT_DATA__ and Next.js-specific attributes."""
        nextjs_indicators = [
            "__NEXT_DATA__",
            "__next",
            "data-nextjs",
            "/_next/",
        ]
        return any(indicator in html for indicator in nextjs_indicators)
    
    @classmethod
    def get_item_selector_hints(cls) -> list[str]:
        """Common Next.js component patterns."""
        return [
            "[class*='card']",
            "[class*='item']",
            "[class*='post']",
            "article",
            "[data-item]",
        ]
    
    @classmethod
    def get_field_mappings(cls) -> dict[str, list[str]]:
        """Next.js typically uses modular CSS or Tailwind - look for semantic patterns."""
        return {
            "title": [
                "h2 a",
                "h3 a",
                "[class*='title']",
                "[class*='heading']",
            ],
            "url": [
                "a[href^='/']::attr(href)",
                "[class*='link']::attr(href)",
            ],
            "date": [
                "time",
                "[datetime]",
                "[class*='date']",
            ],
            "author": [
                "[class*='author']",
                "[rel='author']",
            ],
            "image": [
                "img[src]",
                "[class*='image'] img",
            ],
        }


class ReactComponentProfile(FrameworkProfile):
    """Generic React application detection."""
    
    name = "react"
    
    @classmethod
    def detect(cls, html: str, item_element: Tag | None = None) -> bool:
        """Detect React by looking for data-react attributes and root div."""
        react_indicators = [
            "data-reactroot",
            "data-react-",
            "__REACT",
        ]
        # Only match id="root" or id="app" if data-react* is also present
        if any(indicator in html for indicator in react_indicators):
            return True
        # Be more specific - don't match generic id="app" unless React-specific markers exist
        if 'id="root"' in html and ("data-react" in html or "React" in html):
            return True
        return False
    
    @classmethod
    def get_item_selector_hints(cls) -> list[str]:
        """Common React component patterns."""
        return [
            "[class*='Card']",
            "[class*='Item']",
            "[class*='Post']",
            "[class*='Article']",
            "article",
            "[data-testid*='item']",
        ]
    
    @classmethod
    def get_field_mappings(cls) -> dict[str, list[str]]:
        """React component field mappings (typically use camelCase)."""
        return {
            "title": [
                "[class*='Title']",
                "[class*='Heading']",
                "h2",
                "h3",
            ],
            "url": [
                "a[href]::attr(href)",
                "[class*='Link']::attr(href)",
            ],
            "date": [
                "time",
                "[datetime]",
                "[class*='Date']",
                "[class*='Timestamp']",
            ],
            "author": [
                "[class*='Author']",
                "[class*='User']",
            ],
            "description": [
                "[class*='Description']",
                "[class*='Excerpt']",
                "p",
            ],
        }


class VueJSProfile(FrameworkProfile):
    """Vue.js application detection."""
    
    name = "vuejs"
    
    @classmethod
    def detect(cls, html: str, item_element: Tag | None = None) -> bool:
        """Detect Vue.js by looking for v- directives and Vue-specific attributes."""
        vue_indicators = [
            "v-for=",
            "v-if=",
            "v-bind:",
            ":key=",
            "@click=",
            "__VUE__",
        ]
        return any(indicator in html for indicator in vue_indicators)
    
    @classmethod
    def get_item_selector_hints(cls) -> list[str]:
        """Common Vue.js component patterns."""
        return [
            "[class*='card']",
            "[class*='item']",
            "[class*='post']",
            "article",
            "[v-for]",
        ]
    
    @classmethod
    def get_field_mappings(cls) -> dict[str, list[str]]:
        """Vue.js component field mappings."""
        return {
            "title": [
                "[class*='title']",
                "h2",
                "h3",
            ],
            "url": [
                "a[href]::attr(href)",
                "[class*='link']::attr(href)",
            ],
            "date": [
                "time",
                "[datetime]",
                "[class*='date']",
            ],
            "author": [
                "[class*='author']",
            ],
        }


# Registry of all available profiles
# Order matters: More specific frameworks should come before generic ones
FRAMEWORK_PROFILES: list[type[FrameworkProfile]] = [
    DjangoAdminProfile,     # Very specific (Django admin)
    NextJSProfile,          # Specific (Next.js apps)
    ReactComponentProfile,  # Specific (React apps)
    VueJSProfile,           # Specific (Vue.js apps)
    DrupalViewsProfile,     # Specific CMS
    ShopifyProfile,         # Specific e-commerce
    TailwindProfile,        # Framework/utility CSS
    BootstrapProfile,       # Component library
    WordPressProfile,       # Generic CMS (might match "post" class from others)
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


def is_framework_pattern(selector: str, framework: type[FrameworkProfile] | None) -> bool:
    """
    Check if a selector matches known framework patterns.
    
    Args:
        selector: CSS selector to check
        framework: Detected framework profile class or None
    
    Returns:
        True if selector matches framework patterns
    """
    if not framework:
        return False
    
    # Check if selector matches any container pattern
    for pattern in framework.get_item_selector_hints():
        if pattern in selector or selector in pattern:
            return True
    
    # Check if selector matches any field mapping pattern
    for field_patterns in framework.get_field_mappings().values():
        for pattern in field_patterns:
            # Remove ::attr() suffix for comparison
            base_pattern = pattern.split("::attr(")[0] if "::attr(" in pattern else pattern
            if base_pattern in selector or selector in base_pattern:
                return True
    
    return False

