"""
railui/cli/preview.py

``railui preview`` — preview the production build locally.

Starts a FastAPI server serving the production build output (from config.outdir)
with production settings (no HMR, fast static serving, server action RPCs enabled).
"""
from __future__ import annotations

import logging
import os
import sys
import threading
import time
import webbrowser
from typing import Optional

from .config import RailUIConfig


def run(project_dir: str, host: str, config: RailUIConfig) -> int:
    """
    Start the preview server for a production build.

    Args:
        project_dir: Path to the project root directory.
        host: Host string to bind to.
        config: RailUIConfig instance.

    Returns:
        int: Exit code.
    """
    port = config.port
    open_browser = config.open_browser
    out_dir = os.path.join(project_dir, config.outdir)
    index_file = os.path.join(out_dir, "index.html")

    if not os.path.exists(out_dir) or not os.path.exists(index_file):
        print(
            f"\033[31m[railui preview] Error: build output directory '{config.outdir}' "
            f"not found or missing index.html.\033[0m"
        )
        print(f"\033[33mRun 'railui build' first to compile for production.\033[0m")
        return 1

    sys.path.insert(0, project_dir)
    try:
        from railui.backend.server import create_app
    except ImportError as e:
        print(f"\033[31m[railui preview] Server startup failed: {e}\033[0m")
        return 1

    app = create_app(dist_dir=out_dir, dev=False, project_dir=project_dir)

    import uvicorn

    url = f"http://{host}:{port}"
    print(f"\n  ->  RailUI Preview Server: \033[36m{url}\033[0m")
    print(f"  ->  Platform:               \033[32m{config.platform}\033[0m")
    print(f"  ->  Serving:                {out_dir}\n")

    if open_browser:
        def _open():
            time.sleep(0.8)
            webbrowser.open(url)
        threading.Thread(target=_open, daemon=True).start()

    try:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.error").setLevel(logging.ERROR)
        uvicorn.run(app, host=host, port=port, log_level="warning", access_log=False)
    except (KeyboardInterrupt):
        print("\n[railui] Shutting down preview server...")
        sys.exit(0)
    except Exception:
        sys.exit(0)

    return 0
