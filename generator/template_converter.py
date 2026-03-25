"""
Template Converter — converts Luma phtml templates to Hyvä equivalents.
Uses Hyvä patterns: Alpine.js, Tailwind CSS, no KnockoutJS/RequireJS.

Strategies:
  - "rewrite":   Replace with pre-built Alpine.js Hyvä equivalent from generator/templates/
  - "preserve":  Copy original template as-is (complex templates where rewrite loses structure)
  - "skip":      Use Hyvä default (don't generate any override)
  - "copy":      Copy unchanged (email templates, simple helpers)
  - "remove":    Delete (KnockoutJS .html templates)
  - "customize": Hyvä handles layouts — no template override needed
  - "analyze":   Unknown — flagged for manual review

"preserve" vs "rewrite":
  Use "preserve" when the original template has:
    - Deep navigation structures (3+ levels) with CMS blocks
    - Complex jQuery scripts that are tightly coupled to the HTML structure
    - Brand-specific CSS class hierarchies (ebene1, ebenex, ebene2, etc.)
    - Extensive mobile-specific DOM elements
    - Inline styles for region-specific UI (bilingual popups, etc.)
  In these cases, preserving the original ensures visual fidelity.
  The LESS/jQuery stack from Luma parent still works, so originals render correctly.
"""
import os
import re
from pathlib import Path


# Complexity thresholds for auto-detection
PRESERVE_LINE_THRESHOLD = 300       # Templates above this many lines → prefer preserve
PRESERVE_JQUERY_PATTERNS = 5        # Templates with 5+ jQuery patterns → prefer preserve
PRESERVE_NAVIGATION_DEPTH = 2       # Templates with nested category loops → prefer preserve

# Patterns that indicate high complexity (hard to rewrite faithfully)
HIGH_COMPLEXITY_PATTERNS = [
    # Navigation complexity (universal across Magento themes)
    r'getChildrenCategories\(\)',       # Multi-level category navigation
    r'getSubcategories\(\)',            # Subcategory tree rendering
    r'getLevel\(\)',                    # Category level depth check
    r'nav-back-link|close-nav-arrow',   # Mobile navigation controls
    r'nav-toggle|menu-toggle',         # Hamburger menu patterns

    # CMS block integration
    r'setBlockId\(|cms/block/render',  # CMS blocks embedded in templates
    r'\{\{block\s+class=',            # Magento widget syntax in content

    # jQuery / RequireJS (common across all Luma themes)
    r'ObjectManager::getInstance',      # Direct ObjectManager usage
    r'\$\(document\)\.on\(',            # jQuery delegated event handlers
    r'\.appendTo\(|\.fadeIn\(|\.slideToggle\(',  # jQuery DOM manipulation
    r'\.toggle\(\)|\.toggleClass\(',    # jQuery toggle patterns
    r'matchMedia\(',                    # Responsive JS breakpoints
    r'localStorage\.',                  # Client storage state management
    r'require\(\[',                    # RequireJS module loading
    r'data-mage-init=',               # Magento JS widgets

    # Theme-specific navigation tiers (common patterns across brands)
    r'\.(ebene|level|tier|depth)[_-]?\d',  # Multi-level nav CSS classes
    r'mega-?menu|megamenu',            # Megamenu structures
    r'dropdown-menu.*dropdown-menu',   # Nested dropdown menus
]


# Filename patterns that indicate header/footer templates (auto-detect across themes)
# These templates are typically complex and should be preserved
HEADER_FOOTER_PATTERNS = [
    r'header\.phtml$',                # Standard header template
    r'ftcheader\.phtml$',             # FTC custom header
    r'custom[_-]?header\.phtml$',     # Custom header variants
    r'navigation\.phtml$',            # Navigation templates
    r'topmenu\.phtml$',               # Top menu template
    r'footer\.phtml$',                # Standard footer template
    r'custom[_-]?footer\.phtml$',     # Custom footer variants
]


def is_header_footer_template(rel_path: str) -> bool:
    """Check if a template path matches known header/footer patterns."""
    filename = os.path.basename(rel_path)
    parent_dir = os.path.dirname(rel_path)
    # Only match templates inside Magento_Theme/templates/html/ or similar theme paths
    if 'Magento_Theme/templates' not in rel_path:
        return False
    return any(re.search(pat, filename) for pat in HEADER_FOOTER_PATTERNS)


# Maps Luma modules to their Hyvä template handling strategy
TEMPLATE_STRATEGY = {
    # Templates that Hyvä provides natively — use Hyvä defaults, only customize styling
    "Magento_Catalog/layout": "customize",
    "Magento_Checkout/layout": "customize",
    "Magento_Customer/layout": "customize",
    "Magento_Sales/layout": "customize",

    # Complex header/footer: REWRITE with Hyvä Alpine.js versions
    # Header: centered logo layout with Hyvä Alpine.js components
    # Footer: renders footer CMS block with Alpine.js newsletter
    "Magento_Theme/templates/html/ftcheader.phtml": "preserve",
    "Magento_Theme/templates/html/footer.phtml": "rewrite",
    "Magento_Theme/templates/html/header.phtml": "rewrite",

    # Product list: Hyvä provides its own — custom overrides break product display
    "Magento_Catalog/templates/product/list.phtml": "skip",
    "Magento_Catalog/templates/product/list/items.phtml": "skip",
    "Magento_Catalog/templates/product/list/toolbar.phtml": "skip",  # Hyvä has its own
    "Magento_Catalog/templates/product/list/toolbar/amount.phtml": "skip",
    "Magento_Catalog/templates/product/list/toolbar/sorter.phtml": "skip",
    # Product view: Hyvä provides its own — only override if truly needed
    # Store-specific overrides (size charts, material attributes) should be
    # placed in the store's theme, not generated by the migration tool
    "Magento_Catalog/templates/product/view/addtocart.phtml": "skip",
    "Magento_Catalog/templates/product/view/gallery.phtml": "skip",
    "Magento_Catalog/templates/product/view/images.phtml": "skip",
    "Magento_Catalog/templates/product/view/details.phtml": "skip",  # Hyvä default OK
    "Magento_Catalog/templates/product/view/overview.phtml": "skip",
    "Magento_Catalog/templates/product/view/underview.phtml": "skip",
    "Magento_Catalog/templates/category/cms.phtml": "skip",

    "Magento_CatalogWidget/templates/product/widget/content/grid.phtml": "rewrite",

    "Magento_Checkout/templates/cart/minicart.phtml": "rewrite",
    "Magento_Checkout/templates/cart.phtml": "skip",  # Hyvä provides
    "Magento_Checkout/templates/cart/form.phtml": "skip",
    "Magento_Checkout/templates/cart/item/default.phtml": "skip",
    "Magento_Checkout/templates/cart/item/configure/updatecart.phtml": "skip",
    "Magento_Checkout/templates/cart/item/renderer/actions/edit.phtml": "skip",
    "Magento_Checkout/templates/cart/item/renderer/actions/remove.phtml": "skip",

    # KnockoutJS templates — not needed in Hyvä
    "Magento_Checkout/web/template/minicart/content.html": "remove",
    "Magento_Checkout/web/template/minicart/item/default.html": "remove",
    "Magento_CheckoutAgreements/web/template/checkout/checkout-agreements.html": "remove",
    "Magento_OfflinePayments/web/template/payment/banktransfer.html": "remove",
    "Magento_OfflinePayments/web/template/payment/checkmo.html": "remove",

    "Magento_Cms/templates/newsletter.phtml": "rewrite",
    "Magento_Cms/templates/currentyear.phtml": "copy",

    "Magento_ConfigurableProduct/templates/product/price/final_price.phtml": "skip",

    "Magento_Customer/templates/form/login.phtml": "rewrite",
    "Magento_Customer/templates/form/register.phtml": "rewrite",
    "Magento_Customer/templates/form/edit.phtml": "rewrite",
    "Magento_Customer/templates/form/newsletter.phtml": "skip",
    "Magento_Customer/templates/account/dashboard/address.phtml": "skip",
    "Magento_Customer/templates/account/dashboard/info.phtml": "skip",
    "Magento_Customer/templates/account/link/authorization.phtml": "skip",
    "Magento_Customer/templates/address/edit.phtml": "rewrite",
    "Magento_Customer/templates/address/grid.phtml": "skip",

    "Magento_LayeredNavigation/templates/layer/view.phtml": "skip",  # Hyvä provides

    "Magento_Search/templates/form.mini.phtml": "rewrite",
    "Magento_Store/templates/switch/languages.phtml": "rewrite",

    "Magento_Sales/templates/email": "copy",  # Email templates unaffected by Hyvä
    "Magento_Sales/templates/order/history.phtml": "skip",
    "Magento_Sales/templates/order/recent.phtml": "skip",
    "Magento_Sales/templates/order/view.phtml": "skip",
    "Magento_Sales/templates/order/items.phtml": "skip",
    "Magento_Sales/templates/order/totals.phtml": "skip",
    "Magento_Sales/templates/order/order_status.phtml": "skip",
    "Magento_Sales/templates/order/items/renderer/default.phtml": "skip",

    "Magento_ProductAlert/templates/email": "copy",  # Email only
    "Magento_Tax/templates/order/tax.phtml": "skip",
    "Magento_Weee/templates/item/price/unit.phtml": "skip",

    # Third-party modules: only include if module is installed in target store
    # These are moved to a separate "optional" directory in generator/templates/optional/
    "Magestall_GuestWishlist/templates/link.phtml": "skip",
    "Amasty_Xnotif/templates/product/view_email.phtml": "skip",
}


def analyze_template_complexity(file_path: str) -> dict:
    """
    Analyze a template file's complexity to determine if it should be preserved vs rewritten.

    Returns dict with:
        - line_count: int
        - jquery_patterns: int (count of jQuery/RequireJS patterns)
        - navigation_depth: int (nesting depth of category loops)
        - cms_block_refs: int (CMS block references inside template)
        - mobile_elements: int (mobile-specific DOM elements)
        - complexity_score: int (weighted total)
        - recommended_strategy: str ('preserve' | 'rewrite' | 'analyze')
    """
    try:
        content = Path(file_path).read_text(errors='replace')
    except (IOError, OSError):
        return {"complexity_score": 0, "recommended_strategy": "analyze"}

    lines = content.split('\n')
    line_count = len(lines)

    # Count jQuery/DOM manipulation patterns
    jquery_patterns = 0
    for pattern in HIGH_COMPLEXITY_PATTERNS:
        jquery_patterns += len(re.findall(pattern, content))

    # Detect navigation depth (nested category loops)
    navigation_depth = 0
    # Look for nested foreach patterns on categories/subcategories
    cat_loop_patterns = [
        r'foreach\s*\(\s*\$categor',
        r'foreach\s*\(\s*\$subcats',
        r'getChildrenCategories\(\)',
        r'foreach\s*\(\s*\$subcat[sb]',
    ]
    for pat in cat_loop_patterns:
        if re.search(pat, content):
            navigation_depth += 1

    # Count CMS block references (navigationsblock-*, promotion_header, etc.)
    cms_block_refs = len(re.findall(r"setBlockId\(|cms/block/render|block_id=", content, re.IGNORECASE))

    # Count mobile-specific elements
    mobile_patterns = [
        r'mobile-nav-only', r'mobile-nav-hidden', r'mobile-homepage',
        r'responsive-nav-icon', r'nav-back-link', r'close-nav-arrow',
        r'mobile-all-in-link', r'@media.*max-width',
    ]
    mobile_elements = sum(1 for p in mobile_patterns if re.search(p, content))

    # Weighted complexity score
    score = 0
    score += line_count // 50             # +1 per 50 lines
    score += jquery_patterns * 2          # jQuery patterns are hard to replicate
    score += navigation_depth * 3         # Deep navigation is fragile to rewrite
    score += cms_block_refs * 2           # CMS blocks must be placed correctly
    score += mobile_elements              # Mobile elements must be preserved

    # Determine recommended strategy
    if (line_count >= PRESERVE_LINE_THRESHOLD
            or jquery_patterns >= PRESERVE_JQUERY_PATTERNS
            or navigation_depth >= PRESERVE_NAVIGATION_DEPTH):
        recommended = "preserve"
    elif score >= 15:
        recommended = "preserve"
    elif score >= 8:
        recommended = "analyze"
    else:
        recommended = "rewrite"

    return {
        "line_count": line_count,
        "jquery_patterns": jquery_patterns,
        "navigation_depth": navigation_depth,
        "cms_block_refs": cms_block_refs,
        "mobile_elements": mobile_elements,
        "complexity_score": score,
        "recommended_strategy": recommended,
    }


def get_strategy(rel_path: str) -> str:
    """Determine conversion strategy for a template file."""
    # Check exact match first
    if rel_path in TEMPLATE_STRATEGY:
        return TEMPLATE_STRATEGY[rel_path]

    # Check prefix matches (for directories like email/)
    for pattern, strategy in TEMPLATE_STRATEGY.items():
        if rel_path.startswith(pattern):
            return strategy

    # Auto-detect header/footer templates across any theme
    if is_header_footer_template(rel_path):
        return "preserve"

    return "analyze"  # Unknown — needs manual analysis


def get_strategy_with_analysis(rel_path: str, source_theme_path: str = "") -> tuple:
    """
    Enhanced strategy resolution: first checks explicit mapping, then falls back
    to complexity analysis if the template is unmapped.

    Returns (strategy, analysis_dict_or_None).
    """
    explicit = get_strategy(rel_path)
    if explicit != "analyze":
        return explicit, None

    # For unmapped templates, run complexity analysis
    if source_theme_path:
        full_path = os.path.join(source_theme_path, rel_path)
        if os.path.isfile(full_path):
            analysis = analyze_template_complexity(full_path)
            return analysis["recommended_strategy"], analysis

    return "analyze", None


def plan_conversion(theme_path: str) -> dict:
    """Plan the conversion strategy for all theme templates.

    For unmapped templates, runs complexity analysis to auto-detect
    whether to preserve the original or flag for manual review.
    """
    plan = {
        "rewrite": [],
        "preserve": [],
        "skip": [],
        "copy": [],
        "remove": [],
        "analyze": [],
    }
    analysis_details = {}

    for root, dirs, files in os.walk(theme_path):
        for fname in files:
            fpath = os.path.join(root, fname)
            ext = Path(fname).suffix

            if ext not in (".phtml", ".xml", ".html"):
                continue

            rel = os.path.relpath(fpath, theme_path)
            strategy, analysis = get_strategy_with_analysis(rel, theme_path)

            if strategy not in plan:
                strategy = "analyze"

            plan[strategy].append(rel)
            if analysis:
                analysis_details[rel] = analysis

    return plan, analysis_details
