"""
railui/cli/new.py

``railui new <project-name>`` — scaffold a new RailUI project.
Provides an interactive arrow-key selector for choosing project templates.
"""
from __future__ import annotations

import os
import sys

# ANSI Color Code Helpers
_RESET   = "\033[0m"
_BOLD    = "\033[1m"
_DIM     = "\033[2m"
_CYAN    = "\033[36m"
_GREEN   = "\033[32m"
_YELLOW  = "\033[33m"
_WHITE   = "\033[97m"
_RED     = "\033[31m"


def _safe(text: str) -> str:
    """Safely sanitize text for printing on terminals that don't support utf-8 charmaps."""
    try:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        if encoding.lower().startswith("cp") or encoding.lower().startswith("ansi") or encoding.lower().startswith("ascii"):
            raise UnicodeEncodeError(encoding, text, 0, 1, "force fallback")
        text.encode(encoding)
        return text
    except (UnicodeEncodeError, AttributeError):
        return (
            text.replace("✔", "[v]")
            .replace("❯", ">")
            .replace("↳", "->")
            .replace("—", "-")
            .replace("…", "...")
            .replace("↑", "^")
            .replace("↓", "v")
            .replace("🎉", "*")
        )


def _c(text: str, *codes: str) -> str:
    """Wrap text in ANSI escape codes."""
    safe_text = _safe(text)
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleMode(
                ctypes.windll.kernel32.GetStdHandle(-11), 7
            )
        except Exception:
            pass
    return "".join(codes) + safe_text + _RESET


# ---------------------------------------------------------------------------
# Templates Definition
# ---------------------------------------------------------------------------

_CONFIG_JSON = """\
{
  "outdir": "dist",
  "port": 5173,
  "open_browser": true,
  "bundle": true,
  "platform": "railway",
  "public_dirs": ["public"]
}
"""

_REQUIREMENTS = """\
railui
fastapi
uvicorn
watchdog
"""

_GITIGNORE = """\
__pycache__/
*.pyc
dist/
build/
.railui/
.venv/
.env
"""

_PYRIGHTCONFIG = """\
{
  "pythonVersion": "3.11",
  "extraPaths": ["."],
  "exclude": ["dist", "build", ".railui"]
}
"""

# --- BASE-BLANK TEMPLATE (Minimal / In-Place Routing) ---
_BASE_BLANK_MAIN_PY = '''\
import os
from railui.all import *

app = App(title="{title}")


@app.route("/")
def index() -> Component:
    count, setCount = createSignal(0)

    return Page(
        Container(
            Text("{title}", class_name="text-4xl font-black text-gray-900 mb-2 block"),
            Text("Minimal RailUI application with in-place routing.", class_name="text-gray-500 mb-8 block"),

            Container(
                Button("-", on_click=setCount(count() - 1), class_name="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-l-lg text-xl font-bold transition"),
                Text(count(), class_name="px-6 py-2 bg-white border-y text-xl font-mono text-gray-900"),
                Button("+", on_click=setCount(count() + 1), class_name="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-r-lg text-xl font-bold transition"),
                class_name="flex items-center mb-6",
            ),
            
            Button("Show Alert", on_click=alert("Hello from RailUI!"), class_name="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-lg transition shadow-md"),
            class_name="flex flex-col items-center justify-center min-h-screen bg-gray-50 font-sans p-6 text-center"
        )
    )

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "dist")
    app.build(out_dir=out_dir)
'''

# --- BLANK TEMPLATE (Standard SPA / File-Based Routing) ---
_BLANK_MAIN_PY = '''\
import os
from railui.all import *
from layout import Layout

app = App(title="{title}")

# Discover all pages under pages/ directory automatically
app.discover_pages(os.path.join(os.path.dirname(__file__), "pages"))


def not_found() -> Component:
    return Layout(
        Head(title="404 | {title}"),
        Container(
            Text("404", class_name="text-8xl font-black text-gray-200 block mb-4"),
            Text("Page Not Found", class_name="text-2xl font-bold text-gray-800 block mb-6"),
            Link("Go back home", href="/", class_name="px-6 py-3 bg-gray-900 text-white font-semibold rounded-lg hover:bg-gray-800 transition shadow-md"),
            class_name="flex flex-col items-center justify-center py-20 text-center",
        ),
    )


app.set_not_found(not_found)

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "dist")
    app.build(out_dir=out_dir)
'''

_BLANK_BACKEND_PY = '''\
"""
backend.py

Custom FastAPI backend instance for {title}.
RailUI automatically detects and loads this file on startup.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from railui.backend import RailUI, server_action

app = FastAPI(title="{title} Backend")
rail = RailUI(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": "{title}"}
'''

_BLANK_LAYOUT_PY = '''\
from railui.all import *


def Navbar() -> Component:
    return Container(
        Container(
            Text("{title}", class_name="font-black text-2xl text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-500"),
            Container(
                Link("Home", href="/", class_name="text-gray-600 hover:text-purple-600 font-medium transition"),
                Link("Actions Demo", href="/actions_demo", class_name="text-gray-600 hover:text-purple-600 font-medium transition"),
                class_name="flex flex-row items-center gap-6"
            ),
            class_name="flex flex-row justify-between items-center w-full max-w-5xl mx-auto"
        ),
        class_name="w-full bg-white shadow-sm p-4 border-b border-gray-200 sticky top-0 z-50"
    )


def Layout(*children: Component) -> Component:
    """Shared page layout wrapper with named slots."""
    return Page(
        Navbar(),
        Slot("hero", source=children, default=""),
        Container(
            Slot("body", source=children, default=Slot.Unassigned(children)),
            class_name="w-full max-w-5xl mx-auto p-8 flex-grow"
        ),
        Slot("footer", source=children, default=Container(
            Text("© 2026 {title}. Built with RailUI Framework.", class_name="text-sm text-gray-500"),
            class_name="w-full p-4 border-t border-gray-200 mt-auto text-center bg-white"
        )),
        class_name="min-h-screen bg-gray-50 flex flex-col font-sans"
    )
'''

_BLANK_INDEX_PAGE = '''\
from railui.all import *
from layout import Layout


def page() -> Component:
    count, setCount = createSignal(0)

    return Layout(
        Head(title="Home | {title}"),
        
        # Hero banner using named slot
        SlotFill("hero", Container(
            Text("🎉 Welcome to {title}!", class_name="text-3xl font-black text-white"),
            Text("Python-first, zero-runtime web application framework.", class_name="text-purple-100 mt-1 text-sm block"),
            class_name="w-full bg-gradient-to-r from-purple-600 to-blue-600 p-8 shadow-lg text-center"
        )),
        
        # Main content body
        Container(
            Text("Reactive Signal Counter", class_name="text-2xl font-bold text-gray-900 mb-2 block"),
            Text("State management powered by reactive Python signals.", class_name="text-gray-500 mb-6 block"),
            
            Container(
                Button("-", on_click=setCount(count() - 1), class_name="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-l-lg text-xl font-bold transition"),
                Text(count(), class_name="px-6 py-2 bg-white border-y text-xl font-mono text-gray-900"),
                Button("+", on_click=setCount(count() + 1), class_name="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-r-lg text-xl font-bold transition"),
                class_name="flex items-center mb-8",
            ),
            
            Button("Show Browser Alert", on_click=alert("Hello from RailUI!"), class_name="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg transition shadow-md"),
            class_name="flex flex-col items-start"
        )
    )
'''

_BLANK_ACTIONS_DEMO_PAGE = '''\
from railui.all import *
from layout import Layout


@server_action
def greet_user(name: str):
    """Python function running on backend FastAPI server."""
    clean_name = name.strip() if name else "Developer"
    return {"status": "ok", "message": f"Hello {clean_name}! Server action executed successfully in Python."}


def page() -> Component:
    username, setUsername = createSignal("")
    greet_act, pending, result, error = useAction(greet_user)

    return Layout(
        Head(title="Server Actions | {title}"),
        Container(
            Text("Server Actions Demo", class_name="text-4xl font-black text-gray-900 block mb-2"),
            Text("Call Python backend functions directly with reactive useAction() hook.", class_name="text-gray-500 mb-8 block"),
            
            Container(
                Input(
                    placeholder="Enter your name...", 
                    bind=username,
                    class_name="px-4 py-2 border border-gray-300 rounded-l-lg w-64 focus:outline-none focus:ring-2 focus:ring-purple-500"
                ),
                Button(
                    Show("Calling...", when=pending(), fallback="Call Python Action"), 
                    on_click=greet_act(username()),
                    disabled=pending(),
                    class_name="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-r-lg transition shadow-md disabled:opacity-50"
                ),
                class_name="flex items-center mb-6",
            ),
            
            Show(
                when=result(),
                children=Text(
                    result().message,
                    class_name="p-4 bg-green-100 border border-green-200 text-green-800 rounded-lg font-mono text-sm block mb-4"
                )
            ),
            Show(
                when=error(),
                children=Text(
                    error(),
                    class_name="p-4 bg-red-100 border border-red-200 text-red-800 rounded-lg font-mono text-sm block"
                )
            )
        )
    )
'''


# ---------------------------------------------------------------------------
# Interactive CLI Selector
# ---------------------------------------------------------------------------

TEMPLATES = [
    {
        "id": "base-blank",
        "name": "base-blank (Minimal)",
        "badge": "In-Place Routing",
        "description": "Minimal single-file starter with in-place route definitions directly inside main.py.\n    Ideal for small apps, prototypes, landing pages, or lightweight micro-tools.",
    },
    {
        "id": "blank",
        "name": "blank (Standard SPA)",
        "badge": "File-Based Routing + Server Actions",
        "description": "Fullstack SPA architecture with automatic file-based routing (pages/), layouts, and backend.py.\n    Best for full-featured applications, dashboards, and production projects.",
    },
]


def _interactive_select_template() -> str:
    """
    Render an interactive selector in the terminal using Questionary.
    Falls back to simple prompt if non-TTY.
    """
    if not sys.stdin.isatty():
        print("  Select a template:")
        for idx, t in enumerate(TEMPLATES, 1):
            print(f"    {idx}) {t['name']} - {t['badge']}")
        try:
            choice = input("  Choice [1-2]: ").strip()
            if choice == "1":
                return "base-blank"
            return "blank"
        except Exception:
            return "blank"

    try:
        import questionary
        from questionary import Style, Choice

        custom_style = Style([
            ('qmark', 'fg:#00ffff bold'),
            ('question', 'bold'),
            ('answer', 'fg:#00ff00 bold'),
            ('pointer', 'fg:#00ffff bold'),
            ('highlighted', 'fg:#00ffff bold'),
            ('selected', 'fg:#00ff00'),
            ('separator', 'fg:#cc5454'),
            ('instruction', 'fg:#888888'),
            ('text', ''),
        ])

        choices = []
        for t in TEMPLATES:
            desc = t['description'].strip().replace('\n', '\n      ')
            title = [
                ('class:text', f"{t['name']} "),
                ('class:instruction', f"[{t['badge']}]\n      "),
                ('class:instruction', f"{desc}\n"),
            ]
            choices.append(Choice(title=title, value=t['id']))

        print()
        answer = questionary.select(
            "Select a project template:",
            choices=choices,
            style=custom_style,
            instruction="(Use arrow keys ↑/↓ or j/k to navigate, Enter to select)"
        ).ask()
        
        if answer is None:
            raise KeyboardInterrupt()

        print(_c("✔ ", _GREEN, _BOLD) + _c("Project template: ", _BOLD, _WHITE) + _c(answer, _CYAN, _BOLD) + "\n")
        return answer
    except ImportError:
        # Fallback if questionary is somehow not available
        print("  Select a template:")
        for idx, t in enumerate(TEMPLATES, 1):
            print(f"    {idx}) {t['name']} - {t['badge']}")
        try:
            choice = input("  Choice [1-2]: ").strip()
            if choice == "1":
                return "base-blank"
            return "blank"
        except Exception:
            return "blank"


# ---------------------------------------------------------------------------
# Generator Entry Point
# ---------------------------------------------------------------------------

def run(project_name: str | None = None, base_dir: str = ".", template: str | None = None) -> int:
    """
    Scaffold a new RailUI project.

    Args:
        project_name: The name of the project (used as directory name and title).
        base_dir: Parent directory where the project folder will be created.
        template: Pre-selected template ID ('base-blank' or 'blank'). If None, asks interactively.

    Returns:
        int: Exit code (0 = success).
    """
    print(_c("\n  RailUI Project Generator", _CYAN, _BOLD) + "\n")

    if not project_name:
        if not sys.stdin.isatty():
            print(_c("[railui new] Error: project name is required.", _RED, _BOLD))
            return 1
        try:
            import questionary
            from questionary import Style

            custom_style = Style([
                ('qmark', 'fg:#00ffff bold'),
                ('question', 'bold'),
                ('answer', 'fg:#00ff00 bold'),
            ])
            
            project_name = questionary.text("Project name:", style=custom_style).ask()
            if project_name is None:
                raise KeyboardInterrupt()
                
            project_name = project_name.strip()
            if not project_name:
                print(_c("\n[railui new] Error: project name cannot be empty.", _RED, _BOLD))
                return 1
            print()
        except ImportError:
            try:
                sys.stdout.write(_c("? ", _CYAN, _BOLD) + _c("Project name: ", _BOLD, _WHITE))
                sys.stdout.flush()
                project_name = input().strip()
                if not project_name:
                    print(_c("\n[railui new] Error: project name cannot be empty.", _RED, _BOLD))
                    return 1
                print()
            except KeyboardInterrupt:
                print("\n")
                return 1
            except Exception:
                return 1
        except KeyboardInterrupt:
            print("\n")
            return 1
        except Exception:
            return 1

    project_dir = os.path.join(base_dir, project_name)
    title = project_name.replace("-", " ").replace("_", " ").title()

    if os.path.exists(project_dir):
        print(_c(f"[railui new] Error: directory '{project_dir}' already exists.", _RED, _BOLD))
        return 1

    if not template:
        try:
            template = _interactive_select_template()
        except KeyboardInterrupt:
            print("\n")
            return 1
    else:
        template = template.lower()
        if template not in ("base-blank", "blank"):
            print(_c(f"[railui new] Warning: unknown template '{template}', falling back to 'blank'", _YELLOW))
            template = "blank"
        else:
            print(_c("✔ ", _GREEN, _BOLD) + _c("Project template: ", _BOLD, _WHITE) + _c(template, _CYAN, _BOLD) + "\n")

    os.makedirs(project_dir, exist_ok=True)
    public_dir = os.path.join(project_dir, "public")
    os.makedirs(public_dir, exist_ok=True)

    def write(path: str, content: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.replace("{title}", title))
        rel = os.path.relpath(path, base_dir).replace(os.sep, "/")
        print(f"  {_c('create', _GREEN)}  {rel}")

    write(os.path.join(project_dir, "railui.config.json"), _CONFIG_JSON)
    write(os.path.join(project_dir, "requirements.txt"), _REQUIREMENTS)
    write(os.path.join(project_dir, ".gitignore"), _GITIGNORE)
    write(os.path.join(project_dir, "public", "robots.txt"), "User-agent: *\nAllow: /\n")

    if template == "base-blank":
        # Minimal in-place routing template
        write(os.path.join(project_dir, "main.py"), _BASE_BLANK_MAIN_PY)
    else:
        # Standard fullstack SPA template with file-based routing
        pages_dir = os.path.join(project_dir, "pages")
        os.makedirs(pages_dir, exist_ok=True)

        write(os.path.join(project_dir, "main.py"), _BLANK_MAIN_PY)
        write(os.path.join(project_dir, "backend.py"), _BLANK_BACKEND_PY)
        write(os.path.join(project_dir, "layout.py"), _BLANK_LAYOUT_PY)
        write(os.path.join(project_dir, "pages", "index.py"), _BLANK_INDEX_PAGE)
        write(os.path.join(project_dir, "pages", "actions_demo.py"), _BLANK_ACTIONS_DEMO_PAGE)
        write(os.path.join(project_dir, "pyrightconfig.json"), _PYRIGHTCONFIG)

    print(f"""
  {_c('SUCCESS', _GREEN, _BOLD)} Project '{project_name}' created successfully!

  Next steps:

    {_c('cd ' + project_name, _CYAN)}
    {_c('railui dev', _CYAN)}
""")
    return 0
