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
- [-] Set staging to `noindex,nofollow` (meta + `X-Robots-Tag`).
- [ ] Optionally protect staging by Basic Auth.

### 1.2 Homepage structure and content
- [ ] Restore homepage product tile blocks (client reported missing in report snapshots).
- [ ] Ensure add-to-cart forms exist in homepage tiles where original has them.
- [ ] Remove unintended orange `SALE SALE SALE` strip (if not approved by client).
- [ ] Align hero section content/images with original or with client-approved current campaign.

### 1.3 Mobile global issues
- [-] Fix horizontal overflow (375 viewport must render without widened canvas).
- [ ] Restore mobile header controls (menu/search/account/wishlist/cart) if hidden/broken.
- [ ] Fix mobile footer typography overlaps.

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
- [ ] Verify cart counter baseline alignment (digits must not jump upward).

### 2.2 Top menu parity
- [ ] Match top-level menu with original (`SALE` vs `BABY`) or get explicit client approval for deviation.
- [ ] Match active item underline style/position (`HOME` screenshots marked by client).
- [ ] Ensure hover/focus states and dropdown behavior match original.

### 2.3 Cross-page consistency
- [ ] Ensure checkout/cart headers keep expected visibility and do not collapse incorrectly.
- [-] Fix checkout search field positioning in header.

---

## 3) Homepage parity (`/`)

### 3.1 Above the fold
- [ ] Match hero block dimensions and crop.
- [ ] Match line breaks and spacing in intro copy.
- [ ] Match nav + header offsets for all viewports.

### 3.2 Product rows and cards
- [ ] Match visible product sets/order to original.
- [ ] Match card image aspect ratio/crop.
- [ ] Match title/price typography and card spacing.
- [ ] Match wishlist icon position on each card.
- [ ] Match add-to-cart availability and behavior in card context.

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
- [ ] Match number of initially visible products per viewport.

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
- [ ] Match opening logic (where it appears, whether centered/offset, animation timing).
- [ ] Match overlay opacity and background dim.
- [-] Match modal size, internal paddings, and bottom spacing.
- [ ] Match title row (`WARENKORB`, item count, total, close icon).
- [ ] Match line item row (thumb/title/options/qty/remove/price).
- [ ] Match action buttons (`Weiter zum Warenkorb`, `Weiter zur Kasse`) sizing and spacing.

### 6.2 Cart page (`/de-de/checkout/cart/`)
- [ ] Match left/right layout proportions.
- [ ] Match qty control style and placement.
- [ ] Match summary block typography and rows.
- [ ] Match coupon area appearance and behavior.
- [ ] Reproduce/confirm expected email modal behavior (if this is custom business logic on original).

### 6.3 Checkout step page (`/de-de/checkout/#login_register`)
- [-] Keep header visible and aligned like original.
- [ ] Match stepper circles/lines/labels spacing.
- [ ] Match three columns (Login/New account/Guest) widths and top offsets.
- [ ] Match input/button dimensions and text styles.
- [ ] Validate transitions to shipping/payment/review.

---

## 7) Links / routing parity

### 7.1 Missing links from original homepage context
- [ ] Restore/redirect missing product URLs referenced in report.
- [ ] Restore/redirect original SALE URL tree (`/damen/sale-damen...`, `/herren/sale-herren...`).
- [ ] Restore utility links where expected (`advanced search`, `cart`, language switch, privacy).

### 7.2 Hardcoded domain leakage
- [ ] Replace all links pointing to `shop.ftc-cashmere.com` inside test site content where they should remain local/relative.

---

## 8) Performance and quality

- [ ] Re-check page speed after parity fixes (homepage/category/PDP).
- [ ] Ensure caches/static assets are properly warmed/deployed.
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
