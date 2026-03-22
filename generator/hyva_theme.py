"""
Hyvä Theme Scaffolder — generates a complete Hyvä child theme
from design tokens and Magento project analysis.
"""
import os
import json
import shutil
from pathlib import Path
from generator.style_extractor import DesignTokens


def generate_registration_php(vendor: str, theme_name: str) -> str:
    return f"""<?php
use Magento\\Framework\\Component\\ComponentRegistrar;

ComponentRegistrar::register(
    ComponentRegistrar::THEME,
    'frontend/{vendor}/{theme_name}',
    __DIR__
);
"""


def generate_theme_xml(title: str, parent: str = "Hyva/default") -> str:
    return f"""<?xml version="1.0"?>
<theme xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:noNamespaceSchemaLocation="urn:magento:framework:Config/etc/theme.xsd">
    <title>{title}</title>
    <parent>{parent}</parent>
</theme>
"""


def generate_composer_json(vendor: str, theme_name: str) -> str:
    package = f"{vendor.lower()}/theme-frontend-{theme_name.lower()}"
    return json.dumps({
        "name": package,
        "description": f"Hyvä child theme for {theme_name}",
        "type": "magento2-theme",
        "license": "proprietary",
        "require": {
            "hyva-themes/magento2-default-theme": "^1.3"
        },
        "autoload": {
            "files": ["registration.php"]
        }
    }, indent=4) + "\n"


def generate_tailwind_config(tokens: DesignTokens, vendor: str = "MediaDivision", theme: str = "FTCShopHyva", tailwind_version: int = 4) -> str:
    """Generate Tailwind CSS config from design tokens.

    For Tailwind v4 (Hyvä 1.4.5+): generates CSS-first config (tailwind-source.css handles it all).
    For Tailwind v3 (Hyvä < 1.4): generates traditional tailwind.config.js.
    """
    if tailwind_version >= 4:
        return generate_tailwind_config_v4(tokens, vendor, theme)
    return generate_tailwind_config_v3(tokens, vendor, theme)


def generate_tailwind_config_v3(tokens: DesignTokens, vendor: str = "MediaDivision", theme: str = "FTCShopHyva") -> str:
    """Generate tailwind.config.js for Tailwind v3."""
    colors_js = "{\n"
    # Map FTC color names to Tailwind-friendly names
    color_mapping = {
        "brand-primary": ("primary", "Brand tan/caramel"),
        "brand-secondary": ("secondary", "Coral/orange-red"),
        "green": ("accent", "Sage green"),
        "black": ("dark", "Near-black text"),
        "light-black": ("dark-light", "Dark gray"),
        "lighter-black": ("dark-lighter", "Medium gray"),
        "lightest-black": ("dark-lightest", "Light gray text"),
        "gray": ("gray-DEFAULT", "Medium gray"),
        "light-gray": ("gray-light", "Light gray borders"),
        "lighter-gray": ("gray-lighter", "Very light gray"),
        "lightest-gray": ("gray-lightest", "Off-white"),
    }

    color_groups = {}
    for less_name, value in tokens.colors.items():
        if less_name in color_mapping:
            tw_name, _comment = color_mapping[less_name]
            parts = tw_name.split("-", 1)
            if len(parts) == 2 and parts[0] in ("gray", "dark"):
                group = parts[0]
                shade = parts[1]
                if group not in color_groups or not isinstance(color_groups[group], dict):
                    # Promote existing string to DEFAULT shade in a dict
                    existing = color_groups.get(group)
                    color_groups[group] = {}
                    if isinstance(existing, str):
                        color_groups[group]["DEFAULT"] = existing
                color_groups[group][shade] = value
            else:
                # If this key already exists as a dict, add as DEFAULT
                if tw_name in color_groups and isinstance(color_groups[tw_name], dict):
                    color_groups[tw_name]["DEFAULT"] = value
                else:
                    color_groups[tw_name] = value

    for name, val in color_groups.items():
        if isinstance(val, dict):
            colors_js += f"        '{name}': {{\n"
            for shade, sv in val.items():
                colors_js += f"            '{shade}': '{sv}',\n"
            colors_js += f"        }},\n"
        else:
            colors_js += f"        '{name}': '{val}',\n"

    colors_js += "      }"

    font_family_serif = tokens.fonts.get("serif", '"Korpus-B", serif')
    font_family_sans = tokens.fonts.get("sans", '"KorpusGrotesk-B", sans-serif')

    breakpoints_js = "{\n"
    for name, val in tokens.breakpoints.items():
        breakpoints_js += f"        '{name}': '{val}',\n"
    breakpoints_js += "      }"

    font_sizes_js = "{\n"
    for name, val in tokens.font_sizes.items():
        breakpoints_js_line = f"['{val}', {{ lineHeight: '1.4' }}]"
        font_sizes_js += f"        '{name}': {breakpoints_js_line},\n"
    font_sizes_js += "      }"

    return f"""const {{ spacing }} = require('tailwindcss/defaultTheme');

const hyvaModules = require('@hyva-themes/hyva-modules');

module.exports = hyvaModules.mergeTailwindConfig({{
  theme: {{
    extend: {{
      screens: {breakpoints_js},
      colors: {colors_js},
      fontFamily: {{
        'serif': [{font_family_serif}],
        'sans': [{font_family_sans}],
      }},
      fontSize: {font_sizes_js},
      maxWidth: {{
        'content': '{tokens.max_width}',
      }},
      borderRadius: {{
        'none': '0',
        'full': '50%',
      }},
      boxShadow: {{
        'sm': '0 2px 14px 0 rgba(80, 66, 55, 0.3)',
        'md': '0 2px 14px 0 rgba(80, 66, 55, 0.4)',
      }},
      transitionDuration: {{
        'fast': '150ms',
        'DEFAULT': '300ms',
        'slow': '450ms',
        'slower': '600ms',
      }},
      zIndex: {{
        'behind': '-1',
        'label': '2',
        'modal': '10',
        'toolbar': '20',
        'popup': '30',
        'minicart': '50000',
      }},
    }},
  }},
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
  // Scan phtml and layout xml files for Tailwind classes
  content: [
    // this theme
    '../../../../../../app/design/frontend/{vendor}/{theme}/**/*.phtml',
    '../../../../../../app/design/frontend/{vendor}/{theme}/web/tailwind/*.css',
    // parent theme
    '../../../../../../vendor/hyva-themes/magento2-default-theme/**/*.phtml',
    '../../../../../../vendor/hyva-themes/magento2-default-theme/**/*.xml',
    // compatibility modules (custom Hyvä stubs)
    '../../../../../../app/code/**/*Hyva*/**/*.phtml',
    // hyva modules
    ...hyvaModules.getModuleJitContent(),
  ],
}});
"""


def generate_tailwind_config_v4(tokens: DesignTokens, vendor: str = "MediaDivision", theme: str = "FTCShopHyva") -> str:
    """Generate hyva.config.json for Tailwind v4 (Hyvä 1.4.5+).

    Tailwind v4 uses CSS-first configuration. The JS config is replaced with:
    - hyva.config.json: design tokens as JSON (colors, fonts, etc.)
    - tailwind-source.css: CSS with @import "tailwindcss" and @theme
    """
    config = {
        "parent": "../../../../../../vendor/hyva-themes/magento2-default-theme/web/tailwind",
        "colors": {},
        "fonts": {},
        "screens": {},
    }

    # Map color tokens
    color_mapping = {
        "brand-primary": "primary",
        "brand-secondary": "secondary",
        "green": "accent",
        "black": "dark",
        "light-black": "dark-light",
        "lighter-black": "dark-lighter",
        "lightest-black": "dark-lightest",
        "gray": "gray",
        "light-gray": "gray-light",
        "lighter-gray": "gray-lighter",
        "lightest-gray": "gray-lightest",
    }

    for less_name, value in tokens.colors.items():
        tw_name = color_mapping.get(less_name, less_name)
        config["colors"][tw_name] = value

    # Fonts
    config["fonts"]["serif"] = tokens.fonts.get("serif", "serif")
    config["fonts"]["sans"] = tokens.fonts.get("sans", "sans-serif")
    if "sartex" in tokens.fonts:
        config["fonts"]["display"] = tokens.fonts["sartex"]

    # Breakpoints
    for name, val in tokens.breakpoints.items():
        config["screens"][name] = val

    # Add max-width
    config["maxWidth"] = tokens.max_width

    return json.dumps(config, indent=4) + "\n"


def generate_tailwind_source_css_v4(tokens: DesignTokens, vendor: str = "MediaDivision", theme: str = "FTCShopHyva") -> str:
    """Generate tailwind-source.css for Tailwind v4 (Hyvä 1.4.5+).

    Uses CSS-first configuration with @import "tailwindcss" and @theme.
    Includes all FTC Cashmere brand styles converted from LESS.
    """
    # Build CSS custom properties from tokens
    colors_css = ""
    color_mapping = {
        "brand-primary": "primary",
        "brand-secondary": "secondary",
        "green": "accent",
        "black": "dark",
        "light-black": "dark-light",
        "lighter-black": "dark-lighter",
        "lightest-black": "dark-lightest",
        "gray": "gray",
        "light-gray": "gray-light",
        "lighter-gray": "gray-lighter",
        "lightest-gray": "gray-lightest",
    }
    for less_name, value in tokens.colors.items():
        tw_name = color_mapping.get(less_name, less_name)
        colors_css += f"    --color-{tw_name}: {value};\n"

    font_serif = tokens.fonts.get("serif", "serif")
    font_sans = tokens.fonts.get("sans", "sans-serif")

    return f"""@import "tailwindcss";

/* Scan source paths for Tailwind classes */
@source "../../../../../../app/design/frontend/{vendor}/{theme}/**/*.phtml";
@source "../../../../../../app/design/frontend/{vendor}/{theme}/**/*.xml";
@source "../../../../../../vendor/hyva-themes/magento2-default-theme/**/*.phtml";
@source "../../../../../../vendor/hyva-themes/magento2-default-theme/**/*.xml";
@source "../../../../../../app/code/**/*Hyva*/**/*.phtml";

/* Design tokens */
@theme {{
{colors_css}    --font-serif: {font_serif};
    --font-sans: {font_sans};

    --screen-xxs: 320px;
    --screen-xs: 480px;
    --screen-sm: 640px;
    --screen-md: 768px;
    --screen-lg: 1024px;
    --screen-xl: 1440px;
    --max-width: 1540px;
    --max-screen: 1920px;
}}

/* ================================================================
   BASE LAYER — Typography, body, links
   ================================================================ */
@layer base {{
    body {{
        font-family: var(--font-sans);
        font-size: 15px;
        color: var(--color-dark, #111);
        background: #f9f7f8;
        -webkit-font-smoothing: antialiased;
    }}

    h1, h2, h3, h4, h5, h6 {{
        font-family: var(--font-serif);
        text-transform: uppercase;
        font-weight: normal;
    }}

    a {{
        color: inherit;
        text-decoration: none;
        transition: color 0.3s;
    }}

    a:hover {{
        color: var(--color-primary);
    }}

    img {{
        max-width: 100%;
        height: auto;
    }}

    input, select, textarea {{
        font-family: var(--font-sans);
        font-size: 15px;
    }}

    /* Page wrapper — all pages except homepage get margin-top for fixed header */
    body:not(.cms-index-index) .page-wrapper {{
        margin-top: 100px;
    }}

    /* Page main content area */
    .page-main {{
        background: #fff;
        max-width: var(--max-screen);
        margin: 0 auto;
    }}
}}

/* ================================================================
   COMPONENT LAYER — Buttons, containers, page-title
   ================================================================ */
@layer components {{

    /* Buttons */
    .btn-primary {{
        display: inline-block;
        padding: 0.75rem 2rem;
        background: var(--color-dark, #111);
        color: white;
        text-transform: uppercase;
        font-size: 0.875rem;
        letter-spacing: 0.05em;
        transition: opacity 0.3s;
    }}
    .btn-primary:hover {{
        opacity: 0.9;
    }}

    .btn-secondary {{
        display: inline-block;
        padding: 0.75rem 2rem;
        border: 1px solid var(--color-dark, #111);
        color: var(--color-dark, #111);
        text-transform: uppercase;
        font-size: 0.875rem;
        letter-spacing: 0.05em;
        transition: all 0.3s;
    }}
    .btn-secondary:hover {{
        background: var(--color-dark, #111);
        color: white;
    }}

    /* Layout container */
    .container-ftc {{
        width: 100%;
        max-width: var(--max-width);
        margin: 0 auto;
        padding: 0 1rem;
    }}

    /* Page title (category, CMS, etc.) */
    .page-title {{
        font-family: var(--font-serif);
        text-transform: uppercase;
        font-weight: normal;
    }}

    /* ================================================================
       HEADER
       ================================================================ */
    .ftc-header {{
        position: relative;
        top: 0;
        width: 100%;
        left: 0;
        right: 0;
        z-index: 900;
        height: auto;
        overflow: visible;
        background: white;
    }}

    @media (max-width: 600px) {{
        .ftc-header {{
            min-height: 100px;
        }}
    }}

    .ftc-header-inner {{
        width: 100%;
        position: relative;
        box-sizing: border-box;
        margin: 0 auto;
        padding-bottom: 20px;
    }}

    @media (max-width: 600px) {{
        .ftc-header-inner {{
            padding-bottom: 50px;
        }}
    }}

    /* Promotion banner */
    .header-msg {{
        width: 100%;
        text-align: center;
        background: var(--color-dark);
        color: #fff;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        position: relative;
        z-index: 901;
    }}

    .header-msg .dismiss {{
        position: absolute;
        right: 15px;
        top: 50%;
        transform: translateY(-50%);
        cursor: pointer;
        opacity: 0.6;
        transition: opacity 0.3s;
    }}
    .header-msg .dismiss:hover {{
        opacity: 1;
    }}

    /* Navigation container */
    .ftc-navigation {{
        height: 150px;
        position: relative;
        width: 100%;
    }}

    /* Logo */
    .ftc-logo {{
        text-align: center;
        width: 200px;
        position: absolute;
        top: 0;
        left: 50%;
        margin-left: -100px;
        z-index: 10;
    }}

    @media (max-width: 1300px) {{
        .ftc-logo {{
            top: 25px;
            width: 100px;
            margin-left: -50px;
        }}
    }}

    @media (max-width: 850px) {{
        .ftc-logo {{
            left: 50%;
            margin-left: -35px;
            top: 25px;
            width: 100px;
        }}
    }}

    .ftc-logo img {{
        display: inline-block;
        max-width: 100%;
    }}

    /* Navigation items */
    .ftc-nav-items {{
        margin: 0;
        padding: 0;
        width: auto;
        height: auto;
        display: table;
        list-style: none;
    }}

    @media (max-width: 1100px) {{
        .ftc-nav-items {{
            display: none;
        }}
        .ftc-nav-items.mobile-open {{
            display: block;
            position: fixed;
            left: 0;
            right: 0;
            top: 100px;
            bottom: 0;
            background: #fff;
            z-index: 999;
            overflow-y: auto;
        }}
    }}

    .ftc-nav-item {{
        display: table-cell;
        vertical-align: middle;
        height: 150px;
        padding-right: 30px;
        position: relative;
    }}

    @media (max-width: 1350px) {{
        .ftc-nav-item {{
            padding-right: 20px;
        }}
    }}

    @media (max-width: 1100px) {{
        .ftc-nav-item {{
            display: block;
            height: 50px;
            text-align: center;
            width: 100%;
            padding-right: 0;
        }}
    }}

    .ftc-nav-link {{
        text-transform: uppercase;
        font-size: 16px;
        color: var(--color-dark);
        text-decoration: none;
        transition: color 0.3s;
        display: block;
        height: 150px;
        line-height: 150px;
    }}

    @media (max-width: 1350px) {{
        .ftc-nav-link {{
            font-size: 13px;
        }}
    }}

    @media (max-width: 1100px) {{
        .ftc-nav-link {{
            font-size: 20px;
            height: 50px;
            line-height: 50px;
        }}
    }}

    .ftc-nav-item:hover .ftc-nav-link {{
        color: var(--color-primary);
    }}

    /* Subnav dropdown */
    .ftc-subnav {{
        position: fixed;
        top: 170px;
        left: 0;
        right: 0;
        width: 100%;
        z-index: 900;
        display: none;
        opacity: 0;
        transition: opacity 0.5s;
    }}

    .ftc-nav-item:hover .ftc-subnav {{
        display: block;
        animation: ftcNavAnim 0.5s forwards;
    }}

    .ftc-subnav-inner {{
        max-width: var(--max-screen);
        position: relative;
        box-sizing: border-box;
        padding: 50px 100px 30px;
        margin: 0 auto;
        background: rgba(249, 247, 248, 1);
        display: table;
    }}

    .ftc-subnav-list {{
        margin: 0;
        padding: 0;
        list-style: none;
        display: table-cell;
        vertical-align: middle;
        width: 70%;
    }}

    .ftc-subnav-item {{
        height: 50px;
        line-height: 50px;
        display: inline-block;
        padding: 0 30px 0 20px;
        box-sizing: border-box;
        width: 25%;
        margin-bottom: 20px;
        position: relative;
        cursor: pointer;
        transition: color 0.3s;
    }}

    @media (max-width: 850px) {{
        .ftc-subnav-item {{
            width: 50%;
        }}
    }}

    .ftc-subnav-item::before {{
        content: "";
        position: absolute;
        left: 0;
        width: 1px;
        height: 30px;
        top: 10px;
        background: rgba(0, 0, 0, 0.2);
        transform: rotate(30deg);
        transition: background 0.3s;
    }}

    .ftc-subnav-item:hover::before {{
        background: var(--color-primary);
    }}

    .ftc-subnav-link {{
        text-transform: none;
        font-size: 15px;
        color: rgba(0, 0, 0, 0.5);
        text-decoration: none;
        transition: color 0.3s;
        display: block;
    }}

    .ftc-subnav-item:hover .ftc-subnav-link {{
        color: var(--color-primary);
    }}

    .ftc-subnav-image {{
        width: 30%;
        display: table-cell;
        vertical-align: middle;
        text-align: right;
    }}

    .ftc-subnav-image img {{
        width: 100%;
        height: auto;
    }}

    /* Store switcher */
    .ftc-store-switcher {{
        position: relative;
        float: right;
        text-transform: uppercase;
        font-size: 16px;
        color: #111;
        transition: color 0.3s;
        cursor: pointer;
        line-height: 150px;
        height: 150px;
    }}

    .ftc-store-switcher:hover {{
        color: #A9BA9D;
    }}

    .ftc-store-switcher label {{
        display: inline;
        cursor: pointer;
        transition: color 0.3s;
    }}

    .ftc-store-switcher label:first-of-type {{
        border-right: 1px solid #111;
        padding-right: 6px;
    }}

    .ftc-store-switcher label:last-of-type {{
        padding-left: 6px;
        padding-right: 10px;
    }}

    /* Shop controls (search, account, minicart) */
    .ftc-shopcontrol {{
        position: relative;
        display: inline-block;
    }}

    .ftc-shopcontrol img {{
        height: 20px;
        opacity: 0.8;
        transition: all 0.3s;
    }}

    .ftc-shopcontrol:hover img {{
        opacity: 1;
    }}

    /* Minicart */
    .ftc-header .minicart-wrapper {{
        position: static;
    }}

    .ftc-header .minicart-wrapper .showcart {{
        position: absolute;
        min-width: 44px;
        top: 62px;
        right: 100px;
    }}

    @media (max-width: 1200px) {{
        .ftc-header .minicart-wrapper .showcart {{
            right: 40px;
        }}
    }}

    @media (max-width: 850px) {{
        .ftc-header .minicart-wrapper .showcart {{
            right: 25px;
        }}
    }}

    .ftc-header .minicart-wrapper .counter.qty {{
        background: none;
        color: #111;
        opacity: 0.9;
        transition: all 0.3s;
    }}

    /* Responsive nav icon (hamburger) */
    .responsive-nav-icon {{
        display: none;
        cursor: pointer;
        width: 30px;
        height: 24px;
        position: relative;
        z-index: 1000;
    }}

    @media (max-width: 1100px) {{
        .responsive-nav-icon {{
            display: block;
        }}
    }}

    .responsive-nav-icon span,
    .responsive-nav-icon span::before,
    .responsive-nav-icon span::after {{
        display: block;
        width: 100%;
        height: 2px;
        background: var(--color-dark);
        position: absolute;
        transition: all 0.3s;
    }}

    .responsive-nav-icon span {{
        top: 50%;
        transform: translateY(-50%);
    }}

    .responsive-nav-icon span::before {{
        content: "";
        top: -8px;
    }}

    .responsive-nav-icon span::after {{
        content: "";
        top: 8px;
    }}

    .responsive-nav-icon.active span {{
        background: transparent;
    }}

    .responsive-nav-icon.active span::before {{
        top: 0;
        transform: rotate(45deg);
    }}

    .responsive-nav-icon.active span::after {{
        top: 0;
        transform: rotate(-45deg);
    }}

    /* Wishlist icon in header */
    .ftc-header .guestwishlist-wrapper {{
        position: absolute;
        top: 58px;
        right: 145px;
    }}

    @media (max-width: 1200px) {{
        .ftc-header .guestwishlist-wrapper {{
            right: 75px;
        }}
    }}

    @media (max-width: 850px) {{
        .ftc-header .guestwishlist-wrapper {{
            right: 55px;
        }}
    }}

    @media (max-width: 600px) {{
        .ftc-header .guestwishlist-wrapper {{
            top: 51px;
            right: 43px;
        }}
    }}

    /* ================================================================
       HOMEPAGE
       ================================================================ */
    .cms-index-index .page-wrapper {{
        margin-top: 0;
    }}

    .cms-index-index .page-main {{
        margin: 0;
        padding: 0;
    }}

    .cms-index-index .page-main h1,
    .cms-index-index .page-main h2,
    .cms-index-index .page-main h3,
    .cms-index-index .page-main p,
    .cms-index-index .page-main a {{
        color: #fff;
        text-transform: uppercase;
        font-weight: normal;
    }}

    /* Home zones — image blocks */
    .home-zone {{
        float: left;
        position: relative;
        text-align: center;
        cursor: pointer;
        overflow: hidden;
    }}

    .home-zone img {{
        position: absolute;
        z-index: -1;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        object-fit: cover;
        transition: filter 0.3s, transform 0.3s;
    }}

    .home-zone:hover img {{
        transform: scale(1.05);
    }}

    .home-zone h2 {{
        font-family: var(--font-serif);
    }}

    /* Home arrivals */
    .home-arrivals {{
        margin: 10px 0 0 0;
        overflow: hidden;
    }}

    .home-arrivals .home-zone {{
        width: calc(50% - 5px);
        height: 800px;
    }}

    @media (max-width: 768px) {{
        .home-arrivals .home-zone {{
            width: 100%;
            height: 400px;
        }}
    }}

    .home-arrivals .home-zone.first {{
        margin: 0 10px 0 0;
    }}

    @media (max-width: 768px) {{
        .home-arrivals .home-zone.first {{
            margin: 0 0 10px 0;
        }}
    }}

    .home-arrivals .home-zone h2 {{
        margin: 40px 0 35px 0;
        font-size: 40px;
    }}

    @media (max-width: 768px) {{
        .home-arrivals .home-zone h2 {{
            font-size: 32px;
        }}
    }}

    /* Home links — 3 columns */
    .home-links {{
        margin: 95px 0 0 0;
        overflow: hidden;
    }}

    .home-links .home-zone {{
        width: calc(33.333% - 7px);
        height: 640px;
    }}

    @media (max-width: 768px) {{
        .home-links .home-zone {{
            width: 100%;
            height: 400px;
        }}
    }}

    .home-links .home-zone.first,
    .home-links .home-zone.second {{
        margin: 0 10px 0 0;
    }}

    @media (max-width: 768px) {{
        .home-links .home-zone.first,
        .home-links .home-zone.second {{
            margin-bottom: 10px;
        }}
    }}

    .home-links .home-zone h2 {{
        margin: 250px 20px 40px 20px;
        font-size: 30px;
    }}

    @media (max-width: 768px) {{
        .home-links .home-zone h2 {{
            margin-top: 125px;
        }}
    }}

    /* Home collection */
    .home-collection {{
        max-width: var(--max-width);
        margin: 75px auto 0 auto;
        overflow: hidden;
    }}

    .home-collection .slot {{
        width: 50%;
        float: left;
    }}

    @media (max-width: 768px) {{
        .home-collection .slot {{
            width: 100%;
        }}
    }}

    .home-collection .slot h2 {{
        margin: 0 0 105px 0;
        text-transform: none;
        font-family: var(--font-serif);
        font-size: 50px;
        line-height: 1.3;
        color: var(--color-dark);
    }}

    @media (max-width: 768px) {{
        .home-collection .slot h2 {{
            margin: 50px 0;
            text-align: center;
        }}
    }}

    .home-collection .slot p {{
        text-transform: none;
        font-size: 16px;
        line-height: 2.2;
        color: var(--color-dark);
    }}

    .home-collection .slot a {{
        color: var(--color-primary);
        line-height: 1.4;
    }}

    .home-collection .slot.first {{
        padding: 170px 0 0 0;
    }}

    .home-collection .slot.second {{
        padding: 0 0 0 140px;
    }}

    @media (max-width: 768px) {{
        .home-collection .slot.first,
        .home-collection .slot.second {{
            padding: 0;
        }}
    }}

    /* Home values */
    .home-values {{
        margin: 115px 0 0 0;
    }}

    @media (max-width: 768px) {{
        .home-values {{
            margin: 75px 0 0 0;
        }}
    }}

    .home-values .first.image {{
        width: 100%;
        height: 800px;
        object-fit: cover;
        object-position: left;
    }}

    @media (max-width: 768px) {{
        .home-values .first.image {{
            height: 400px;
        }}
    }}

    .home-values .layout-container {{
        position: relative;
        max-width: var(--max-width);
        margin: 0 auto;
    }}

    .home-values .layout-container h2 {{
        margin: 100px 0 350px 100px;
        font-family: var(--font-serif);
        font-size: 50px;
        text-transform: none;
        color: var(--color-dark);
    }}

    @media (max-width: 768px) {{
        .home-values .layout-container h2 {{
            width: 100%;
            margin: 75px 0;
            padding: 0 25px;
            font-size: 30px;
            text-align: center;
        }}
    }}

    .home-values .layout-container .text {{
        position: absolute;
        width: 960px;
        max-width: 100%;
        top: 250px;
        left: 0;
        right: 0;
        margin: 0 auto;
        padding: 0 20px;
        columns: 2;
        column-gap: 12.5%;
        text-transform: none;
        color: var(--color-dark);
        line-height: 2;
    }}

    @media (max-width: 768px) {{
        .home-values .layout-container .text {{
            position: static;
            padding: 0 20px 40px 20px;
            columns: 1;
        }}
    }}

    /* Home companies (logos) */
    .home-companies {{
        width: 100%;
        max-width: var(--max-width);
        margin: 125px auto 50px auto;
        padding: 100px 0 0 0;
        text-align: center;
    }}

    .home-companies h2 {{
        font-family: var(--font-serif);
        font-size: 42px;
        text-transform: none;
        color: var(--color-dark);
        padding: 0 35px 50px;
    }}

    .home-companies img {{
        height: 60px;
        width: auto;
        filter: saturate(0);
        transition: filter 0.3s;
    }}

    .home-companies img:hover {{
        filter: saturate(1);
    }}

    /* Home instagram */
    .home-instagram {{
        max-width: 1580px;
        margin: 105px auto 0 auto;
        overflow: hidden;
        text-align: center;
    }}

    @media (max-width: 768px) {{
        .home-instagram {{
            margin-top: 50px;
        }}
    }}

    .home-instagram > h2 {{
        font-family: var(--font-serif);
        font-size: 42px;
        text-transform: none;
        color: var(--color-dark);
    }}

    /* Home info bar */
    .home-info {{
        max-width: var(--max-width);
        margin: 0 auto;
        overflow: hidden;
    }}

    .home-info div {{
        float: left;
        position: relative;
        width: 25%;
        height: 50px;
        padding: 0 0 0 60px;
        line-height: 50px;
        text-transform: uppercase;
        color: #fff;
    }}

    @media (max-width: 1024px) {{
        .home-info div {{
            width: 50%;
            height: 90px;
            padding: 30px 0 30px 70px;
            color: var(--color-dark);
        }}
    }}

    @media (max-width: 768px) {{
        .home-info div {{
            width: 100%;
            padding-left: 90px;
        }}
    }}

    .home-info div img {{
        position: absolute;
        top: 0;
        left: 0;
        width: 50px;
        height: 50px;
    }}

    /* ================================================================
       FOOTER
       ================================================================ */
    .page-footer {{
        width: 100%;
        background: var(--color-gray-lightest, #f8f8f8);
    }}

    .page-footer .area {{
        max-width: var(--max-width);
        margin: 0 auto;
        padding: 15px 0 30px 0;
        overflow: hidden;
    }}

    .page-footer .area a {{
        transition: color 0.3s;
    }}

    .page-footer .area a:hover {{
        color: var(--color-primary);
    }}

    .page-footer .area.methods,
    .page-footer .area.bottom {{
        border-top: 1px solid var(--color-gray-light, #e0e0e0);
    }}

    @media (max-width: 768px) {{
        .page-footer .area.methods,
        .page-footer .area.bottom {{
            border-top: none;
        }}
    }}

    .page-footer .area .section {{
        float: left;
        width: calc(100% / 3);
    }}

    @media (max-width: 768px) {{
        .page-footer .area .section {{
            width: 100%;
            max-height: 50px;
            margin-top: 30px;
            border-top: 1px solid var(--color-gray-light, #e0e0e0);
            overflow: hidden;
            transition: max-height 0.3s;
        }}
        .page-footer .area .section.open {{
            max-height: 300px;
        }}
    }}

    .page-footer .area .section h3 {{
        position: relative;
        margin: 20px 0;
        font-family: var(--font-serif);
        font-size: 24px;
        font-weight: normal;
    }}

    .page-footer .area .section img {{
        height: 32px;
        margin: 0 16px 0 0;
        filter: saturate(0);
        transition: filter 0.3s;
    }}

    .page-footer .area .section img:hover {{
        filter: saturate(1);
    }}

    .page-footer .area .section .column {{
        float: left;
        width: 50%;
    }}

    /* Newsletter */
    .page-footer .block.newsletter {{
        width: 100%;
        margin: 30px 0 0 0;
        max-width: none;
    }}

    .page-footer .block.newsletter .field.newsletter {{
        width: 70%;
        margin: 0 5% 0 0;
        float: left;
    }}

    .page-footer .block.newsletter .field.newsletter input {{
        padding: 20px 0;
        border: none;
        border-bottom: 1px solid var(--color-gray-lighter, #eee);
        background-color: transparent;
        font-size: 15px;
        width: 100%;
    }}

    .page-footer .block.newsletter .actions {{
        width: 25%;
        float: left;
    }}

    .page-footer .block.newsletter .actions button {{
        opacity: 80%;
        width: 100%;
        padding: 12px 0;
        border: none;
        border-radius: 0;
        background-color: transparent;
        font-size: 14px;
        color: var(--color-primary);
        text-transform: uppercase;
        border-bottom: 2px solid var(--color-primary);
        transition: opacity 0.3s;
        cursor: pointer;
    }}

    .page-footer .block.newsletter .actions button:hover {{
        opacity: 100%;
    }}

    /* Legal & social */
    .page-footer .area .legal {{
        float: left;
        height: 20px;
        line-height: 20px;
        font-size: 12px;
        text-transform: uppercase;
    }}

    @media (max-width: 768px) {{
        .page-footer .area .legal {{
            float: none;
            width: 100%;
            text-align: center;
        }}
    }}

    .page-footer .area .social {{
        float: right;
    }}

    @media (max-width: 768px) {{
        .page-footer .area .social {{
            float: none;
            width: 100%;
            margin: 10px auto;
            text-align: center;
        }}
    }}

    .page-footer .area .social .icon {{
        display: inline-block;
        height: 20px;
        width: 20px;
        margin: 0 0 0 5px;
        background-size: 100% 100%;
        filter: saturate(0);
        transition: filter 0.3s;
    }}

    .page-footer .area .social .icon:hover {{
        filter: saturate(1);
    }}

    /* ================================================================
       CATEGORY PAGE
       ================================================================ */
    .catalog-category-view .page-title-wrapper,
    .catalogsearch-result-index .page-title-wrapper {{
        display: none;
    }}

    .category-view .category-image {{
        position: relative;
    }}

    .category-view .category-image h1 {{
        position: absolute;
        width: 100%;
        top: 50%;
        margin: -50px 0;
        text-align: center;
        font-family: var(--font-serif);
        font-size: 90px;
        color: #fff;
    }}

    @media (max-width: 768px) {{
        .category-view .category-image h1 {{
            top: 130px;
            font-size: 60px;
        }}
    }}

    @media (max-width: 768px) {{
        .category-view .category-image img {{
            width: 100%;
            height: 315px;
            object-fit: cover;
            object-position: left;
        }}
    }}

    .category-view .category-description {{
        width: 900px;
        max-width: 100%;
        margin: 60px auto 70px auto;
        text-align: center;
        font-size: 20px;
        line-height: 1.5;
    }}

    /* ================================================================
       REGION CHOOSER POPUP
       ================================================================ */
    .region-chooser {{
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 10000;
        background: rgba(0, 0, 0, 0.5);
    }}

    .region-chooser.active {{
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    .region-chooser-inner {{
        background: #fff;
        padding: 40px;
        max-width: 800px;
        width: 90%;
        position: relative;
        max-height: 90vh;
        overflow-y: auto;
    }}

    .region-chooser .close {{
        position: absolute;
        top: 15px;
        right: 15px;
        cursor: pointer;
        opacity: 0.6;
        transition: opacity 0.3s;
    }}

    .region-chooser .close:hover {{
        opacity: 1;
    }}

    .region-chooser .countries {{
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        justify-content: center;
        margin: 20px 0;
    }}

    .region-chooser .country {{
        width: 120px;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid var(--color-gray-light, #e0e0e0);
        cursor: pointer;
        transition: border-color 0.3s;
        background-size: 40px auto;
        background-repeat: no-repeat;
        background-position: center 15px;
        padding-top: 35px;
        font-size: 12px;
        text-transform: uppercase;
    }}

    .region-chooser .country:hover,
    .region-chooser .country.selected {{
        border-color: var(--color-primary);
    }}

    .region-chooser .apply {{
        display: inline-block;
        padding: 12px 40px;
        background: var(--color-dark);
        color: #fff;
        text-transform: uppercase;
        cursor: pointer;
        transition: opacity 0.3s;
    }}

    .region-chooser .apply:hover {{
        opacity: 0.9;
    }}

    /* ================================================================
       POPUP SYSTEM (product detail popups, size charts)
       ================================================================ */
    .ftc-overlay {{
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 9999;
        background: rgba(0, 0, 0, 0.7);
    }}

    .ftc-overlay .ftc-popup {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 800px;
        max-width: 90%;
        max-height: 80vh;
        background: #fff;
        overflow-y: auto;
        padding: 40px;
    }}

    .ftc-close {{
        position: absolute;
        top: 15px;
        right: 15px;
        cursor: pointer;
        width: 20px;
        height: 20px;
        opacity: 0.5;
        transition: opacity 0.3s;
    }}

    .ftc-close:hover {{
        opacity: 1;
    }}

    /* ================================================================
       BACK TO TOP
       ================================================================ */
    .back-to-top {{
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: rgba(173, 139, 112, 0.8);
        cursor: pointer;
        z-index: 100;
        opacity: 0;
        transition: opacity 0.3s;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    .back-to-top.visible {{
        opacity: 1;
    }}

    .back-to-top:hover {{
        background: rgba(173, 139, 112, 1);
    }}

    .back-to-top::after {{
        content: "";
        width: 12px;
        height: 12px;
        border-top: 2px solid #fff;
        border-right: 2px solid #fff;
        transform: rotate(-45deg);
        margin-top: 4px;
    }}

    /* ================================================================
       TOGGLE / ACCORDION (used in footer, filters, CMS pages)
       ================================================================ */
    .ftc-title-toggle {{
        cursor: pointer;
        position: relative;
    }}

    .ftc-title-toggle::after {{
        content: "+";
        position: absolute;
        right: 0;
        top: 0;
        transition: transform 0.3s;
    }}

    .ftc-title-toggle.active::after {{
        content: "−";
    }}

    .ftc-text-toggle {{
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.3s;
    }}

    .ftc-text-toggle.active {{
        max-height: 500px;
    }}

    /* ================================================================
       ANIMATIONS
       ================================================================ */
    @keyframes ftcNavAnim {{
        0% {{
            opacity: 0;
            height: 0;
        }}
        100% {{
            opacity: 1;
            height: auto;
        }}
    }}

    /* FTC fade slider */
    .ftc-fadeslider {{
        position: relative;
        overflow: hidden;
    }}

    .ftc-fadeslider .ftc-item {{
        display: none;
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
    }}

    .ftc-fadeslider .ftc-item:first-child {{
        display: block;
        position: relative;
    }}

    /* Slider arrows */
    .slider-arrow {{
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        opacity: 0.7;
        cursor: pointer;
        z-index: 10;
        width: 45px;
        height: 21px;
        background-size: 100% 100%;
        transition: opacity 0.3s;
    }}

    .slider-arrow:hover {{
        opacity: 1;
    }}

    .slider-arrow.prev {{
        left: 5px;
    }}

    .slider-arrow.next {{
        right: 5px;
    }}
}}
"""


def generate_tailwind_source_css() -> str:
    """Generate tailwind-source.css for Tailwind v3."""
    return """@tailwind base;
@tailwind components;
@tailwind utilities;

/* Brand layer on top of Hyvä */
@layer base {
  body {
    @apply font-sans text-base text-dark bg-[#f9f7f8];
  }

  h1, h2, h3, h4, h5, h6 {
    @apply font-serif uppercase;
  }

  a {
    @apply text-dark transition-colors duration-DEFAULT;
  }

  a:hover {
    @apply text-primary;
  }
}

@layer components {
  .btn-primary {
    @apply inline-block px-8 py-3 bg-dark text-white uppercase text-sm
           tracking-wider transition-opacity duration-DEFAULT
           hover:opacity-90;
  }

  .btn-secondary {
    @apply inline-block px-8 py-3 border border-dark text-dark uppercase text-sm
           tracking-wider transition-all duration-DEFAULT
           hover:bg-dark hover:text-white;
  }

  .page-title {
    @apply font-serif text-5xl md:text-7xl lg:text-9xl uppercase text-center;
  }

  .section-title {
    @apply font-serif text-3xl md:text-4xl uppercase;
  }

  .product-name {
    @apply font-sans text-lg uppercase;
  }

  .product-price {
    @apply font-sans text-3xl;
  }

  .product-price--old {
    @apply line-through text-dark-lightest text-sm;
  }

  .product-price--special {
    @apply text-secondary;
  }

  .container-ftc {
    @apply w-full max-w-content mx-auto px-4 md:px-6;
  }
}
"""


def generate_package_json(theme_name: str, tailwind_version: int = 4) -> str:
    if tailwind_version >= 4:
        return json.dumps({
            "name": theme_name.lower(),
            "version": "1.0.0",
            "private": True,
            "scripts": {
                "build": "npx @tailwindcss/cli -i web/tailwind/tailwind-source.css -o web/css/styles.css --minify",
                "watch": "npx @tailwindcss/cli -i web/tailwind/tailwind-source.css -o web/css/styles.css --watch"
            },
            "devDependencies": {
                "tailwindcss": "^4.1",
                "@tailwindcss/cli": "^4.1",
                "@hyva-themes/hyva-modules": "^1.3"
            }
        }, indent=4) + "\n"

    return json.dumps({
        "name": theme_name.lower(),
        "version": "1.0.0",
        "private": True,
        "scripts": {
            "build": "npx tailwindcss -i web/tailwind/tailwind-source.css -o web/css/styles.css --minify",
            "watch": "npx tailwindcss -i web/tailwind/tailwind-source.css -o web/css/styles.css --watch"
        },
        "devDependencies": {
            "tailwindcss": "^3.4",
            "@tailwindcss/forms": "^0.5",
            "@tailwindcss/typography": "^0.5",
            "@hyva-themes/hyva-modules": "^1.1"
        }
    }, indent=4) + "\n"


def generate_default_xml() -> str:
    """Generate Magento_Theme/layout/default.xml with head assets and Tailwind CSS."""
    return """<?xml version="1.0"?>
<page xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:noNamespaceSchemaLocation="urn:magento:framework:View/Layout/etc/page_configuration.xsd">
    <head>
        <css src="css/fonts.css"/>
        <css src="css/styles.css"/>
    </head>
</page>
"""


def generate_default_head_xml() -> str:
    """Generate default_head_blocks.xml for custom fonts."""
    return """<?xml version="1.0"?>
<page xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:noNamespaceSchemaLocation="urn:magento:framework:View/Layout/etc/page_configuration.xsd">
    <head>
        <!-- Custom fonts from source theme -->
        <css src="css/fonts.css"/>
    </head>
</page>
"""


def generate_fonts_css(source_fonts_dir: str = "") -> str:
    """Generate @font-face declarations for custom fonts.

    If source_fonts_dir is provided, scans it to discover actual font files
    and generates correct src references. Otherwise uses sensible defaults.
    """
    # Default font definitions — if source dir exists, we'll auto-detect
    font_defs = [
        {
            "family": "Korpus-B",
            "basename": "korpus-b-webfont",
            "weight": "normal",
            "style": "normal",
        },
        {
            "family": "KorpusGrotesk-B",
            "basename": "Korpus-Grotesk-B-webfont",
            "weight": "normal",
            "style": "normal",
        },
        {
            "family": "KorpusGrotesk-C",
            "basename": "Korpus-Grotesk-C-webfont",
            "weight": "normal",
            "style": "normal",
        },
        {
            "family": "Sartex",
            "basename": "sartex",
            "weight": "normal",
            "style": "normal",
        },
        {
            "family": "Cormorant Infant",
            "basename": "CormorantInfant-Regular",
            "weight": "normal",
            "style": "normal",
        },
        {
            "family": "Montserrat",
            "basename": "Montserrat-Regular",
            "weight": "normal",
            "style": "normal",
        },
    ]

    # Map extensions to CSS format names
    format_map = {
        ".woff2": "woff2",
        ".woff": "woff",
        ".ttf": "truetype",
        ".otf": "opentype",
        ".eot": "embedded-opentype",
        ".svg": "svg",
    }

    # Preferred order for modern browsers
    format_order = [".woff2", ".woff", ".ttf", ".otf", ".eot", ".svg"]

    css = "/* Brand Fonts (auto-detected) */\n"

    for fdef in font_defs:
        basename = fdef["basename"]
        available_exts = []

        if source_fonts_dir and os.path.isdir(source_fonts_dir):
            # Scan source directory for actual files matching this basename
            for ext in format_order:
                candidate = os.path.join(source_fonts_dir, basename + ext)
                if os.path.isfile(candidate):
                    available_exts.append(ext)
        else:
            # Default: assume woff2 + woff are available
            available_exts = [".woff2", ".woff"]

        if not available_exts:
            continue

        src_parts = []
        for ext in available_exts:
            fmt = format_map[ext]
            src_parts.append(f"url('../fonts/{basename}{ext}') format('{fmt}')")

        src_str = ",\n         ".join(src_parts)

        css += f"""
@font-face {{
    font-family: '{fdef["family"]}';
    src: {src_str};
    font-weight: {fdef["weight"]};
    font-style: {fdef["style"]};
    font-display: swap;
}}
"""

    return css


def scaffold_hyva_theme(
    output_path: str,
    vendor: str,
    theme_name: str,
    title: str,
    tokens: DesignTokens,
    source_theme_path: str = "",
    tailwind_version: int = 4,
):
    """Create the complete Hyvä child theme directory structure."""
    base = os.path.join(output_path, vendor, theme_name)
    os.makedirs(base, exist_ok=True)

    # Detect source fonts directory for accurate @font-face generation
    source_fonts_dir = ""
    if source_theme_path:
        candidate = os.path.join(source_theme_path, "web", "fonts")
        if os.path.isdir(candidate):
            source_fonts_dir = candidate

    # Core theme files
    files = {
        "registration.php": generate_registration_php(vendor, theme_name),
        "theme.xml": generate_theme_xml(title),
        "composer.json": generate_composer_json(vendor, theme_name),
        "package.json": generate_package_json(theme_name, tailwind_version),
        "web/css/fonts.css": generate_fonts_css(source_fonts_dir),
        "Magento_Theme/layout/default.xml": generate_default_xml(),
        "Magento_Theme/layout/default_head_blocks.xml": generate_default_head_xml(),
    }

    # Tailwind config files depend on version
    if tailwind_version >= 4:
        files["web/tailwind/hyva.config.json"] = generate_tailwind_config(
            tokens, vendor, theme_name, tailwind_version
        )
        files["web/tailwind/tailwind-source.css"] = generate_tailwind_source_css_v4(
            tokens, vendor, theme_name
        )
    else:
        files["web/tailwind/tailwind.config.js"] = generate_tailwind_config(
            tokens, vendor, theme_name, tailwind_version
        )
        files["web/tailwind/tailwind-source.css"] = generate_tailwind_source_css()

    # Create directories for fonts (placeholder)
    os.makedirs(os.path.join(base, "web", "fonts"), exist_ok=True)
    os.makedirs(os.path.join(base, "web", "images", "icons"), exist_ok=True)
    os.makedirs(os.path.join(base, "web", "images", "social"), exist_ok=True)
    os.makedirs(os.path.join(base, "web", "images", "flags"), exist_ok=True)
    os.makedirs(os.path.join(base, "web", "css"), exist_ok=True)
    os.makedirs(os.path.join(base, "i18n"), exist_ok=True)

    for rel_path, content in files.items():
        full_path = os.path.join(base, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

    return base
