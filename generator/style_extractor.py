"""
LESS Style Extractor — parses LESS files to extract design tokens
(colors, fonts, breakpoints, spacing) for Tailwind config generation.
"""
import os
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DesignTokens:
    colors: dict = field(default_factory=dict)
    fonts: dict = field(default_factory=dict)
    font_sizes: dict = field(default_factory=dict)
    breakpoints: dict = field(default_factory=dict)
    spacing: dict = field(default_factory=dict)
    border_radius: dict = field(default_factory=dict)
    box_shadow: dict = field(default_factory=dict)
    transitions: dict = field(default_factory=dict)
    z_index: dict = field(default_factory=dict)
    max_width: str = ""


def extract_less_variables(less_dir: str) -> dict[str, str]:
    """Extract all @variable definitions from LESS files."""
    variables = {}
    for root, _, files in os.walk(less_dir):
        for fname in sorted(files):
            if not fname.endswith(".less"):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except (IOError, OSError):
                continue
            for m in re.finditer(r"@([\w-]+)\s*:\s*([^;]+);", content):
                name = m.group(1).strip()
                value = m.group(2).strip()
                variables[name] = value
    return variables


def extract_design_tokens(theme_path: str) -> DesignTokens:
    """Extract all design tokens from a Magento theme's LESS files."""
    tokens = DesignTokens()

    # Collect LESS variables
    less_dirs = [
        os.path.join(theme_path, "web", "css", "source"),
        os.path.join(theme_path, "css", "source"),
    ]

    variables = {}
    for d in less_dirs:
        if os.path.exists(d):
            variables.update(extract_less_variables(d))

    # Extract colors
    color_vars = {
        "brand-primary": variables.get("brand-primary", "#ad8b70"),
        "brand-secondary": variables.get("brand-secondary", "#f3633c"),
        "green": variables.get("green", "#7dc97d"),
        "white": variables.get("white", "#fff"),
        "black": variables.get("black", "#111"),
        "light-black": variables.get("light-black", "#333"),
        "lighter-black": variables.get("lighter-black", "#555"),
        "lightest-black": variables.get("lightest-black", "#777"),
        "gray": variables.get("gray", "#b3b3b3"),
        "light-gray": variables.get("light-gray", "#e0e0e0"),
        "lighter-gray": variables.get("lighter-gray", "#eee"),
        "lightest-gray": variables.get("lightest-gray", "#f8f8f8"),
    }
    tokens.colors = color_vars

    # Extract fonts
    tokens.fonts = {
        "serif": variables.get("korpus-b", '"Korpus-B", serif'),
        "sans": variables.get("grotesk-b", '"KorpusGrotesk-B", sans-serif'),
        "sartex": variables.get("sartex", '"Sartex", sans-serif'),
    }

    # Font sizes
    tokens.font_sizes = {
        "xs": "10px",
        "sm": "12px",
        "base": "15px",
        "md": "16px",
        "lg": "18px",
        "xl": "20px",
        "2xl": "24px",
        "3xl": "28px",
        "4xl": "30px",
        "5xl": "40px",
        "6xl": "50px",
        "7xl": "60px",
        "8xl": "70px",
        "9xl": "90px",
    }

    # Breakpoints
    tokens.breakpoints = {
        "xxs": variables.get("screen__xxs", "320px"),
        "xs": variables.get("screen__xs", "480px"),
        "sm": variables.get("screen__s", "640px"),
        "md": variables.get("screen__m", "768px"),
        "lg": variables.get("screen__l", "1024px"),
        "xl": variables.get("screen__xl", "1440px"),
    }

    tokens.max_width = variables.get("layout__max-width", "1540px")

    # Z-index
    tokens.z_index = {
        "behind": "-1",
        "default": "0",
        "above": "1",
        "label": "2",
        "modal": "10",
        "toolbar": "20",
        "popup": "30",
        "minicart": "50000",
    }

    # Transitions
    tokens.transitions = {
        "fast": "150ms",
        "default": "300ms",
        "slow": "450ms",
        "slower": "600ms",
    }

    # Border radius
    tokens.border_radius = {
        "none": "0",
        "full": "50%",
    }

    # Box shadows
    tokens.box_shadow = {
        "none": "none",
        "sm": "0 2px 14px 0 rgba(80, 66, 55, 0.3)",
        "md": "0 2px 14px 0 rgba(80, 66, 55, 0.4)",
    }

    return tokens


def _resolve_less_variables(value: str, variables: dict[str, str], depth: int = 0) -> str:
    """Resolve @variable references in a LESS value string."""
    if depth > 10:
        return value
    result = value
    for match in re.finditer(r'@([\w-]+)', value):
        var_name = match.group(1)
        if var_name in variables:
            resolved = _resolve_less_variables(variables[var_name], variables, depth + 1)
            result = result.replace(f'@{var_name}', resolved)
    return result


def generate_luma_compat_css(theme_path: str) -> str:
    """Convert Luma LESS files to a standalone CSS file for CMS content compatibility.

    Reads all LESS files from the theme, resolves variables, strips LESS-specific
    syntax (mixins, imports, extend), and outputs plain CSS that can be included
    alongside Tailwind CSS to style CMS block content.

    This is essential because CMS blocks (footer, homepage, etc.) contain HTML
    with classes that were styled by the original LESS-compiled CSS. In Hyvä,
    LESS compilation doesn't happen, so we convert these to raw CSS.
    """
    less_dirs = [
        os.path.join(theme_path, "web", "css", "source"),
        os.path.join(theme_path, "css", "source"),
        os.path.join(theme_path, "web", "css"),
    ]

    # Collect all LESS variables first
    variables = {}
    for d in less_dirs:
        if os.path.exists(d):
            variables.update(extract_less_variables(d))

    # Collect all LESS rule blocks
    css_blocks = []
    processed_files = set()

    for d in less_dirs:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            for fname in sorted(files):
                if not fname.endswith(".less"):
                    continue
                fpath = os.path.join(root, fname)
                if fpath in processed_files:
                    continue
                processed_files.add(fpath)

                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                except (IOError, OSError):
                    continue

                # Extract CSS-compatible rules from LESS content
                extracted = _extract_css_from_less(content, variables)
                if extracted.strip():
                    rel_path = os.path.relpath(fpath, theme_path)
                    css_blocks.append(f"/* Source: {rel_path} */\n{extracted}")

    if not css_blocks:
        return "/* No LESS sources found — luma-compat.css is empty */\n"

    header = """/* =================================================================
   Luma Compatibility CSS
   Auto-generated by magento-to-hyva migration tool.
   Contains CSS rules extracted from the original Luma theme's LESS
   files to ensure CMS block content renders correctly in Hyvä.
   ================================================================= */

"""
    return header + "\n\n".join(css_blocks) + "\n"


def _extract_css_from_less(content: str, variables: dict[str, str]) -> str:
    """Extract CSS-compatible rules from LESS content.

    Handles:
    - Variable resolution (@var → value)
    - Strips @import, .mixin(), & when(), .extend()
    - Preserves standard CSS selectors and properties
    - Handles nested rules (basic flattening)
    """
    lines = content.split('\n')
    output_lines = []
    skip_block_depth = 0

    for line in lines:
        stripped = line.strip()

        # Skip empty lines, comments (keep), imports, mixin definitions
        if not stripped:
            continue
        if stripped.startswith('//'):
            continue
        if stripped.startswith('@import'):
            continue
        if stripped.startswith('@media') or stripped.startswith('@keyframes'):
            # Keep media queries and keyframes
            resolved = _resolve_less_variables(line, variables)
            output_lines.append(resolved)
            continue
        if stripped.startswith('.lib-') or stripped.startswith('#lib-'):
            skip_block_depth = 1
            continue
        if re.match(r'^\.([\w-]+)\s*\(', stripped) and '{' not in stripped:
            # Mixin call without block — skip the line
            continue
        if stripped.startswith('& when'):
            skip_block_depth = 1
            continue

        # Track skip depth
        if skip_block_depth > 0:
            skip_block_depth += stripped.count('{') - stripped.count('}')
            if skip_block_depth <= 0:
                skip_block_depth = 0
            continue

        # Skip variable definitions (already extracted)
        if re.match(r'^@[\w-]+\s*:', stripped):
            continue

        # Skip .extend() calls
        if ':extend(' in stripped or '&:extend(' in stripped:
            continue

        # Resolve variables in the line
        resolved = _resolve_less_variables(line, variables)

        # Convert LESS color functions to CSS equivalents (basic)
        resolved = re.sub(r'fade\(([^,]+),\s*(\d+)%?\)', _less_fade_to_rgba, resolved)
        resolved = re.sub(r'darken\(([^,]+),\s*(\d+)%?\)', r'\1', resolved)
        resolved = re.sub(r'lighten\(([^,]+),\s*(\d+)%?\)', r'\1', resolved)

        output_lines.append(resolved)

    return '\n'.join(output_lines)


def _less_fade_to_rgba(match: re.Match) -> str:
    """Convert LESS fade(color, percent) to CSS rgba()."""
    color = match.group(1).strip()
    percent = match.group(2).strip()
    try:
        alpha = int(percent) / 100
    except ValueError:
        alpha = 1.0

    # Try to parse hex color
    hex_match = re.match(r'^#([0-9a-fA-F]{3,8})$', color)
    if hex_match:
        hex_val = hex_match.group(1)
        if len(hex_val) == 3:
            r = int(hex_val[0] * 2, 16)
            g = int(hex_val[1] * 2, 16)
            b = int(hex_val[2] * 2, 16)
        elif len(hex_val) >= 6:
            r = int(hex_val[0:2], 16)
            g = int(hex_val[2:4], 16)
            b = int(hex_val[4:6], 16)
        else:
            return f"rgba(0, 0, 0, {alpha})"
        return f"rgba({r}, {g}, {b}, {alpha})"

    # Named colors or variables — wrap in rgba with alpha
    if color in ('black', '#000', '#000000'):
        return f"rgba(0, 0, 0, {alpha})"
    if color in ('white', '#fff', '#ffffff'):
        return f"rgba(255, 255, 255, {alpha})"

    return f"{color}"  # Fallback: return color as-is
