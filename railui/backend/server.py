"""
railui/backend/server.py

FastAPI application factory for RailUI.

In **dev mode** (default):
  - Serves files from ``dist/`` directly.
  - Injects an HMR script into ``index.html`` via SSE for live reload.
  - All unrecognized routes return ``dist/index.html`` (SPA catch-all).

In **production mode**:
  - Same behaviour without HMR injection.
  - Run with::

        uvicorn railui.backend.server:create_app --factory --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import asyncio
import mimetypes
import os
from pathlib import Path
from typing import AsyncGenerator, List, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response, StreamingResponse, JSONResponse

# ---------------------------------------------------------------------------
# SSE broadcast queue — the dev watcher pushes reload events here
# ---------------------------------------------------------------------------
_hmr_queues: List[asyncio.Queue] = []
_active_project_dir: Optional[str] = None


def reload_project_actions(project_dir: Optional[str] = None) -> None:
    """
    Reload project modules in-process so that modified ``@server_action`` functions
    are updated dynamically without restarting the server process.
    """
    import sys
    target_dir = project_dir or _active_project_dir
    if not target_dir or not os.path.isdir(target_dir):
        return

    proj_path = os.path.abspath(target_dir)
    to_remove = []
    for mod_name, mod in list(sys.modules.items()):
        if mod and hasattr(mod, "__file__") and mod.__file__:
            try:
                mod_file = os.path.abspath(mod.__file__)
                if mod_file.startswith(proj_path):
                    to_remove.append(mod_name)
            except Exception:
                pass

    for mod_name in to_remove:
        sys.modules.pop(mod_name, None)

    _import_project_main(target_dir)


def broadcast_reload(project_dir: Optional[str] = None) -> None:
    """Push a reload event to all connected browser clients and refresh backend actions."""
    if project_dir or _active_project_dir:
        reload_project_actions(project_dir or _active_project_dir)

    for q in list(_hmr_queues):
        try:
            q.put_nowait("reload")
        except asyncio.QueueFull:
            pass


# ---------------------------------------------------------------------------
# HMR client script injected into index.html in dev mode
# ---------------------------------------------------------------------------
_HMR_SCRIPT = """\
<script>
(function() {
  var es = new EventSource('/railui-hmr');
  es.addEventListener('reload', function() {
    console.log('[RailUI HMR] reloading...');
    window.location.reload();
  });
  es.onerror = function() {
    setTimeout(function() { window.location.reload(); }, 2000);
  };
})();
</script>"""


def _inject_hmr(html: str) -> str:
    if "</body>" in html:
        return html.replace("</body>", _HMR_SCRIPT + "\n</body>", 1)
    return html + _HMR_SCRIPT


# ---------------------------------------------------------------------------
# Import project main.py to register server actions
# ---------------------------------------------------------------------------

def _import_project_main(project_dir: str) -> None:
    """Import the project's ``main.py`` so that ``@server_action`` decorators fire."""
    import importlib.util
    import sys

    main_py = os.path.join(project_dir, "main.py")
    if not os.path.isfile(main_py):
        return  # No main.py — no actions to register

    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

    spec = importlib.util.spec_from_file_location("railui_project_main", main_py)
    if spec and spec.loader:
        try:
            spec.loader.exec_module(importlib.util.module_from_spec(spec))
        except Exception as exc:
            print(f"\033[33m[railui] Warning: could not import main.py to register server actions: {exc}\033[0m")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------
def create_app(
    dist_dir: Optional[str] = None,
    dev: bool = False,
    project_dir: Optional[str] = None,
) -> FastAPI:
    """
    Create and configure the RailUI FastAPI application.

    Args:
        dist_dir:    Absolute path to the compiled ``dist/`` folder.
        dev:         Enable HMR injection and the ``/railui-hmr`` SSE endpoint.
        project_dir: Project root directory. If provided, ``main.py`` is imported
                     so that ``@server_action`` decorators are registered.

    Returns:
        FastAPI: The configured application instance.
    """
    app = FastAPI(
        title="RailUI App",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    global _active_project_dir
    if project_dir:
        _active_project_dir = project_dir
        _import_project_main(project_dir)

    resolved_dist = Path(dist_dir) if dist_dir else Path.cwd() / "dist"
    index_path = resolved_dist / "index.html"

    # ------------------------------------------------------------------
    # SSE hot-reload endpoint (dev only)
    # ------------------------------------------------------------------
    if dev:
        @app.get("/railui-hmr")
        async def hmr_stream() -> StreamingResponse:
            queue: asyncio.Queue = asyncio.Queue(maxsize=10)
            _hmr_queues.append(queue)

            async def _gen() -> AsyncGenerator[str, None]:
                try:
                    yield "data: connected\n\n"
                    while True:
                        try:
                            msg = await asyncio.wait_for(queue.get(), timeout=15)
                            yield f"event: {msg}\ndata: {msg}\n\n"
                        except asyncio.TimeoutError:
                            yield ": ping\n\n"
                except (asyncio.CancelledError, Exception):
                    pass
                finally:
                    if queue in _hmr_queues:
                        _hmr_queues.remove(queue)

            return StreamingResponse(
                _gen(),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
            )

    # ------------------------------------------------------------------
    # Server Actions RPC Endpoint
    # ------------------------------------------------------------------
    @app.post("/_railui_action/{action_name}")
    async def handle_server_action(action_name: str, request: Request):
        from railui.core.actions import get_action_registry
        
        if dev and project_dir:
            reload_project_actions(project_dir)

        registry = get_action_registry()
        if action_name not in registry:
            raise HTTPException(status_code=404, detail=f"Server action '{action_name}' not found.")
            
        func = registry[action_name]
        
        try:
            # The frontend sends JSON.stringify([arg1, arg2])
            args = await request.json()
            if not isinstance(args, list):
                args = [args]
                
            # If the action is async, await it(also using asyncio for backward compat)
            # pyrefly: ignore [deprecated]
            if asyncio.iscoroutinefunction(func):
                result = await func(*args)
            else:
                # Run sync functions in thread pool to avoid blocking the event loop
                result = await asyncio.to_thread(func, *args)
                
            return JSONResponse(content=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ------------------------------------------------------------------
    # Universal request handler:
    #   1. If a real file exists in dist/ → serve it directly.
    #   2. Otherwise → serve index.html (SPA fallback).
    # ------------------------------------------------------------------
    @app.get("/{full_path:path}")
    async def serve(full_path: str) -> Response:
        # Root path
        if not full_path or full_path == "/":
            candidate = index_path
        else:
            # full_path may start with a slash, we want to join it cleanly
            clean_path = full_path.lstrip("/")
            candidate = resolved_dist / clean_path

        if candidate.exists() and candidate.is_file():
            # If serving index.html directly, inject HMR script in dev mode
            if candidate == index_path or candidate.name == "index.html":
                html = candidate.read_text(encoding="utf-8")
                if dev:
                    html = _inject_hmr(html)
                return HTMLResponse(html)

            # Serve other static files (js, css, images) with correct MIME type
            mime, _ = mimetypes.guess_type(str(candidate))
            return FileResponse(str(candidate), media_type=mime or "application/octet-stream")

        # SPA fallback — any "page" route that has no matching file gets index.html
        if not index_path.exists():
            return HTMLResponse(
                "<h1>Build not found.</h1><p>Run <code>railui build</code> first.</p>",
                status_code=404,
            )

        html = index_path.read_text(encoding="utf-8")
        if dev:
            html = _inject_hmr(html)
        return HTMLResponse(html)

    return app
