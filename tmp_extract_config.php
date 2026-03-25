<?php
// Extract jsonConfig from a product page to analyze swatch/image configuration
$url = $argv[1] ?? 'https://shop.ftc-cashmere.com/de-de/00001-0550-kaschmir-baby-m-tze.html';
$html = file_get_contents($url);

// Find jsonConfig in spConfig
if (preg_match('/"jsonConfig"\s*:\s*(\{.+?\})\s*,\s*"jsonSwatchConfig"/s', $html, $m)) {
    $json = json_decode($m[1], true);
    if (!$json) {
        echo "JSON decode failed\n";
        exit(1);
    }
    echo "=== ATTRIBUTES ===\n";
    foreach ($json['attributes'] ?? [] as $aid => $attr) {
        echo "  $aid ({$attr['code']}): " . count($attr['options']) . " options\n";
        foreach ($attr['options'] as $opt) {
            echo "    {$opt['id']}: {$opt['label']} products:" . implode(',', $opt['products']) . "\n";
        }
    }
    echo "\n=== IMAGES ===\n";
    foreach ($json['images'] ?? [] as $pid => $imgs) {
        echo "Product $pid: " . count($imgs) . " images\n";
    }
} else {
    echo "jsonConfig not found in pattern\n";
}

// Find jsonSwatchConfig
if (preg_match('/"jsonSwatchConfig"\s*:\s*(\{.+?\})\s*[,}]/s', $html, $m2)) {
    $swatch = json_decode($m2[1], true);
    echo "\n=== SWATCH CONFIG ===\n";
    foreach ($swatch ?? [] as $attrId => $options) {
        echo "Attribute $attrId:\n";
        if (is_array($options)) {
            foreach ($options as $optId => $optData) {
                if (is_array($optData)) {
                    echo "  Option $optId: type=" . ($optData['type'] ?? '?') . " value=" . ($optData['value'] ?? '?') . " label=" . ($optData['label'] ?? '?') . "\n";
                }
            }
        }
    }
}
