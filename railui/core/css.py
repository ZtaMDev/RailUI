"""
Lightweight CSS Compiler Engine.

This module parses Tailwind-like utility strings and generates standard CSS rules.
It allows RailUI to function without a heavy external CSS framework dependency.
"""

import re
from typing import Set, Dict

class CSSContext:
    """Holds the registered CSS classes and rules for the current compilation pass."""
    registered_rules: Dict[str, str] = {}
    
    @classmethod
    def reset(cls) -> None:
        cls.registered_rules = {}

def parse_size(value: str) -> str:
    """Convert Tailwind size units (usually 0.25rem per unit) to standard CSS values."""
    if value.endswith("px"): return value
    if value == "auto": return "auto"
    if value == "full": return "100%"
    if value == "screen": return "100vh"
    if value.isdigit(): return f"{int(value) * 0.25}rem"
    return value

def extract_color(value: str) -> str:
    """A simplistic color map for the prototype."""
    colors = {
        "white": "#ffffff", "black": "#000000", "transparent": "transparent",
        "gray-50": "#f9fafb", "gray-100": "#f3f4f6", "gray-200": "#e5e7eb",
        "gray-300": "#d1d5db", "gray-500": "#6b7280", "gray-800": "#1f2937",
        "red-50": "#fef2f2", "red-500": "#ef4444", "red-600": "#dc2626",
        "blue-400": "#60a5fa", "blue-500": "#3b82f6", "blue-600": "#2563eb",
        "green-500": "#22c55e", "green-600": "#16a34a",
        "purple-500": "#a855f7", "purple-600": "#9333ea"
    }
    return colors.get(value, value)

def compile_class(cls_name: str) -> str:
    """
    Given a single tailwind-like class string (e.g. 'px-4' or 'mb-[20px]'), 
    return the corresponding CSS rule body.
    """
    if cls_name in ["flex", "block", "inline-block", "grid", "hidden"]:
        return f"display: {cls_name};"
    if cls_name == "transition":
        return "transition-property: color, background-color, border-color, text-decoration-color, fill, stroke, opacity, box-shadow, transform, filter, backdrop-filter; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms;"
    
    # Handle arbitrary values like mb-[20px]
    match = re.match(r"^(.*?)-\[(.*)\]$", cls_name)
    if match:
        prefix, arb_val = match.groups()
        arb_map = {
            "p": "padding", "pt": "padding-top", "pb": "padding-bottom", "pl": "padding-left", "pr": "padding-right",
            "m": "margin", "mt": "margin-top", "mb": "margin-bottom", "ml": "margin-left", "mr": "margin-right",
            "bg": "background-color", "text": "color", "border": "border-color", "rounded": "border-radius",
            "w": "width", "h": "height", "min-w": "min-width", "min-h": "min-height", 
            "max-w": "max-width", "max-h": "max-height", "top": "top", "bottom": "bottom", 
            "left": "left", "right": "right", "gap": "gap", "z": "z-index", "fs": "font-size"
        }
        if prefix in arb_map:
            return f"{arb_map[prefix]}: {arb_val};"
        if prefix == "px": return f"padding-left: {arb_val}; padding-right: {arb_val};"
        if prefix == "py": return f"padding-top: {arb_val}; padding-bottom: {arb_val};"
        if prefix == "mx": return f"margin-left: {arb_val}; margin-right: {arb_val};"
        if prefix == "my": return f"margin-top: {arb_val}; margin-bottom: {arb_val};"

    if cls_name.startswith("p-"): return f"padding: {parse_size(cls_name[2:])};"
    if cls_name.startswith("px-"): val = parse_size(cls_name[3:]); return f"padding-left: {val}; padding-right: {val};"
    if cls_name.startswith("py-"): val = parse_size(cls_name[3:]); return f"padding-top: {val}; padding-bottom: {val};"
    
    if cls_name.startswith("m-"): return f"margin: {parse_size(cls_name[2:])};"
    if cls_name.startswith("mx-"):
        if cls_name[3:] == "auto": return "margin-left: auto; margin-right: auto;"
        val = parse_size(cls_name[3:]); return f"margin-left: {val}; margin-right: {val};"
    if cls_name.startswith("my-"): val = parse_size(cls_name[3:]); return f"margin-top: {val}; margin-bottom: {val};"
    if cls_name.startswith("mb-"): return f"margin-bottom: {parse_size(cls_name[3:])};"
    if cls_name.startswith("mt-"): return f"margin-top: {parse_size(cls_name[3:])};"
    if cls_name.startswith("mr-"): return f"margin-right: {parse_size(cls_name[3:])};"
    if cls_name.startswith("ml-"): return f"margin-left: {parse_size(cls_name[3:])};"
    
    if cls_name.startswith("w-"): return f"width: {parse_size(cls_name[2:])};"
    if cls_name.startswith("h-"): return f"height: {parse_size(cls_name[2:])};"
    if cls_name.startswith("max-w-"): 
        if cls_name == "max-w-2xl": return "max-width: 42rem;"
        return f"max-width: {parse_size(cls_name[6:])};"

    # Typography
    if cls_name.startswith("text-"):
        part = cls_name[5:]
        if part in ["xs", "sm", "base", "lg", "xl", "2xl", "3xl", "4xl"]:
            sizes = {"xs": "0.75rem", "sm": "0.875rem", "base": "1rem", "lg": "1.125rem", "xl": "1.25rem", "2xl": "1.5rem", "3xl": "1.875rem", "4xl": "2.25rem"}
            return f"font-size: {sizes[part]};"
        if part in ["center", "left", "right", "justify"]:
            return f"text-align: {part};"
        if part == "transparent":
            return "color: transparent;"
        return f"color: {extract_color(part)};"
        
    if cls_name.startswith("bg-"):
        part = cls_name[3:]
        if part.startswith("gradient"):
            return "background-image: linear-gradient(to right, var(--tw-gradient-stops));"
        if part == "clip-text":
            return "-webkit-background-clip: text; background-clip: text;"
        return f"background-color: {extract_color(part)};"
        
    if cls_name.startswith("from-"):
        return f"--tw-gradient-from: {extract_color(cls_name[5:])} var(--tw-gradient-from-position); --tw-gradient-to: {extract_color(cls_name[5:])}00 var(--tw-gradient-to-position); --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);"
    if cls_name.startswith("to-"):
        return f"--tw-gradient-to: {extract_color(cls_name[3:])} var(--tw-gradient-to-position);"

    if cls_name.startswith("font-"):
        part = cls_name[5:]
        weights = {"thin": 100, "light": 300, "normal": 400, "medium": 500, "semibold": 600, "bold": 700, "extrabold": 800}
        if part in weights: return f"font-weight: {weights[part]};"
        if part == "sans": return "font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;"
        
    if cls_name.startswith("rounded"):
        if cls_name == "rounded": return "border-radius: 0.25rem;"
        if cls_name == "rounded-lg": return "border-radius: 0.5rem;"
        if cls_name == "rounded-xl": return "border-radius: 0.75rem;"
        if cls_name == "rounded-full": return "border-radius: 9999px;"
        
    if cls_name == "border": return "border-width: 1px;"
    if cls_name.startswith("border-"):
        return f"border-color: {extract_color(cls_name[7:])};"
        
    if cls_name == "shadow": return "box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);"
    if cls_name == "shadow-sm": return "box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);"
    
    if cls_name == "min-h-screen": return "min-height: 100vh;"
    
    if cls_name == "focus:outline-none": return "outline: 2px solid transparent; outline-offset: 2px;"
    
    return ""

def register_classes(class_string: str, pseudo: str = "") -> None:
    """Parse a space-separated class string and register CSS rules."""
    if not class_string:
        return
        
    for cls in class_string.split():
        cls = cls.strip()
        if not cls: continue
        
        # Handle Focus/Hover prefixes written natively in the string
        actual_cls = cls
        pseudo_suffix = pseudo
        if ":" in cls:
            parts = cls.split(":", 1)
            pseudo_suffix = f":{parts[0]}"
            actual_cls = parts[1]
            
        rule_body = compile_class(actual_cls)
        if rule_body:
            # Escape special characters for the CSS selector
            safe_selector = cls.replace(":", "\\:").replace("[", "\\[").replace("]", "\\]").replace("%", "\\%").replace("#", "\\#").replace(".", "\\.").replace("/", "\\/")
            selector = f".{safe_selector}{pseudo_suffix}"
            if selector not in CSSContext.registered_rules:
                CSSContext.registered_rules[selector] = rule_body

def build_css() -> str:
    """Generate the final CSS stylesheet string from registered rules."""
    css_lines = []
    # Tailwind base reset
    css_lines.append("*, ::before, ::after { box-sizing: border-box; border-width: 0; border-style: solid; border-color: #e5e7eb; }")
    css_lines.append("button, input { font-family: inherit; font-size: 100%; margin: 0; }")
    css_lines.append("button { background-color: transparent; background-image: none; cursor: pointer; }")
    
    for selector, rule in CSSContext.registered_rules.items():
        css_lines.append(f"{selector} {{ {rule} }}")
        
    return "\n".join(css_lines)
