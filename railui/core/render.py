"""
Rendering and compilation engine for RailUI.

This module handles taking a Component tree and a populated SignalContext,
and converting them into a full HTML string and embedded JavaScript bundle.
"""

from railui.components.base import Component
import os
import json
import hashlib
from typing import List
from .context import SignalContext, RenderContext
from .css import CSSContext, build_css

def build_js() -> str:
    """
    Build the JavaScript bundle by concatenating all runtime files from railui/js/
    and appending the user's compiled signals and effects.
    
    Returns:
        str: The raw JavaScript string to be injected into the HTML.
    """
    js = ""
    
    # Dynamically read all runtime .js files
    js_dir = os.path.join(os.path.dirname(__file__), "..", "js")
    if os.path.exists(js_dir):
        for filename in os.listdir(js_dir):
            if filename.endswith(".js"):
                with open(os.path.join(js_dir, filename), "r", encoding="utf-8") as f:
                    js += f.read() + "\n"
    
    # Instantiate user signals
    for sig in SignalContext.signals:
        sid = sig["id"]
        initial_val = json.dumps(sig["initial"])
        js += f"createSignal('{sid}', {initial_val});\n"
        
    # Register user effects
    for effect in RenderContext.effects:
        js += f"$effects.push(() => {{ {effect} }});\n"
    
    # Register user-declared createEffect() calls (declared before compile_app)
    for effect in RenderContext.user_effects:
        js += f"$effects.push(() => {{ {effect} }});\n"
        
    # Register init scripts (event listeners)
    for script in RenderContext.init_scripts:
        js += f"{script}\n"
        
    js += "runEffects();\n"
    return js

def _write_assets(output_dir: str, app_name: str, html_content: str, js_content: str, css_content: str) -> None:
    import shutil
    
    if os.path.exists(output_dir):
        for f in os.listdir(output_dir):
            if f.startswith(f"{app_name}.") and (f.endswith(".js") or f.endswith(".css")):
                try:
                    os.remove(os.path.join(output_dir, f))
                except Exception:
                    pass
    else:
        os.makedirs(output_dir)
    
    # Create hashes
    js_hash = hashlib.md5(js_content.encode('utf-8')).hexdigest()[:8]
    css_hash = hashlib.md5(css_content.encode('utf-8')).hexdigest()[:8]
    
    js_filename = f"{app_name}.{js_hash}.js"
    css_filename = f"{app_name}.{css_hash}.css"
    
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RailUI App</title>
    <link rel="stylesheet" href="{css_filename}">
</head>
<body>
    {html_content}
    <script src="{js_filename}"></script>
</body>
</html>
"""
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(full_html)
        
    with open(os.path.join(output_dir, js_filename), "w", encoding="utf-8") as f:
        f.write(js_content)
        
    with open(os.path.join(output_dir, css_filename), "w", encoding="utf-8") as f:
        f.write(css_content)

def compile_app(page_component: "Component", output_dir: str = "test", app_name: str = "app") -> None:
    """
    Compile the given root component into an index.html file, along with hashed .js and .css files.
    """
    # Reset contexts for this render pass
    RenderContext.reset()
    CSSContext.reset()
    
    # Render component tree, populates RenderContext.effects and CSSContext.registered_rules
    html_content = page_component.render()
    
    # Build external assets
    js_content = build_js()
    css_content = build_css()
    
    # Write to disk
    _write_assets(output_dir, app_name, html_content, js_content, css_content)
        
    print(f"Build complete. Output written to {output_dir}/")
