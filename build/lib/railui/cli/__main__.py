"""
railui/cli/__main__.py

Entry point for the ``railui`` CLI command.

Usage::

    railui dev [--host HOST] [--port PORT] [--no-open]
    railui build
    railui new <project-name>

Can also be invoked as::

    python -m railui dev
"""
from __future__ import annotations

import argparse
import os
import sys


def _resolve_project(path: str | None) -> str:
    """Return the absolute path to the project root."""
    if path:
        return os.path.abspath(path)
    return os.getcwd()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="railui",
        description="RailUI — Python-first, zero-runtime fullstack web framework",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ---- railui dev -------------------------------------------------------
    dev_p = sub.add_parser("dev", help="Start the development server with hot reload")
    dev_p.add_argument(
        "project",
        nargs="?",
        default=None,
        help="Path to the project root (default: current directory)",
    )
    dev_p.add_argument("--host", default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    dev_p.add_argument("--port", type=int, default=5173, help="Server port (default: 5173)")
    dev_p.add_argument("--no-open", action="store_true", help="Do not open the browser automatically")

    # ---- railui build -----------------------------------------------------
    build_p = sub.add_parser("build", help="Compile to a production bundle")
    build_p.add_argument(
        "project",
        nargs="?",
        default=None,
        help="Path to the project root (default: current directory)",
    )

    # ---- railui new -------------------------------------------------------
    new_p = sub.add_parser("new", help="Scaffold a new RailUI project")
    new_p.add_argument("name", help="Project name (also used as directory name)")
    new_p.add_argument(
        "--dir",
        default=".",
        help="Parent directory where the project will be created (default: .)",
    )

    args = parser.parse_args()

    if args.command == "dev":
        from railui.cli.dev import run
        project = _resolve_project(args.project)
        sys.exit(run(project, host=args.host, port=args.port, open_browser=not args.no_open))

    elif args.command == "build":
        from railui.cli.build import run
        project = _resolve_project(args.project)
        sys.exit(run(project))

    elif args.command == "new":
        from railui.cli.new import run
        sys.exit(run(args.name, base_dir=args.dir))


if __name__ == "__main__":
    main()
