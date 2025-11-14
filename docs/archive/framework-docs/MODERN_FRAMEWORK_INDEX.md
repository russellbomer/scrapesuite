# Modern Framework Support - Documentation Index

**Quarry includes comprehensive tools for handling modern JavaScript frameworks with dynamic CSS.**

---

## 📚 Documentation Suite

### 🎯 Getting Started

1. **[Quick Start: Modern Sites](QUICK_START_MODERN_SITES.md)** ⭐ **START HERE**
   - 10-minute tutorial
   - Real NYT example
   - Step-by-step walkthrough
   - Troubleshooting guide
   - **Best for:** First-time users

2. **[Selector Quick Reference](SELECTOR_QUICK_REFERENCE.md)** ⭐ **BOOKMARK THIS**
   - DO/DON'T patterns
   - Common extraction scenarios
   - Framework-specific patterns
   - Quick decision tree
   - **Best for:** Daily reference

---

### 📖 In-Depth Guides

3. **[Dynamic CSS Strategy](DYNAMIC_CSS_STRATEGY.md)** 📘 **COMPREHENSIVE**
   - Complete problem analysis
   - Solution architecture
   - 5 major components explained
   - Real-world NYT case study
   - Best practices
   - Migration guide
   - Testing strategies
   - Future roadmap
   - **Best for:** Understanding the full system

4. **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** 🔧 **TECHNICAL**
   - Problem statement
   - Solutions implemented
   - Integration points
   - Usage workflows
   - Testing strategy
   - Future enhancements
   - Metrics & success criteria
   - **Best for:** Developers & contributors

---

### 🛠️ Tools & Utilities

5. **Selector Audit Tool** - `scripts/audit_schema_selectors.py`
   ```bash
   python scripts/audit_schema_selectors.py my_schema.yml
   ```
   - Detects brittle selectors
   - Suggests robust alternatives
   - Generates migration reports
   - Severity scoring (ok/medium/high)

6. **Selector Utilities Library** - `quarry/lib/selectors.py`
   ```python
   from quarry.lib.selectors import (
       build_robust_selector,
       validate_selector,
       build_fallback_chain,
       SelectorChain
   )
   ```
   - Selector validation
   - Dynamic CSS detection
   - Robust selector building
   - Fallback chain generation

7. **Framework Detection** - `quarry/framework_profiles.py`
   ```python
   from quarry.framework_profiles import (
       detect_framework,
       suggest_extraction_strategy
   )
   ```
   - Identifies React, Vue, Angular, Drupal, WordPress
   - Confidence scoring
   - Framework-specific patterns
   - Strategy recommendations

---

### 📝 Examples & Templates

8. **Working Schema Example** - `examples/schemas/nyt_resilient.yml`
   - Production-ready NYT schema
   - Structural selectors throughout
   - Inline documentation
   - Maintenance notes

9. **Utility Examples** - `examples/use_selector_utilities.py`
   - 5 complete workflow examples
   - Real-world integration
   - Copy-paste ready code
   - Framework detection demo

---

## 🗺️ Learning Paths

### Path 1: "I need to scrape a modern site NOW"
1. Read [Quick Start](QUICK_START_MODERN_SITES.md) (10 min)
2. Copy [NYT example](../examples/schemas/nyt_resilient.yml)
3. Modify for your site
4. Validate with audit tool
5. Deploy

**Time:** 30 minutes

---

### Path 2: "I want to understand the system"
1. Read [Dynamic CSS Strategy](DYNAMIC_CSS_STRATEGY.md) (30 min)
2. Study [Implementation Summary](IMPLEMENTATION_SUMMARY.md) (15 min)
3. Review [selector utilities code](../quarry/lib/selectors.py)
4. Review [framework profiles code](../quarry/framework_profiles.py)
5. Try [example workflows](../examples/use_selector_utilities.py)

**Time:** 2 hours

---

### Path 3: "I need to migrate existing schemas"
1. Read [Selector Quick Reference](SELECTOR_QUICK_REFERENCE.md) (5 min)
2. Run audit tool on existing schemas
3. Read migration guide in [Dynamic CSS Strategy](DYNAMIC_CSS_STRATEGY.md#migration-guide)
4. Update selectors based on suggestions
5. Re-validate with audit tool

**Time:** 1-2 hours per schema

---

### Path 4: "I want to contribute"
1. Read [Implementation Summary](IMPLEMENTATION_SUMMARY.md)
2. Study [integration points](IMPLEMENTATION_SUMMARY.md#integration-points)
3. Review [pending work](IMPLEMENTATION_SUMMARY.md#pending-work)
4. Check [future enhancements](DYNAMIC_CSS_STRATEGY.md#future-enhancements)
5. Pick a task and start coding

**Time:** Varies

---

## 🎯 Quick Links by Use Case

### "My schema stopped working"
→ [Troubleshooting](QUICK_START_MODERN_SITES.md#troubleshooting)

### "I'm getting None values"
→ [Fields extracting as None](QUICK_START_MODERN_SITES.md#fields-extracting-as-none)

### "What selectors should I use for React?"
→ [React patterns](SELECTOR_QUICK_REFERENCE.md#react--nextjs--css-in-js)

### "How do I detect frameworks?"
→ [Framework detection](../quarry/framework_profiles.py)

### "How do I validate selectors?"
→ [Selector validation](../quarry/lib/selectors.py)

### "What's the best practice for titles?"
→ [Common patterns](SELECTOR_QUICK_REFERENCE.md#title-extraction)

### "How do I build fallback chains?"
→ [Fallback chains](SELECTOR_QUICK_REFERENCE.md#advanced-selector-fallback-chains)

### "Where's the complete API reference?"
→ [Implementation Summary](IMPLEMENTATION_SUMMARY.md)

---

## 📊 Documentation Stats

```
Total Documents:     4 guides + 3 tools
Total Pages:         ~100 equivalent pages
Code Examples:       50+
Real Examples:       NYT, Guardian, WordPress, Drupal
Frameworks Covered:  React, Vue, Angular, Drupal, WordPress, CSS-in-JS
Tools:               3 (audit, utilities, detection)
```

---

## 🔄 Update Schedule

- **Quick Reference:** Updated with each framework addition
- **Strategy Guide:** Updated quarterly with new patterns
- **Implementation Summary:** Updated with each major release
- **Examples:** Added as new use cases emerge

---

## 🤝 Contributing to Docs

Found a typo? Have a better example? Want to add a framework?

1. Edit the relevant markdown file
2. Test any code examples
3. Submit PR with clear description
4. Update this index if adding new docs

---

## 📞 Support

**Questions about modern framework support?**
- Check [Quick Start](QUICK_START_MODERN_SITES.md) first
- Try [Quick Reference](SELECTOR_QUICK_REFERENCE.md)
- Read [Strategy Guide](DYNAMIC_CSS_STRATEGY.md)
- Still stuck? Open GitHub issue

**Bug in selector utilities?**
- Check [Implementation Summary](IMPLEMENTATION_SUMMARY.md#testing-strategy)
- Run test suite: `pytest tests/`
- Open issue with reproducible example

**Want new framework support?**
- See [Contributing guide](DYNAMIC_CSS_STRATEGY.md#contributing)
- Study existing profiles in `quarry/framework_profiles.py`
- Submit PR with profile + tests

---

## 🗺️ Roadmap

**Current (v2.0):**
- ✅ Selector utilities library
- ✅ Framework detection system
- ✅ Audit tools
- ✅ Complete documentation

**Next (v2.1):**
- [ ] Selector chain integration into GenericConnector
- [ ] Wizard framework integration
- [ ] Unit tests for all utilities
- [ ] Performance benchmarks

**Future (v2.2+):**
- [ ] Auto-healing selectors
- [ ] Visual selector builder
- [ ] Schema version control
- [ ] ML-based selector suggestion

See [full roadmap](DYNAMIC_CSS_STRATEGY.md#future-enhancements) for details.

---

**Last Updated:** 2024  
**Maintainer:** Quarry Team
