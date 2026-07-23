"""
railui/cli/start.py

``railui start`` — run the production server.

Serves the compiled production build (dist/) using uvicorn + FastAPI.
This is the recommended way to run RailUI apps in production on platforms
like Railway, Heroku, Render, or any container environment.

Unlike ``railui preview``, this command:
  - Binds to 0.0.0.0 by default (for public/container access).
  - Reads $PORT from the environment variable (set by Railway and similar platforms).
  - Does NOT open a browser or inject HMR.

Usage::

    railui start
    railui start ./my-app --port 8000
"""
from __future__ import annotations

import logging
import os
import sys
from typing import Optional

from .config import RailUIConfig


def run(project_dir: str, host: str, config: RailUIConfig) -> int:
    """
    Start the production server.

    Args:
        project_dir: Path to the project root directory.
        host: Host string to bind to. Defaults to 0.0.0.0 for public access.
        config: RailUIConfig instance.

    Returns:
        int: Exit code.
    """
    # Read $PORT from environment (Railway, Render, Heroku etc.) or use config
    env_port = os.environ.get("PORT")
    if env_port:
        try:
            port = int(env_port)
        except ValueError:
            port = config.port
    else:
        port = config.port

    out_dir = os.path.join(project_dir, config.outdir)
    index_file = os.path.join(out_dir, "index.html")

    if not os.path.exists(out_dir) or not os.path.exists(index_file):
        print(
            f"\033[31m[railui start] Error: build output directory '{config.outdir}' "
            f"not found or missing index.html.\033[0m"
        )
        print(f"\033[33mRun 'railui build' first to compile for production.\033[0m")
        return 1

    sys.path.insert(0, project_dir)
    try:
        from railui.backend.server import create_app
    except ImportError as e:
        print(f"\033[31m[railui start] Server startup failed: {e}\033[0m")
        return 1

    app = create_app(dist_dir=out_dir, dev=False, project_dir=project_dir)

    import uvicorn

    url = f"http://{host}:{port}"
    print(f"\n  ->  RailUI Production Server: \033[36m{url}\033[0m")
    print(f"  ->  Platform:                 \033[32m{config.platform}\033[0m")
    print(f"  ->  Serving:                  {out_dir}\n")

    try:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.error").setLevel(logging.ERROR)
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="warning",
            access_log=False,
        )
    except KeyboardInterrupt:
        print("\n[railui] Shutting down production server...")
        sys.exit(0)
    except Exception:
        sys.exit(0)

    return 0
