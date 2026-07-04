"""
railui/backend/server.py

FastAPI application factory for RailUI.

In **dev mode** (default):
  - Serves ``dist/`` as static files.
  - Injects an HMR script into ``index.html`` that listens for Server-Sent Events.
  - Exposes ``GET /railui-hmr`` as an SSE stream; the dev watcher sends a
    ``reload`` event through this stream whenever a rebuild completes.
  - All unrecognised routes return ``dist/index.html`` (SPA catch-all).

In **production mode**:
  - Same static serving + SPA catch-all, but *without* the HMR injection.
  - Run with::

        uvicorn railui.backend.server:create_app --factory --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import AsyncGenerator, List, Optional

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

# ---------------------------------------------------------------------------
# Global SSE broadcast queue — the dev watcher puts messages here
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
# HMR SSE client script injected into index.html in dev mode
# ---------------------------------------------------------------------------
_HMR_SCRIPT = """
<script>
(function() {
  var src = new EventSource('/railui-hmr');
  src.addEventListener('reload', function() {
    console.log('[RailUI HMR] Reloading…');
    window.location.reload();
  });
  src.onerror = function() {
    setTimeout(function() {
      window.location.reload();
    }, 2000);
  };
})();
</script>
"""


def _inject_hmr(html: str) -> str:
    """Inject the HMR script just before </body>."""
    if "</body>" in html:
        return html.replace("</body>", _HMR_SCRIPT + "</body>", 1)
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
                  Defaults to a ``dist/`` directory next to the caller's ``main.py``.
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

    # ------------------------------------------------------------------
    # SSE hot-reload endpoint (dev only)
    # ------------------------------------------------------------------
    if dev:
        @app.get("/railui-hmr")
        async def hmr_stream() -> StreamingResponse:
            queue: asyncio.Queue = asyncio.Queue(maxsize=10)
            _hmr_queues.append(queue)

            async def event_generator() -> AsyncGenerator[str, None]:
                try:
                    yield "data: connected\n\n"
                    while True:
                        try:
                            msg = await asyncio.wait_for(queue.get(), timeout=15)
                            yield f"event: {msg}\ndata: {msg}\n\n"
                        except asyncio.TimeoutError:
                            # Keep-alive ping
                            yield ": ping\n\n"
                finally:
                    _hmr_queues.remove(queue)

            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "X-Accel-Buffering": "no",
                },
            )

    # ------------------------------------------------------------------
    # SPA index.html handler
    # ------------------------------------------------------------------
    index_path = resolved_dist / "index.html"

    @app.get("/{full_path:path}", response_class=HTMLResponse)
    async def spa_fallback(full_path: str) -> HTMLResponse:
        """Serve index.html for all non-static routes (SPA catch-all)."""
        # Let static files (js, css, assets) pass through; only html routes here
        if "." in full_path.split("/")[-1]:
            # Has a file extension — likely a missing static asset
            from fastapi.responses import Response
            return Response(status_code=404)

        if not index_path.exists():
            return HTMLResponse("<h1>Build not found. Run <code>railui build</code>.</h1>", status_code=404)

        html = index_path.read_text(encoding="utf-8")
        if dev:
            html = _inject_hmr(html)
        return HTMLResponse(html)

    # ------------------------------------------------------------------
    # Static files (js, css, assets) — mounted BEFORE the catch-all
    # ------------------------------------------------------------------
    if resolved_dist.exists():
        app.mount(
            "/",
            StaticFiles(directory=str(resolved_dist), html=False),
            name="static",
        )

    return app
