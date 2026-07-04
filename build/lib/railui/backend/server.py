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


def broadcast_reload() -> None:
    """Push a reload event to all connected browser clients."""
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
# Application factory
# ---------------------------------------------------------------------------
def create_app(
    dist_dir: Optional[str] = None,
    dev: bool = False,
) -> FastAPI:
    """
    Create and configure the RailUI FastAPI application.

    Args:
        dist_dir: Absolute path to the compiled ``dist/`` folder.
        dev:      Enable HMR injection and the ``/railui-hmr`` SSE endpoint.

    Returns:
        FastAPI: The configured application instance.
    """
    app = FastAPI(
        title="RailUI App",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

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
            # Serve the real file with correct MIME type
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
