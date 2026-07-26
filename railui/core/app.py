"""
App orchestration for RailUI.

Manages global application configuration, external asset injection,
route registration, and compilation of the SPA router bundle.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional
import os
import shutil
import uuid

from ..components.base import Component
from .context import RenderContext
from .css import build_css, CSSContext


class App:
    """
    The root application object that drives a RailUI project.

    Every RailUI application starts with one ``App`` instance.  It is
    responsible for:

    - Holding global configuration (title, external assets, raw scripts).
    - Registering routes — either via the :meth:`route` decorator or via
      :meth:`discover_pages` for file-based routing.
    - Compiling the entire application into a static
      ``dist/`` bundle (:meth:`build`).

    Args:
        title: The ``<title>`` of the generated ``index.html``.
            Shown in the browser tab bar. Defaults to ``"RailUI App"``.
        trailing_slash: When ``True``, the SPA router treats
            ``/about`` and ``/about/`` as separate routes.  When ``False``
            (the default), trailing slashes are stripped before matching.

    Example — minimal in-place routing::

        from railui.all import *

        app = App(title="My App")

        @app.route("/")
        def home() -> Component:
            return Page(Text("Hello from RailUI!"))

        @app.route("/about")
        def about() -> Component:
            return Page(Text("About page"))

        if __name__ == "__main__":
            app.build(out_dir="dist")

    Example — file-based routing::

        from railui.all import *

        app = App(title="My App")
        app.discover_pages("pages")     # scans pages/*.py

        if __name__ == "__main__":
            app.build(out_dir="dist")
    """

    def __init__(self, title: str = "RailUI App", trailing_slash: bool = False) -> None:
        self.title = title
        self.trailing_slash = trailing_slash

        # External asset lists
        self.external_css: List[str] = []
        self.external_js: List[str] = []
        self.raw_scripts: List[str] = []

        # Route registry  — path -> component_factory
        self.routes: Dict[str, Callable[[], Component]] = {}

        # Optional global fallback pages
        self.not_found_component: Optional[Callable[[], Component]] = None
        self.forbidden_component: Optional[Callable[[], Component]] = None

    # ------------------------------------------------------------------
    # Asset injection
    # ------------------------------------------------------------------

    def add_style(self, url: str) -> None:
        """
        Inject an external CSS stylesheet as a global ``<link>`` tag.

        The link is added to the generated ``index.html``'s ``<head>`` and
        is present on every route.  Use this for CDN-hosted CSS like Tailwind
        CDN, Google Fonts, or third-party component libraries.

        Args:
            url: Fully-qualified URL or root-relative path to the stylesheet.

        Example::

            app.add_style("https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap")
            app.add_style("https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css")
        """
        self.external_css.append(url)

    def add_script(self, url: str) -> None:
        """
        Inject an external JavaScript file as a global ``<script src>`` tag.

        The script tag is placed just before the application bundle in the
        generated ``index.html``, so it loads on every route.

        Args:
            url: Fully-qualified URL or root-relative path to the script.

        Example::

            app.add_script("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js")
        """
        self.external_js.append(url)

    def add_raw_script(self, js_code: str) -> None:
        """
        Inject a raw inline JavaScript snippet into the ``<head>`` of the
        generated HTML, wrapped in a ``<script>`` tag.

        Useful for initialising third-party SDKs, setting global constants,
        or injecting analytics snippets that must run before the SPA boots.

        Args:
            js_code: Any valid JavaScript string.

        Example::

            app.add_raw_script(\"\"\"
                window.__APP_VERSION__ = '1.0.0';
                window.__ENVIRONMENT__ = 'production';
            \"\"\")
        """
        self.raw_scripts.append(js_code)

    # ------------------------------------------------------------------
    # Route registration
    # ------------------------------------------------------------------

    def route(self, path: str) -> Callable:
        """
        Decorator that registers a function as the handler for a URL route.

        The decorated function must accept **no arguments** and return a
        :class:`~railui.components.base.Component`.

        Args:
            path: URL path to register.  Must start with ``"/"``.
                Supports dynamic segments using the ``:param`` syntax
                (e.g. ``"/users/:id"``).

        Returns:
            The decorator that wraps the component factory function unchanged
            (allowing the function to also be called directly in Python).

        Example::

            @app.route("/")
            def home() -> Component:
                return Page(H1("Home"))

            @app.route("/products/:id")
            def product_detail() -> Component:
                # Access :id via window.location or a signal in the real browser
                return Page(Text("Product detail page"))

            @app.route("/dashboard")
            def dashboard() -> Component:
                visits, _ = createSignal(0)
                return Page(Text(visits()))
        """
        def decorator(func: Callable[[], Component]) -> Callable[[], Component]:
            self.routes[path] = func
            return func
        return decorator

    def set_not_found(self, component_factory: Callable[[], Component]) -> None:
        """
        Register a custom **404 Not Found** page.

        The factory is called when the SPA router cannot match the current
        URL to any registered route.

        Args:
            component_factory: A zero-argument callable that returns a
                :class:`~railui.components.base.Component`.

        Example::

            @app.set_not_found
            def not_found():
                return Page(
                    H1("404 — Page Not Found"),
                    Link("Go home", href="/"),
                )

            # Or pass a function directly
            def my_404():
                return Page(Text("Oops!"))

            app.set_not_found(my_404)
        """
        self.not_found_component = component_factory

    def set_forbidden(self, component_factory: Callable[[], Component]) -> None:
        """
        Register a custom **403 Forbidden** page.

        Args:
            component_factory: A zero-argument callable that returns a
                :class:`~railui.components.base.Component`.

        Example::

            def forbidden_page():
                return Page(
                    H1("403 — Access Denied"),
                    Paragraph("You don't have permission to view this page."),
                )

            app.set_forbidden(forbidden_page)
        """
        self.forbidden_component = component_factory

    # ------------------------------------------------------------------
    # File-based routing
    # ------------------------------------------------------------------

    def discover_pages(self, directory: str = "pages") -> None:
        """
        Scan a directory for ``.py`` files and register them as routes.

        Each ``.py`` file must export a ``page()`` function that returns a
        :class:`~railui.components.base.Component`.  Files whose names start
        with an underscore (``_``) are skipped.

        **File → Route mapping conventions:**

        ==========================================  ============================
        File path (relative to ``directory``)       Route
        ==========================================  ============================
        ``index.py``                                ``/``
        ``about.py``                                ``/about``
        ``blog/index.py``                           ``/blog``
        ``blog/post.py``                            ``/blog/post``
        ``users/[id].py``                           ``/users/:id``
        ``products/[category]/[id].py``             ``/products/:category/:id``
        ==========================================  ============================

        This method also inserts the **parent directory of the pages folder**
        into ``sys.path`` so that sibling modules (e.g. ``layout.py``,
        ``store.py``) are importable from within page files without any manual
        path manipulation.

        Args:
            directory: Path to the pages directory, relative to the current
                working directory or absolute.  Defaults to ``"pages"``.

        Example::

            app.discover_pages("pages")          # ./pages/
            app.discover_pages("/srv/app/views") # absolute path

        .. note::

            Dynamic route segments use the Next.js / file-system router
            convention ``[param]`` in the filename which becomes ``:param``
            in the URL pattern.  For example ``pages/users/[id].py`` →
            route ``/users/:id``.
        """
        import sys
        import importlib.util

        if not os.path.exists(directory):
            print(f"[railui] Warning: Pages directory '{directory}' not found.")
            return

        # Make the app root (parent of `pages/`) importable so sibling modules
        # like `layout.py` resolve correctly from any working directory.
        app_root = os.path.abspath(os.path.dirname(directory))
        if app_root not in sys.path:
            sys.path.insert(0, app_root)

        for root, dirs, files in os.walk(directory):
            # Sort to ensure deterministic registration order
            dirs.sort()
            for file in sorted(files):
                if not file.endswith(".py") or file.startswith("_"):
                    continue

                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, directory)

                # Build the URL route from the file path
                route_path = rel_path[:-3].replace(os.sep, "/")
                if route_path == "index":
                    route_path = "/"
                elif route_path.endswith("/index"):
                    route_path = "/" + route_path[:-6]
                else:
                    route_path = "/" + route_path

                # Convert Next.js-style [param] segments to :param
                route_path = route_path.replace("[", ":").replace("]", "")

                spec = importlib.util.spec_from_file_location("_railui_page", full_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    if hasattr(module, "page"):
                        self.routes[route_path] = module.page
                    else:
                        print(f"[railui] Warning: {full_path} has no 'page()' function — skipping.")

    # ------------------------------------------------------------------
    # Build / compile
    # ------------------------------------------------------------------

    def build(self, out_dir: str = "dist") -> None:
        """
        Compile all registered routes and generate a static SPA bundle.

        This is the heart of RailUI's compilation model.  It:

        1. Renders every registered route's component tree to HTML strings
           and collects the reactive JavaScript effects.
        2. Serialises all routes into the SPA router JavaScript bundle.
        3. Concatenates the runtime, control-flow helpers, and router into
           a single hashed ``app.<hash>.js`` file.
        4. Builds the CSS bundle (Tailwind-like utility classes used in the
           app) into a hashed ``app.<hash>.css`` file.
        5. Writes a single ``index.html`` entry point that references both
           bundles.

        The output directory is created if it does not exist.  Old ``.js``
        and ``.css`` files in the output directory are removed before writing
        new ones, so stale assets never accumulate.

        Args:
            out_dir: Path to the output directory.  Defaults to ``"dist"``.
                Can be overridden at runtime by setting the
                ``RAILUI_OUTDIR`` environment variable (used by the dev server).

        .. note::

            After calling ``build``, the ``out_dir`` will contain:

            - ``index.html`` — the SPA shell.
            - ``app.<hash>.js`` — the entire compiled application bundle.
            - ``app.<hash>.css`` — the generated CSS utility bundle.

            Any directories listed in ``public_dirs`` inside
            ``railui.config.json`` (or the default ``public/`` folder) are
            **copied as-is** into ``out_dir`` by the dev/build CLI, not by
            this method.  Binary files (images, fonts, videos) should live
            there.

        Example::

            if __name__ == "__main__":
                app.build(out_dir="dist")
        """
        from ..router.builder import build_router_js

        # Allow CLI config to override out_dir via environment variable
        env_outdir = os.environ.get("RAILUI_OUTDIR")
        if env_outdir:
            out_dir = env_outdir

        print(f"[railui] Building into '{out_dir}'...")

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        # Clean old hashed assets so stale bundles don't accumulate
        for file in os.listdir(out_dir):
            if file.endswith(".js") or file.endswith(".css"):
                try:
                    os.remove(os.path.join(out_dir, file))
                except OSError:
                    pass

        # 1. Render each route to HTML + reactive effects
        compiled_routes: Dict = {}
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

        # Render optional 404 page
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

        # 2. Build hashed JS + CSS output filenames
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

        # 3. Write index.html
        css_links = "\n    ".join(
            f'<link rel="stylesheet" href="{url}">' for url in self.external_css
        )
        js_links = "\n    ".join(
            f'<script src="{url}"></script>' for url in self.external_js
        )
        raw_script_tags = "\n    ".join(
            f'<script>{code}</script>' for code in self.raw_scripts
        )

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

        print(f"[railui] Build complete -> {out_dir}/")
