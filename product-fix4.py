#!/usr/bin/env python3
"""Product page CSS fixes: price display, swatch, gallery thumbs, accordion icons"""
import os

CSS_PATH = "app/design/frontend/MediaDivision/HyvaTestTheme/web/css/luma-compat.css"

with open(CSS_PATH) as f:
    css = f.read()

# ============================================================
# FIX 1: Gallery thumbnails - show scroll arrows, bigger thumbs
# ============================================================
# The current CSS hides thumb scroll buttons - we need them visible for vertical scroll
old_thumbs_hide = """    /* Hide prev/next arrows for vertical thumbs (scroll arrows) */
    #thumbs > button {
        display: none !important;
    }"""

new_thumbs_arrows = """    /* Thumbnail scroll arrows — visible, rotated 90° for vertical layout */
    #thumbs > button {
        display: flex !important;
        width: 75px;
        height: 28px;
        padding: 0;
        align-items: center;
        justify-content: center;
        background: transparent;
        border: none;
        cursor: pointer;
        flex-shrink: 0;
    }
    #thumbs > button svg {
        transform: rotate(90deg);
        width: 18px;
        height: 18px;
        color: #666;
    }
    #thumbs > button:hover svg {
        color: #000;
    }
    #thumbs > button.opacity-25 {
        opacity: 0.25;
    }"""

css = css.replace(old_thumbs_hide, new_thumbs_arrows)

# ============================================================
# FIX 2: Gallery thumbnails - scrollable container with fixed height
# ============================================================
old_thumbs_slides = """    .js_thumbs_slides {
        flex-direction: column !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        max-height: 800px;
        width: 75px !important;
        flex-wrap: nowrap !important;
    }"""

new_thumbs_slides = """    .js_thumbs_slides {
        flex-direction: column !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        max-height: 650px;
        width: 80px !important;
        flex-wrap: nowrap !important;
        scrollbar-width: none;
        -ms-overflow-style: none;
    }
    .js_thumbs_slides::-webkit-scrollbar {
        display: none;
    }"""

css = css.replace(old_thumbs_slides, new_thumbs_slides)

# Fix thumbnail sizes — 80px to match original
old_thumb_size1 = """    .js_thumbs_slide {
        margin-right: 0 !important;
        margin-bottom: 0 !important;
        width: 75px;
    }
    .js_thumbs_slide img {
        width: 75px;
        height: auto;
    }"""

new_thumb_size1 = """    .js_thumbs_slide {
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
    }
    .js_thumbs_slide img:hover {
        border-color: #ccc;
    }"""

css = css.replace(old_thumb_size1, new_thumb_size1)

# Fix thumbnail wrapper width
css = css.replace(
    """    #gallery > div > div:nth-child(2) {
        order: -1;
        width: 75px !important;
        flex-shrink: 0;
        min-width: 75px;
    }""",
    """    #gallery > div > div:nth-child(2) {
        order: -1;
        width: 80px !important;
        flex-shrink: 0;
        min-width: 80px;
    }"""
)

# Fix main image max-width
css = css.replace(
    """        max-width: calc(100% - 87px);""",
    """        max-width: calc(100% - 92px);"""
)

# Fix #thumbs container for vertical layout
old_thumbs_nav = """    /* Thumbnail container must also be flex column */
    #gallery > div > div:nth-child(2) > nav {
        flex-direction: column !important;
    }
    /* Thumbnails nav vertical */
    #thumbs {
        flex-direction: column !important;
        min-height: auto !important;
        gap: 8px !important;
        align-items: flex-start !important;
    }"""

new_thumbs_nav = """    /* Thumbnail container must also be flex column */
    #gallery > div > div:nth-child(2) > nav {
        flex-direction: column !important;
    }
    /* Thumbnails nav vertical */
    #thumbs {
        flex-direction: column !important;
        min-height: auto !important;
        gap: 0 !important;
        align-items: center !important;
        width: 80px;
    }"""

css = css.replace(old_thumbs_nav, new_thumbs_nav)

# ============================================================
# FIX 3: Price display — ensure both prices show correctly
# ============================================================
# The HTML now has:
# <div class="old-price"> ... 669,00 € </div>
# <div class="final-price"> ... 535,00 € </div>
# CSS already has the right rules. Let's enhance the price-box display.

old_price_box = """.catalog-product-view .product-info-price .price-box {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 10px;
}"""

new_price_box = """.catalog-product-view .product-info-price .price-box {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 10px;
}
/* Ensure price container shows both prices inline */
.catalog-product-view .price-box .price-container {
    display: flex;
    align-items: baseline;
    gap: 10px;
}
.catalog-product-view .price-box .price-container .old-price {
    order: 2;
}
.catalog-product-view .price-box .price-container .final-price {
    order: 1;
}"""

css = css.replace(old_price_box, new_price_box)

# ============================================================
# FIX 4: Swatch — proper size for visual swatch with background image
# ============================================================
# The swatch has class="swatch-option relative shadow-sm cursor-pointer select-none bg-white..."
# and conditional class 'w-6 h-6' : !isTextSwatch(173, item.id)
# We need to override w-6 h-6 (24px x 24px) to our desired size

old_swatch = """.catalog-product-view .swatch-option {
    border: 1px solid #ccc !important;
    border-radius: 0 !important;
    min-width: 60px !important;
    min-height: 60px !important;
    width: 60px !important;
    height: 60px !important;
    background-size: cover !important;
}"""

new_swatch = """.catalog-product-view .swatch-option {
    border: 1px solid #ccc !important;
    border-radius: 0 !important;
    min-width: 80px !important;
    min-height: 80px !important;
    width: 80px !important;
    height: 80px !important;
    background-size: cover !important;
    box-shadow: none !important;
}
/* Override Tailwind w-6 h-6 (24x24) on swatch options */
.catalog-product-view .swatch-option.w-6 {
    width: 80px !important;
    min-width: 80px !important;
}
.catalog-product-view .swatch-option.h-6 {
    height: 80px !important;
    min-height: 80px !important;
}"""

css = css.replace(old_swatch, new_swatch)

# Also update the earlier swatch rule
old_swatch2 = """/* Color swatch image size — match original */
.catalog-product-view .swatch-option.w-6.h-6,
.catalog-product-view .swatch-option[style*="background"],
.catalog-product-view label.swatch-option,
.catalog-product-view .swatch-attribute-options .swatch-option {
    width: 60px !important;
    height: 60px !important;
    background-size: cover !important;
    border: 1px solid #ccc !important;
    border-radius: 0 !important;
    display: inline-flex !important;
    overflow: hidden;
}"""

new_swatch2 = """/* Color swatch image size — match original */
.catalog-product-view .swatch-option.w-6.h-6,
.catalog-product-view .swatch-option[style*="background"],
.catalog-product-view label.swatch-option,
.catalog-product-view .swatch-attribute-options .swatch-option {
    width: 80px !important;
    height: 80px !important;
    background-size: cover !important;
    border: 1px solid #ccc !important;
    border-radius: 0 !important;
    display: inline-flex !important;
    overflow: hidden;
    box-shadow: none !important;
}"""

css = css.replace(old_swatch2, new_swatch2)

# ============================================================
# FIX 5: Swatch attribute label — show "Farbe" + selected value
# ============================================================
# The HTML has: <label class="w-full sm:w-1/2 text-left text-gray-700 label product-option-label">
# with <span>Farbe</span> and <span x-text="getSwatchText(173, selectedValues[173])"></span>
# We need to make sure the label row and the swatch display correctly

old_swatch_label = """.catalog-product-view .swatch-attribute-label {
    font-family: "KorpusGrotesk-B", sans-serif;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.catalog-product-view .swatch-attribute {
    margin-bottom: 16px;
}"""

new_swatch_label = """.catalog-product-view .swatch-attribute-label,
.catalog-product-view .product-option-label {
    font-family: "KorpusGrotesk-B", sans-serif;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    display: block !important;
    width: 100% !important;
    margin-bottom: 8px;
}
/* Swatch label row — stack vertically, not side-by-side */
.catalog-product-view .swatch-attribute .flex.flex-col.sm\\:flex-row {
    flex-direction: column !important;
    align-items: flex-start !important;
}
.catalog-product-view .swatch-attribute .sm\\:w-1\\/2 {
    width: 100% !important;
}
.catalog-product-view .swatch-attribute .product-option-values {
    margin-left: 0 !important;
    width: 100% !important;
}
.catalog-product-view .swatch-attribute {
    margin-bottom: 16px;
    border-top: none !important;
    border-bottom: none !important;
    padding: 8px 0 !important;
}"""

css = css.replace(old_swatch_label, new_swatch_label)

# ============================================================
# FIX 6: Accordion +/- icons
# ============================================================
# Current CSS uses .ftc-section-title::after with + and —
# The "open" class is set by Alpine :class="{ 'open': openSection === 'details' }"
# This should already work, but let's make sure

old_accordion = """.product-info-column .ftc-section-title {
    font-size: 13px;
    letter-spacing: 0.1em;
}"""

new_accordion = """.product-info-column .ftc-section-title {
    font-size: 13px;
    letter-spacing: 0.1em;
    position: relative;
    padding-right: 30px;
}
/* Accordion +/- icons */
.product-info-column .ftc-section-title::after {
    content: "+";
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    font-size: 20px;
    font-weight: 300;
    line-height: 1;
    color: #000;
    font-family: "KorpusGrotesk-B", sans-serif;
}
.product-info-column .ftc-section-title.open::after {
    content: "\\2013";
}"""

css = css.replace(old_accordion, new_accordion)

# ============================================================
# FIX 7: Hide "Product Options:" heading
# ============================================================
# The Hyvä template renders <h2 class="... title-font">Product Options:</h2>
# We have CSS to hide it but let's ensure it works

# ============================================================
# FIX 8: Gallery main image – add overlay arrow for next image
# ============================================================
# On the original, there's a > arrow on the right side. In Hyvä, the gallery
# uses a fullscreen button overlay. We can add a pseudo-element arrow.
# But actually Hyvä uses touch/swipe gestures. The original also doesn't have
# permanent arrows. Skip this.

# ============================================================
# FIX 9: Price order — final price first, then old price
# ============================================================
# On the original: "535,00 €" (orange) then "669,00 €" (strikethrough)
# Our CSS has .old-price { order: 2 } which should push it after

with open(CSS_PATH, "w") as f:
    f.write(css)

lines = css.count('\n') + 1
print(f"Done. Total lines: {lines}")
