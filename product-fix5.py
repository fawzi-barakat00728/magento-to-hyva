#!/usr/bin/env python3
"""
Product page CSS fixes round 5:
1. Gallery thumbnails width 135px (native 135x180)
2. Gallery prev/next arrows on main image
3. Zoom icon in bottom-right corner of main image
4. Swatch variation refinements
"""
import os

CSS_PATH = "app/design/frontend/MediaDivision/HyvaTestTheme/web/css/luma-compat.css"

with open(CSS_PATH) as f:
    css = f.read()

# ============================================================
# 1. Gallery thumbnails — 135px wide (images are 135x180 natively)
# ============================================================

# Fix thumbnail wrapper width: 80 → 135
css = css.replace(
    """    #gallery > div > div:nth-child(2) {
        order: -1;
        width: 80px !important;
        flex-shrink: 0;
        min-width: 80px;
    }""",
    """    #gallery > div > div:nth-child(2) {
        order: -1;
        width: 135px !important;
        flex-shrink: 0;
        min-width: 135px;
    }"""
)

# Fix main image max-width accounting for larger thumbnails
css = css.replace(
    """        max-width: calc(100% - 92px);""",
    """        max-width: calc(100% - 150px);"""
)

# Fix thumbs nav width
css = css.replace(
    """    #thumbs {
        flex-direction: column !important;
        min-height: auto !important;
        gap: 0 !important;
        align-items: center !important;
        width: 80px;
    }""",
    """    #thumbs {
        flex-direction: column !important;
        min-height: auto !important;
        gap: 0 !important;
        align-items: center !important;
        width: 135px;
    }"""
)

# Fix slides container width
css = css.replace(
    """        width: 80px !important;
        flex-wrap: nowrap !important;
        scrollbar-width: none;""",
    """        width: 135px !important;
        flex-wrap: nowrap !important;
        scrollbar-width: none;"""
)

# Fix individual slide width
css = css.replace(
    """    .js_thumbs_slide {
        margin-right: 0 !important;
        margin-bottom: 4px !important;
        width: 80px;
        flex-shrink: 0;
    }
    .js_thumbs_slide img {
        width: 80px;
        height: auto;
        object-fit: cover;
        border: 1px solid transparent;
        cursor: pointer;
    }""",
    """    .js_thumbs_slide {
        margin-right: 0 !important;
        margin-bottom: 6px !important;
        width: 135px;
        flex-shrink: 0;
    }
    .js_thumbs_slide img {
        width: 135px;
        height: 180px;
        object-fit: cover;
        border: 1px solid transparent;
        cursor: pointer;
    }"""
)

# Fix scroll arrow button width
css = css.replace(
    """    #thumbs > button {
        display: flex !important;
        width: 75px;
        height: 28px;""",
    """    #thumbs > button {
        display: flex !important;
        width: 135px;
        height: 28px;"""
)

# ============================================================
# 2. Gallery prev/next arrows on main image
# ============================================================
# The Hyvä gallery has a transparent fullscreen button overlay.
# We'll add CSS-only prev/next arrows using the gallery-main container.
# Since Hyvä uses Alpine x-data initGallery with previousItem()/nextItem(),
# we can't add click handlers via CSS alone. Instead, we'll style the
# existing fullscreen button area, and add visual arrow indicators.
# Actually, the gallery has touch handlers but no visible arrows.
# Let's add visual arrow overlays using ::before and ::after pseudo-elements
# on #gallery-main.

gallery_arrows_css = """
/* === Gallery: prev/next navigation arrows on main image === */
#gallery-main {
    position: relative;
}
/* Right arrow (next) */
#gallery-main::after {
    content: "";
    position: absolute;
    right: 16px;
    top: 50%;
    transform: translateY(-50%);
    width: 36px;
    height: 36px;
    background: rgba(255,255,255,0.85);
    border-radius: 50%;
    z-index: 5;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke-width='2' stroke='%23333'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M9 5l7 7-7 7'/%3E%3C/svg%3E");
    background-size: 20px 20px;
    background-repeat: no-repeat;
    background-position: center;
}
/* Left arrow (previous) */
#gallery-main::before {
    content: "";
    position: absolute;
    left: 16px;
    top: 50%;
    transform: translateY(-50%);
    width: 36px;
    height: 36px;
    background: rgba(255,255,255,0.85);
    border-radius: 50%;
    z-index: 5;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke-width='2' stroke='%23333'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M15 19l-7-7 7-7'/%3E%3C/svg%3E");
    background-size: 20px 20px;
    background-repeat: no-repeat;
    background-position: center;
}
/* Show arrows on hover */
#gallery-main:hover::after,
#gallery-main:hover::before {
    opacity: 1;
}
"""

# Insert after the gallery-main margin-bottom rule
css = css.replace(
    """    /* Remove bottom margin on main gallery */
    #gallery-main {
        margin-bottom: 0 !important;
    }
}""",
    """    /* Remove bottom margin on main gallery */
    #gallery-main {
        margin-bottom: 0 !important;
    }
}""" + gallery_arrows_css
)

# ============================================================
# 3. Zoom/magnify icon in bottom-right corner of main image
# ============================================================
# The Hyvä gallery has a transparent button overlaying the image for fullscreen.
# Let's add a visible zoom icon in the bottom-right corner.

zoom_icon_css = """
/* === Zoom icon in bottom-right of main gallery image === */
#gallery-main > button[aria-label*="fullscreen"],
#gallery-main > button[aria-label*="Vollbild"],
#gallery-main > button[x-ref="galleryFullscreenBtn"] {
    /* Keep the button full overlay for click but add a visible icon */
    cursor: zoom-in !important;
}
#gallery-main > button[x-ref="galleryFullscreenBtn"]::after {
    content: "";
    position: absolute;
    right: 16px;
    bottom: 16px;
    width: 40px;
    height: 40px;
    background: rgba(255,255,255,0.9);
    border-radius: 50%;
    z-index: 6;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke-width='1.5' stroke='%23333'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z'/%3E%3C/svg%3E");
    background-size: 22px 22px;
    background-repeat: no-repeat;
    background-position: center;
    pointer-events: none;
    box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    transition: transform 0.2s;
}
#gallery-main > button[x-ref="galleryFullscreenBtn"]:hover::after {
    transform: scale(1.1);
}
"""

# Insert after the gallery arrows CSS
css += zoom_icon_css

# ============================================================
# 4. Swatch label — always full width, label above, options below
# ============================================================
# The original shows "Farbe 980,835" on one line, swatch image below.
# The size dropdown shows "Grösse" label on left, dropdown on right in a row.
# Hyvä uses flex sm:flex-row — on desktop it puts label and options side-by-side.
# We want: color = stacked (full width label, then swatch below)
#          size  = row (label left, dropdown right)

swatch_layout_css = """
/* === Swatch layout: color stacked, size row === */
/* Color swatch — full width vertical layout */
.catalog-product-view .swatch-attribute.color_name .flex.sm\\:flex-row {
    flex-direction: column !important;
    align-items: flex-start !important;
    padding: 12px 0 !important;
}
.catalog-product-view .swatch-attribute.color_name .product-option-label {
    width: 100% !important;
    margin-bottom: 10px;
}
.catalog-product-view .swatch-attribute.color_name .product-option-values {
    width: 100% !important;
    margin-left: 0 !important;
}
/* Size row — label left, dropdown right */
.catalog-product-view .swatch-attribute + div .flex.items-center {
    flex-direction: row;
    align-items: center;
}
/* Remove top/bottom borders from swatch wrapper — cleaner look */
.catalog-product-view .swatch-attribute.border-t {
    border-top: none !important;
}
.catalog-product-view .swatch-attribute.last\\:border-b {
    border-bottom: none !important;
}
/* Size select row: keep horizontal */
.catalog-product-view div:has(> select.super-attribute-select) {
    display: flex;
    flex-direction: row;
    align-items: center;
}
"""

css += swatch_layout_css

with open(CSS_PATH, "w") as f:
    f.write(css)

lines = css.count('\n') + 1
print(f"Done. Total lines: {lines}")
