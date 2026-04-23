# FTC Hyva Parity Checklist (Full)

Date: 2026-04-21  
Source: `ftc-hyva-check.zip` (`reports/2026-04-21_17-10-report*.md`, `reports/2026-04-21_17-50-report-EN-v2.md`, `screenshots/*`, `diffs/*`, `links-*.json`) + latest client screenshots in chat.

Status legend:
- `[ ]` not done
- `[-]` in progress
- `[x]` done
- `[!]` blocked / needs client decision

---

## 0) Release Gate (must be green before client sign-off)

- [ ] Pixel + behavior parity on key pages:
  - `/`
  - `/de-de/damen.html`
  - `/de-de/herren.html`
  - `/de-de/care.html` (`/de-de/living.html`)
  - sample PDP (`/de-de/10304-0320-gestreifter-polo-cardigan.html`)
- [ ] Checkout parity:
  - `/de-de/checkout/cart/`
  - `/de-de/checkout/#login_register`
  - shipping/payment/review steps
- [ ] No critical functionality regressions:
  - add-to-cart
  - wishlist
  - minicart
  - cart qty/edit/remove
  - checkout transitions
- [ ] No obvious visual regressions on desktop/tablet/mobile.

---

## 1) Critical blockers (from archive reports)

### 1.1 Staging safety / SEO
- [x] Set staging to `noindex,nofollow` (meta + `X-Robots-Tag`).
- [ ] Optionally protect staging by Basic Auth.

### 1.2 Homepage structure and content
- [x] Restore homepage product tile blocks (client reported missing in report snapshots).
- [ ] Ensure add-to-cart forms exist in homepage tiles where original has them.
- [ ] Remove unintended orange `SALE SALE SALE` strip (if not approved by client).
- [x] Align hero section content/images with original or with client-approved current campaign.

### 1.3 Mobile global issues
- [x] Fix horizontal overflow (375 viewport must render without widened canvas).
- [x] Restore mobile header controls (menu/search/account/wishlist/cart) if hidden/broken.
- [x] Fix mobile footer typography overlaps.

### 1.4 Tracking parity
- [ ] Restore GTM/GA4/Ads/Pinterest/HubSpot tags (if they must match original setup).
- [ ] Verify consent integration does not block intended tracking unexpectedly.

### 1.5 PDP commerce parity
- [ ] Restore configurable variant parity on sampled PDP (original has more color variants).
- [ ] Verify swatch switching updates image/price/availability correctly.

---

## 2) Header / navigation parity

### 2.1 Header geometry and spacing
- [x] Normalize header paddings/vertical rhythm to original.
- [ ] Verify exact spacing in desktop/tablet/mobile for logo, nav, locale, search, icons.
- [-] Verify cart counter baseline alignment (digits must not jump upward).

### 2.2 Top menu parity
- [ ] Match top-level menu with original (`SALE` vs `BABY`) or get explicit client approval for deviation.
- [x] Match active item underline style/position (`HOME` screenshots marked by client).
- [ ] Ensure hover/focus states and dropdown behavior match original.

### 2.3 Cross-page consistency
- [x] Ensure checkout/cart headers keep expected visibility and do not collapse incorrectly.
- [x] Fix checkout search field positioning in header.

---

## 3) Homepage parity (`/`)

### 3.1 Above the fold
- [ ] Match hero block dimensions and crop.
- [ ] Match line breaks and spacing in intro copy.
- [-] Match nav + header offsets for all viewports.

### 3.2 Product rows and cards
- [-] Match visible product sets/order to original.
- [-] Match card image aspect ratio/crop.
- [-] Match title/price typography and card spacing.
- [ ] Match wishlist icon position on each card.
- [-] Match add-to-cart availability and behavior in card context.

### 3.3 Below-the-fold sections
- [ ] Match all promotional content blocks (Essence/Care/Tiny Luxe etc. where present in original scope).
- [ ] Match slider/carousel behavior and controls if used.

---

## 4) Category pages parity

Targets:
- `/de-de/damen.html`
- `/de-de/herren.html`
- `/de-de/care.html` / `/de-de/living.html`

### 4.1 Hero and CMS blocks
- [x] Restore main hero/cms visual block where missing.
- [ ] Validate exact text/image parity per category.

### 4.2 Toolbar row
- [x] Restore product count (`toolbar-amount`, e.g. `13 ARTIKEL`).
- [ ] Match sorting control spacing/alignment/text exactly.
- [ ] Keep/remove breadcrumbs exactly as in original behavior.

### 4.3 Listing behavior
- [ ] Match pagination strategy (`infinite` vs `Mehr laden`) to original, especially on Herren mobile.
- [-] Match number of initially visible products per viewport.

### 4.4 Product card details
- [ ] Match hover overlays and transitions.
- [ ] Match swatches/badges/wishlist icon placements.
- [ ] Match typography and inter-card gaps.

---

## 5) PDP parity

Target:
- `/de-de/10304-0320-gestreifter-polo-cardigan.html`

### 5.1 Gallery behavior
- [ ] Match thumbnail rail spacing and selected-state border.
- [-] Match arrow style, placement, hover-trigger animation.
- [ ] Match zoom icon behavior/position (appears on hover, same anchor point).
- [ ] Remove residual borders/artifacts not present in original.

### 5.2 Info column
- [ ] Match title/article/price vertical spacing.
- [ ] Match swatch row layout and thumbnail sizes.
- [ ] Match size label + size guide row alignment.
- [-] Match add-to-cart button dimensions and vertical offsets.
- [ ] Match wishlist heart alignment next to add-to-cart.

### 5.3 Accordion
- [ ] Match divider spacing and stroke.
- [-] Move plus icons to the same inset as original (not glued to the edge).
- [ ] Match expand/collapse animation speed/easing.

### 5.4 Additional content below fold
- [ ] Restore missing promotional blocks/images if they are part of original expected PDP scope.

---

## 6) Minicart / cart / checkout parity

### 6.1 Mini-cart modal/drawer
- [-] Match opening logic (where it appears, whether centered/offset, animation timing).
- [-] Match overlay opacity and background dim.
- [-] Match modal size, internal paddings, and bottom spacing.
- [-] Match title row (`WARENKORB`, item count, total, close icon).
- [-] Match line item row (thumb/title/options/qty/remove/price).
- [-] Match action buttons (`Weiter zum Warenkorb`, `Weiter zur Kasse`) sizing and spacing.

### 6.2 Cart page (`/de-de/checkout/cart/`)
- [-] Match left/right layout proportions.
- [-] Match qty control style and placement.
- [-] Match summary block typography and rows.
- [-] Match coupon area appearance and behavior.
- [x] Reproduce expected guest email modal behavior on cart (session-gated popup with close-on-backdrop/button).

### 6.3 Checkout step page (`/de-de/checkout/#login_register`)
- [x] Keep header visible and aligned like original.
- [x] Match stepper circles/lines/labels spacing.
- [x] Match three columns (Login/New account/Guest) widths and top offsets.
- [x] Match input/button dimensions and text styles.
- [ ] Validate transitions to shipping/payment/review.

---

## 7) Links / routing parity

### 7.1 Missing links from original homepage context
- [ ] Restore/redirect missing product URLs referenced in report.
- [ ] Restore/redirect original SALE URL tree (`/damen/sale-damen...`, `/herren/sale-herren...`).
- [ ] Restore utility links where expected (`advanced search`, `cart`, language switch, privacy).

### 7.2 Hardcoded domain leakage
- [x] Replace all links pointing to `shop.ftc-cashmere.com` inside test site content where they should remain local/relative.

---

## 8) Performance and quality

- [ ] Re-check page speed after parity fixes (homepage/category/PDP).
- [-] Ensure caches/static assets are properly warmed/deployed.
- [ ] Confirm no console errors introduced by parity fixes.

---

## 9) Final QA loop and delivery

- [ ] Re-run screenshot comparison on desktop/tablet/mobile for all key pages.
- [ ] Re-run functional checks:
  - add to cart
  - wishlist
  - minicart
  - cart update/remove
  - checkout start
- [ ] Mark each checklist item with final status.
- [ ] Prepare concise client update:
  - what was fixed
  - what remains
  - what requires explicit client decision/approval

---

## 10) Execution log (current run)

- [x] Parse client archive `ftc-hyva-check.zip`.
- [x] Build full checklist in repo root.
- [-] Continue with fixes by priority (critical -> page parity -> final QA).
- [x] Re-run screenshot capture + image diff audit (desktop/mobile, key pages).
- [-] Apply mobile parity fixpack in `deploy/design-fixes.css` (header controls row + footer stacking).
- [-] Force HOME underline parity for homepage/living pages.
- [x] Deploy updated `design-fixes.css` to staging theme/static and clear Magento caches.
- [x] Replace hardcoded `shop.ftc-cashmere.com` links in staging DB content tables (`cms_block`, `cms_page`, `catalog_category_entity_text`).
- [x] Re-check key mobile pages: viewport width now stable at `375px` (`/`, `care`, PDP, cart).
- [x] Re-check checkout login step state on staging (header + search alignment now stable).
- [x] Add reusable script `deploy/replace_hardcoded_live_domain_links.php` for domain-leak cleanup.
- [-] Add checkout/cart parity CSS pass in `deploy/design-fixes.css` (stepper, cart table/summary, minicart overlay alignment).
- [-] Add guest e-mail prompt modal skeleton on cart page (`deploy/cart.phtml`) to mirror original cart flow.
- [x] Sync top categories product ordering from original HTML: `4 (Damen)`, `5 (Herren)`, `7 (Home/Living)`, `270 (Care)`, `281 (Baby)`.
- [x] Sync CMS homepage `home-de` from original GraphQL and re-run hardcoded domain replacement.
- [-] Inject guest e-mail popup directly into active Luma fallback cart template (`FTCShop/Magento_Checkout/templates/cart/form.phtml`) and continue visual tuning.
- [x] Sync missing media assets from original to staging (`pub/media/cms`, `pub/media/product`, `pub/media/catalog/category`) to eliminate broken homepage/category visuals.
- [x] Re-run desktop screenshot comparison after media sync:
  - `/de-de/checkout/#login_register` parity check with cart item context (`RMSE 0.0099`).
  - `/de-de/living.html` visual pass (close parity).
  - PDP `/de-de/00008-0251-schal-mit-rippenmuster.html` visual pass (close parity, minor dynamic-state diffs).
- [-] Start full catalog image cache regeneration on staging (`bin/magento catalog:images:resize`, running).
- [x] Fix FTCShop checkout/cart static asset delivery on staging:
  - remove broken symlinks in `pub/static/frontend/MediaDivision/FTCShop/de_DE` by re-syncing real files
  - restore missing files (`Mirasvit_Core/css/fontawesome.min.css`, `images/loader-2.gif`)
  - verify `checkout/#login_register` and `checkout/cart/` load `27/27` FTCShop assets with no 4xx.
- [x] Enable and deploy `MediaDivision_StagingSecurity` module on staging; verify `X-Robots-Tag: noindex, nofollow` in HTTP headers.
- [x] Re-run Magento build steps on staging after module deployment:
  - `setup:upgrade`
  - `setup:di:compile` (with increased PHP memory limit)
  - `setup:static-content:deploy -f de_DE` for required themes.
- [x] Deploy original FTC CatalogWidget homepage template override into active `HyvaTestTheme`:
  - add `deploy/Magento_CatalogWidget/templates/product/widget/content/grid.phtml`
  - deploy to staging theme and clear `layout/block_html/full_page` caches.
- [-] Rework homepage widget container CSS parity:
  - normalize `.products-grid` / `.product-items.widget-product-grid` width behavior (remove 317px narrow column issue)
  - continue tuning desktop row clipping/spacing and duplicated-loop visibility vs original screenshots.
- [x] Disable checkout SRI hash injection in active Hyva theme (`Magento_Csp/layout/checkout_index_index.xml`) to remove integrity-mismatch script blocking.
- [x] Remove duplicated Luma search block from checkout/cart layout (`top.search`) and keep only inline header search to prevent floating second-row search field.
- [x] Stabilize cart guest-email modal logic in deploy templates:
  - switch to `.is-open` class toggle (no CSS-vs-inline display race)
  - keep popup limited to guest + checkout-cart page
  - preserve close behavior (close icon, submit button, backdrop).
- [-] Apply final checkout/cart header parity override pass in `deploy/design-fixes.css`:
  - hide fallback `.block-search` / overlay on checkout/cart
  - harden right-nav baseline and counter alignment
  - lower minicart modal vertical anchor and restore bottom breathing room.
- [x] Deploy updated parity files to staging theme (`HyvaTestTheme`) and run Magento cache clean/flush (`layout`, `block_html`, `full_page`).
