#!/usr/bin/env python3
"""
Hyvä Theme Generator — Main entry point.
Reads a Magento project, analyzes the Luma theme, and generates
a complete Hyvä child theme with converted templates and layouts.

Usage:
    python generate.py --project projects/ftcshop \
                       --vendor MediaDivision \
                       --theme FTCShopHyva \
                       --output output/ftcshop
"""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generator.style_extractor import extract_design_tokens
from generator.hyva_theme import scaffold_hyva_theme
from generator.template_converter import (
    analyze_template_complexity,
    TEMPLATE_STRATEGY,
)
from generator.layout_converter import (
    process_all_layouts,
    generate_hyva_default_xml,
    generate_hyva_catalog_product_view_xml,
    generate_hyva_catalog_category_view_xml,
)
from compatibility.compat_generator import run_phase3


DEPLOY_THEME_FILE_MAP = {
    # Core theme fixes
    "header.phtml": "Magento_Theme/templates/html/header.phtml",
    "footer-fix.phtml": "Magento_Theme/templates/html/footer.phtml",
    "luma-compat.css": "web/css/luma-compat.css",
    "design-fixes.css": "web/css/design-fixes.css",
    "design-fixes-additions.css": "web/css/design-fixes-additions.css",
    "announcement-bar.css": "web/css/announcement-bar.css",
    "css-fixes.css": "web/css/css-fixes.css",
    "product-css-section.css": "web/css/product-css-section.css",
    "default_head_blocks.xml": "Magento_Theme/layout/default_head_blocks.xml",
    "private-content-bootstrap.phtml": "Magento_Theme/templates/html/private-content-bootstrap.phtml",
    "requirejs-config.js": "requirejs-config.js",
    "checkout_index_index.xml": "Magento_Checkout/layout/checkout_index_index.xml",
    "checkout_cart_index.xml": "Magento_Checkout/layout/checkout_cart_index.xml",
    "checkout-require-baseurl.js": "web/js/checkout-require-baseurl.js",
    "catalog_product_view.xml": "Magento_Catalog/layout/catalog_product_view.xml",
    "view.xml": "etc/view.xml",
    "de_DE.csv": "i18n/de_DE.csv",
    # Template overrides that were previously applied manually
    "gallery.phtml": "Magento_Catalog/templates/product/view/gallery.phtml",
    "list.phtml": "Magento_Catalog/templates/product/list.phtml",
    "toolbar.phtml": "Magento_Catalog/templates/product/list/toolbar.phtml",
    "sorter.phtml": "Magento_Catalog/templates/product/list/toolbar/sorter.phtml",
    "swatch-renderer.phtml": "Magento_Swatches/templates/product/view/renderer.phtml",
    "swatch-item.phtml": "Magento_Swatches/templates/product/swatch-item.phtml",
    "product-detail-page.phtml": "Magento_Catalog/templates/product/product-detail-page.phtml",
    "product-info.phtml": "Magento_Catalog/templates/product/view/product-info.phtml",
    "ftc-product-sections.phtml": "Magento_Catalog/templates/product/view/sections/ftc-product-sections.phtml",
    "menu-desktop.phtml": "Hyva_Theme/templates/html/header/menu/desktop.phtml",
    "cart-drawer.phtml": "Magento_Theme/templates/html/cart/cart-drawer.phtml",
    "cart.phtml": "Magento_Checkout/templates/cart.phtml",
    "cart/form.phtml": "Magento_Checkout/templates/cart/form.phtml",
    "cart/item/default.phtml": "Magento_Checkout/templates/cart/item/default.phtml",
    "cart/item/configure/updatecart.phtml": "Magento_Checkout/templates/cart/item/configure/updatecart.phtml",
    "cart/item/renderer/actions/edit.phtml": "Magento_Checkout/templates/cart/item/renderer/actions/edit.phtml",
    "cart/item/renderer/actions/remove.phtml": "Magento_Checkout/templates/cart/item/renderer/actions/remove.phtml",
    "Mollie_Payment/requirejs-config.js": "Mollie_Payment/requirejs-config.js",
    "Mollie_Payment/web/js/view/payment/method-renderer.js": "Mollie_Payment/web/js/view/payment/method-renderer.js",
    "Mollie_Payment/web/js/view/payment/method-renderer-safe.js": "Mollie_Payment/web/js/view/payment/method-renderer-safe.js",
}

DEPLOY_CUSTOM_MODULES = {
    "DisabledProductView": "MediaDivision/DisabledProductView",
    "PaginationFix": "MediaDivision/PaginationFix",
    "SodiumFallback": "MediaDivision/SodiumFallback",
}


def find_luma_theme(project_path: str) -> str:
    """Find the Luma theme directory in the project."""
    design_path = os.path.join(project_path, "app", "design", "frontend")
    if not os.path.exists(design_path):
        return ""

    for vendor in os.listdir(design_path):
        vendor_dir = os.path.join(design_path, vendor)
        if not os.path.isdir(vendor_dir) or vendor == "Magento":
            continue
        for theme in os.listdir(vendor_dir):
            theme_dir = os.path.join(vendor_dir, theme)
            theme_xml = os.path.join(theme_dir, "theme.xml")
            if os.path.exists(theme_xml):
                return theme_dir
    return ""


def copy_templates(templates_dir: str, output_theme: str, strategy_map: dict) -> list:
    """
    Copy generator templates to the output theme directory only when the
    strategy explicitly allows deployment (`rewrite` or `copy`).

    `optional/` templates are intentionally excluded from automatic deployment.
    Templates with strategy `preserve` are handled separately by
    copy_preserved_templates() which copies originals from the source theme.

    Returns list of copied template paths.
    """
    copied = []
    if not os.path.exists(templates_dir):
        return copied

    for root, _, files in os.walk(templates_dir):
        for fname in files:
            if not fname.endswith(".phtml"):
                continue
            src = os.path.join(root, fname)
            rel = os.path.relpath(src, templates_dir)

            # Optional templates are never auto-deployed.
            if rel.startswith("optional/"):
                continue

            strategy = strategy_map.get(rel, "")
            if strategy not in {"rewrite", "copy"}:
                continue

            dst = os.path.join(output_theme, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            copied.append(rel)

    return copied


def copy_preserved_templates(source_theme: str, output_theme: str, strategy_map: dict) -> list:
    """
    Copy original templates from source Luma theme when strategy is 'preserve'.
    These are complex templates (headers, footers, deep navigation) where the
    original HTML structure must be kept intact for visual fidelity.

    The original LESS/jQuery stack continues to work through the Luma parent theme,
    so preserving the original ensures:
    - Exact same CSS class hierarchy (ebene1, ebenex, ebene2, etc.)
    - Correct CMS block placement inside navigation
    - Mobile navigation elements (nav-back-link, close-nav-arrow, etc.)
    - jQuery scripts for search relocation, region chooser, etc.
    - Bilingual region chooser with correct German/English toggle
    """
    preserved = []
    missing_preserved = []
    if not source_theme or not os.path.isdir(source_theme):
        return preserved

    for rel_path, strategy in strategy_map.items():
        if strategy != "preserve":
            continue

        src = os.path.join(source_theme, rel_path)
        if not os.path.isfile(src):
            missing_preserved.append(rel_path)
            continue

        dst = os.path.join(output_theme, rel_path)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        preserved.append(rel_path)

    if missing_preserved:
        print(f"  ⚠ {len(missing_preserved)} preserve templates not found in source theme:")
        for m in missing_preserved:
            print(f"    MISSING: {m}")
        print(f"    → Ensure these files exist in the source Magento theme directory.")

    # Also detect and preserve any unmapped templates that score high on complexity
    for root, _, files in os.walk(source_theme):
        for fname in files:
            if not fname.endswith(".phtml"):
                continue
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, source_theme)

            # Skip if already handled by explicit strategy or already copied
            if rel in strategy_map or rel in preserved:
                continue

            # Run complexity analysis
            analysis = analyze_template_complexity(fpath)
            if analysis.get("recommended_strategy") == "preserve":
                dst = os.path.join(output_theme, rel)
                # Don't overwrite templates that were already copied by rewrite strategy
                if not os.path.exists(dst):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(fpath, dst)
                    preserved.append(rel)

    return preserved


def copy_luma_assets(source_theme: str, output_theme: str) -> list:
    """
    Copy static assets (images, fonts) from the Luma theme
    that the Hyvä theme will also need.
    """
    copied = []
    asset_dirs = [
        ("web/images", "web/images"),
        ("web/fonts", "web/fonts"),
        ("web/js", "web/js"),
    ]

    for src_rel, dst_rel in asset_dirs:
        src_dir = os.path.join(source_theme, src_rel)
        dst_dir = os.path.join(output_theme, dst_rel)
        if not os.path.exists(src_dir):
            continue
        for root, _, files in os.walk(src_dir):
            for fname in files:
                src_file = os.path.join(root, fname)
                rel = os.path.relpath(src_file, src_dir)
                dst_file = os.path.join(dst_dir, rel)
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                shutil.copy2(src_file, dst_file)
                copied.append(os.path.join(dst_rel, rel))

    return copied


def copy_less_sources(source_theme: str, output_theme: str) -> list:
    """
    Copy LESS source files from the Luma theme.

    When using the "preserve" strategy, original templates keep their CSS class hierarchy
    which depends on LESS-compiled stylesheets. Copying LESS sources ensures:
    - The theme's web/css/source/ directory is available for LESS compilation
    - Brand-specific variables (_variables.less, _theme.less) are preserved
    - Custom component styles maintain their original selectors
    - The compiled styles-m.css / styles-l.css match what the templates expect

    The LESS files are compiled by Magento's built-in LESS processor in developer mode,
    or via `setup:static-content:deploy` in production mode.
    """
    copied = []
    less_dirs = [
        "web/css",       # Main CSS/LESS source directory
    ]

    for less_rel in less_dirs:
        src_dir = os.path.join(source_theme, less_rel)
        dst_dir = os.path.join(output_theme, less_rel)
        if not os.path.exists(src_dir):
            continue
        for root, _, files in os.walk(src_dir):
            for fname in files:
                # Copy LESS source files and any CSS overrides
                if not (fname.endswith('.less') or fname.endswith('.css')):
                    continue
                src_file = os.path.join(root, fname)
                rel = os.path.relpath(src_file, src_dir)
                dst_file = os.path.join(dst_dir, rel)
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                shutil.copy2(src_file, dst_file)
                copied.append(os.path.join(less_rel, rel))

    return copied


def copy_i18n(source_theme: str, output_theme: str) -> list:
    """Copy translation CSV files from the Luma theme."""
    copied = []
    i18n_dir = os.path.join(source_theme, "i18n")
    if not os.path.exists(i18n_dir):
        return copied

    dst_dir = os.path.join(output_theme, "i18n")
    os.makedirs(dst_dir, exist_ok=True)

    for fname in os.listdir(i18n_dir):
        if fname.endswith(".csv"):
            shutil.copy2(os.path.join(i18n_dir, fname), os.path.join(dst_dir, fname))
            copied.append(fname)

    return copied


def extract_template_strings(theme_path: str) -> set:
    """Extract all __('...') translatable strings from .phtml templates."""
    import re
    strings = set()
    for phtml in Path(theme_path).rglob("*.phtml"):
        content = phtml.read_text(errors="replace")
        matches = re.findall(r"__\(['\"](.+?)['\"]\)", content)
        strings.update(matches)
    return strings


def enrich_i18n(output_theme: str, template_strings: set) -> int:
    """
    Add missing translatable strings from templates into all i18n CSV files.
    For English locales: identity translations (key = value).
    For German locales: provide German translations for common UI strings.
    For other locales: identity translations as placeholders.
    Returns the number of strings added.
    """
    import csv
    import io

    # German translations for common Hyvä frontend strings
    de_translations = {
        "Account Information": "Kontoinformationen",
        "Add to Cart": "In den Warenkorb",
        "Add to Wish List": "Zur Wunschliste hinzufügen",
        "Adding...": "Wird hinzugefügt...",
        "Address": "Adresse",
        "Already have an account? Sign in": "Bereits ein Konto? Anmelden",
        "Back": "Zurück",
        "Back to Address Book": "Zurück zum Adressbuch",
        "Cashmere Care": "Kaschmir Pflege",
        "Change Email": "E-Mail ändern",
        "Change Email and Password": "E-Mail und Passwort ändern",
        "Change Password": "Passwort ändern",
        "City": "Stadt",
        "Close": "Schliessen",
        "Close Window": "Fenster schliessen",
        "Close fullscreen": "Vollbild schliessen",
        "Close minicart": "Miniwarenkorb schliessen",
        "Company": "Firma",
        "Confirm New Password": "Neues Passwort bestätigen",
        "Confirm Password": "Passwort bestätigen",
        "Contact Information": "Kontaktinformationen",
        "Cotton Care": "Baumwoll Pflege",
        "Country": "Land",
        "Create New Customer Account": "Neues Kundenkonto erstellen",
        "Create an Account": "Konto erstellen",
        "Creating...": "Wird erstellt...",
        "Current Password": "Aktuelles Passwort",
        "Decrease quantity": "Menge verringern",
        "Edit Account Information": "Kontoinformationen bearbeiten",
        "Edit Address": "Adresse bearbeiten",
        "Email": "E-Mail",
        "Email address": "E-Mail-Adresse",
        "Fair": "Fair",
        "First Name": "Vorname",
        "Forgot Your Password?": "Passwort vergessen?",
        "Go back": "Zurück",
        "Good": "Gut",
        "Hide password": "Passwort verbergen",
        "Increase quantity": "Menge erhöhen",
        "Last Name": "Nachname",
        "Linen Care": "Leinen Pflege",
        "Login": "Anmelden",
        "Lyocell Care": "Lyocell Pflege",
        "Men Size Chart": "Herren Grössentabelle",
        "More Choices:": "Mehr Auswahl:",
        "New Password": "Neues Passwort",
        "New Products": "Neue Produkte",
        "New": "Neu",
        "Next": "Weiter",
        "Next image": "Nächstes Bild",
        "No Password": "Kein Passwort",
        "Notify Me": "Benachrichtigen",
        "Open fullscreen gallery": "Galerie im Vollbild öffnen",
        "Password": "Passwort",
        "Password Strength": "Passwortstärke",
        "Personal Information": "Persönliche Informationen",
        "Phone Number": "Telefonnummer",
        "Please select a region, state or province.": "Bitte wählen Sie eine Region oder ein Bundesland.",
        "Previous": "Zurück",
        "Previous image": "Vorheriges Bild",
        "Qty": "Menge",
        "Required Fields": "Pflichtfelder",
        "Save": "Speichern",
        "Save Address": "Adresse speichern",
        "Saving...": "Wird gespeichert...",
        "Search": "Suche",
        "Show password": "Passwort anzeigen",
        "Sign In": "Anmelden",
        "Sign Up for Newsletter": "Newsletter abonnieren",
        "Sign up to get notified when this product is back in stock.": "Melden Sie sich an, um benachrichtigt zu werden, wenn dieses Produkt wieder verfügbar ist.",
        "Sign-in Information": "Anmeldeinformationen",
        "Signing in...": "Anmeldung...",
        "Sizes Chart": "Grössentabelle",
        "State/Province": "Bundesland/Region",
        "Street Address": "Strassenadresse",
        "Strong": "Stark",
        "Subscribe": "Abonnieren",
        "Subscribing...": "Wird abonniert...",
        "Toggle minicart": "Miniwarenkorb umschalten",
        "Upcycled": "Upcycling",
        "Use as my default billing address": "Als Standard-Rechnungsadresse verwenden",
        "Use as my default shipping address": "Als Standard-Lieferadresse verwenden",
        "Very Strong": "Sehr stark",
        "View Cart": "Warenkorb anzeigen",
        "View image": "Bild ansehen",
        "We found other products you might like!": "Wir haben andere Produkte gefunden, die Ihnen gefallen könnten!",
        "Weak": "Schwach",
        "Wishlist": "Wunschliste",
        "Women Size Chart": "Damen Grössentabelle",
        "You May Also Like": "Das könnte Ihnen auch gefallen",
        "You have no items in your shopping cart.": "Ihr Warenkorb ist leer.",
        "Zip/Postal Code": "PLZ",
    }

    # Dutch translations
    nl_translations = {
        "Add to Cart": "In winkelwagen",
        "Add to Wish List": "Aan verlanglijst toevoegen",
        "Back": "Terug",
        "City": "Stad",
        "Close": "Sluiten",
        "Company": "Bedrijf",
        "Country": "Land",
        "Create an Account": "Account aanmaken",
        "Email": "E-mail",
        "First Name": "Voornaam",
        "Last Name": "Achternaam",
        "Login": "Inloggen",
        "Password": "Wachtwoord",
        "Qty": "Aantal",
        "Save": "Opslaan",
        "Search": "Zoeken",
        "Sign In": "Inloggen",
        "View Cart": "Winkelwagen bekijken",
    }

    # Danish translations
    da_translations = {
        "Add to Cart": "Læg i kurv",
        "Back": "Tilbage",
        "Close": "Luk",
        "Email": "E-mail",
        "First Name": "Fornavn",
        "Last Name": "Efternavn",
        "Login": "Log ind",
        "Password": "Adgangskode",
        "Qty": "Antal",
        "Save": "Gem",
        "Search": "Søg",
        "Sign In": "Log ind",
        "View Cart": "Se kurv",
    }

    # Swedish translations
    sv_translations = {
        "Add to Cart": "Lägg i varukorg",
        "Back": "Tillbaka",
        "Close": "Stäng",
        "Email": "E-post",
        "First Name": "Förnamn",
        "Last Name": "Efternamn",
        "Login": "Logga in",
        "Password": "Lösenord",
        "Qty": "Antal",
        "Save": "Spara",
        "Search": "Sök",
        "Sign In": "Logga in",
        "View Cart": "Visa varukorg",
    }

    # Polish translations
    pl_translations = {
        "Add to Cart": "Dodaj do koszyka",
        "Back": "Wstecz",
        "Close": "Zamknij",
        "Email": "E-mail",
        "First Name": "Imię",
        "Last Name": "Nazwisko",
        "Login": "Zaloguj się",
        "Password": "Hasło",
        "Qty": "Ilość",
        "Save": "Zapisz",
        "Search": "Szukaj",
        "Sign In": "Zaloguj się",
        "View Cart": "Zobacz koszyk",
    }

    locale_translations = {
        "de_DE": de_translations,
        "de_AT": de_translations,
        "de_CH": de_translations,
        "nl_NL": nl_translations,
        "da_DK": da_translations,
        "sv_SE": sv_translations,
        "pl_PL": pl_translations,
    }

    i18n_dir = os.path.join(output_theme, "i18n")
    if not os.path.isdir(i18n_dir):
        os.makedirs(i18n_dir, exist_ok=True)

    total_added = 0
    csv_files = [f for f in os.listdir(i18n_dir) if f.endswith(".csv")]

    # If no CSV files, create at least en_US and de_DE
    if not csv_files:
        csv_files = ["en_US.csv", "de_DE.csv"]
        for f in csv_files:
            Path(os.path.join(i18n_dir, f)).touch()

    for csv_name in csv_files:
        csv_path = os.path.join(i18n_dir, csv_name)
        locale = csv_name.replace(".csv", "")

        # Read existing translations
        existing_keys = set()
        existing_lines = []
        if os.path.isfile(csv_path):
            with open(csv_path, "r", errors="replace") as f:
                existing_lines = f.readlines()
            for line in existing_lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Parse CSV key (first field)
                try:
                    reader = csv.reader(io.StringIO(line))
                    row = next(reader)
                    if row:
                        existing_keys.add(row[0])
                except (csv.Error, StopIteration):
                    pass

        # Find missing strings
        missing = template_strings - existing_keys
        if not missing:
            continue

        # Get locale-specific translations
        trans_map = locale_translations.get(locale, {})

        # Append missing strings
        new_lines = []
        for s in sorted(missing):
            if locale.startswith("en_"):
                # English: identity translation
                translation = s
            elif s in trans_map:
                translation = trans_map[s]
            else:
                # Use English as placeholder for untranslated strings
                translation = s
            # Proper CSV quoting
            out = io.StringIO()
            writer = csv.writer(out)
            writer.writerow([s, translation])
            new_lines.append(out.getvalue())

        if new_lines:
            with open(csv_path, "a") as f:
                # Add separator comment
                f.write(f"# --- Hyvä frontend translations (auto-generated) ---\n")
                for line in new_lines:
                    f.write(line)
            total_added += len(new_lines)

    return total_added


def generate_layout_xmls(source_theme: str, output_theme: str, preserve_header: bool = True) -> list:
    """
    Process layout XMLs: convert where needed, generate Hyvä-specific ones.

    Args:
        preserve_header: Legacy flag kept for backward compatibility.
                        Layout generation now always keeps Hyvä header containers intact
                        and overrides only `header-content` template.
    """
    generated = []

    script_root = os.path.dirname(os.path.abspath(__file__))
    deploy_dir = os.path.join(script_root, "deploy")
    brand_config = {
        "preserve_header": preserve_header,
        "header_template": "header.phtml",
        "include_design_fixes": os.path.isfile(os.path.join(deploy_dir, "design-fixes.css")),
        "include_design_fix_additions": os.path.isfile(os.path.join(deploy_dir, "design-fixes-additions.css")),
    }

    # Generate Hyvä-specific layout XMLs
    hyva_layouts = {
        "Magento_Theme/layout/default.xml":
            generate_hyva_default_xml(brand_config),
        "Magento_Catalog/layout/catalog_product_view.xml":
            generate_hyva_catalog_product_view_xml(),
        "Magento_Catalog/layout/catalog_category_view.xml":
            generate_hyva_catalog_category_view_xml(),
    }

    for rel_path, content in hyva_layouts.items():
        dst = os.path.join(output_theme, rel_path)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w") as f:
            f.write(content)
        generated.append(rel_path)

    # Process source theme layouts — copy non-checkout ones
    layout_results = process_all_layouts(source_theme, output_theme)
    for result in layout_results:
        if result["action"] == "copy":
            src = os.path.join(source_theme, result["source"])
            dst = os.path.join(output_theme, result["source"])
            # Don't overwrite our generated layouts
            if not os.path.exists(dst):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                generated.append(result["source"])

    return generated


def apply_deploy_theme_overrides(deploy_dir: str, output_theme: str) -> list[tuple[str, str]]:
    """
    Apply production-tested files from deploy/ to the generated theme.

    Returns list of (source_name, destination_relative_path).
    """
    applied = []
    if not os.path.isdir(deploy_dir):
        return applied

    for src_name, rel_dst in DEPLOY_THEME_FILE_MAP.items():
        src = os.path.join(deploy_dir, src_name)
        if not os.path.isfile(src):
            continue
        dst = os.path.join(output_theme, rel_dst)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        applied.append((src_name, rel_dst))

    return applied


def copy_deploy_custom_modules(deploy_dir: str, output_path: str) -> list[str]:
    """
    Copy custom Magento modules from deploy/ into output/custom-modules/.

    These modules are not theme files and must be copied to app/code on target Magento.
    """
    copied = []
    if not os.path.isdir(deploy_dir):
        return copied

    modules_base = os.path.join(output_path, "custom-modules")
    if os.path.isdir(modules_base):
        shutil.rmtree(modules_base)

    for src_dir_name, rel_module_dst in DEPLOY_CUSTOM_MODULES.items():
        src = os.path.join(deploy_dir, src_dir_name)
        if not os.path.isdir(src):
            continue

        dst = os.path.join(modules_base, rel_module_dst)
        if os.path.exists(dst):
            shutil.rmtree(dst)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copytree(src, dst)
        copied.append(rel_module_dst)

    return copied


def clean_theme_runtime_artifacts(output_theme: str) -> list[str]:
    """
    Remove runtime directories that should never be versioned/deployed from generated theme.
    """
    removed = []
    runtime_paths = [
        "node_modules",
    ]
    for rel in runtime_paths:
        path = os.path.join(output_theme, rel)
        if os.path.isdir(path):
            shutil.rmtree(path)
            removed.append(rel)
    return removed


def main():
    parser = argparse.ArgumentParser(description="Generate Hyvä child theme from Magento Luma theme")
    parser.add_argument("--project", required=True, help="Path to Magento project (e.g. projects/ftcshop)")
    parser.add_argument("--vendor", default="MediaDivision", help="Theme vendor name")
    parser.add_argument("--theme", default="FTCShopHyva", help="Hyvä theme name")
    parser.add_argument("--title", default="FTC Cashmere Hyvä", help="Theme title")
    parser.add_argument("--output", required=True, help="Output directory (e.g. output/ftcshop)")
    parser.add_argument("--with-stubs", action="store_true",
                        help="Generate Hyvä parent theme + module stubs for testing without a license")
    parser.add_argument("--tailwind-version", type=int, default=4, choices=[3, 4],
                        help="Tailwind CSS version: 3 for Hyvä <1.4, 4 for Hyvä >=1.4.5 (default: 4)")
    args = parser.parse_args()

    project_path = os.path.abspath(args.project)
    output_path = os.path.abspath(args.output)

    print(f"\n{'='*60}")
    print(f"  Hyvä Theme Generator")
    print(f"{'='*60}")
    print(f"  Project:  {project_path}")
    print(f"  Vendor:   {args.vendor}")
    print(f"  Theme:    {args.theme}")
    print(f"  Output:   {output_path}")
    print(f"  Tailwind: v{args.tailwind_version}")
    print(f"{'='*60}\n")

    script_root = os.path.dirname(os.path.abspath(__file__))
    deploy_dir = os.path.join(script_root, "deploy")

    # 1. Find Luma theme
    print("[1/8] Finding Luma theme...")
    luma_theme = find_luma_theme(project_path)
    if not luma_theme:
        print("  ERROR: No Luma theme found in project!")
        sys.exit(1)
    print(f"  Found: {luma_theme}")

    # 2. Extract design tokens from LESS
    print("\n[2/8] Extracting design tokens from LESS...")
    tokens = extract_design_tokens(luma_theme)
    print(f"  Colors:      {len(tokens.colors)}")
    print(f"  Fonts:       {len(tokens.fonts)}")
    print(f"  Breakpoints: {len(tokens.breakpoints)}")
    print(f"  Font sizes:  {len(tokens.font_sizes)}")

    # 3. Scaffold Hyvä theme (registration.php, theme.xml, tailwind config, etc.)
    print("\n[3/8] Scaffolding Hyvä child theme...")
    theme_target = os.path.join(output_path, args.vendor, args.theme)
    if os.path.isdir(theme_target):
        shutil.rmtree(theme_target)
        print(f"  Removed previous output: {theme_target}")

    theme_base = scaffold_hyva_theme(
        output_path=output_path,
        vendor=args.vendor,
        theme_name=args.theme,
        title=args.title,
        tokens=tokens,
        source_theme_path=luma_theme,
        tailwind_version=args.tailwind_version,
    )
    print(f"  Created: {theme_base}")

    # 4. Copy converted phtml templates + preserve complex originals
    print("\n[4/8] Copying Hyvä template rewrites...")
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generator", "templates")
    copied_templates = copy_templates(templates_dir, theme_base, TEMPLATE_STRATEGY)
    print(f"  Rewritten: {len(copied_templates)} template files:")
    for t in sorted(copied_templates):
        print(f"    ✓ {t}")

    # Copy preserved (original) templates for complex components
    preserved_templates = copy_preserved_templates(luma_theme, theme_base, TEMPLATE_STRATEGY)
    if preserved_templates:
        print(f"\n  Preserved (original): {len(preserved_templates)} complex templates:")
        for t in sorted(preserved_templates):
            print(f"    ⊕ {t}")

    # Show template strategy summary
    rewrite_count = sum(1 for v in TEMPLATE_STRATEGY.values() if v == "rewrite")
    preserve_count = sum(1 for v in TEMPLATE_STRATEGY.values() if v == "preserve")
    skip_count = sum(1 for v in TEMPLATE_STRATEGY.values() if v == "skip")
    copy_count = sum(1 for v in TEMPLATE_STRATEGY.values() if v == "copy")
    remove_count = sum(1 for v in TEMPLATE_STRATEGY.values() if v == "remove")
    auto_detected = max(0, len(preserved_templates) - preserve_count)
    print(f"\n  Strategy summary:")
    print(f"    Rewrite (Hyvä version):      {rewrite_count}")
    print(f"    Preserve (original intact):  {preserve_count} mapped + {auto_detected} auto-detected")
    print(f"    Skip (Hyvä default):         {skip_count}")
    print(f"    Copy (unchanged):            {copy_count}")
    print(f"    Remove (KO templates):       {remove_count}")

    # 5. Generate/convert layout XMLs
    has_preserved = len(preserved_templates) > 0
    print(f"\n[5/8] Processing layout XMLs (preserve_header={has_preserved})...")
    layout_files = generate_layout_xmls(luma_theme, theme_base, preserve_header=has_preserved)
    print(f"  Generated {len(layout_files)} layout files:")
    for l in sorted(layout_files):
        print(f"    ✓ {l}")

    # 6. Copy static assets, LESS sources, and translations
    print("\n[6/8] Copying assets, styles, and translations...")
    assets = copy_luma_assets(luma_theme, theme_base)
    less_files = copy_less_sources(luma_theme, theme_base)
    translations = copy_i18n(luma_theme, theme_base)

    # Extract translatable strings from templates and enrich CSV files
    template_strings = extract_template_strings(theme_base)
    enriched = enrich_i18n(theme_base, template_strings)

    print(f"  Assets:       {len(assets)} files")
    print(f"  LESS sources: {len(less_files)} files")
    print(f"  Translations: {len(translations)} CSV files")
    print(f"  Enriched:     {enriched} strings added to {len(translations)} locales")
    print(f"  Template strings: {len(template_strings)} unique translatable strings")

    # 7. Apply deploy overrides and remove runtime artifacts
    print("\n[7/8] Applying deploy overrides...")
    deploy_overrides = apply_deploy_theme_overrides(deploy_dir, theme_base)
    custom_modules = copy_deploy_custom_modules(deploy_dir, output_path)
    removed_runtime = clean_theme_runtime_artifacts(theme_base)

    print(f"  Deploy overrides applied: {len(deploy_overrides)}")
    for src_name, dst_rel in deploy_overrides:
        print(f"    ✓ deploy/{src_name} → {dst_rel}")

    print(f"  Custom modules copied: {len(custom_modules)}")
    for module_rel in custom_modules:
        print(f"    ✓ custom-modules/{module_rel}")

    if removed_runtime:
        print(f"  Removed runtime dirs: {', '.join(removed_runtime)}")

    # 8. Phase 3: Compatibility modules
    print("\n[8/8] Phase 3: Analyzing module compatibility...")
    compat_output = os.path.join(output_path, "compatibility")
    compat_analysis, compat_modules = run_phase3(project_path, compat_output)

    # Generate summary report
    report = {
        "vendor": args.vendor,
        "theme": args.theme,
        "source_theme": luma_theme,
        "output_path": theme_base,
        "templates_converted": len(copied_templates),
        "templates_preserved": len(preserved_templates),
        "preserve_mode": has_preserved,
        "layout_xmls": len(layout_files),
        "assets_copied": len(assets),
        "less_sources": len(less_files),
        "translations": len(translations),
        "design_tokens": {
            "colors": len(tokens.colors),
            "fonts": len(tokens.fonts),
            "breakpoints": len(tokens.breakpoints),
        },
        "compatibility": {
            "packages_available": len(compat_analysis.get("compatible", [])),
            "needs_custom": len(compat_analysis.get("needs_custom", [])),
            "stub_modules_generated": len(compat_modules),
        },
        "deploy_overrides": {
            "files_applied": len(deploy_overrides),
            "custom_modules": custom_modules,
        },
        "cleanup": {
            "runtime_artifacts_removed": removed_runtime,
        },
    }

    report_path = os.path.join(output_path, "GENERATION_REPORT.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    # Optional: Generate Hyvä stubs for testing without a license
    stubs_generated = False
    if args.with_stubs:
        print("\n[Stubs] Generating Hyvä parent theme + module stubs...")
        from tests.hyva_stub_generator import generate_hyva_stub, generate_hyva_module_stub
        stubs_dir = os.path.join(output_path, "stubs")
        stub_theme = generate_hyva_stub(stubs_dir)
        stub_module = generate_hyva_module_stub(stubs_dir)
        stubs_generated = True
        print(f"  Stub theme:  {stub_theme}")
        print(f"  Stub module: {stub_module}")

    print(f"\n{'='*60}")
    print(f"  Generation complete!")
    print(f"{'='*60}")
    print(f"  Theme:      {theme_base}")
    print(f"  Rewritten:  {len(copied_templates)} templates (Alpine.js)")
    print(f"  Preserved:  {len(preserved_templates)} templates (original)")
    print(f"  Layouts:    {len(layout_files)}")
    print(f"  Assets:     {len(assets)}")
    print(f"  LESS:       {len(less_files)} source files")
    print(f"  Deploy:     {len(deploy_overrides)} overrides")
    print(f"  Modules:    {len(custom_modules)} custom deploy modules")
    print(f"  Compat:     {len(compat_modules)} stub modules")
    print(f"  Report:     {report_path}")
    print(f"\n  Next steps:")
    if stubs_generated:
        print(f"  0. Copy stubs/{os.path.basename(stub_theme)} → app/design/frontend/Hyva/default/")
        print(f"     Copy stubs/{os.path.basename(stub_module)} → app/code/Hyva/Theme/")
    print(f"  1. cd {theme_base} && npm install && npm run build")
    print(f"  2. Deploy theme with rsync excluding node_modules/.git")
    print(f"  3. Install Hyvä compat packages (see compatibility/COMPATIBILITY_REPORT.md)")
    print(f"  4. Copy stub modules from compatibility/stubs/ to app/code/")
    if custom_modules:
        print(f"  5. Copy custom-modules/* to app/code/")
        print(f"  6. Activate theme, configure logo/search, flush caches")
    else:
        print(f"  5. Activate theme, configure logo/search, flush caches")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
