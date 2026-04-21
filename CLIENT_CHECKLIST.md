# Client Checklist — FTC Hyva Parity

Source: `/tmp/ftc-hyva-check/reports/2026-04-21_17-10-report.md`, `2026-04-21_17-10-report-EN.md`, `2026-04-21_17-50-report-EN-v2.md` + latest client screenshots.

Status legend:
- `[ ]` not done
- `[-]` in progress
- `[x]` done

## 1) Launch blockers (Critical)

### 1.1 SEO / indexing / staging safety
- [ ] Set staging to `noindex,nofollow` in HTML meta and HTTP `X-Robots-Tag`.
- [ ] (Optional hardening) Protect staging with HTTP Basic Auth.

### 1.2 Homepage structural parity
- [ ] Restore homepage product grid (product cards visible like original).
- [ ] Restore homepage Add-to-Cart forms inside product tiles.
- [ ] Remove unintended orange "SALE SALE SALE" strip if not in original.
- [ ] Align homepage hero section layout and image blocks to original.

### 1.3 Navigation parity
- [ ] Restore top navigation parity (`SALE` vs `BABY` difference to be resolved).
- [ ] Ensure active menu underline style/position matches original (`HOME` highlight issue from screenshots).
- [ ] Fix header vertical spacing/height mismatch from client screenshots.

### 1.4 Mobile critical UX
- [ ] Eliminate horizontal overflow (375px viewport must render 375px, no forced 497px width).
- [ ] Restore mobile header controls (menu/search/account/wishlist/cart) if missing.
- [ ] Fix mobile footer overlap/typography collisions.

### 1.5 Tracking / analytics
- [ ] Restore GTM + GA4 + Ads + Pinterest + HubSpot tracking parity (respecting consent integration).
- [ ] Verify no tracking regressions on homepage/category/PDP/cart/checkout.

### 1.6 Commerce data parity
- [ ] PDP configurable variants parity (5 colors in original vs 1 in Hyva for sampled PDP).
- [ ] Validate swatches, variant switching and price/image sync.

## 2) Category pages parity (Damen / Herren / Care/Living)

### 2.1 Hero / content blocks
- [x] Restore category hero/content blocks where present on original (Care/Living mismatch).
- [ ] Keep/remove category breadcrumbs exactly like original behavior.

### 2.2 Toolbar / listing controls
- [x] Show correct product count (`toolbar-amount`, e.g. `13 ARTIKEL`) where original shows it.
- [ ] Match sorting row spacing, labels and alignment.
- [ ] Match load-more / infinite scroll behavior to original (notably Herren mobile).

### 2.3 Product cards
- [ ] Verify card image sizes, crop, spacing, hover overlays and wishlist icon positions.
- [ ] Match badge/swatch/count rendering and typography.

## 3) PDP (product page) parity

### 3.1 Layout and spacing
- [ ] Match gallery rail spacing, arrows, and hover-trigger behavior (desktop/tablet/mobile).
- [ ] Match zoom icon behavior and position (show on hover, same anchor point).
- [ ] Remove any extra borders/artifacts not present on original.

### 3.2 Product info block
- [ ] Match title, article number, price block, swatches row spacing.
- [ ] Match size dropdown row label + size guide alignment.
- [ ] Match Add-to-Cart button height/width/offset and heart icon alignment.

### 3.3 Accordion section
- [ ] Match accordion divider thickness/spacing.
- [ ] Move plus icons to original inset position (not glued to edge).

### 3.4 Below-the-fold content
- [ ] Restore missing promotional/content blocks visible on original PDP (tablet/mobile deltas).

## 4) Cart / mini-cart / checkout parity

### 4.1 Mini-cart drawer/modal
- [ ] Reproduce original mini-cart opening behavior, animation and placement.
- [ ] Match mini-cart container size, margins, bottom gap, overlay opacity.
- [ ] Match line-item layout (thumb, title, qty controls, remove icon, totals).
- [ ] Match action buttons style and spacing (cart/checkout buttons).

### 4.2 Cart page
- [ ] Match desktop cart layout (left items + right summary block spacing/typography).
- [ ] Fix header cart counter vertical alignment (digits should not jump upward).
- [ ] Ensure coupon/promo row and controls match original styles.

### 4.3 Checkout flow (`/de-de/checkout/#login_register` and next steps)
- [ ] Keep checkout header visible and identical (logo/menu/icons/search positioning).
- [ ] Fix search field placement in checkout header.
- [ ] Match stepper circles/lines/text alignment and spacing.
- [ ] Match login/register/guest columns, inputs and buttons dimensions.
- [ ] Validate functional parity for login → shipping → payment → review.

### 4.4 Email modal behavior (client note)
- [ ] Verify and reproduce original email modal behavior on cart/checkout trigger, if it is expected business logic.

## 5) Links / routing / domain integrity

### 5.1 Missing links from original homepage
- [ ] Restore/redirect 21 product links present in original homepage tiles.
- [ ] Restore/redirect SALE URL tree (13 original links), avoid broken routes.
- [ ] Restore important utility links (advanced search, cart, language switch, privacy) where expected.

### 5.2 Cross-domain leakage
- [ ] Replace all `shop.ftc-cashmere.com` hard links in new site with correct local-domain/relative URLs.

## 6) SEO and structured data parity

- [ ] Add Product JSON-LD on PDP (both original/new currently lacking full product schema).
- [ ] Review canonical/hreflang/title/meta description gaps and align strategy.
- [ ] Improve `alt` coverage for migrated images (new site currently worse ratio).

## 7) Performance parity

- [ ] Investigate FCP/load regression (new site much slower in reports).
- [ ] Verify cache/CDN/static deployment parity for fair comparison.
- [ ] Re-measure homepage/category/PDP on desktop/tablet/mobile after fixes.

## 8) Final QA pass (pixel + behavior)

- [ ] Re-run screenshot diff on 5 key pages (`/`, `/de-de/damen.html`, `/de-de/herren.html`, `/de-de/care.html`, sampled PDP).
- [ ] Re-test hover, transitions, sticky elements, mini-cart, wishlist, add-to-cart, checkout.
- [ ] Prepare final client message with list of fixed points and any remaining explicit blockers.

## 9) Current execution plan (this run)

- [x] A. Create consolidated checklist in repo root.
- [x] B. Remove CSS rules that hide category hero and toolbar amount; restore announcement bar behavior to match original.
- [-] C. Fix header/search layout parity for checkout + homepage height/spacing deltas from screenshots.
- [ ] D. Fix PDP accordion plus offsets and cart counter alignment.
- [ ] E. Validate on live test domain, then commit and push.
