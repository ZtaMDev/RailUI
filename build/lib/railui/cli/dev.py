"""
railui/cli/dev.py

``railui dev`` — development server with hot module replacement.

Starts a FastAPI server that:
1. Performs an initial build.
2. Watches ``.py`` files for changes and rebuilds automatically.
3. Broadcasts a ``reload`` Server-Sent Event to connected browsers after each rebuild.
4. Serves ``dist/`` statically and handles SPA routing.
"""
from __future__ import annotations

import asyncio
import importlib.util
import os
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Rebuild helper
# ---------------------------------------------------------------------------

def _rebuild(main_py: str, project_dir: str) -> bool:
    """
    Re-execute ``main.py`` to trigger a fresh build.

    Returns True on success, False on error.
    """
    # Remove cached module so it re-runs from scratch
    mod_name = "__railui_main__"
    if mod_name in sys.modules:
        del sys.modules[mod_name]

    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

    spec = importlib.util.spec_from_file_location(mod_name, main_py)
    if not spec or not spec.loader:
        return False
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        return True
    except SystemExit:
        return True  # normal exit from build
    except Exception as exc:
        print(f"[railui] Rebuild error: {exc}")
        return False


# ---------------------------------------------------------------------------
# Watchdog file watcher
# ---------------------------------------------------------------------------

def _start_watcher(
    watch_dir: str,
    main_py: str,
    project_dir: str,
    on_rebuilt: callable,
) -> None:
    """
    Start a background thread that polls ``.py`` file mtimes and rebuilds on changes.
    Uses stdlib ``os.stat`` polling (no external deps beyond watchdog for full events).
    Falls back gracefully if watchdog is unavailable.
    """
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        class _Handler(FileSystemEventHandler):
            _debounce: Optional[float] = None

            def on_modified(self, event):
                if not event.is_directory and event.src_path.endswith(".py"):
                    now = time.monotonic()
                    if self._debounce is None or now - self._debounce > 0.5:
                        self._debounce = now
                        self._trigger()

            def on_created(self, event):
                self.on_modified(event)

            def _trigger(self):
                print(f"[railui] Change detected — rebuilding…")
                ok = _rebuild(main_py, project_dir)
                if ok:
                    print("[railui] Rebuild complete ✓ — reloading browser")
                    on_rebuilt()

        observer = Observer()
        observer.schedule(_Handler(), path=watch_dir, recursive=True)
        observer.start()
        return  # observer runs in its own thread

    except ImportError:
        # watchdog not installed — fall back to polling
        pass

    def _poll():
        mtimes: dict = {}
        while True:
            time.sleep(1)
            for root, _, files in os.walk(watch_dir):
                for f in files:
                    if f.endswith(".py"):
                        fp = os.path.join(root, f)
                        try:
                            mt = os.stat(fp).st_mtime
                        except OSError:
                            continue
                        old = mtimes.get(fp)
                        if old is not None and mt != old:
                            print(f"[railui] Change detected — rebuilding…")
                            ok = _rebuild(main_py, project_dir)
                            if ok:
                                print("[railui] Rebuild complete ✓ — reloading browser")
                                on_rebuilt()
                        mtimes[fp] = mt

    t = threading.Thread(target=_poll, daemon=True)
    t.start()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run(project_dir: str, host: str = "127.0.0.1", port: int = 5173, open_browser: bool = True) -> int:
    """
    Start the RailUI development server.

    Args:
        project_dir: Absolute path to the project root (contains ``main.py``).
        host: Hostname to bind to.
        port: Port to listen on (default: 5173 to feel familiar).
        open_browser: Automatically open the browser on start.

    Returns:
        int: Exit code.
    """
    main_py = os.path.join(project_dir, "main.py")
    dist_dir = os.path.join(project_dir, "dist")

    if not os.path.exists(main_py):
        print(f"[railui dev] Error: no main.py found in {project_dir}")
        return 1

    # ---- Initial build --------------------------------------------------
    print("[railui] Starting development server…")
    print(f"[railui] Building initial bundle…")
    ok = _rebuild(main_py, project_dir)
    if not ok:
        print("[railui dev] Initial build failed — fix the errors above and try again.")
        return 1

    # ---- Import server + broadcast helper --------------------------------
    from railui.backend.server import create_app, broadcast_reload

    app = create_app(dist_dir=dist_dir, dev=True)

    # ---- File watcher → SSE broadcast ------------------------------------
    _start_watcher(
        watch_dir=project_dir,
        main_py=main_py,
        project_dir=project_dir,
        on_rebuilt=broadcast_reload,
    )

    # ---- Uvicorn --------------------------------------------------------
    import uvicorn

    url = f"http://{host}:{port}"
    print(f"\n  ➜  RailUI Dev Server: \033[36m{url}\033[0m")
    print(f"  ➜  Hot reload: \033[32menabled\033[0m")
    print(f"  ➜  Watching:   {project_dir}\n")

    if open_browser:
        # Delay slightly so the server is ready
        def _open():
            time.sleep(1.2)
            webbrowser.open(url)
        threading.Thread(target=_open, daemon=True).start()

    uvicorn.run(app, host=host, port=port, log_level="warning")
    return 0
