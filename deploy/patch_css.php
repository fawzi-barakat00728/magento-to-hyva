<?php
/**
 * Patch design-fixes.css: Replace gallery pseudo-element zoom with proper button CSS
 * and remove section 15 duplicate zoom rules (now handled by gallery.phtml buttons)
 */
$file = '/home/vibeadd/vibeadd.com/hyvatestproject/app/design/frontend/MediaDivision/HyvaTestTheme/web/css/design-fixes.css';
$css = file_get_contents($file);

// 1. Replace Section 7 (Gallery) — from "7. GALLERY" to the end of the "Gallery height" section
$oldSection7 = '/* =====================================================
   7. GALLERY — Zoom, Thumbnails, Active Border
   ===================================================== */
#gallery-main {
    position: relative;
}
/* Zoom icon — bottom-right corner (fully override luma-compat arrow) */
#gallery-main::after {
    content: "" !important;
    position: absolute !important;
    right: 15px !important;
    bottom: 15px !important;
    top: unset !important;
    left: unset !important;
    width: 22px !important;
    height: 22px !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'%23666\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3E%3Ccircle cx=\'11\' cy=\'11\' r=\'7\'/%3E%3Cpath d=\'M21 21l-4.35-4.35\'/%3E%3C/svg%3E") !important;
    background-size: contain !important;
    background-repeat: no-repeat !important;
    border: none !important;
    transform: none !important;
    z-index: 10;
    pointer-events: none;
    opacity: 0.5;
    transition: opacity 0.3s;
}
/* Hide left arrow */
#gallery-main::before {
    display: none !important;
}
#gallery-main:hover::after {
    opacity: 1 !important;
}';

$newSection7 = '/* =====================================================
   7. GALLERY — Arrows, Zoom Button, Thumbnails
   ===================================================== */
#gallery-main {
    position: relative;
}

/* Hide old luma-compat pseudo-element arrows/zoom */
#gallery-main::before,
#gallery-main::after {
    display: none !important;
}

/* Gallery prev/next arrow buttons (appear on hover) */
.gallery-arrow {
    cursor: pointer;
}
.gallery-arrow:focus {
    outline: 2px solid #a9ba9d;
    outline-offset: 2px;
}

/* Zoom button (bottom-right corner) */
.gallery-zoom:focus {
    outline: 2px solid #a9ba9d;
    outline-offset: 2px;
}

/* Ensure arrows and zoom appear above the fullscreen button overlay */
.gallery-arrow,
.gallery-zoom {
    z-index: 20 !important;
}

/* The invisible fullscreen button needs lower z-index than arrows/zoom */
#gallery-main > button[x-ref="galleryFullscreenBtn"] {
    z-index: 10 !important;
}';

if (strpos($css, $oldSection7) !== false) {
    $css = str_replace($oldSection7, $newSection7, $css);
    echo "Section 7 replaced OK\n";
} else {
    echo "WARNING: Section 7 not found for replacement, trying line-by-line...\n";
    // Try a simpler replacement
    $css = preg_replace(
        '/\/\*\s*=+\s*\n\s*7\. GALLERY.*?#gallery-main:hover::after\s*\{[^}]+\}/s',
        $newSection7,
        $css,
        1,
        $count
    );
    echo "Regex replacement count: $count\n";
}

// 2. Replace Section 15 — remove the duplicate zoom rules since we now have proper buttons
$oldSection15 = '/* Hide "Sale" ::before text on gallery fullscreen button (from luma-compat) */
#gallery-main > button[x-ref="galleryFullscreenBtn"]::before {
    display: none !important;
}
/* Hide duplicate zoom ::after on button (we use #gallery-main::after instead) */
#gallery-main > button[x-ref="galleryFullscreenBtn"]::after {
    display: none !important;
}';

$newSection15 = '/* Hide any pseudo-element decorations on the fullscreen button (luma-compat remnants) */
#gallery-main > button[x-ref="galleryFullscreenBtn"]::before,
#gallery-main > button[x-ref="galleryFullscreenBtn"]::after {
    display: none !important;
}';

if (strpos($css, $oldSection15) !== false) {
    $css = str_replace($oldSection15, $newSection15, $css);
    echo "Section 15 replaced OK\n";
} else {
    echo "WARNING: Section 15 old text not found\n";
}

// Write back
file_put_contents($file, $css);
echo "CSS patched successfully. Total size: " . strlen($css) . " bytes\n";
