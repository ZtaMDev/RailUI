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
from typing import Callable, Optional
from .config import RailUIConfig
import shutil
import subprocess


# ---------------------------------------------------------------------------
# Rebuild helper
# ---------------------------------------------------------------------------

def _rebuild(main_py: str, project_dir: str, config: RailUIConfig) -> bool:
    """
    Execute ``main.py`` in a subprocess to trigger a fresh build.
    Using a subprocess guarantees we don't hit sys.modules caching issues.
    
    Returns True on success, False on error.
    """
    try:
        # Inject config into the environment
        env = os.environ.copy()
        env["RAILUI_OUTDIR"] = config.outdir

        # Run in subprocess to ensure a completely clean state
        result = subprocess.run(
            [sys.executable, main_py],
            cwd=project_dir,
            env=env,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            sys.stdout.write("\033[K")  # Clear the current line
            print(f"\033[31m\n[railui dev] Build failed:\033[0m")
            print(result.stderr)
            return False
            
        # Copy public directories to outdir for dev serving
        dist_dir = os.path.join(project_dir, config.outdir)
        for pdir in config.public_dirs:
            src = os.path.join(project_dir, pdir)
            if os.path.isdir(src):
                for item in os.listdir(src):
                    s = os.path.join(src, item)
                    d = os.path.join(dist_dir, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
            
        return True
    except Exception as exc:
        sys.stdout.write("\033[K")
        print(f"\033[31m[railui] Rebuild error: {exc}\033[0m")
        return False


# ---------------------------------------------------------------------------
# Watchdog file watcher
# ---------------------------------------------------------------------------

_rebuild_lock = threading.Lock()
_last_rebuild_time = 0.0

def _start_watcher(
    watch_dir: str,
    main_py: str,
    project_dir: str,
    config: RailUIConfig,
    on_rebuilt: Callable[[], None],
) -> None:
    """
    Start a background thread that polls ``.py`` file mtimes and rebuilds on changes.
    """
    
    def _trigger():
        global _last_rebuild_time
        now = time.monotonic()
        # Debounce: ignore events within 1 second of the last rebuild start
        if now - _last_rebuild_time < 1.0:
            return
            
        if not _rebuild_lock.acquire(blocking=False):
            return  # Already building
            
        try:
            _last_rebuild_time = time.monotonic()
            
            # Print timestamp like Vite
            ts = time.strftime("%I:%M:%S %p")
            sys.stdout.write(f"\033[36m{ts} [railui]\033[0m \033[33mrebuilding...\033[0m\r")
            sys.stdout.flush()
            
            ok = _rebuild(main_py, project_dir, config)
            
            # Clear the rebuilding line
            sys.stdout.write("\033[K")
            
            if ok:
                print(f"\033[36m{ts} [railui]\033[0m \033[32mpage reload\033[0m")
                on_rebuilt()
            else:
                print(f"\033[36m{ts} [railui]\033[0m \033[31mbuild error\033[0m")
        finally:
            _rebuild_lock.release()

    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        class _Handler(FileSystemEventHandler):
            def on_modified(self, event):
                if not event.is_directory and event.src_path.endswith(".py"):
                    _trigger()
            def on_created(self, event):
                self.on_modified(event)

        observer = Observer()
        observer.schedule(_Handler(), path=watch_dir, recursive=True)
        observer.start()
        return

    except ImportError:
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
                            _trigger()
                        mtimes[fp] = mt

    t = threading.Thread(target=_poll, daemon=True)
    t.start()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run(project_dir: str, host: str, config: RailUIConfig) -> int:
    """
    Start the dev server with hot module replacement.
    """
    import logging
    
    port = config.port
    open_browser = config.open_browser
    
    main_py = os.path.join(project_dir, "main.py")
    dist_dir = os.path.join(project_dir, config.outdir)

    if not os.path.exists(main_py):
        print(f"\033[31m[railui dev] Error: no main.py found in {project_dir}\033[0m")
        return 1

    # ---- Initial build --------------------------------------------------
    print("[railui] Starting development server...")
    print(f"[railui] Building initial bundle...")
    ok = _rebuild(main_py, project_dir, config)
    if not ok:
        print("\033[31m[railui dev] Initial build failed — fix the errors above and try again.\033[0m")

    # Pass RAILUI_OUTDIR to the server script via env var so it serves from config.outdir
    os.environ["RAILUI_OUTDIR"] = config.outdir
    sys.path.insert(0, project_dir)
    try:
        from railui.backend.server import create_app, broadcast_reload  # type: ignore
    except ImportError as e:
        print(f"\033[31m[railui dev] Server startup failed: {e}\033[0m")
        return 1

    # ---- File watcher → SSE broadcast ------------------------------------
    _start_watcher(
        watch_dir=project_dir,
        main_py=main_py,
        project_dir=project_dir,
        config=config,
        on_rebuilt=broadcast_reload,
    )

    # ---- Uvicorn --------------------------------------------------------
    import uvicorn

    url = f"http://{host}:{port}"
    print(f"\n  ->  RailUI Dev Server: \033[36m{url}\033[0m")
    print(f"  ->  Hot reload: \033[32menabled\033[0m")
    print(f"  ->  Watching:   {project_dir}\n")

    if open_browser:
        # Delay slightly so the server is ready
        def _open():
            time.sleep(1.2)
            webbrowser.open(url)
        threading.Thread(target=_open, daemon=True).start()

    try:
        # Disable access logs for a quiet, Vite-like output
        import logging
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        uvicorn.run(create_app(dist_dir=dist_dir, dev=True), host=host, port=port, log_level="warning", access_log=False)
    except KeyboardInterrupt:
        print("\n[railui] Shutting down development server...")
        sys.exit(0)
        
    return 0
