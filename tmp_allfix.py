import base64, re

# ===== 1. FIX CSS =====
css_path = "/home/vibeadd/vibeadd.com/hyvatestproject/app/design/frontend/MediaDivision/HyvaTestTheme/web/css/design-fixes.css"

with open(css_path, "r") as f:
    css = f.read()

# 1a. Fix the page title - currently targets .page-title-wrapper but Hyva uses h1.page-title
# Replace the existing rule
old_title = """.catalog-category-view .page-title-wrapper {
    display: none !important;
}"""

new_title = """.catalog-category-view .page-title-wrapper,
.catalog-category-view h1.page-title,
.catalog-category-view [data-ui-id="page-title-wrapper"] {
    display: none !important;
}"""

if old_title in css:
    css = css.replace(old_title, new_title)
    print("1a. Page title CSS FIXED")
else:
    print("1a. Page title - pattern not found, checking alternatives...")
    # Try adding if not present
    if 'h1.page-title' not in css:
        css += "\n/* Hide category title in Hyva */\n.catalog-category-view h1.page-title,\n.catalog-category-view [data-ui-id=\"page-title-wrapper\"] {\n    display: none !important;\n}\n"
        print("1a. Page title CSS ADDED")
    else:
        print("1a. Page title CSS already has h1.page-title rule")

# 1b. Fix column.main - remove max-width to make products full-width, add proper side padding
# Section 20 has: .catalog-category-view .column.main { max-width: 1540px; margin: 0 auto; padding: 20px 4px 40px }
old_colmain = """.catalog-category-view .column.main {
    max-width: 1540px !important;
    margin: 0 auto !important;
    padding: 20px 4px 40px !important;
}"""

new_colmain = """.catalog-category-view .column.main {
    max-width: 100% !important;
    margin: 0 auto !important;
    padding: 20px 40px 40px !important;
}"""

if old_colmain in css:
    css = css.replace(old_colmain, new_colmain)
    print("1b. column.main full-width FIXED (section 20)")
else:
    print("1b. column.main pattern not found in section 20")

# Also fix the duplicate rule from earlier section (~line 848)
old_colmain2 = """.catalog-category-view .column.main,
.catalogsearch-result-index .column.main {
    max-width: 1540px !important;
    margin: 0 auto !important;
    padding: 20px 20px 40px !important;
}"""

new_colmain2 = """.catalog-category-view .column.main,
.catalogsearch-result-index .column.main {
    max-width: 100% !important;
    margin: 0 auto !important;
    padding: 20px 40px 40px !important;
}"""

if old_colmain2 in css:
    css = css.replace(old_colmain2, new_colmain2)
    print("1b2. column.main full-width FIXED (section 18)")
else:
    print("1b2. column.main section 18 pattern not found")

# 1c. Fix category-description centering
# Currently: max-width: 1200px, margin: 0 auto
# The container div around it (category-view.container) might also need centering
old_catdesc = """.catalog-category-view .category-description {
    text-align: center !important;
    max-width: 1200px !important;
    margin: 0 auto 20px auto !important;
    padding: 0 2rem !important;
}"""

new_catdesc = """.catalog-category-view .category-description {
    text-align: center !important;
    max-width: 100% !important;
    margin: 0 auto 20px auto !important;
    padding: 0 !important;
}"""

if old_catdesc in css:
    css = css.replace(old_catdesc, new_catdesc)
    print("1c. category-description centering FIXED")
else:
    print("1c. category-description pattern not found")

# Also fix the category-view container and category-image
old_catdesc2 = """.catalog-category-view .category-description,
.catalog-category-view .category-image,
.catalog-category-view .category-view .category-cms {
    text-align: center;
    max-width: 1540px;
    margin-left: auto;
    margin-right: auto;
    padding: 0 1rem;
}"""

new_catdesc2 = """.catalog-category-view .category-description,
.catalog-category-view .category-image,
.catalog-category-view .category-view .category-cms {
    text-align: center;
    max-width: 100%;
    margin-left: auto;
    margin-right: auto;
    padding: 0;
}"""

if old_catdesc2 in css:
    css = css.replace(old_catdesc2, new_catdesc2)
    print("1c2. category section centering FIXED")
else:
    print("1c2. category section pattern not found")

# Also fix the earlier category-description rule (~line 883)
old_catdesc3 = """.catalog-category-view .category-description,
.catalog-category-view .category-cms {
    max-width: 1540px !important;
    margin: 0 auto !important;
    padding: 40px 20px !important;
    text-align: center !important;
}"""

new_catdesc3 = """.catalog-category-view .category-description,
.catalog-category-view .category-cms {
    max-width: 100% !important;
    margin: 0 auto !important;
    padding: 0 !important;
    text-align: center !important;
}"""

if old_catdesc3 in css:
    css = css.replace(old_catdesc3, new_catdesc3)
    print("1c3. earlier category-description FIXED")
else:
    print("1c3. earlier category-description pattern not found")

# 1d. Add rule for the parent category-view container
# The category-view.container in Hyva might have its own max-width
css += """
/* Category view container - full width, centered content */
.catalog-category-view .category-view.container,
.catalog-category-view #category-view-container {
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 auto !important;
}

/* Category image full width */
.catalog-category-view .category-image img {
    width: 100% !important;
    max-width: 100% !important;
    height: auto !important;
    margin: 0 !important;
}

/* Hide the parent title container too */
.catalog-category-view .container.flex.flex-col.md\\:flex-row.flex-wrap:has(h1.page-title) {
    display: none !important;
}
"""
print("1d. Category container and image rules ADDED")

with open(css_path, "w") as f:
    f.write(css)
print("CSS FILE SAVED")

# ===== 2. FIX HOVER IMAGE IN LIST.PHTML =====
list_path = "/home/vibeadd/vibeadd.com/hyvatestproject/app/design/frontend/MediaDivision/HyvaTestTheme/Magento_Catalog/templates/product/list.phtml"

with open(list_path, "r") as f:
    tpl = f.read()

# Replace the hover image logic to also check child products
old_hover = """                            <?php
                            // Hover image: second gallery image
                            $galleryImages = $_product->getMediaGalleryImages();
                            $hoverImageUrl = null;
                            if ($galleryImages && count($galleryImages) > 1) {
                                $allImages = array_values($galleryImages->getItems());
                                $hoverImg = $allImages[1] ?? null;
                                if ($hoverImg) {
                                    $hoverImageUrl = $hoverImg->getUrl();
                                }
                            }
                            ?>"""

new_hover = """                            <?php
                            // Hover image: second gallery image, or child product image
                            $galleryImages = $_product->getMediaGalleryImages();
                            $hoverImageUrl = null;
                            if ($galleryImages && count($galleryImages) > 1) {
                                $allImages = array_values($galleryImages->getItems());
                                $hoverImg = $allImages[1] ?? null;
                                if ($hoverImg) {
                                    $hoverImageUrl = $hoverImg->getUrl();
                                }
                            }
                            // If configurable with only 1 image, get 2nd image from first visible child
                            if (!$hoverImageUrl && $_product->getTypeId() === 'configurable') {
                                $children = $_product->getTypeInstance()->getUsedProducts($_product);
                                foreach ($children as $child) {
                                    $childGallery = $child->getMediaGalleryImages();
                                    if ($childGallery && count($childGallery) > 1) {
                                        $childImages = array_values($childGallery->getItems());
                                        if (isset($childImages[1])) {
                                            $hoverImageUrl = $childImages[1]->getUrl();
                                            break;
                                        }
                                    }
                                }
                            }
                            ?>"""

if old_hover in tpl:
    tpl = tpl.replace(old_hover, new_hover)
    with open(list_path, "w") as f:
        f.write(tpl)
    print("2. Hover image template FIXED (checks child products)")
else:
    print("2. ERROR: Could not find hover image pattern in list.phtml")
    # Show what's there
    idx = tpl.find("Hover image")
    if idx >= 0:
        print("   Found 'Hover image' at position", idx)
        print("   Context:", repr(tpl[idx:idx+200]))
    else:
        print("   'Hover image' not found at all")

print("\nALL FIXES COMPLETE")
