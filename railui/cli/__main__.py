"""
railui/cli/__main__.py

Entry point for the ``railui`` CLI command.

Usage::

    railui dev [--host HOST] [--port PORT] [--no-open]
    railui build [project_dir]
    railui new <project-name>
    railui --help

Can also be invoked as::

    python -m railui dev
"""
from __future__ import annotations
from railui.cli.config import load_config

import argparse
import os
import sys


# ---------------------------------------------------------------------------
# ANSI colour helpers
# ---------------------------------------------------------------------------
_RESET  = "\033[0m"
_BOLD   = "\033[1m"
_DIM    = "\033[2m"
_CYAN   = "\033[36m"
_GREEN  = "\033[32m"
_YELLOW = "\033[33m"
_MAGENTA = "\033[35m"
_WHITE  = "\033[97m"
_RED    = "\033[31m"


def _c(text: str, *codes: str) -> str:
    """Wrap text in ANSI escape codes (no-op on Windows without ANSI support)."""
    if sys.platform == "win32":
        # Enable ANSI on Windows 10+
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleMode(  # type: ignore[attr-defined]
                ctypes.windll.kernel32.GetStdHandle(-11), 7  # type: ignore[attr-defined]
            )
        except Exception:
            pass
    return "".join(codes) + text + _RESET


def _banner() -> None:
    """Print the RailUI ASCII banner."""
    print()
    print(_c("  ██████╗  █████╗ ██╗██╗     ██╗   ██╗██╗", _CYAN, _BOLD))
    print(_c("  ██╔══██╗██╔══██╗██║██║     ██║   ██║██║", _CYAN, _BOLD))
    print(_c("  ██████╔╝███████║██║██║     ██║   ██║██║", _CYAN, _BOLD))
    print(_c("  ██╔══██╗██╔══██║██║██║     ██║   ██║██║", _CYAN, _BOLD))
    print(_c("  ██║  ██║██║  ██║██║███████╗╚██████╔╝██║", _CYAN, _BOLD))
    print(_c("  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝ ╚═════╝ ╚═╝", _CYAN, _BOLD))
    print()
    print(_c("  Python-first · Fullstack Web-Framework", _DIM))
    print()


def _print_help() -> None:
    _banner()
    print(_c("  USAGE", _BOLD, _WHITE))
    print(f"    {_c('railui', _CYAN)} {_c('<command>', _YELLOW)} {_c('[options]', _DIM)}")
    print()
    print(_c("  COMMANDS", _BOLD, _WHITE))
    cmds = [
        ("dev   [path]", "Start the dev server with hot reload"),
        ("build [path]", "Compile to a production bundle"),
        ("new   <name>", "Scaffold a new RailUI project"),
    ]
    for cmd, desc in cmds:
        print(f"    {_c(cmd, _GREEN, _BOLD)}    {_c(desc, _DIM)}")
    print()
    print(_c("  OPTIONS (railui dev)", _BOLD, _WHITE))
    opts = [
        ("--host HOST ", "Bind host (default: 127.0.0.1)"),
        ("--port PORT ", "Listen port (default: 5173)"),
        ("--no-open   ", "Do not open browser automatically"),
    ]
    for flag, desc in opts:
        print(f"    {_c(flag, _YELLOW)}  {_c(desc, _DIM)}")
    print()
    print(_c("  EXAMPLES", _BOLD, _WHITE))
    examples = [
        ("railui new my-app", "Scaffold a new project"),
        ("railui dev        ", "Start dev server (current dir)"),
        ("railui dev ./app  ", "Start dev server for a specific path"),
        ("railui build      ", "Production build (current dir)"),
    ]
    for ex, desc in examples:
        print(f"    {_c(ex, _MAGENTA)}  {_c('# ' + desc, _DIM)}")
    print()


def _resolve_project(path: str | None) -> str:
    if path:
        return os.path.abspath(path)
    return os.getcwd()


def main() -> None:
    # Show the pretty help when invoked with no arguments
    if len(sys.argv) == 1:
        _print_help()
        sys.exit(0)

    parser = argparse.ArgumentParser(
        prog="railui",
        description="RailUI — Python-first, zero-runtime fullstack web framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=True,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---- railui dev -------------------------------------------------------
    parser_dev = subparsers.add_parser("dev", help="Start the development server")
    parser_dev.add_argument("project", nargs="?", default=".", help="Project directory (default: current directory)")
    parser_dev.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser_dev.add_argument("--port", type=int, default=None, help="Port to bind to (overrides config)")
    parser_dev.add_argument("--no-open", action="store_true", help="Do not open browser automatically")
    parser_dev.add_argument("--platform", choices=["railway", "vercel"], default=None, help="Target deployment platform")

    # railui build [project]
    parser_build = subparsers.add_parser("build", help="Build the project for production")
    parser_build.add_argument("project", nargs="?", default=".", help="Project directory (default: current directory)")
    parser_build.add_argument("--outdir", default=None, help="Output directory (overrides config)")
    parser_build.add_argument("--no-bundle", action="store_true", help="Disable JS/CSS minification via dars-bundler")
    parser_build.add_argument("--platform", choices=["railway", "vercel"], default=None, help="Target deployment platform")

    # ---- railui new -------------------------------------------------------
    new_p = subparsers.add_parser("new", help="Scaffold a new RailUI project")
    new_p.add_argument("name", help="Project name (used as directory name)")
    new_p.add_argument("--dir", default=".", help="Parent directory (default: .)")

    args = parser.parse_args()
    if args.command == "dev":
        from railui.cli.dev import run
        project = _resolve_project(getattr(args, "project", "."))
        config = load_config(project, args)
        sys.exit(run(project, host=args.host, config=config))
    elif args.command == "build":
        from railui.cli.build import run
        project = _resolve_project(getattr(args, "project", "."))
        config = load_config(project, args)
        sys.exit(run(project, config))
    elif args.command == "new":
        from railui.cli.new import run
        sys.exit(run(args.name, base_dir=args.dir))


if __name__ == "__main__":
    main()
