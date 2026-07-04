"""
App orchestration for RailUI.
Manages global configuration, dependencies, and compilation of the SPA router.
"""

from typing import List, Optional, Dict, Callable
import os
import shutil
import uuid

from ..components.base import Component
from .context import RenderContext
from .css import build_css, CSSContext


class App:
    """The root Application class."""
    
    def __init__(self, title: str = "RailUI App", trailing_slash: bool = False):
        self.title = title
        self.trailing_slash = trailing_slash
        self.external_css: List[str] = []
        self.external_js: List[str] = []
        self.raw_scripts: List[str] = []
        
        # path -> component_factory
        self.routes: Dict[str, Callable[[], Component]] = {}
        
        # Global fallback components
        self.not_found_component: Optional[Callable[[], Component]] = None
        self.forbidden_component: Optional[Callable[[], Component]] = None

    def add_style(self, url: str) -> None:
        """Inject an external CSS stylesheet globally (e.g. from a CDN)."""
        self.external_css.append(url)

    def add_script(self, url: str) -> None:
        """Inject an external JS script globally."""
        self.external_js.append(url)

    def add_raw_script(self, js_code: str) -> None:
        """Inject an inline JS snippet into the global <head>."""
        self.raw_scripts.append(js_code)

    def set_not_found(self, component_factory: Callable[[], Component]) -> None:
        self.not_found_component = component_factory

    def route(self, path: str):
        """Decorator to register a function as a route."""
        def decorator(func: Callable[[], Component]):
            self.routes[path] = func
            return func
        return decorator

    def discover_pages(self, directory: str = "pages") -> None:
        """
        Scans a directory for .py files and automatically registers them as routes.
        e.g., pages/index.py -> /
        pages/dashboard.py -> /dashboard
        pages/users/[id].py -> /users/:id (dynamic routing marker)
        
        Requires each file to export a `page()` function returning a Component.
        """
        import importlib.util
        
        if not os.path.exists(directory):
            print(f"Warning: Pages directory '{directory}' not found.")
            return

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py") and not file.startswith("_"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, directory)
                    
                    route_path = rel_path[:-3].replace(os.sep, "/")
                    
                    if route_path == "index":
                        route_path = "/"
                    elif route_path.endswith("/index"):
                        route_path = "/" + route_path[:-6]
                    else:
                        route_path = "/" + route_path
                        
                    # Handle Next.js style dynamic segments [id] -> :id
                    route_path = route_path.replace("[", ":").replace("]", "")
                    
                    # Load the module dynamically
                    spec = importlib.util.spec_from_file_location("dynamic_page", full_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        if hasattr(module, "page"):
                            self.routes[route_path] = module.page
                        else:
                            print(f"Warning: {full_path} has no 'page()' function exported.")

    def build(self, out_dir: str = "dist") -> None:
        """Compile the entire application into an SPA bundle."""
        from ..router.builder import build_router_js
        
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        # Clean old assets safely
        for file in os.listdir(out_dir):
            if file.endswith(".js") or file.endswith(".css"):
                try:
                    os.remove(os.path.join(out_dir, file))
                except OSError:
                    pass

        # 1. Compile each route to HTML and Effects
        compiled_routes = {}
        CSSContext.reset()
        
        for path, factory in self.routes.items():
            RenderContext.reset()
            root_comp = factory()
            html = root_comp.render()
            
            compiled_routes[path] = {
                "html": html,
                "effects": list(RenderContext.effects),
                "init": list(RenderContext.init_scripts),
                "destroy": list(RenderContext.destroy_scripts),
                "head_styles": list(RenderContext.head_styles),
                "head_scripts": list(RenderContext.head_scripts),
            }

        not_found_data = None
        if self.not_found_component:
            RenderContext.reset()
            html = self.not_found_component().render()
            not_found_data = {
                "html": html,
                "effects": list(RenderContext.effects),
                "init": list(RenderContext.init_scripts),
                "destroy": list(RenderContext.destroy_scripts),
                "head_styles": list(RenderContext.head_styles),
                "head_scripts": list(RenderContext.head_scripts),
            }

        # 2. Build Router JS Bundle
        build_hash = uuid.uuid4().hex[:8]
        js_filename = f"app.{build_hash}.js"
        css_filename = f"app.{build_hash}.css"
        
        runtime_path = os.path.join(os.path.dirname(__file__), "..", "js", "runtime.js")
        control_flow_path = os.path.join(os.path.dirname(__file__), "..", "js", "control_flow.js")
        
        with open(runtime_path, "r", encoding="utf-8") as f:
            runtime_js = f.read()
        with open(control_flow_path, "r", encoding="utf-8") as f:
            control_flow_js = f.read()
            
        router_js = build_router_js(compiled_routes, not_found_data, self.trailing_slash)
        
        global_init = "\n".join(RenderContext.user_init_scripts)
        global_effects = "\n".join(RenderContext.user_effects)

        final_js = f"""
{runtime_js}
{control_flow_js}

// -- Global State Initialization --
{global_init}

// -- Global Effects --
$effects.push(() => {{
{global_effects}
}});

// -- SPA Router --
{router_js}
        """

        with open(os.path.join(out_dir, js_filename), "w", encoding="utf-8") as f:
            f.write(final_js)
            
        final_css = build_css()
        with open(os.path.join(out_dir, css_filename), "w", encoding="utf-8") as f:
            f.write(final_css)

        css_links = "\n    ".join(f'<link rel="stylesheet" href="{url}">' for url in self.external_css)
        js_links = "\n    ".join(f'<script src="{url}"></script>' for url in self.external_js)
        raw_script_tags = "\n    ".join(f'<script>{code}</script>' for code in self.raw_scripts)

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    {css_links}
    <link rel="stylesheet" href="{css_filename}">
    {raw_script_tags}
</head>
<body class="bg-gray-50 min-h-screen text-gray-900 font-sans">
    <div id="railui-root"></div>
    {js_links}
    <script src="{js_filename}"></script>
</body>
</html>
"""
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_template)
            
        print(f"Build complete. Output written to {out_dir}/")
