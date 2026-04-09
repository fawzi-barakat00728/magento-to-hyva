# Magento Luma → Hyvä Migration Tool

Automated toolset for migrating Magento 2 shops from Luma-based themes to Hyvä frontend.
Converts KnockoutJS/RequireJS/jQuery templates to Alpine.js, LESS styles to Tailwind CSS.

**Tested with**: Magento 2.4.8 + Hyvä 1.4.5 (Tailwind CSS v4)

## Features

- **Design token extraction** — Automatically extracts colors, fonts, breakpoints, and font sizes from LESS variables
- **Tailwind v3 & v4 support** — Generates CSS-first config (`@theme` block) for v4 or JS config for v3
- **Safe template strategy** — Uses rewrite/skip/preserve rules, then applies production overrides from `deploy/` as final layer
- **Layout XML conversion** — Adapts Luma layout XMLs for Hyvä block structure
- **Hyvä-native header wiring** — Uses `header-content` template override (keeps logo/topmenu/search/cart child blocks alive)
- **Deploy pack auto-apply** — Production-tested files from `deploy/` are copied automatically into generated output
- **No RequireJS shim by default** — Avoids silent failures from no-op `require()` shims in Hyvä
- **i18n enrichment** — Extracts translatable strings from templates and enriches locale CSV files
- **Module compatibility analysis** — Identifies modules needing Hyvä compatibility packages, generates stub modules
- **Asset migration** — Copies fonts, images, icons, and social media assets

## Structure

- **analyzer/** — Phase 1: Scan & analyze existing Magento installation
  - `scan.py` — Main orchestrator
  - `theme_scanner.py` — Detects KO/RequireJS/jQuery patterns, assigns complexity
  - `modules_checker.py` — Checks Hyvä compatibility for all modules
  - `report_generator.py` — Generates Markdown + JSON reports with effort estimates
- **generator/** — Phase 2: Generate Hyvä child theme
  - `style_extractor.py` — Extracts design tokens from LESS files
  - `hyva_theme.py` — Scaffolds complete Hyvä child theme with Tailwind v3 or v4 config
  - `template_converter.py` — Strategy mapping for all template overrides
  - `layout_converter.py` — Converts Luma layout XMLs to Hyvä equivalents
  - `templates/` — Safe Hyvä phtml rewrites (Alpine.js, Tailwind CSS)
  - `templates/optional/` — Store-specific templates (product views, third-party modules) — not deployed by default
- **config/** — Known modules DB (Hyvä compatibility database)
- **projects/** — Local copies of Magento installations (gitignored: vendor, pub/media)
- **output/** — Generated themes and reports (gitignored)
- **tests/** — Theme validation and Hyvä stub generation

## Usage

### Phase 1: Analyze
```bash
python3 analyzer/scan.py --project projects/myshop --output output/myshop
```

### Phase 2: Generate Hyvä Theme

**Tailwind v4** (default, for Hyvä 1.4.5+):
```bash
python3 generate.py \
  --project projects/myshop \
  --vendor MyVendor \
  --theme MyShopHyva \
  --title "My Shop Hyvä" \
  --output output/myshop
```

**Tailwind v3** (for older Hyvä versions):
```bash
python3 generate.py \
  --project projects/myshop \
  --vendor MyVendor \
  --theme MyShopHyva \
  --title "My Shop Hyvä" \
  --output output/myshop \
  --tailwind-version 3
```

### CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `--project` | required | Path to local Magento project copy |
| `--vendor` | required | Vendor name for the theme |
| `--theme` | required | Theme name |
| `--title` | `"{theme} Theme"` | Human-readable theme title |
| `--output` | required | Output directory |
| `--tailwind-version` | `4` | Tailwind CSS version (3 or 4) |

### Output

The generator produces a complete Hyvä child theme:

**Tailwind v4** (default):
- `web/tailwind/hyva.config.json` — Design tokens as JSON (colors, fonts, screens)
- `web/tailwind/tailwind-source.css` — CSS-first config with `@import "tailwindcss"`, `@theme` block, `@source` directives
- `package.json` — Uses `@tailwindcss/cli ^4.1` and `@hyva-themes/hyva-modules ^1.3`

**Tailwind v3**:
- `web/tailwind/tailwind.config.js` — JS-based Tailwind config with design tokens
- `web/tailwind/tailwind-source.css` — Traditional `@tailwind` directives
- `package.json` — Uses `tailwindcss ^3.4` with PostCSS plugins

**Both versions also include**:
- `registration.php`, `theme.xml`, `composer.json`
- `web/css/fonts.css` — @font-face declarations auto-detected from source theme
- Template rewrites (Alpine.js replacements for safe overrides)
- Layout XMLs (adapted for Hyvä block structure)
- Static assets (images, fonts, translations)

## Deploy Overrides (`deploy/`)

The generator now automatically applies production-tested overrides from `deploy/` after normal template/layout generation.

Critical files copied automatically include:
- `deploy/header.phtml` → `Magento_Theme/templates/html/header.phtml`
- `deploy/luma-compat.css` → `web/css/luma-compat.css`
- `deploy/design-fixes.css` → `web/css/design-fixes.css`
- `deploy/design-fixes-additions.css` → `web/css/design-fixes-additions.css`
- `deploy/catalog_product_view.xml` → `Magento_Catalog/layout/catalog_product_view.xml`
- `deploy/view.xml` → `etc/view.xml`
- `deploy/de_DE.csv` → `i18n/de_DE.csv`

Additional product/swatch/listing template overrides from `deploy/` are also copied automatically.

Custom modules from `deploy/DisabledProductView` and `deploy/PaginationFix` are copied to:
- `output/<project>/custom-modules/MediaDivision/...`

## Deployment

After generating the theme:

```bash
# 1. Build Tailwind CSS
cd output/myshop/MyVendor/MyShopHyva
npm install && npm run build

# 2. Deploy theme to Magento (exclude runtime dirs)
rsync -a --delete \
  --exclude node_modules \
  --exclude .git \
  output/myshop/MyVendor/MyShopHyva/ \
  /path/to/magento/app/design/frontend/MyVendor/MyShopHyva/

# 3. Install Hyvä compat packages (see compatibility report)
composer require hyva-themes/hyva-compat-<module>

# 4. Copy stub modules
cp -r output/myshop/compatibility/stubs/* /path/to/magento/app/code/

# 5. Copy custom deploy modules (if generated)
cp -r output/myshop/custom-modules/* /path/to/magento/app/code/

# 6. Activate and deploy
bin/magento setup:upgrade
bin/magento setup:di:compile
bin/magento setup:static-content:deploy
bin/magento cache:flush
```

For a full production workflow (Git -> server), issue closure matrix (points 1-12),
and DB dump instructions for `hyvatestproject`, use:

- [`docs/GIT_TO_SERVER_RUNBOOK.md`](/Users/oleksandr/Documents/GitHub/magento-to-hyva/docs/GIT_TO_SERVER_RUNBOOK.md)

### Magento Admin / Config Checklist

```bash
# Activate theme
bin/magento config:set design/theme/theme_id <THEME_ID>

# Configure logo (used by $block->getChildHtml('logo') in header.phtml)
bin/magento config:set design/header/logo_src images/logo.svg
bin/magento config:set design/header/logo_alt "Store Logo"

# Search engine (shared hosting fallback)
bin/magento config:set catalog/search/engine lmysql
```

## Shared Hosting Notes

If deploying on shared hosting without OpenSearch/Elasticsearch:
- Install [swissup/module-search-mysql-legacy](https://github.com/nickthecoder/module-search-mysql-legacy) for MySQL-based catalog search
- Set search engine: `bin/magento config:set catalog/search/engine lmysql`
- Reindex: `bin/magento indexer:reindex`

## Requirements
- Python 3.10+
- Magento 2.4.x project files (local copy or SSH access)
- Hyvä Theme license (for deployment)
- Node.js 18+ (for Tailwind CSS build)
