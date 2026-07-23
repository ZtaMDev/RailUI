"""
railui/cli/__main__.py

Entry point for the ``railui`` CLI command.

Usage::

    railui dev [--host HOST] [--port PORT] [--no-open]
    railui build [project_dir]
    railui new <project-name>
    railui --help
    railui --version

Can also be invoked as::

    python -m railui dev
"""
from __future__ import annotations
from railui.cli.config import load_config

import argparse
import os
import sys


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------
def _get_version() -> str:
    from railui import __version__
    return __version__


def _print_version() -> None:
    ver = _get_version()
    print(f"\n  {_c('railui', _CYAN, _BOLD)} {_c('v' + ver, _GREEN, _BOLD)}  {_c('-', _DIM)}  {_c('Python-first Fullstack Web-Framework', _WHITE)}\n")


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
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleMode(
                ctypes.windll.kernel32.GetStdHandle(-11), 7
            )
        except Exception:
            pass
    return "".join(codes) + text + _RESET


def _banner() -> None:
    """Print the RailUI ASCII banner."""
    ver = _get_version()
    lines = [
        "  ██████╗  █████╗ ██╗██╗     ██╗   ██╗██╗",
        "  ██╔══██╗██╔══██╗██║██║     ██║   ██║██║",
        "  ██████╔╝███████║██║██║     ██║   ██║██║",
        "  ██╔══██╗██╔══██║██║██║     ██║   ██║██║",
        "  ██║  ██║██║  ██║██║███████╗╚██████╔╝██║",
        "  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝ ╚═════╝ ╚═╝",
        f"  v{ver}  ·  Python-first · Fullstack Web-Framework",
    ]
    try:
        print()
        for line in lines:
            print(_c(line, _CYAN, _BOLD))
        print()
    except UnicodeEncodeError:
        print()
        print(f"RailUI v{ver}  -  Python-first Fullstack Web-Framework")
        print()


def _print_help() -> None:
    _banner()
    print(_c("  USAGE", _BOLD, _WHITE))
    print(f"    {_c('railui', _CYAN)} {_c('<command>', _YELLOW)} {_c('[options]', _DIM)}")
    print()
    print(_c("  COMMANDS", _BOLD, _WHITE))
    cmds = [
        ("dev     [path]", "Start the dev server with hot reload"),
        ("build   [path]", "Compile to a production bundle"),
        ("preview [path]", "Preview the production build locally"),
        ("start   [path]", "Run the production server (for Railway, Render, etc.)"),
        ("new     <name>", "Scaffold a new RailUI project"),
    ]
    for cmd, desc in cmds:
        print(f"    {_c(cmd, _GREEN, _BOLD)}    {_c(desc, _DIM)}")
    print()
    print(_c("  GLOBAL FLAGS", _BOLD, _WHITE))
    flags = [
        ("-h, --help   ", "Show this help message"),
        ("-v, --version", "Print version and exit"),
    ]
    for flag, desc in flags:
        print(f"    {_c(flag, _YELLOW)}  {_c(desc, _DIM)}")
    print()
    print(_c("  OPTIONS", _BOLD, _WHITE))
    opts = [
        ("dev    ", "--host HOST  --port PORT  --no-open  --platform railway|vercel"),
        ("build  ", "--outdir DIR  --no-bundle  --platform railway|vercel"),
        ("preview", "--host HOST  --port PORT  --no-open  --outdir DIR"),
        ("start  ", "--host HOST  --port PORT  (reads $PORT env var)"),
        ("new    ", "<name>  --dir PARENT_DIR"),
    ]
    for cmd, desc in opts:
        print(f"    {_c(cmd, _YELLOW, _BOLD)}  {_c(desc, _DIM)}")
    print()
    print(_c("  EXAMPLES", _BOLD, _WHITE))
    examples = [
        ("railui new my-app", "Scaffold a new project"),
        ("railui dev        ", "Start dev server (current dir)"),
        ("railui dev ./app  ", "Start dev server for a specific path"),
        ("railui build      ", "Production build (current dir)"),
        ("railui preview    ", "Preview production build (current dir)"),
        ("railui start      ", "Run production server (reads $PORT)"),
    ]
    for ex, desc in examples:
        print(f"    {_c(ex, _MAGENTA)}  {_c('# ' + desc, _DIM)}")
    print()


def _resolve_project(path: str | None) -> str:
    if path:
        return os.path.abspath(path)
    return os.getcwd()


def main() -> None:
    # Handle --version / -v before argparse
    if len(sys.argv) == 2 and sys.argv[1] in ("-v", "--version"):
        _print_version()
        sys.exit(0)

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

    # ---- railui preview [project]
    parser_preview = subparsers.add_parser("preview", help="Preview the production build locally")
    parser_preview.add_argument("project", nargs="?", default=".", help="Project directory (default: current directory)")
    parser_preview.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser_preview.add_argument("--port", type=int, default=None, help="Port to bind to (default: 4173)")
    parser_preview.add_argument("--no-open", action="store_true", help="Do not open browser automatically")
    parser_preview.add_argument("--outdir", default=None, help="Output directory to preview")

    # ---- railui start [project]
    parser_start = subparsers.add_parser("start", help="Run the production server (for Railway, Render, etc.)")
    parser_start.add_argument("project", nargs="?", default=".", help="Project directory (default: current directory)")
    parser_start.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser_start.add_argument("--port", type=int, default=None, help="Port override ($PORT env var takes precedence)")

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
    elif args.command == "preview":
        from railui.cli.preview import run
        project = _resolve_project(getattr(args, "project", "."))
        config = load_config(project, args)
        # Default preview port is 4173 if not explicitly provided
        if args.port is None and config.port == 5173:
            config.port = 4173
        sys.exit(run(project, host=args.host, config=config))
    elif args.command == "start":
        from railui.cli.start import run
        project = _resolve_project(getattr(args, "project", "."))
        config = load_config(project, args)
        host = getattr(args, "host", "0.0.0.0")
        sys.exit(run(project, host=host, config=config))
    elif args.command == "new":
        from railui.cli.new import run
        sys.exit(run(args.name, base_dir=args.dir))


if __name__ == "__main__":
    main()
