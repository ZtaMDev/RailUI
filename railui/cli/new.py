"""
railui/cli/new.py

``railui new <project-name>`` — scaffold a new RailUI project.
"""
from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Templates
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

_MAIN_PY = '''\
import os
from railui.all import *
from layout import Layout

app = App(title="{title}")
# Discover all pages under pages/ directory
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

_LAYOUT_PY = '''\
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

_INDEX_PAGE = '''\
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

_ACTIONS_DEMO_PAGE = '''\
from railui.all import *
from layout import Layout


@server_action
def greet_user(name: str):
    """Python function running on backend FastAPI server."""
    clean_name = name.strip() if name else "Developer"
    return {"status": "ok", "message": f"Hello {clean_name}! Server action executed successfully in Python."}


def page() -> Component:
    username, setUsername = createSignal("")
    status_msg, setStatusMsg = createSignal("")

    return Layout(
        Head(title="Server Actions | {title}"),
        Container(
            Text("Server Actions Demo", class_name="text-4xl font-black text-gray-900 block mb-2"),
            Text("Call Python backend functions directly from frontend component events.", class_name="text-gray-500 mb-8 block"),
            
            Container(
                Input(
                    placeholder="Enter your name...", 
                    value=username(),
                    on_input=setUsername(RawJS("e.target.value")),
                    class_name="px-4 py-2 border border-gray-300 rounded-l-lg w-64 focus:outline-none focus:ring-2 focus:ring-purple-500"
                ),
                Button(
                    "Call Python Action", 
                    on_click=RawJS(
                        greet_user(username()).to_js() + 
                        f".then(res => {{ {setStatusMsg(RawJS('res.message')).to_js()} }})"
                    ),
                    class_name="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-r-lg transition shadow-md"
                ),
                class_name="flex items-center mb-6",
            ),
            
            Show(
                when=status_msg() != "",
                fallback=None,
                children=Text(
                    status_msg(),
                    class_name="p-4 bg-green-100 border border-green-200 text-green-800 rounded-lg font-mono text-sm block"
                )
            )
        )
    )
'''

_REQUIREMENTS = """\
railui
fastapi>=0.115
uvicorn[standard]>=0.30
watchdog>=4.0
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


def run(project_name: str, base_dir: str = ".") -> int:
    """
    Scaffold a new RailUI project.

    Args:
        project_name: The name of the project (used as directory name and title).
        base_dir: Parent directory where the project folder will be created.

    Returns:
        int: Exit code (0 = success).
    """
    project_dir = os.path.join(base_dir, project_name)
    pages_dir = os.path.join(project_dir, "pages")
    public_dir = os.path.join(project_dir, "public")
    title = project_name.replace("-", " ").replace("_", " ").title()

    if os.path.exists(project_dir):
        print(f"[railui new] Error: directory '{project_dir}' already exists.")
        return 1

    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(public_dir, exist_ok=True)

    def write(path: str, content: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.replace("{title}", title))
        rel = os.path.relpath(path, base_dir)
        print(f"  create  {rel}")

    print(f"\n  Scaffolding RailUI project '{project_name}'…\n")
    write(os.path.join(project_dir, "railui.config.json"), _CONFIG_JSON)
    write(os.path.join(project_dir, "main.py"), _MAIN_PY)
    write(os.path.join(project_dir, "layout.py"), _LAYOUT_PY)
    write(os.path.join(project_dir, "pages", "index.py"), _INDEX_PAGE)
    write(os.path.join(project_dir, "pages", "actions_demo.py"), _ACTIONS_DEMO_PAGE)
    write(os.path.join(project_dir, "requirements.txt"), _REQUIREMENTS)
    write(os.path.join(project_dir, ".gitignore"), _GITIGNORE)
    write(os.path.join(project_dir, "pyrightconfig.json"), _PYRIGHTCONFIG)
    
    # Create empty placeholder in public/
    write(os.path.join(project_dir, "public", "robots.txt"), "User-agent: *\nAllow: /\n")

    print(f"""
  -> Done! Next steps:

    cd {project_name}
    railui dev
""")
    return 0
