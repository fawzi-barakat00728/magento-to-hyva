#!/bin/bash
# Deploy gallery, swatch fixes to test server
# Run from: /Users/oleksandr/Documents/GitHub/magento-to-hyva/

SERVER="vibeadd@vibeadd.ftp.tools"
PASS="bQ5wsN5kyR6crG4rtW4n"
BASE="/home/vibeadd/vibeadd.com/hyvatestproject"
THEME="$BASE/app/design/frontend/MediaDivision/HyvaTestTheme"

echo "=== 1. Upload gallery.phtml ==="
B64=$(base64 -i deploy/gallery.phtml)
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$SERVER" "echo '$B64' | base64 -d > $THEME/Magento_Catalog/templates/product/view/gallery.phtml"

echo "=== 2. Upload swatch renderer.phtml ==="
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$SERVER" "mkdir -p $THEME/Magento_Swatches/templates/product/view/"
B64=$(base64 -i deploy/swatch-renderer.phtml)
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$SERVER" "echo '$B64' | base64 -d > $THEME/Magento_Swatches/templates/product/view/renderer.phtml"

echo "=== 3. Upload swatch-item.phtml ==="
B64=$(base64 -i deploy/swatch-item.phtml)
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$SERVER" "echo '$B64' | base64 -d > $THEME/Magento_Swatches/templates/product/swatch-item.phtml"

echo "=== 4. Apply CSS patch ==="
B64=$(base64 -i deploy/gallery-css-patch.css)
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$SERVER" "echo '$B64' | base64 -d > /tmp/gallery-css-patch.css"
# Apply patch via PHP script
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$SERVER" "/usr/local/php83/bin/php /tmp/apply_css_patch.php"

echo "=== 5. Flush cache ==="
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$SERVER" "cd $BASE && /usr/local/php83/bin/php bin/magento cache:flush layout block_html full_page"

echo "=== 6. Rebuild static content ==="
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$SERVER" "cd $BASE && rm -rf pub/static/frontend/MediaDivision/HyvaTestTheme/ var/view_preprocessed/ && /usr/local/php83/bin/php bin/magento setup:static-content:deploy de_DE --theme MediaDivision/HyvaTestTheme -f 2>&1 | tail -5"

echo "=== DONE ==="
