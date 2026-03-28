#!/bin/bash
# Deploy gallery, swatch fixes to test server
# Run from: /Users/oleksandr/Documents/GitHub/magento-to-hyva/

SERVER="${DEPLOY_SERVER:-vibeadd@vibeadd.ftp.tools}"
PASS="${DEPLOY_PASS:-}"
BASE="${DEPLOY_BASE:-/home/vibeadd/vibeadd.com/hyvatestproject}"
THEME="${DEPLOY_THEME:-$BASE/app/design/frontend/MediaDivision/HyvaTestTheme}"
PHP_BIN="${DEPLOY_PHP_BIN:-/usr/local/php83/bin/php}"
THEME_CODE="${DEPLOY_THEME_CODE:-MediaDivision/HyvaTestTheme}"
LOCALE="${DEPLOY_LOCALE:-de_DE}"

if [[ -n "$PASS" ]]; then
  SSH_PREFIX=(sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no -o PubkeyAuthentication=no -o PreferredAuthentications=password -o NumberOfPasswordPrompts=1 "$SERVER")
else
  SSH_PREFIX=(ssh -o StrictHostKeyChecking=no "$SERVER")
fi

ssh_exec() {
  "${SSH_PREFIX[@]}" "$1"
}

echo "=== 1. Upload gallery.phtml ==="
B64=$(base64 -i deploy/gallery.phtml)
ssh_exec "echo '$B64' | base64 -d > $THEME/Magento_Catalog/templates/product/view/gallery.phtml"

echo "=== 2. Upload swatch renderer.phtml ==="
ssh_exec "mkdir -p $THEME/Magento_Swatches/templates/product/view/"
B64=$(base64 -i deploy/swatch-renderer.phtml)
ssh_exec "echo '$B64' | base64 -d > $THEME/Magento_Swatches/templates/product/view/renderer.phtml"

echo "=== 3. Upload swatch-item.phtml ==="
B64=$(base64 -i deploy/swatch-item.phtml)
ssh_exec "echo '$B64' | base64 -d > $THEME/Magento_Swatches/templates/product/swatch-item.phtml"

echo "=== 4. Apply CSS patch ==="
B64=$(base64 -i deploy/gallery-css-patch.css)
ssh_exec "echo '$B64' | base64 -d > /tmp/gallery-css-patch.css"
# Apply patch via PHP script
ssh_exec "$PHP_BIN /tmp/apply_css_patch.php"

echo "=== 5. Flush cache ==="
ssh_exec "cd $BASE && $PHP_BIN bin/magento cache:flush layout block_html full_page"

echo "=== 6. Rebuild static content ==="
ssh_exec "cd $BASE && rm -rf pub/static/frontend/MediaDivision/HyvaTestTheme/ var/view_preprocessed/ && $PHP_BIN bin/magento setup:static-content:deploy $LOCALE --theme $THEME_CODE -f 2>&1 | tail -5"

echo "=== DONE ==="
