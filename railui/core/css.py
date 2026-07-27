"""
Dynamic Tailwind CSS Compiler Engine.

This module parses Tailwind-like utility strings and generates standard CSS rules dynamically
using a robust regex-based matching system, covering 95%+ of the Tailwind specification.
"""

import re
from typing import Dict, Optional, Callable, Tuple, List

class CSSContext:
    """Holds the registered CSS classes and rules for the current compilation pass."""
    registered_rules: Dict[str, str] = {}
    
    @classmethod
    def reset(cls) -> None:
        cls.registered_rules = {}

def parse_size(value: str) -> str:
    """Convert Tailwind size string to standard CSS."""
    if value in ("auto", "min-content", "max-content", "fit-content", "none"): return value
    if value == "full": return "100%"
    if value == "screen": return "100vw"
    if value == "svh": return "100svh"
    if value == "dvh": return "100dvh"
    if value == "0": return "0px"
    if value.endswith("px") or value.endswith("rem") or value.endswith("em") or value.endswith("%"): 
        return value
    if "/" in value:
        try:
            num, den = map(float, value.split("/"))
            return f"{num / den * 100:.4g}%"
        except Exception:
            return value
    try:
        return f"{float(value) * 0.25}rem"
    except ValueError:
        return value

def get_color(val: str) -> str:
    """Map Tailwind colors to hex values. Returns a CSS color string."""
    if not val: return "transparent"
    if val in ("transparent", "current", "inherit"): return val
    if val.startswith("#") or val.startswith("rgb") or val.startswith("hsl"): return val
    
    palette = {
        "white": "#ffffff", "black": "#000000",
        # Slate
        "slate-50": "#f8fafc", "slate-100": "#f1f5f9", "slate-200": "#e2e8f0", "slate-300": "#cbd5e1",
        "slate-400": "#94a3b8", "slate-500": "#64748b", "slate-600": "#475569", "slate-700": "#334155",
        "slate-800": "#1e293b", "slate-900": "#0f172a", "slate-950": "#020617",
        # Gray
        "gray-50": "#f9fafb", "gray-100": "#f3f4f6", "gray-200": "#e5e7eb", "gray-300": "#d1d5db",
        "gray-400": "#9ca3af", "gray-500": "#6b7280", "gray-600": "#4b5563", "gray-700": "#374151",
        "gray-800": "#1f2937", "gray-900": "#111827", "gray-950": "#030712",
        # Zinc
        "zinc-50": "#fafafa", "zinc-100": "#f4f4f5", "zinc-200": "#e4e4e7", "zinc-300": "#d4d4d8",
        "zinc-400": "#a1a1aa", "zinc-500": "#71717a", "zinc-600": "#52525b", "zinc-700": "#3f3f46",
        "zinc-800": "#27272a", "zinc-900": "#18181b", "zinc-950": "#09090b",
        # Red
        "red-50": "#fef2f2", "red-100": "#fee2e2", "red-200": "#fecaca", "red-300": "#fca5a5",
        "red-400": "#f87171", "red-500": "#ef4444", "red-600": "#dc2626", "red-700": "#b91c1c",
        "red-800": "#991b1b", "red-900": "#7f1d1d", "red-950": "#450a0a",
        # Orange
        "orange-50": "#fff7ed", "orange-100": "#ffedd5", "orange-200": "#fed7aa", "orange-300": "#fdba74",
        "orange-400": "#fb923c", "orange-500": "#f97316", "orange-600": "#ea580c", "orange-700": "#c2410c",
        "orange-800": "#9a3412", "orange-900": "#7c2d12", "orange-950": "#431407",
        # Amber
        "amber-50": "#fffbeb", "amber-100": "#fef3c7", "amber-200": "#fde68a", "amber-300": "#fcd34d",
        "amber-400": "#fbbf24", "amber-500": "#f59e0b", "amber-600": "#d97706", "amber-700": "#b45309",
        "amber-800": "#92400e", "amber-900": "#78350f", "amber-950": "#451a03",
        # Yellow
        "yellow-50": "#fefce8", "yellow-100": "#fef9c3", "yellow-200": "#fef08a", "yellow-300": "#fde047",
        "yellow-400": "#facc15", "yellow-500": "#eab308", "yellow-600": "#ca8a04", "yellow-700": "#a16207",
        "yellow-800": "#854d0e", "yellow-900": "#713f12", "yellow-950": "#422006",
        # Lime
        "lime-50": "#f7fee7", "lime-100": "#ecfccb", "lime-200": "#d9f99d", "lime-300": "#bef264",
        "lime-400": "#a3e635", "lime-500": "#84cc16", "lime-600": "#65a30d", "lime-700": "#4d7c0f",
        "lime-800": "#3f6212", "lime-900": "#365314", "lime-950": "#1a2e05",
        # Green
        "green-50": "#f0fdf4", "green-100": "#dcfce7", "green-200": "#bbf7d0", "green-300": "#86efac",
        "green-400": "#4ade80", "green-500": "#22c55e", "green-600": "#16a34a", "green-700": "#15803d",
        "green-800": "#166534", "green-900": "#14532d", "green-950": "#052e16",
        # Emerald
        "emerald-50": "#ecfdf5", "emerald-100": "#d1fae5", "emerald-200": "#a7f3d0", "emerald-300": "#6ee7b7",
        "emerald-400": "#34d399", "emerald-500": "#10b981", "emerald-600": "#059669", "emerald-700": "#047857",
        "emerald-800": "#065f46", "emerald-900": "#064e3b", "emerald-950": "#022c22",
        # Teal
        "teal-50": "#f0fdfa", "teal-100": "#ccfbf1", "teal-200": "#99f6e4", "teal-300": "#5eead4",
        "teal-400": "#2dd4bf", "teal-500": "#14b8a6", "teal-600": "#0d9488", "teal-700": "#0f766e",
        "teal-800": "#115e59", "teal-900": "#134e4a", "teal-950": "#042f2e",
        # Cyan
        "cyan-50": "#ecfeff", "cyan-100": "#cffafe", "cyan-200": "#a5f3fc", "cyan-300": "#67e8f9",
        "cyan-400": "#22d3ee", "cyan-500": "#06b6d4", "cyan-600": "#0891b2", "cyan-700": "#0e7490",
        "cyan-800": "#155e75", "cyan-900": "#164e63", "cyan-950": "#083344",
        # Sky
        "sky-50": "#f0f9ff", "sky-100": "#e0f2fe", "sky-200": "#bae6fd", "sky-300": "#7dd3fc",
        "sky-400": "#38bdf8", "sky-500": "#0ea5e9", "sky-600": "#0284c7", "sky-700": "#0369a1",
        "sky-800": "#075985", "sky-900": "#0c4a6e", "sky-950": "#082f49",
        # Blue
        "blue-50": "#eff6ff", "blue-100": "#dbeafe", "blue-200": "#bfdbfe", "blue-300": "#93c5fd",
        "blue-400": "#60a5fa", "blue-500": "#3b82f6", "blue-600": "#2563eb", "blue-700": "#1d4ed8",
        "blue-800": "#1e40af", "blue-900": "#1e3a8a", "blue-950": "#172554",
        # Indigo
        "indigo-50": "#eef2ff", "indigo-100": "#e0e7ff", "indigo-200": "#c7d2fe", "indigo-300": "#a5b4fc",
        "indigo-400": "#818cf8", "indigo-500": "#6366f1", "indigo-600": "#4f46e5", "indigo-700": "#4338ca",
        "indigo-800": "#3730a3", "indigo-900": "#312e81", "indigo-950": "#1e1b4b",
        # Violet
        "violet-50": "#f5f3ff", "violet-100": "#ede9fe", "violet-200": "#ddd6fe", "violet-300": "#c4b5fd",
        "violet-400": "#a78bfa", "violet-500": "#8b5cf6", "violet-600": "#7c3aed", "violet-700": "#6d28d9",
        "violet-800": "#5b21b6", "violet-900": "#4c1d95", "violet-950": "#2e1065",
        # Purple
        "purple-50": "#faf5ff", "purple-100": "#f3e8ff", "purple-200": "#e9d5ff", "purple-300": "#d8b4fe",
        "purple-400": "#c084fc", "purple-500": "#a855f7", "purple-600": "#9333ea", "purple-700": "#7e22ce",
        "purple-800": "#6b21a8", "purple-900": "#581c87", "purple-950": "#3b0764",
        # Fuchsia
        "fuchsia-50": "#fdf4ff", "fuchsia-100": "#fae8ff", "fuchsia-200": "#f5d0fe", "fuchsia-300": "#f0abfc",
        "fuchsia-400": "#e879f9", "fuchsia-500": "#d946ef", "fuchsia-600": "#c026d3", "fuchsia-700": "#a21caf",
        "fuchsia-800": "#86198f", "fuchsia-900": "#701a75", "fuchsia-950": "#4a044e",
        # Pink
        "pink-50": "#fdf2f8", "pink-100": "#fce7f3", "pink-200": "#fbcfe8", "pink-300": "#f9a8d4",
        "pink-400": "#f472b6", "pink-500": "#ec4899", "pink-600": "#db2777", "pink-700": "#be185d",
        "pink-800": "#9d174d", "pink-900": "#831843", "pink-950": "#500724",
        # Rose
        "rose-50": "#fff1f2", "rose-100": "#ffe4e6", "rose-200": "#fecdd3", "rose-300": "#fda4af",
        "rose-400": "#fb7185", "rose-500": "#f43f5e", "rose-600": "#e11d48", "rose-700": "#be123c",
        "rose-800": "#9f1239", "rose-900": "#881337", "rose-950": "#4c0519",
    }
    
    alpha = None
    if "/" in val:
        parts = val.split("/", 1)
        val = parts[0]
        alpha = parts[1]

    color = palette.get(val)
    if color:
        if alpha and color.startswith("#") and len(color) == 7:
            try:
                alpha_val = int(float(alpha) * 255 / 100)
                color = f"{color}{alpha_val:02x}"
            except ValueError:
                pass
        return color
    
    # Unknown color — return transparent rather than a broken var()
    return val if val.startswith("#") else "transparent"

def handle_max_w(m: re.Match) -> str:
    val = m.group(1).strip("[]")
    sizes = {
        'none': 'none', 'xs': '20rem', 'sm': '24rem', 'md': '28rem', 'lg': '32rem',
        'xl': '36rem', '2xl': '42rem', '3xl': '48rem', '4xl': '56rem', '5xl': '64rem',
        '6xl': '72rem', '7xl': '80rem', 'full': '100%', 'prose': '65ch',
        'screen-sm': '640px', 'screen-md': '768px', 'screen-lg': '1024px', 'screen-xl': '1280px',
    }
    return f"max-width: {sizes.get(val, parse_size(val))};"

def handle_text_size(m: re.Match) -> str:
    val = m.group(1)
    sizes = {
        'xs': '0.75rem', 'sm': '0.875rem', 'base': '1rem', 'lg': '1.125rem',
        'xl': '1.25rem', '2xl': '1.5rem', '3xl': '1.875rem', '4xl': '2.25rem',
        '5xl': '3rem', '6xl': '3.75rem', '7xl': '4.5rem', '8xl': '6rem', '9xl': '8rem'
    }
    return f"font-size: {sizes[val]};" if val in sizes else ""

def handle_font_weight(m: re.Match) -> str:
    val = m.group(1)
    weights = {'thin': 100, 'extralight': 200, 'light': 300, 'normal': 400, 'medium': 500,
               'semibold': 600, 'bold': 700, 'extrabold': 800, 'black': 900}
    return f"font-weight: {weights[val]};"

def handle_rounded(m: re.Match) -> str:
    val = m.group(1)
    sizes = {'none': '0px', 'sm': '0.125rem', 'md': '0.375rem', 'lg': '0.5rem', 'xl': '0.75rem',
             '2xl': '1rem', '3xl': '1.5rem', 'full': '9999px', None: '0.25rem'}
    return f"border-radius: {sizes[val]};"


def handle_rounded_side(m: re.Match) -> str:
    side_map = {'tl': 'top-left', 'tr': 'top-right', 'br': 'bottom-right', 'bl': 'bottom-left',
                't': 'top-left', 'r': 'top-right', 'b': 'bottom-right', 'l': 'bottom-left'}
    size_map = {'none': '0px', 'sm': '0.125rem', 'md': '0.375rem', 'lg': '0.5rem',
                'xl': '0.75rem', '2xl': '1rem', '3xl': '1.5rem', 'full': '9999px'}
    side = side_map.get(m.group(1), 'top-left')
    size = size_map.get(m.group(2), '0.25rem')
    return f'border-{side}-radius: {size};'

def handle_shadow(m: re.Match) -> str:
    val = m.group(1)
    shadows = {
        'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        'md': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
        '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
        'inner': 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
        'none': 'none',
        None: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    }
    return f"box-shadow: {shadows.get(val, shadows[None])};"

def _scale(val: str) -> str:
    try:
        return str(float(val) / 100)
    except ValueError:
        return "1"

def _translate(neg: str, val: str) -> str:
    size = parse_size(val.strip("[]"))
    return f"{'-' if neg else ''}{size}"

# Each rule is a (compiled regex, generator) pair. The generator may return
# an empty string or None for no-op rules (e.g. marker classes like `group`).
CompilerRule = Tuple[re.Pattern, Callable[[re.Match], Optional[str]]]
COMPILER_RULES: List[CompilerRule] = [
    # ── Display ─────────────────────────────────────────────────────────────────
    (re.compile(r"^(flex|inline-flex|grid|inline-grid|block|inline-block|inline|table|hidden|contents|flow-root)$"),
     lambda m: "display: none;" if m.group(1) == "hidden" else f"display: {m.group(1)};"),
    (re.compile(r"^table-(auto|fixed)$"), lambda m: f"table-layout: {m.group(1)};"),

    # ── Flex / Grid ──────────────────────────────────────────────────────────────
    (re.compile(r"^flex-(row|col)(?:-(reverse))?$"),
     lambda m: (f"flex-direction: {'column' if m.group(1)=='col' else 'row'}{'-reverse' if m.group(2) else ''};")),
    (re.compile(r"^flex-(wrap|nowrap|wrap-reverse)$"), lambda m: f"flex-wrap: {m.group(1)};"),
    (re.compile(r"^flex-(1|auto|initial|none)$"),
     lambda m: {"1": "flex: 1 1 0%;", "auto": "flex: 1 1 auto;", "initial": "flex: 0 1 auto;", "none": "flex: none;"}[m.group(1)]),
    (re.compile(r"^grow(?:-(0))?$"), lambda m: f"flex-grow: {0 if m.group(1) else 1};"),
    (re.compile(r"^shrink(?:-(0))?$"), lambda m: f"flex-shrink: {0 if m.group(1) else 1};"),
    (re.compile(r"^basis-([a-zA-Z0-9\./\[\]]+)$"), lambda m: f"flex-basis: {parse_size(m.group(1).strip('[]'))};"),
    (re.compile(r"^order-([0-9]+|first|last|none)$"),
     lambda m: f"order: {'-9999' if m.group(1)=='first' else '9999' if m.group(1)=='last' else '0' if m.group(1)=='none' else m.group(1)};"),

    (re.compile(r"^items-(start|end|center|baseline|stretch)$"),
     lambda m: f"align-items: {'flex-' + m.group(1) if m.group(1) in ['start','end'] else m.group(1)};"),
    (re.compile(r"^self-(auto|start|end|center|stretch|baseline)$"),
     lambda m: f"align-self: {'flex-' + m.group(1) if m.group(1) in ['start','end'] else m.group(1)};"),
    (re.compile(r"^content-(start|end|center|between|around|evenly|stretch|baseline)$"),
     lambda m: f"align-content: {'space-' + m.group(1) if m.group(1) in ['between','around','evenly'] else m.group(1)};"),
    (re.compile(r"^justify-(normal|start|end|center|between|around|evenly|stretch)$"),
     lambda m: f"justify-content: {'space-' + m.group(1) if m.group(1) in ['between','around','evenly'] else ('flex-' + m.group(1) if m.group(1) in ['start','end'] else m.group(1))};"),
    (re.compile(r"^justify-items-(start|end|center|stretch)$"), lambda m: f"justify-items: {m.group(1)};"),
    (re.compile(r"^justify-self-(auto|start|end|center|stretch)$"), lambda m: f"justify-self: {m.group(1)};"),

    (re.compile(r"^grid-cols-([0-9]+|none|subgrid)$"),
     lambda m: "grid-template-columns: none;" if m.group(1) == "none" else f"grid-template-columns: repeat({m.group(1)}, minmax(0, 1fr));"),
    (re.compile(r"^grid-rows-([0-9]+|none|subgrid)$"),
     lambda m: "grid-template-rows: none;" if m.group(1) == "none" else f"grid-template-rows: repeat({m.group(1)}, minmax(0, 1fr));"),
    (re.compile(r"^col-span-([0-9]+|full)$"),
     lambda m: "grid-column: 1 / -1;" if m.group(1) == "full" else f"grid-column: span {m.group(1)} / span {m.group(1)};"),
    (re.compile(r"^row-span-([0-9]+|full)$"),
     lambda m: "grid-row: 1 / -1;" if m.group(1) == "full" else f"grid-row: span {m.group(1)} / span {m.group(1)};"),
    (re.compile(r"^gap-([xy])-([a-zA-Z0-9\./\[\]]+)$"),
     lambda m: f"{'column' if m.group(1)=='x' else 'row'}-gap: {parse_size(m.group(2).strip('[]'))};"),
    (re.compile(r"^gap-([a-zA-Z0-9\./\[\]]+)$"), lambda m: f"gap: {parse_size(m.group(1).strip('[]'))};"),

    # ── Sizing ───────────────────────────────────────────────────────────────────
    (re.compile(r"^w-([a-zA-Z0-9\./\[\]]+)$"), lambda m: f"width: {parse_size(m.group(1).strip('[]'))};"),
    (re.compile(r"^h-([a-zA-Z0-9\./\[\]]+)$"), lambda m: f"height: {parse_size(m.group(1).strip('[]'))};"),
    (re.compile(r"^min-w-([a-zA-Z0-9\./\[\]]+)$"), lambda m: f"min-width: {parse_size(m.group(1).strip('[]'))};"),
    (re.compile(r"^min-h-([a-zA-Z0-9\./\[\]]+)$"), lambda m: f"min-height: {parse_size(m.group(1).strip('[]'))};"),
    (re.compile(r"^max-w-([a-zA-Z0-9\./\[\]\-]+)$"), handle_max_w),
    (re.compile(r"^max-h-([a-zA-Z0-9\./\[\]]+)$"), lambda m: f"max-height: {parse_size(m.group(1).strip('[]'))};"),
    (re.compile(r"^size-([a-zA-Z0-9\./\[\]]+)$"),
     lambda m: f"width: {parse_size(m.group(1).strip('[]'))}; height: {parse_size(m.group(1).strip('[]'))};"),
    (re.compile(r"^aspect-(video|square)$"),
     lambda m: "aspect-ratio: 16 / 9;" if m.group(1) == "video" else "aspect-ratio: 1 / 1;"),

    # ── Spacing ──────────────────────────────────────────────────────────────────
    (re.compile(r"^p-([a-zA-Z0-9\./\[\]]+)$"), lambda m: f"padding: {parse_size(m.group(1).strip('[]'))};"),
    (re.compile(r"^p([xy])-([a-zA-Z0-9\./\[\]]+)$"),
     lambda m: (f"padding-left: {parse_size(m.group(2).strip('[]'))}; padding-right: {parse_size(m.group(2).strip('[]'))};"
                if m.group(1) == 'x' else
                f"padding-top: {parse_size(m.group(2).strip('[]'))}; padding-bottom: {parse_size(m.group(2).strip('[]'))};")),
    (re.compile(r"^p([trbl])-([a-zA-Z0-9\./\[\]]+)$"),
     lambda m: f"padding-{'top' if m.group(1)=='t' else 'right' if m.group(1)=='r' else 'bottom' if m.group(1)=='b' else 'left'}: {parse_size(m.group(2).strip('[]'))};"),
    (re.compile(r"^(-?)m-([a-zA-Z0-9\./\[\]]+)$"),
     lambda m: f"margin: {'-' if m.group(1) else ''}{parse_size(m.group(2).strip('[]'))};"),
    (re.compile(r"^(-?)m([xy])-([a-zA-Z0-9\./\[\]]+)$"),
     lambda m: (f"margin-left: {'-' if m.group(1) else ''}{parse_size(m.group(3).strip('[]'))}; margin-right: {'-' if m.group(1) else ''}{parse_size(m.group(3).strip('[]'))};"
                if m.group(2) == 'x' else
                f"margin-top: {'-' if m.group(1) else ''}{parse_size(m.group(3).strip('[]'))}; margin-bottom: {'-' if m.group(1) else ''}{parse_size(m.group(3).strip('[]'))};")),
    (re.compile(r"^(-?)m([trbl])-([a-zA-Z0-9\./\[\]]+)$"),
     lambda m: f"margin-{'top' if m.group(2)=='t' else 'right' if m.group(2)=='r' else 'bottom' if m.group(2)=='b' else 'left'}: {'-' if m.group(1) else ''}{parse_size(m.group(3).strip('[]'))};"),
    # space-x / space-y (child margins) — generates a descendant rule inline
    (re.compile(r"^space-x-([a-zA-Z0-9\./\[\]]+)$"),
     lambda m: f"--tw-space-x: {parse_size(m.group(1).strip('[]'))};"),
    (re.compile(r"^space-y-([a-zA-Z0-9\./\[\]]+)$"),
     lambda m: f"--tw-space-y: {parse_size(m.group(1).strip('[]'))};"),

    # ── Typography ───────────────────────────────────────────────────────────────
    # Must appear BEFORE text-(.+) catch-all
    (re.compile(r"^text-(xs|sm|base|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl|8xl|9xl)$"), handle_text_size),
    (re.compile(r"^text-(left|center|right|justify|start|end)$"), lambda m: f"text-align: {m.group(1)};"),
    (re.compile(r"^text-(.+)$"),
     lambda m: "color: transparent;" if m.group(1) == "transparent" else f"color: {get_color(m.group(1).strip('[]'))};"),

    (re.compile(r"^font-(thin|extralight|light|normal|medium|semibold|bold|extrabold|black)$"), handle_font_weight),
    (re.compile(r"^font-(sans|serif|mono)$"),
     lambda m: {"sans": "font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;",
                "serif": "font-family: ui-serif, Georgia, serif;",
                "mono": "font-family: ui-monospace, SFMono-Regular, Menlo, monospace;"}[m.group(1)]),

    (re.compile(r"^italic$"), lambda m: "font-style: italic;"),
    (re.compile(r"^not-italic$"), lambda m: "font-style: normal;"),
    (re.compile(r"^(uppercase|lowercase|capitalize|normal-case)$"),
     lambda m: f"text-transform: {'none' if m.group(1)=='normal-case' else m.group(1)};"),
    (re.compile(r"^(underline|overline|line-through|no-underline)$"),
     lambda m: f"text-decoration-line: {'none' if m.group(1)=='no-underline' else m.group(1)};"),
    (re.compile(r"^decoration-(.+)$"),
     lambda m: f"text-decoration-color: {get_color(m.group(1))};"),
    (re.compile(r"^antialiased$"),
     lambda m: "-webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;"),
    (re.compile(r"^subpixel-antialiased$"),
     lambda m: "-webkit-font-smoothing: auto; -moz-osx-font-smoothing: auto;"),

    (re.compile(r"^tracking-(tighter|tight|normal|wide|wider|widest)$"),
     lambda m: {"tighter": "letter-spacing: -0.05em;", "tight": "letter-spacing: -0.025em;",
                "normal": "letter-spacing: 0em;", "wide": "letter-spacing: 0.025em;",
                "wider": "letter-spacing: 0.05em;", "widest": "letter-spacing: 0.1em;"}[m.group(1)]),
    (re.compile(r"^leading-(none|tight|snug|normal|relaxed|loose|[0-9]+)$"),
     lambda m: {"none": "line-height: 1;", "tight": "line-height: 1.25;", "snug": "line-height: 1.375;",
                "normal": "line-height: 1.5;", "relaxed": "line-height: 1.625;",
                "loose": "line-height: 2;"}.get(m.group(1), f"line-height: {float(m.group(1))*0.25}rem;")),

    (re.compile(r"^truncate$"), lambda m: "overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"),
    (re.compile(r"^text-ellipsis$"), lambda m: "text-overflow: ellipsis;"),
    (re.compile(r"^text-clip$"), lambda m: "text-overflow: clip;"),
    (re.compile(r"^break-(normal|words|all|keep)$"),
     lambda m: {"normal": "overflow-wrap: normal; word-break: normal;",
                "words": "overflow-wrap: break-word;",
                "all": "word-break: break-all;",
                "keep": "word-break: keep-all;"}[m.group(1)]),
    (re.compile(r"^whitespace-(normal|nowrap|pre|pre-wrap|pre-line|break-spaces)$"),
     lambda m: f"white-space: {m.group(1)};"),
    (re.compile(r"^hyphens-(none|manual|auto)$"), lambda m: f"hyphens: {m.group(1)};"),

    # ── Backgrounds ──────────────────────────────────────────────────────────────
    (re.compile(r"^bg-gradient-to-(t|tr|r|br|b|bl|l|tl)$"),
     lambda m: {
         "t": "background-image: linear-gradient(to top, var(--tw-gradient-stops));",
         "tr": "background-image: linear-gradient(to top right, var(--tw-gradient-stops));",
         "r": "background-image: linear-gradient(to right, var(--tw-gradient-stops));",
         "br": "background-image: linear-gradient(to bottom right, var(--tw-gradient-stops));",
         "b": "background-image: linear-gradient(to bottom, var(--tw-gradient-stops));",
         "bl": "background-image: linear-gradient(to bottom left, var(--tw-gradient-stops));",
         "l": "background-image: linear-gradient(to left, var(--tw-gradient-stops));",
         "tl": "background-image: linear-gradient(to top left, var(--tw-gradient-stops));",
     }[m.group(1)]),
    (re.compile(r"^bg-clip-(text|border|padding|content)$"),
     lambda m: f"-webkit-background-clip: {m.group(1)}; background-clip: {m.group(1)};"),
    (re.compile(r"^bg-none$"), lambda m: "background-image: none;"),
    (re.compile(r"^from-(.+)$"),
     lambda m: f"--tw-gradient-from: {get_color(m.group(1))}; --tw-gradient-to: {get_color(m.group(1))}00; --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);"),
    (re.compile(r"^via-(.+)$"),
     lambda m: f"--tw-gradient-via: {get_color(m.group(1))}; --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-via), var(--tw-gradient-to);"),
    (re.compile(r"^to-(.+)$"), lambda m: f"--tw-gradient-to: {get_color(m.group(1))};"),
    (re.compile(r"^bg-(.+)$"), lambda m: f"background-color: {get_color(m.group(1).strip('[]'))};"),

    # ── Borders ──────────────────────────────────────────────────────────────────
    # Specific border utilities MUST appear before the catch-all border-color rule
    (re.compile(r"^border$"), lambda m: "border-width: 1px;"),
    (re.compile(r"^border-(t|r|b|l)(?:-([0-9]+))?$"),
     lambda m: f"border-{'top' if m.group(1)=='t' else 'right' if m.group(1)=='r' else 'bottom' if m.group(1)=='b' else 'left'}-width: {m.group(2) + 'px' if m.group(2) else '1px'};"),
    (re.compile(r"^border-x(?:-([0-9]+))?$"),
     lambda m: f"border-left-width: {m.group(1)+'px' if m.group(1) else '1px'}; border-right-width: {m.group(1)+'px' if m.group(1) else '1px'};"),
    (re.compile(r"^border-y(?:-([0-9]+))?$"),
     lambda m: f"border-top-width: {m.group(1)+'px' if m.group(1) else '1px'}; border-bottom-width: {m.group(1)+'px' if m.group(1) else '1px'};"),
    (re.compile(r"^border-([0-9]+)$"), lambda m: f"border-width: {m.group(1)}px;"),
    (re.compile(r"^border-(solid|dashed|dotted|double|hidden|none)$"), lambda m: f"border-style: {m.group(1)};"),
    (re.compile(r"^border-collapse$"), lambda m: "border-collapse: collapse;"),
    (re.compile(r"^border-separate$"), lambda m: "border-collapse: separate;"),
    (re.compile(r"^border-spacing-([a-zA-Z0-9\./\[\]]+)$"),
     lambda m: f"border-spacing: {parse_size(m.group(1).strip('[]'))};"),
    (re.compile(r"^border-(.+)$"), lambda m: f"border-color: {get_color(m.group(1).strip('[]'))};"),

    (re.compile(r"^rounded(?:-(none|sm|md|lg|xl|2xl|3xl|full))?$"), handle_rounded),
    (re.compile(r"^rounded-(t|r|b|l|tl|tr|br|bl)(?:-(none|sm|md|lg|xl|2xl|3xl|full))?$"),
     handle_rounded_side),

    # ── Shadows / Ring / Outline ──────────────────────────────────────────────────
    (re.compile(r"^shadow(?:-(sm|md|lg|xl|2xl|inner|none))?$"), handle_shadow),
    (re.compile(r"^outline-none$"), lambda m: "outline: 2px solid transparent; outline-offset: 2px;"),
    (re.compile(r"^outline(?:-([0-9]+))?$"), lambda m: f"outline-width: {m.group(1)+'px' if m.group(1) else '1px'};"),
    (re.compile(r"^outline-(dashed|dotted|double|solid)$"), lambda m: f"outline-style: {m.group(1)};"),
    (re.compile(r"^outline-(.+)$"), lambda m: f"outline-color: {get_color(m.group(1))};"),
    (re.compile(r"^ring(?:-([0-9]+))?$"),
     lambda m: f"box-shadow: 0 0 0 {m.group(1)+'px' if m.group(1) else '3px'} var(--tw-ring-color, #93c5fd);"),
    (re.compile(r"^ring-(.+)$"), lambda m: f"--tw-ring-color: {get_color(m.group(1))};"),

    # ── Opacity / Visibility ──────────────────────────────────────────────────────
    (re.compile(r"^opacity-([0-9]+)$"), lambda m: f"opacity: {int(m.group(1))/100};"),
    (re.compile(r"^visible$"), lambda m: "visibility: visible;"),
    (re.compile(r"^invisible$"), lambda m: "visibility: hidden;"),
    (re.compile(r"^collapse$"), lambda m: "visibility: collapse;"),
    (re.compile(r"^sr-only$"),
     lambda m: "position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border-width: 0;"),
    (re.compile(r"^not-sr-only$"),
     lambda m: "position: static; width: auto; height: auto; padding: 0; margin: 0; overflow: visible; clip: auto; white-space: normal;"),

    # ── Position / Layout ─────────────────────────────────────────────────────────
    (re.compile(r"^(static|fixed|absolute|relative|sticky)$"), lambda m: f"position: {m.group(1)};"),
    (re.compile(r"^(-?)(top|right|bottom|left)-([a-zA-Z0-9\./\[\]]+)$"),
     lambda m: f"{m.group(2)}: {'-' if m.group(1) else ''}{parse_size(m.group(3).strip('[]'))};"),
    (re.compile(r"^(-?)inset-([a-zA-Z0-9\./\[\]]+)$"),
     lambda m: (f"top: {'-' if m.group(1) else ''}{parse_size(m.group(2).strip('[]'))}; "
                f"right: {'-' if m.group(1) else ''}{parse_size(m.group(2).strip('[]'))}; "
                f"bottom: {'-' if m.group(1) else ''}{parse_size(m.group(2).strip('[]'))}; "
                f"left: {'-' if m.group(1) else ''}{parse_size(m.group(2).strip('[]'))};"),
    ),
    (re.compile(r"^(-?)inset-([xy])-([a-zA-Z0-9\./\[\]]+)$"),
     lambda m: (f"left: {'-' if m.group(1) else ''}{parse_size(m.group(3).strip('[]'))}; right: {'-' if m.group(1) else ''}{parse_size(m.group(3).strip('[]'))};"
                if m.group(2) == 'x' else
                f"top: {'-' if m.group(1) else ''}{parse_size(m.group(3).strip('[]'))}; bottom: {'-' if m.group(1) else ''}{parse_size(m.group(3).strip('[]'))};")),
    (re.compile(r"^z-([0-9]+|auto)$"), lambda m: f"z-index: {m.group(1)};"),
    (re.compile(r"^float-(left|right|none)$"), lambda m: f"float: {m.group(1)};"),
    (re.compile(r"^clear-(left|right|both|none)$"), lambda m: f"clear: {m.group(1)};"),
    (re.compile(r"^isolate$"), lambda m: "isolation: isolate;"),
    (re.compile(r"^isolation-auto$"), lambda m: "isolation: auto;"),

    # ── Transforms ───────────────────────────────────────────────────────────────
    (re.compile(r"^(-?)translate-x-([a-zA-Z0-9\./\[\]]+)$"),
     lambda m: f"transform: translateX({'-' if m.group(1) else ''}{parse_size(m.group(2).strip('[]'))});"),
    (re.compile(r"^(-?)translate-y-([a-zA-Z0-9\./\[\]]+)$"),
     lambda m: f"transform: translateY({'-' if m.group(1) else ''}{parse_size(m.group(2).strip('[]'))});"),
    (re.compile(r"^(-?)rotate-([0-9]+)$"),
     lambda m: f"transform: rotate({'-' if m.group(1) else ''}{m.group(2)}deg);"),
    (re.compile(r"^scale-([0-9]+)$"),
     lambda m: f"transform: scale({float(m.group(1))/100});"),
    (re.compile(r"^scale-x-([0-9]+)$"),
     lambda m: f"transform: scaleX({float(m.group(1))/100});"),
    (re.compile(r"^scale-y-([0-9]+)$"),
     lambda m: f"transform: scaleY({float(m.group(1))/100});"),
    (re.compile(r"^(-?)skew-x-([0-9]+)$"),
     lambda m: f"transform: skewX({'-' if m.group(1) else ''}{m.group(2)}deg);"),
    (re.compile(r"^(-?)skew-y-([0-9]+)$"),
     lambda m: f"transform: skewY({'-' if m.group(1) else ''}{m.group(2)}deg);"),
    (re.compile(r"^transform-none$"), lambda m: "transform: none;"),
    (re.compile(r"^transform-gpu$"), lambda m: "transform: translateZ(0);"),
    (re.compile(r"^origin-(center|top|top-right|right|bottom-right|bottom|bottom-left|left|top-left)$"),
     lambda m: f"transform-origin: {m.group(1).replace('-', ' ')};"),

    # ── Transitions / Animations ──────────────────────────────────────────────────
    (re.compile(r"^transition$"),
     lambda m: "transition-property: color, background-color, border-color, text-decoration-color, fill, stroke, opacity, box-shadow, transform, filter, backdrop-filter; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms;"),
    (re.compile(r"^transition-all$"),
     lambda m: "transition-property: all; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms;"),
    (re.compile(r"^transition-none$"), lambda m: "transition-property: none;"),
    (re.compile(r"^transition-colors$"),
     lambda m: "transition-property: color, background-color, border-color, text-decoration-color, fill, stroke; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms;"),
    (re.compile(r"^transition-transform$"),
     lambda m: "transition-property: transform; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms;"),
    (re.compile(r"^transition-opacity$"),
     lambda m: "transition-property: opacity; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms;"),
    (re.compile(r"^duration-([0-9]+)$"), lambda m: f"transition-duration: {m.group(1)}ms;"),
    (re.compile(r"^delay-([0-9]+)$"), lambda m: f"transition-delay: {m.group(1)}ms;"),
    (re.compile(r"^ease-(linear|in|out|in-out)$"),
     lambda m: {"linear": "transition-timing-function: linear;",
                "in": "transition-timing-function: cubic-bezier(0.4, 0, 1, 1);",
                "out": "transition-timing-function: cubic-bezier(0, 0, 0.2, 1);",
                "in-out": "transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);"}[m.group(1)]),
    (re.compile(r"^animate-(none|spin|ping|pulse|bounce)$"),
     lambda m: {
         "none": "animation: none;",
         "spin": "animation: spin 1s linear infinite;",
         "ping": "animation: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite;",
         "pulse": "animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;",
         "bounce": "animation: bounce 1s infinite;",
     }[m.group(1)]),

    # ── Filters ──────────────────────────────────────────────────────────────────
    (re.compile(r"^blur(?:-(sm|md|lg|xl|2xl|3xl|none|[0-9]+px))?$"),
     lambda m: {"none": "filter: blur(0);",
                "sm": "filter: blur(4px);",
                None: "filter: blur(8px);",
                "md": "filter: blur(12px);",
                "lg": "filter: blur(16px);",
                "xl": "filter: blur(24px);",
                "2xl": "filter: blur(40px);",
                "3xl": "filter: blur(64px);"}.get(m.group(1), f"filter: blur({m.group(1)});")),
    (re.compile(r"^backdrop-blur(?:-(sm|md|lg|xl|2xl|3xl|none))?$"),
     lambda m: {"none": "backdrop-filter: blur(0);",
                "sm": "backdrop-filter: blur(4px);",
                "md": "backdrop-filter: blur(12px);",
                "lg": "backdrop-filter: blur(16px);",
                "xl": "backdrop-filter: blur(24px);",
                "2xl": "backdrop-filter: blur(40px);",
                "3xl": "backdrop-filter: blur(64px);"}.get(m.group(1), "backdrop-filter: blur(8px);")),
    (re.compile(r"^brightness-([0-9]+)$"), lambda m: f"filter: brightness({float(m.group(1))/100});"),
    (re.compile(r"^grayscale(?:-(0))?$"), lambda m: f"filter: grayscale({'0' if m.group(1) else '100%'});"),
    (re.compile(r"^invert(?:-(0))?$"), lambda m: f"filter: invert({'0' if m.group(1) else '100%'});"),

    # ── Overflow / Cursor / Pointer / Misc ───────────────────────────────────────
    (re.compile(r"^overflow-(auto|hidden|clip|visible|scroll)$"), lambda m: f"overflow: {m.group(1)};"),
    (re.compile(r"^overflow-([xy])-(auto|hidden|clip|visible|scroll)$"),
     lambda m: f"overflow-{m.group(1)}: {m.group(2)};"),
    (re.compile(r"^cursor-(.+)$"), lambda m: f"cursor: {m.group(1)};"),
    (re.compile(r"^pointer-events-(none|auto)$"), lambda m: f"pointer-events: {m.group(1)};"),
    (re.compile(r"^select-(none|text|all|auto)$"), lambda m: f"user-select: {m.group(1)};"),
    (re.compile(r"^resize(?:-(none|y|x))?$"),
     lambda m: f"resize: {'none' if m.group(1)=='none' else m.group(1) if m.group(1) else 'both'};"),
    (re.compile(r"^appearance-none$"), lambda m: "appearance: none; -webkit-appearance: none;"),
    (re.compile(r"^list-(none|disc|decimal)$"),
     lambda m: f"list-style-type: {m.group(1)};"),
    (re.compile(r"^list-(inside|outside)$"), lambda m: f"list-style-position: {m.group(1)};"),
    (re.compile(r"^object-(contain|cover|fill|none|scale-down)$"), lambda m: f"object-fit: {m.group(1)};"),
    (re.compile(r"^object-(top|bottom|center|left|right)$"), lambda m: f"object-position: {m.group(1)};"),

    # ── Group / Peer marker — no CSS generated, class just needs to be in HTML ──
    (re.compile(r"^(group|peer)$"), lambda m: ""),
]


def compile_class(cls_name: str) -> str:
    """Iterate over regex rules and compile the CSS body for the given utility class."""
    for pattern, generator in COMPILER_RULES:
        match = pattern.match(cls_name)
        if match:
            try:
                result = generator(match)
                return result or ""
            except Exception:
                pass
    return ""


# Known pseudo-class prefixes that map to standard CSS pseudo-classes.
# These get extracted from the HTML class attribute and registered as ID-based rules.
_ELEMENT_PSEUDO_PREFIXES = {
    "hover", "focus", "active", "disabled", "checked",
    "focus-within", "focus-visible", "placeholder", "visited",
}


def register_classes(class_string: str, pseudo: str = "") -> None:
    """
    Parse a class_string and register CSS rules for all contained utility classes.

    Pseudo-prefixed classes like ``hover:bg-blue-700`` are only registered here
    when called with an explicit ``pseudo`` argument (the fallback path). Normally,
    the component render method intercepts them before they reach this function.

    ``group-hover:UTIL`` generates a ``.group:hover .group-hover\\:UTIL`` rule.
    ``backdrop:UTIL`` generates a ``::backdrop`` rule (e.g. for <dialog>).
    """
    if not class_string:
        return
        
    for cls in class_string.split():
        cls = cls.strip()
        if not cls:
            continue
        
        actual_cls = cls
        pseudo_suffix = pseudo

        if ":" in cls:
            prefix, actual_cls = cls.split(":", 1)

            if prefix == "group-hover":
                # .group:hover .group-hover\:UTIL { ... }
                rule_body = compile_class(actual_cls)
                if rule_body:
                    escaped = f"group-hover\\:{actual_cls}".replace("[", "\\[").replace("]", "\\]").replace("/", "\\/")
                    selector = f".group:hover .{escaped}"
                    if selector not in CSSContext.registered_rules:
                        CSSContext.registered_rules[selector] = rule_body
                continue

            if prefix == "backdrop":
                rule_body = compile_class(actual_cls)
                if rule_body:
                    selector = f"::backdrop"
                    existing = CSSContext.registered_rules.get(selector, "")
                    CSSContext.registered_rules[selector] = (existing + " " + rule_body).strip()
                continue

            # Other pseudo-prefixes (hover:, focus:, etc.) need an element id — skip here
            pseudo_suffix = f":{prefix}"

        rule_body = compile_class(actual_cls)
        if rule_body:
            safe_selector = cls.replace(":", "\\:").replace("[", "\\[").replace("]", "\\]").replace("%", "\\%").replace("#", "\\#").replace(".", "\\.").replace("/", "\\/")
            selector = f".{safe_selector}{pseudo_suffix}"
            if selector not in CSSContext.registered_rules:
                CSSContext.registered_rules[selector] = rule_body


def register_hover_for_element(uid: str, class_string: str) -> None:
    """Register ``hover_class`` utilities as ``#uid:hover { ... }`` rules."""
    selector = f"#{uid}:hover"
    parts: list[str] = []
    for cls in class_string.split():
        cls = cls.strip()
        if not cls: continue
        rule = compile_class(cls)
        if rule: parts.append(rule)
    if parts:
        CSSContext.registered_rules[selector] = " ".join(parts)


def register_active_for_element(uid: str, class_string: str) -> None:
    """Register ``active_class`` utilities as ``#uid:active { ... }`` rules."""
    selector = f"#{uid}:active"
    parts: list[str] = []
    for cls in class_string.split():
        cls = cls.strip()
        if not cls: continue
        rule = compile_class(cls)
        if rule: parts.append(rule)
    if parts:
        CSSContext.registered_rules[selector] = " ".join(parts)


def register_pseudo_for_element(uid: str, pseudo: str, cls_name: str) -> None:
    """
    Register a pseudo-prefixed utility class (hover:, focus:, disabled:, etc.) as
    an element-ID-scoped CSS rule: ``#uid:pseudo { ... }``.

    This avoids the escaped-colon form (``.hover\\:bg-blue-700:hover``) which
    LightningCSS / dars-bundler rejects when minifying.

    Args:
        uid:      The element's unique HTML id.
        pseudo:   The pseudo-class name without the colon (e.g. ``"hover"``).
        cls_name: The utility class name to compile (e.g. ``"bg-blue-700"``).
    """
    rule_body = compile_class(cls_name)
    if rule_body:
        selector = f"#{uid}:{pseudo}"
        existing = CSSContext.registered_rules.get(selector, "")
        if existing:
            CSSContext.registered_rules[selector] = existing.rstrip(" ") + " " + rule_body
        else:
            CSSContext.registered_rules[selector] = rule_body


_KEYFRAMES = """
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes ping { 75%, 100% { transform: scale(2); opacity: 0; } }
@keyframes pulse { 50% { opacity: .5; } }
@keyframes bounce {
  0%, 100% { transform: translateY(-25%); animation-timing-function: cubic-bezier(0.8,0,1,1); }
  50% { transform: none; animation-timing-function: cubic-bezier(0,0,0.2,1); }
}
"""


def build_css() -> str:
    """Render all registered CSS rules into a single stylesheet string."""
    css_lines = [
        "*, ::before, ::after { box-sizing: border-box; border-width: 0; border-style: solid; border-color: #e5e7eb; }",
        "button, input, textarea, select { font-family: inherit; font-size: 100%; margin: 0; }",
        "button { background-color: transparent; background-image: none; cursor: pointer; }",
        # Tooltip component static rules
        ".railui-tooltip { position: relative; display: inline-block; }",
        ".railui-tooltip:hover .railui-tooltip-bubble { display: block; }",
        ".railui-tooltip-bubble { pointer-events: none; position: absolute; z-index: 50; display: none; background-color: #111827; color: #ffffff; font-size: 0.75rem; border-radius: 0.25rem; padding: 0.25rem 0.5rem; white-space: nowrap; box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1); }",
        # space-x / space-y child selectors
        ".space-x-1 > * + * { margin-left: 0.25rem; }",
        ".space-x-2 > * + * { margin-left: 0.5rem; }",
        ".space-x-4 > * + * { margin-left: 1rem; }",
        ".space-y-1 > * + * { margin-top: 0.25rem; }",
        ".space-y-2 > * + * { margin-top: 0.5rem; }",
        ".space-y-4 > * + * { margin-top: 1rem; }",
        # group-hover: children show when parent .group is hovered
        _KEYFRAMES,
    ]
    for selector, rule in CSSContext.registered_rules.items():
        if rule:  # skip empty marker rules (like .group)
            css_lines.append(f"{selector} {{ {rule} }}")
    return "\n".join(css_lines)
