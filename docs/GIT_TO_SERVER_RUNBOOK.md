# Git-to-Server Runbook (FTC Luma -> Hyva Migration)

This document is the canonical deployment workflow for moving generated code from Git/local workspace to the Magento server and reproducing the working result on:

- `https://hyvatestproject.vibeadd.com/`

The runbook is fully in English and addresses the Team Leader feedback points 1-12.

## 1. Feedback Closure Matrix (Points 1-12)

### Critical (Theme Breaks)

1. Deploy files not auto-deployed  
Status: Fixed.  
Implementation: `generate.py` now auto-copies critical files from `deploy/` to generated theme output.

2. Generated header uses jQuery instead of Alpine.js  
Status: Fixed.  
Implementation: `deploy/header.phtml` is auto-copied to `Magento_Theme/templates/html/header.phtml`. `ftcheader.phtml` is no longer deployed.

3. Layout XML breaks search/minicart/wishlist  
Status: Fixed.  
Implementation: default layout now overrides `header-content` template instead of hiding `header.container`, preserving child blocks:
- `logo`
- `topmenu`
- `header-search`
- `cart-drawer`

4. `require-shim.js` no-op  
Status: Fixed.  
Implementation: generator no longer injects/depends on `require-shim.js` in `default_head_blocks.xml`.

### High (Visual/Functional Issues)

5. LESS-to-CSS converter incomplete  
Status: Fixed for deployment pipeline.  
Implementation: manually validated `deploy/luma-compat.css` is auto-copied and overrides generated converter output.

6. Homepage works but inner pages break  
Status: Fixed for FTC workflow.  
Implementation: preserve-based header flow is bypassed for deploy output; production-tested deploy templates/layout/css are now the final layer.

7. Logo not configured  
Status: Fixed in documentation/workflow.  
Implementation: runbook now includes explicit logo/theme/search config commands.

### Medium (Documentation/Workflow)

8. No instructions for deploy files  
Status: Fixed.  
Implementation: this runbook and README now document deploy overrides as a standard step (automatic in generator).

9. No instructions for layout XML override  
Status: Fixed.  
Implementation: documented that `default.xml` uses `header-content` override and must keep Hyva block tree alive.

10. No instructions for Magento admin configuration  
Status: Fixed.  
Implementation: theme activation, logo setup, search engine config, and validation commands are included below.

### Low (Minor)

11. Translation differences  
Status: Mitigated.  
Implementation: `deploy/de_DE.csv` is auto-copied. Translation QA checklist is included below.

12. `node_modules` included in output  
Status: Fixed.  
Implementation: generated theme now includes `.gitignore`, deploy commands exclude `node_modules`, and generator cleanup removes runtime artifacts if present.

---

## 2. End-to-End Commands (Local -> Server)

## 2.1 Generate theme locally

Run from repository root:

```bash
python3 generate.py \
  --project projects/ftcshop \
  --vendor MediaDivision \
  --theme FTCShopHyva \
  --title "FTC Cashmere Hyvä" \
  --output output/ftcshop
```

Expected generator output should include:

- `Deploy overrides applied: ...`
- `Custom modules copied: ...`

## 2.2 Verify critical generated artifacts locally

```bash
THEME_OUT="output/ftcshop/MediaDivision/FTCShopHyva"

test -f "$THEME_OUT/Magento_Theme/templates/html/header.phtml"
test -f "$THEME_OUT/web/css/luma-compat.css"
test -f "$THEME_OUT/web/css/design-fixes.css"
test -f "$THEME_OUT/web/css/design-fixes-additions.css"
test -f "$THEME_OUT/Magento_Theme/layout/default.xml"

rg -n "header-content|cart-drawer|header-search|topmenu|logo" \
  "$THEME_OUT/Magento_Theme/layout/default.xml"

rg -n "require-shim|window\\.require\\s*=|display=\"false\"" \
  "$THEME_OUT/Magento_Theme/layout/default.xml" \
  "$THEME_OUT/Magento_Theme/layout/default_head_blocks.xml" \
  "$THEME_OUT"
```

The last `rg` command should return no problematic matches.

## 2.3 Build Tailwind locally

```bash
cd output/ftcshop/MediaDivision/FTCShopHyva
npm install
npm run build
cd -
```

## 2.4 Deploy theme to server (hyvatestproject)

Do not copy `node_modules` or `.git`.

```bash
LOCAL_THEME="$(pwd)/output/ftcshop/MediaDivision/FTCShopHyva/"
REMOTE_THEME="vibeadd@vibeadd.ftp.tools:/home/vibeadd/vibeadd.com/hyvatestproject/app/design/frontend/MediaDivision/HyvaTestTheme/"

rsync -az --delete \
  --exclude node_modules \
  --exclude .git \
  --exclude pub/static \
  --exclude var/view_preprocessed \
  "$LOCAL_THEME" \
  "$REMOTE_THEME"
```

## 2.5 Deploy custom modules copied from `deploy/`

```bash
LOCAL_MODULES="$(pwd)/output/ftcshop/custom-modules/"
REMOTE_MODULES="vibeadd@vibeadd.ftp.tools:/home/vibeadd/vibeadd.com/hyvatestproject/app/code/"

rsync -az "$LOCAL_MODULES" "$REMOTE_MODULES"
```

## 2.6 Verify files on server right after upload

```bash
ssh vibeadd@vibeadd.ftp.tools '
set -e
THEME=/home/vibeadd/vibeadd.com/hyvatestproject/app/design/frontend/MediaDivision/HyvaTestTheme

test -f "$THEME/Magento_Theme/templates/html/header.phtml"
test -f "$THEME/web/css/luma-compat.css"
test -f "$THEME/web/css/design-fixes.css"
test -f "$THEME/web/css/design-fixes-additions.css"
test -f "$THEME/Magento_Theme/layout/default.xml"

echo "[OK] critical deploy files exist"

if find "$THEME" -type d -name node_modules | grep -q .; then
  echo "[FAIL] node_modules exists in deployed theme"
  exit 1
fi

echo "[OK] node_modules is not deployed"
'
```

---

## 3. Magento Server Activation Commands

SSH to server:

```bash
ssh vibeadd@vibeadd.ftp.tools
cd /home/vibeadd/vibeadd.com/hyvatestproject
```

Set PHP binary if needed:

```bash
PHP_BIN=/usr/local/php83/bin/php
```

Run Magento maintenance commands:

```bash
$PHP_BIN bin/magento setup:upgrade
$PHP_BIN bin/magento setup:di:compile
$PHP_BIN bin/magento setup:static-content:deploy de_DE en_US -f
$PHP_BIN bin/magento cache:flush
$PHP_BIN bin/magento indexer:reindex
```

## 3.1 Validate layout/header wiring on server

```bash
rg -n "header-content|cart-drawer|header-search|topmenu|logo" \
  app/design/frontend/MediaDivision/HyvaTestTheme/Magento_Theme/layout/default.xml

rg -n "display=\"false\"|require-shim|window\\.require\\s*=" \
  app/design/frontend/MediaDivision/HyvaTestTheme/Magento_Theme/layout/default.xml \
  app/design/frontend/MediaDivision/HyvaTestTheme/Magento_Theme/layout/default_head_blocks.xml \
  app/design/frontend/MediaDivision/HyvaTestTheme
```

---

## 4. Theme, Logo, Search Configuration

## 4.1 Get Theme ID for `MediaDivision/HyvaTestTheme`

```bash
mysql -e "SELECT theme_id, theme_path, theme_title FROM theme WHERE theme_path='MediaDivision/HyvaTestTheme';" -N
```

If needed, insert theme row (example pattern, adjust parent ID):

```bash
mysql -e "INSERT INTO theme (area, theme_path, parent_id, theme_title, is_featured, type, code) \
SELECT 'frontend','MediaDivision/HyvaTestTheme',(SELECT theme_id FROM theme WHERE theme_path='Hyva/default' LIMIT 1),'FTC Cashmere Hyva Test',0,0,'MediaDivision/HyvaTestTheme' \
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM theme WHERE theme_path='MediaDivision/HyvaTestTheme');"
```

## 4.2 Activate theme

```bash
THEME_ID="$(mysql -N -e "SELECT theme_id FROM theme WHERE theme_path='MediaDivision/HyvaTestTheme' LIMIT 1;")"
$PHP_BIN bin/magento config:set design/theme/theme_id "$THEME_ID"
```

## 4.3 Configure logo used by `$block->getChildHtml('logo')`

```bash
$PHP_BIN bin/magento config:set design/header/logo_src images/logo.svg
$PHP_BIN bin/magento config:set design/header/logo_alt "FTC Cashmere"
$PHP_BIN bin/magento config:set design/header/logo_width 220
$PHP_BIN bin/magento config:set design/header/logo_height 80
```

## 4.4 Configure search engine fallback for shared hosting

```bash
$PHP_BIN bin/magento config:set catalog/search/engine lmysql
$PHP_BIN bin/magento indexer:reindex catalogsearch_fulltext
```

---

## 5. DB Dump Procedure (hyvatestproject)

This section provides reproducible commands your dev team can run to create and share a dump from `https://hyvatestproject.vibeadd.com/`.

SSH:

```bash
ssh vibeadd@vibeadd.ftp.tools
cd /home/vibeadd/vibeadd.com/hyvatestproject
```

Extract DB credentials from Magento `env.php`:

```bash
eval "$(
php -r '
$env = include "app/etc/env.php";
$db = $env["db"]["connection"]["default"];
echo "DB_HOST=" . escapeshellarg($db["host"]) . PHP_EOL;
echo "DB_NAME=" . escapeshellarg($db["dbname"]) . PHP_EOL;
echo "DB_USER=" . escapeshellarg($db["username"]) . PHP_EOL;
echo "DB_PASS=" . escapeshellarg($db["password"]) . PHP_EOL;
'
)"
```

Create dump:

```bash
mkdir -p var/backups
DUMP_FILE="var/backups/hyvatestproject_$(date +%F_%H%M%S).sql.gz"

mysqldump \
  --host="$DB_HOST" \
  --user="$DB_USER" \
  --password="$DB_PASS" \
  --single-transaction \
  --quick \
  --routines \
  --triggers \
  --no-tablespaces \
  "$DB_NAME" \
  | gzip -1 > "$DUMP_FILE"

echo "Dump file: $DUMP_FILE"
```

Validate dump:

```bash
gzip -t "$DUMP_FILE"
sha256sum "$DUMP_FILE"
ls -lh "$DUMP_FILE"
```

Download dump to local machine:

```bash
scp vibeadd@vibeadd.ftp.tools:/home/vibeadd/vibeadd.com/hyvatestproject/$DUMP_FILE .
```

---

## 6. Post-Deploy Smoke Test Checklist

Validate these pages and components:

- Homepage
- Category pages
- Product pages
- Login/Register pages
- Header logo + top menu + search + cart drawer
- Wishlist icon/counter
- Swatches (including custom swatch image behavior)
- German copy in key UI strings (newsletter wording, cart labels)

Recommended quick checks:

```bash
curl -I https://hyvatestproject.vibeadd.com/
curl -s https://hyvatestproject.vibeadd.com/ | head -n 40
```

Manual browser QA:

- No broken layout on inner pages
- No JS console errors tied to RequireJS/jQuery fallbacks
- Header interactions work (region chooser, search, cart)

## 6.1 Translation QA (Point 11)

Check whether required German wording is present:

```bash
rg -n "Newsletter abonnieren|Anmeldung zum Newsletter|Sign Up for Newsletter" \
  app/design/frontend/MediaDivision/HyvaTestTheme/i18n/de_DE.csv
```

If you need to enforce the exact phrase:

```bash
echo '"Sign Up for Newsletter","Anmeldung zum Newsletter"' >> \
  app/design/frontend/MediaDivision/HyvaTestTheme/i18n/de_DE.csv

$PHP_BIN bin/magento setup:static-content:deploy de_DE -f
$PHP_BIN bin/magento cache:flush
```

---

## 7. Rollback (Fast)

If deployment fails visually/functionally:

1. Restore previous theme snapshot with `rsync`/backup archive.
2. Revert `design/theme/theme_id` to previous value.
3. Flush cache and redeploy static content.

Example:

```bash
$PHP_BIN bin/magento config:set design/theme/theme_id <PREVIOUS_THEME_ID>
$PHP_BIN bin/magento cache:flush
$PHP_BIN bin/magento setup:static-content:deploy de_DE en_US -f
```

---

## 8. Dev Team Handoff Package (SSH + DB Dump)

When your dev team asks for direct access + database snapshot, send:

1. SSH endpoint:
- Host: `vibeadd.ftp.tools`
- User: `<team-specific user>`
- Project path: `/home/vibeadd/vibeadd.com/hyvatestproject`

2. Database dump artifact:
- Absolute file path on server, for example: `/home/vibeadd/vibeadd.com/hyvatestproject/var/backups/hyvatestproject_YYYY-MM-DD_HHMMSS.sql.gz`
- SHA256 checksum from `sha256sum`
- File size from `ls -lh`

3. Theme build identity:
- Git commit hash used for generation
- Generator command used
- Timestamp of deployment

Template message you can paste:

```text
SSH access is ready on vibeadd.ftp.tools.
Magento root: /home/vibeadd/vibeadd.com/hyvatestproject
DB dump: /home/vibeadd/vibeadd.com/hyvatestproject/var/backups/hyvatestproject_YYYY-MM-DD_HHMMSS.sql.gz
SHA256: <checksum>
Theme commit: <git hash>
Generation command: python3 generate.py --project projects/ftcshop --vendor MediaDivision --theme FTCShopHyva --output output/ftcshop
Deployment timestamp: <UTC timestamp>
```
