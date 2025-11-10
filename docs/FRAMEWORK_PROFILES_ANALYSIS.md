# Framework Profiles: Comprehensive Analysis & Expansion Strategy

## Executive Summary

This document analyzes the current framework profile implementation, identifies gaps, and proposes a comprehensive expansion strategy based on modern web development patterns, emerging frameworks, and alternative detection approaches.

---

## Current State Analysis

### Implemented Profiles (9 total)

1. **DrupalViewsProfile** - Government/enterprise CMS
2. **WordPressProfile** - Popular CMS (40%+ of web)
3. **BootstrapProfile** - CSS framework
4. **TailwindProfile** - Utility-first CSS
5. **ShopifyProfile** - E-commerce platform
6. **DjangoAdminProfile** - Python admin interface
7. **NextJSProfile** - React framework
8. **ReactComponentProfile** - React library
9. **VueJSProfile** - Progressive framework

### Current Strengths

✅ **Good coverage of major ecosystems**: WordPress, Drupal, React, Vue, Django
✅ **CSS framework detection**: Bootstrap, Tailwind
✅ **E-commerce support**: Shopify
✅ **Modern JS frameworks**: Next.js, React, Vue
✅ **Pattern-based detection**: Uses HTML markers, class patterns, meta tags

### Critical Gaps & Limitations

#### 1. **Detection Logic Weaknesses**

**Issue**: Simple string matching can produce false positives
```python
# Current approach
if "views-row" in html or "views-field" in html:
    return True
```

**Problems**:
- No scoring mechanism (first match wins)
- Can't handle sites using multiple frameworks
- String matching too simplistic (matches in comments, JSON data, etc.)

**Better Approach**:
```python
def detect(cls, html: str, item_element: Tag | None = None) -> int:
    """Return confidence score 0-100 instead of boolean."""
    score = 0
    soup = BeautifulSoup(html, "html.parser")
    
    # Multiple signals with weights
    if soup.find(class_=re.compile(r"views-row")):  # Actual element
        score += 40
    if soup.find("meta", attrs={"name": "Generator", "content": re.compile(r"Drupal")}):
        score += 30
    if soup.find("body", class_=re.compile(r"not-front")):
        score += 15
    # etc.
    
    return score
```

#### 2. **Selector Generation Limitations**

**Current issues**:
- No CSS selector validation
- Can't handle complex combinators (>, +, ~)
- No support for :nth-child, :not(), :has()
- Attribute selectors only partially supported
- No pseudo-element handling

**Example gaps**:
```css
/* These patterns aren't handled well */
article:not(.sponsored) > h2
div.card:has(> img.thumbnail)
li:nth-child(odd)
.item:first-of-type
```

#### 3. **Field Type Coverage**

**Currently supported**: title, url, date, author, description, image, price

**Missing critical fields**:
- `category` / `tags`
- `rating` / `score`
- `location` / `address`
- `phone` / `email`
- `published_date` vs `updated_date`
- `thumbnail` vs `full_image`
- `excerpt` vs `full_content`
- `metadata` (JSON-LD, microdata)

#### 4. **No Microdata/Schema.org Integration**

Many modern sites use structured data that's **perfect for scraping**:

```html
<div itemscope itemtype="http://schema.org/Article">
  <h1 itemprop="headline">Title</h1>
  <time itemprop="datePublished">2025-01-15</time>
  <span itemprop="author">John Doe</span>
</div>
```

**Current code**: Completely ignores this goldmine of semantic data

**Proposed**: SchemaOrgProfile that prioritizes microdata attributes

#### 5. **No JSON-LD Extraction**

Many sites embed structured data in `<script type="application/ld+json">`:

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Article Title",
  "datePublished": "2025-01-15",
  "author": {"@type": "Person", "name": "John Doe"}
}
```

**Gap**: No profile extracts this even though it's machine-readable

#### 6. **No Multi-Framework Detection**

Real sites often combine frameworks:
- WordPress + WooCommerce
- Drupal + Bootstrap
- Next.js + Tailwind
- Django + React frontend

**Current**: First match wins, ignores combinations
**Needed**: Composite profile scoring system

---

## Missing Framework Profiles

### High Priority (Wide Adoption)

#### 1. **Angular / AngularJS**
- **Usage**: 20%+ of SPAs, especially enterprise
- **Detection patterns**: 
  - `ng-app`, `ng-controller`, `ng-repeat`, `[ng-*]`
  - `<script src="angular.js">`
  - `data-ng-*` attributes
- **Container patterns**: `[ng-repeat]`, `.ng-scope`, custom directives
- **Field patterns**: `{{}}` template syntax in source, `ng-bind` attributes

#### 2. **Svelte / SvelteKit**
- **Usage**: Fast-growing, modern framework
- **Detection**: 
  - `__SVELTEKIT__`, `/_app/`, `.svelte-`
  - `data-sveltekit-*` attributes
- **Patterns**: Component-scoped CSS, `svelte:head` blocks

#### 3. **Astro**
- **Usage**: Rising static site generator
- **Detection**: `/_astro/`, `.astro` file references, island architecture markers
- **Patterns**: Server-rendered + client-side hydration

#### 4. **Nuxt.js** (Vue meta-framework)
- **Usage**: Popular in enterprise Vue apps
- **Detection**: `__NUXT__`, `/_nuxt/`, `data-n-head`
- **Similar to**: Next.js but for Vue ecosystem

#### 5. **Remix**
- **Usage**: Modern React framework gaining traction
- **Detection**: `__remix`, `/build/`, loader/action patterns

#### 6. **WooCommerce** (WordPress plugin)
- **Usage**: 28% of all e-commerce sites
- **Detection**: `.woocommerce`, `.product`, `.shop`
- **Patterns**: 
  - Product grids: `.products .product`
  - Single product: `.single-product`
  - Price: `.price .woocommerce-Price-amount`

#### 7. **Joomla** (Enhanced)
- **Current**: Missing or minimal
- **Usage**: 2-3% of CMS market, common in enterprise
- **Patterns**: `com_content`, `.item-page`, `#system-message-container`

#### 8. **Ghost** (Blogging platform)
- **Usage**: Popular modern CMS for content creators
- **Detection**: `ghost-version`, `.post-card`, `.gh-`
- **Patterns**: 
  - `.post-card`, `.post-card-title`
  - `.post-card-excerpt`, `.author-name`

#### 9. **Strapi / Headless CMS**
- **Usage**: Increasingly common with JAMstack
- **Detection**: API endpoints, JSON responses
- **Challenge**: Often served via API, not HTML
- **Strategy**: Detect API patterns in network requests

#### 10. **Hugo** (Static site generator)
- **Detection**: `generator="Hugo"`, specific taxonomy patterns
- **Patterns**: Consistent URL structures, taxonomy pages

### E-Commerce Platforms

#### 11. **Magento / Adobe Commerce**
- **Current**: Missing
- **Usage**: 1% but high-value enterprise sites
- **Patterns**: 
  - `.product-item`, `.product-info-main`
  - `data-role="tocart-form"`
  - Magento-specific JS libraries

#### 12. **BigCommerce**
- **Detection**: `.productView`, Stencil theme patterns
- **Patterns**: Similar to Shopify but different class conventions

#### 13. **PrestaShop**
- **Usage**: Popular in Europe
- **Patterns**: `.product-miniature`, `.product-description`

#### 14. **OpenCart**
- **Patterns**: `.product-thumb`, `.product-info`

### Content Management

#### 15. **Contentful** (Headless CMS)
- **Detection**: Via API responses, content delivery patterns
- **Strategy**: Detect API URL patterns

#### 16. **Sanity.io**
- **Detection**: `_type`, `_id` fields in embedded JSON
- **Patterns**: GROQ query patterns

#### 17. **Webflow**
- **Current**: Missing
- **Usage**: Growing among designers/agencies
- **Detection**: `.w-`, `webflow.js`, specific data attributes
- **Patterns**: `.w-dyn-item`, `.w-dyn-list`

#### 18. **Wix**
- **Current**: Missing  
- **Detection**: `wix.com` domains, `data-hook` attributes
- **Patterns**: Wix-specific data attributes, React-based structure

#### 19. **Squarespace**
- **Current**: Missing
- **Detection**: `.sqs-`, `squarespace.com` assets
- **Patterns**: `.sqs-block`, `.BlogItem`, `.ProductItem`

### Forum / Community Platforms

#### 20. **Discourse**
- **Usage**: Modern forum platform (thousands of sites)
- **Detection**: `discourse`, `.topic-list`, `data-topic-id`
- **Patterns**:
  - `.topic-list-item`, `.topic-title`
  - `.topic-body`, `.username`

#### 21. **phpBB**
- **Patterns**: `.topiclist`, `.post`, `viewtopic.php`

#### 22. **vBulletin**
- **Patterns**: `.threadbit`, `.postbit`

#### 23. **Reddit** (public pages)
- **Patterns**: `[data-testid="post"]`, `.Post`, React-based

### Social Media / User-Generated Content

#### 24. **Medium**
- **Current**: Missing
- **Detection**: `medium.com`, specific article structure
- **Patterns**: `article`, `h1`, `.pw-post-title`

#### 25. **Substack**
- **Detection**: `substack.com`, specific post patterns
- **Patterns**: `.post`, `.post-title`, `.post-content`

#### 26. **LinkedIn** (public profiles/posts)
- **Patterns**: React-based, `data-urn` attributes

#### 27. **Twitter/X** (embedded tweets)
- **Patterns**: `.tweet`, `data-tweet-id`

### Enterprise / Specialized

#### 28. **SharePoint**
- **Usage**: Ubiquitous in enterprises
- **Patterns**: `.ms-`, SharePoint-specific classes

#### 29. **Salesforce Community Cloud**
- **Patterns**: `.forceCommunity`, Lightning components

#### 30. **SAP Commerce Cloud**
- **Patterns**: SAP-specific data attributes

### Static Site Generators

#### 31. **Jekyll**
- **Detection**: `generator="Jekyll"`, consistent URL patterns

#### 32. **Gatsby**
- **Detection**: `__gatsby`, `.gatsby-`, webpack bundles
- **Patterns**: GraphQL data layer signatures

#### 33. **Eleventy (11ty)**
- **Detection**: Minimal markers, mostly via build artifacts

#### 34. **Pelican** (Python SSG)
- **Patterns**: Consistent category/tag structures

### Emerging / Niche

#### 35. **htmx**
- **Detection**: `hx-get`, `hx-post`, `hx-target` attributes
- **Patterns**: Server-side rendered with hypermedia controls

#### 36. **Alpine.js**
- **Detection**: `x-data`, `x-bind`, Alpine attributes
- **Patterns**: Often paired with Laravel/Rails

#### 37. **Turbo / Hotwire**
- **Detection**: `data-turbo-track`, `<turbo-frame>`
- **Patterns**: Rails/Phoenix server-rendered SPA

---

## Alternative & Enhanced Detection Strategies

### 1. **Multi-Signal Scoring System**

Instead of boolean detection, use weighted scoring:

```python
class EnhancedFrameworkProfile(FrameworkProfile):
    
    @classmethod
    def get_detection_signals(cls) -> dict[str, int]:
        """Return detection signals with confidence weights."""
        return {
            "meta_generator": 30,      # <meta name="Generator" content="...">
            "body_class": 20,          # <body class="framework-specific">
            "script_src": 25,          # <script src="/framework.js">
            "css_link": 15,            # <link href="/framework.css">
            "dom_pattern": 40,         # Actual DOM elements with classes
            "data_attributes": 20,     # data-framework-*
            "json_ld": 35,             # Structured data
        }
    
    @classmethod
    def detect_with_confidence(cls, html: str) -> tuple[bool, int]:
        """Return (detected, confidence_score)."""
        soup = BeautifulSoup(html, "html.parser")
        signals = cls.get_detection_signals()
        score = 0
        max_score = sum(signals.values())
        
        # Check each signal type...
        # Return (True, 85) for 85% confidence
        return score >= 50, score
```

### 2. **Schema.org / Microdata Priority**

Create a universal profile that prioritizes structured data:

```python
class SchemaOrgProfile(FrameworkProfile):
    """Prioritize Schema.org microdata/JSON-LD."""
    
    name = "schema_org"
    
    @classmethod
    def detect(cls, html: str, item_element: Tag | None = None) -> bool:
        return "itemscope" in html or "application/ld+json" in html
    
    @classmethod
    def extract_json_ld(cls, html: str) -> list[dict]:
        """Extract all JSON-LD scripts."""
        soup = BeautifulSoup(html, "html.parser")
        scripts = soup.find_all("script", type="application/ld+json")
        return [json.loads(s.string) for s in scripts if s.string]
    
    @classmethod
    def get_field_mappings(cls) -> dict[str, list[str]]:
        return {
            "title": ["[itemprop='headline']", "[itemprop='name']"],
            "date": ["[itemprop='datePublished']", "time[itemprop='datePublished']"],
            "author": ["[itemprop='author']", "[itemprop='author'] [itemprop='name']"],
            "description": ["[itemprop='description']", "[itemprop='articleBody']"],
            "image": ["[itemprop='image']", "img[itemprop='image']"],
            "url": ["[itemprop='url']::attr(href)", "a[itemprop='url']::attr(href)"],
        }
```

### 3. **Open Graph / Twitter Card Detection**

Social meta tags are **highly structured** and **consistent**:

```python
class SocialMetaProfile(FrameworkProfile):
    """Extract from Open Graph and Twitter Card meta tags."""
    
    name = "social_meta"
    
    @classmethod
    def extract_metadata(cls, html: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")
        
        meta = {}
        # Open Graph
        for tag in soup.find_all("meta", property=re.compile(r"^og:")):
            key = tag.get("property").replace("og:", "")
            meta[key] = tag.get("content")
        
        # Twitter Card
        for tag in soup.find_all("meta", attrs={"name": re.compile(r"^twitter:")}):
            key = tag.get("name").replace("twitter:", "")
            meta[key] = tag.get("content")
        
        return meta  # {title, description, image, url, etc.}
```

### 4. **Accessibility Attribute Detection**

Modern sites use ARIA attributes that reveal structure:

```python
class AccessibilityProfile(FrameworkProfile):
    """Use ARIA attributes for structure detection."""
    
    @classmethod
    def get_item_selector_hints(cls) -> list[str]:
        return [
            "[role='article']",
            "[role='listitem']",
            "[role='row']",
            "[aria-label*='post']",
            "[aria-label*='item']",
        ]
    
    @classmethod
    def get_field_mappings(cls) -> dict[str, list[str]]:
        return {
            "title": ["[role='heading'][aria-level='1']", "[role='heading'][aria-level='2']"],
            "date": ["time", "[aria-label*='date']", "[aria-label*='published']"],
            "author": ["[rel='author']", "[aria-label*='author']"],
        }
```

### 5. **BEM (Block Element Modifier) Convention Detection**

Many modern sites use BEM naming:

```python
class BEMProfile(FrameworkProfile):
    """Detect BEM naming conventions."""
    
    @classmethod
    def detect_bem_blocks(cls, html: str) -> list[str]:
        """Find BEM block names like 'card', 'post', 'article'."""
        soup = BeautifulSoup(html, "html.parser")
        bem_pattern = re.compile(r"^([a-z][a-z0-9-]*?)(?:__|--)")
        
        blocks = set()
        for elem in soup.find_all(class_=True):
            for cls_name in elem.get("class", []):
                match = bem_pattern.match(cls_name)
                if match:
                    blocks.add(match.group(1))
        
        return list(blocks)  # ['card', 'post', 'article']
```

### 6. **Data Attribute Mining**

Many modern frameworks use `data-*` attributes:

```python
class DataAttributeProfile(FrameworkProfile):
    """Mine data-* attributes for patterns."""
    
    @classmethod
    def find_data_patterns(cls, html: str) -> dict[str, int]:
        """Find common data-* attribute patterns."""
        soup = BeautifulSoup(html, "html.parser")
        patterns = {}
        
        for elem in soup.find_all(True):
            for attr in elem.attrs:
                if attr.startswith("data-"):
                    base = attr.split("-")[1] if len(attr.split("-")) > 1 else attr
                    patterns[base] = patterns.get(base, 0) + 1
        
        return patterns  # {testid: 50, component: 30, id: 25}
```

### 7. **URL Pattern Analysis**

Framework detection from URL structure:

```python
class URLPatternProfile(FrameworkProfile):
    """Detect framework from URL patterns."""
    
    PATTERNS = {
        "wordpress": [r"/wp-content/", r"/wp-includes/", r"\?p=\d+"],
        "drupal": [r"/node/\d+", r"/admin/", r"/sites/default/"],
        "django": [r"/admin/", r"/static/admin/"],
        "rails": [r"/assets/", r"\.html$"],
        "nextjs": [r"/_next/", r"/api/"],
    }
```

### 8. **HTTP Header Analysis**

Server headers often reveal framework:

```python
class HTTPHeaderProfile(FrameworkProfile):
    """Detect via HTTP response headers."""
    
    HEADER_PATTERNS = {
        "x-powered-by": {
            "Express": "express",
            "PHP": "php",
            "ASP.NET": "aspnet",
        },
        "server": {
            "nginx": "nginx",
            "Apache": "apache",
        },
        "x-drupal-cache": "drupal",
        "x-generator": "wordpress",  # Some WP installs
    }
```

### 9. **CSS Class Frequency Analysis**

Statistical approach to detect framework patterns:

```python
class CSSFrequencyProfile(FrameworkProfile):
    """Analyze CSS class usage frequency."""
    
    @classmethod
    def analyze_class_patterns(cls, html: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")
        
        # Count prefixes
        prefixes = {}
        for elem in soup.find_all(class_=True):
            for cls_name in elem.get("class", []):
                prefix = cls_name.split("-")[0] if "-" in cls_name else cls_name
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
        
        # Top prefixes reveal framework
        # wp- = WordPress, views- = Drupal, etc.
        return dict(sorted(prefixes.items(), key=lambda x: x[1], reverse=True)[:10])
```

### 10. **Nested Pattern Detection**

Detect hierarchical patterns (card > header > title):

```python
class HierarchicalProfile(FrameworkProfile):
    """Detect nested component patterns."""
    
    HIERARCHIES = {
        "bootstrap_card": [".card", ".card-header", ".card-title"],
        "wordpress_post": [".post", ".entry-header", ".entry-title"],
        "drupal_node": [".node", ".node__title", ".node__content"],
    }
    
    @classmethod
    def detect_hierarchy(cls, html: str) -> list[str]:
        """Find which hierarchies exist."""
        soup = BeautifulSoup(html, "html.parser")
        found = []
        
        for name, selectors in cls.HIERARCHIES.items():
            # Check if all levels exist in order
            root = soup.select_one(selectors[0])
            if root:
                if all(root.select_one(sel) for sel in selectors[1:]):
                    found.append(name)
        
        return found
```

---

## Recommended Implementation Roadmap

### Phase 1: Core Infrastructure (Week 1-2)

1. **Refactor detection to use scoring system**
   - Change `detect()` to return confidence score 0-100
   - Implement multi-signal scoring
   - Add `detect_all()` to return sorted list of matches

2. **Add Schema.org/JSON-LD extraction**
   - SchemaOrgProfile with microdata support
   - JSON-LD script parsing
   - Automatic field mapping from structured data

3. **Expand field type coverage**
   - Add: category, tags, rating, location, metadata
   - Add: published_date vs updated_date distinction
   - Add: excerpt vs content distinction

### Phase 2: High-Value Profiles (Week 3-4)

4. **Add e-commerce profiles**
   - WooCommerce (high priority - 28% of e-commerce)
   - Magento/Adobe Commerce
   - BigCommerce

5. **Add popular CMS profiles**
   - Ghost blogging platform
   - Webflow
   - Squarespace
   - Wix

6. **Add modern framework profiles**
   - Angular/AngularJS
   - Svelte/SvelteKit
   - Nuxt.js
   - Astro

### Phase 3: Advanced Detection (Week 5-6)

7. **Implement alternative detection strategies**
   - BEM convention detection
   - Data attribute mining
   - URL pattern analysis
   - CSS frequency analysis

8. **Add accessibility-based detection**
   - ARIA attribute patterns
   - Semantic HTML emphasis
   - Screen reader-friendly structure

9. **Social meta extraction**
   - Open Graph tags
   - Twitter Cards
   - Fallback for missing microdata

### Phase 4: Specialized Domains (Week 7-8)

10. **Forum/community platforms**
    - Discourse
    - phpBB
    - Reddit (public pages)

11. **Enterprise platforms**
    - SharePoint
    - Salesforce Community Cloud

12. **Static site generators**
    - Gatsby
    - Hugo
    - Jekyll
    - Eleventy

### Phase 5: Profile Management Tools (Week 9-10)

13. **User-defined profiles**
    - YAML/JSON format for custom profiles
    - Profile inheritance/composition
    - Profile sharing/import

14. **Profile testing framework**
    - Fixtures for each framework
    - Automated detection tests
    - Benchmark suite

15. **Profile analytics**
    - Detection accuracy metrics
    - False positive/negative tracking
    - Profile usage statistics

---

## Advanced Features

### 1. **Composite Profiles**

Handle sites using multiple frameworks:

```python
class CompositeProfile:
    """Combine multiple framework detections."""
    
    def __init__(self, profiles: list[FrameworkProfile]):
        self.profiles = profiles
    
    def get_field_mappings(self) -> dict:
        """Merge field mappings from all profiles."""
        merged = {}
        for profile in self.profiles:
            for field_type, patterns in profile.get_field_mappings().items():
                merged.setdefault(field_type, []).extend(patterns)
        return merged
```

### 2. **Learning System**

Track which patterns work best:

```python
class ProfileLearningSystem:
    """Learn from successful/failed extractions."""
    
    def record_success(self, framework: str, field_type: str, selector: str):
        """Record a successful selector."""
        # Update confidence scores
        pass
    
    def record_failure(self, framework: str, field_type: str, selector: str):
        """Record a failed selector."""
        # Reduce confidence, suggest alternatives
        pass
    
    def suggest_improvements(self, framework: str) -> list[str]:
        """Suggest profile improvements based on data."""
        pass
```

### 3. **Profile Versioning**

Handle framework evolution:

```python
class VersionedProfile(FrameworkProfile):
    """Support multiple framework versions."""
    
    versions = {
        "5.x": {"patterns": [...], "detection": [...]},
        "6.x": {"patterns": [...], "detection": [...]},
        "7.x": {"patterns": [...], "detection": [...]},
    }
    
    @classmethod
    def detect_version(cls, html: str) -> str:
        """Detect framework version."""
        pass
```

### 4. **RegEx-Based Flexible Patterns**

More flexible pattern matching:

```python
class RegexProfile(FrameworkProfile):
    """Use regex for flexible pattern matching."""
    
    @classmethod
    def get_field_mappings(cls) -> dict[str, list[str]]:
        return {
            "title": [
                r"[class*='title']",           # Any class containing 'title'
                r"[class^='post-title']",      # Starts with 'post-title'
                r"[class$='-heading']",        # Ends with '-heading'
                r"[class~='article-title']",   # Word match
            ]
        }
```

---

## Metrics & Success Criteria

### Detection Accuracy
- **Target**: 90%+ precision on framework identification
- **Measure**: False positive rate < 10%
- **Test**: Against 1000+ real-world sites

### Field Extraction Success
- **Target**: 75%+ of fields auto-detected correctly
- **Measure**: Manual verification on sample sites
- **Test**: Per-framework test suites

### Coverage
- **Target**: Support top 30 frameworks (80% of web traffic)
- **Current**: 9 frameworks (~40% coverage)
- **Roadmap**: Add 21+ frameworks over 10 weeks

---

## Conclusion

The current framework profile system is **solid foundation** but has significant **expansion opportunities**:

1. **Technical improvements**: Scoring system, better selector parsing, microdata support
2. **Coverage expansion**: 21+ missing frameworks, especially e-commerce and modern JS
3. **Alternative strategies**: Schema.org, social meta, BEM, data attributes, accessibility
4. **Advanced features**: Composite profiles, learning system, versioning

**Recommended priority order**:
1. Schema.org/JSON-LD (universal, high-value)
2. WooCommerce (28% of e-commerce)
3. Angular (20% of SPAs)
4. Scoring system refactor (improves all profiles)
5. Ghost, Webflow, Squarespace (modern CMS growth)

This roadmap would transform the framework detection from "good coverage of major frameworks" to "comprehensive, intelligent, self-improving system covering 80%+ of modern web."
