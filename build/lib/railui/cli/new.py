"""
railui/cli/new.py

``railui new <project-name>`` — scaffold a new RailUI project.
"""
from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
_MAIN_PY = '''\
import os
from railui.all import *
from layout import Layout

app = App(title="{title}")
app.discover_pages(os.path.join(os.path.dirname(__file__), "pages"))


def not_found() -> Component:
    return Layout(
        Head(title="404 | {title}"),
        Container(
            Text("404", class_name="text-8xl font-black text-gray-200 block mb-4"),
            Text("Page Not Found", class_name="text-2xl font-bold text-gray-800 block mb-6"),
            Link("Go home", href="/", class_name="px-6 py-3 bg-gray-900 text-white rounded-lg"),
            class_name="flex flex-col items-center justify-center py-32 text-center",
        ),
    )


app.set_not_found(not_found)

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "dist")
    app.build(out_dir=out_dir)
    print(f"Build complete. Output written to {{out_dir}}/")
'''

_LAYOUT_PY = '''\
from railui.all import *


def Layout(*children: Component) -> Component:
    """Shared page layout wrapper."""
    return Container(
        # Nav
        Container(
            Link("{title}", href="/", class_name="font-bold text-lg"),
            Container(
                Link("Home", href="/", class_name="text-gray-600 hover:text-gray-900 transition"),
                class_name="flex gap-6",
            ),
            class_name="flex items-center justify-between max-w-5xl mx-auto px-6 py-4",
        ),
        class_name="min-h-screen bg-gray-50 font-sans",
        # Slot for page content
        *[Container(child, class_name="max-w-5xl mx-auto px-6 py-8") for child in children],
    )
'''

_INDEX_PAGE = '''\
from railui.all import *
from layout import Layout


def page() -> Component:
    count, setCount = createSignal(0)

    return Layout(
        Head(title="Home | {title}"),
        Container(
            Text("Welcome to {title}", class_name="text-4xl font-black text-gray-900 block mb-4"),
            Text("Built with RailUI — Python-first, zero-runtime.", class_name="text-gray-500 mb-8 block"),
            Container(
                Button("-", on_click=setCount(count() - 1), class_name="px-4 py-2 bg-gray-200 rounded-l-lg text-xl font-bold"),
                Text(count(), class_name="px-6 py-2 bg-white border-y text-xl font-mono"),
                Button("+", on_click=setCount(count() + 1), class_name="px-4 py-2 bg-gray-200 rounded-r-lg text-xl font-bold"),
                class_name="flex items-center",
            ),
        ),
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
.venv/
.env
"""

_PYRIGHTCONFIG = """\
{
  "pythonVersion": "3.11",
  "extraPaths": ["."],
  "exclude": ["dist"]
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
    title = project_name.replace("-", " ").replace("_", " ").title()

    if os.path.exists(project_dir):
        print(f"[railui new] Error: directory '{project_dir}' already exists.")
        return 1

    os.makedirs(pages_dir, exist_ok=True)

    def write(path: str, content: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.replace("{title}", title))
        rel = os.path.relpath(path, base_dir)
        print(f"  create  {rel}")

    print(f"\n  Scaffolding RailUI project '{project_name}'…\n")
    write(os.path.join(project_dir, "main.py"), _MAIN_PY)
    write(os.path.join(project_dir, "layout.py"), _LAYOUT_PY)
    write(os.path.join(project_dir, "pages", "index.py"), _INDEX_PAGE)
    write(os.path.join(project_dir, "requirements.txt"), _REQUIREMENTS)
    write(os.path.join(project_dir, ".gitignore"), _GITIGNORE)
    write(os.path.join(project_dir, "pyrightconfig.json"), _PYRIGHTCONFIG)

    print(f"""
  ✓ Done! Next steps:

    cd {project_name}
    pip install -r requirements.txt
    railui dev
""")
    return 0
