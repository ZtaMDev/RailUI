import os
import sys

# Add the root directory to path to import railui
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from railui.all import *
from layout import Layout

app = App(title="RailUI File-Based Routing Demo")

# File-based routing magically maps everything in "pages" to URL routes!
# /pages/index.py -> /
# /pages/dashboard.py -> /dashboard
app.discover_pages(os.path.join(os.path.dirname(__file__), "pages"))

def not_found() -> Component:
    return Layout(
        Head(title="404 Not Found"),
        Container(
            Text("404", class_name="text-8xl font-black text-gray-200 block mb-4"),
            Text("Page Not Found", class_name="text-2xl font-bold text-gray-800 block mb-6"),
            Link("Go back home", href="/", class_name="px-6 py-3 bg-gray-900 text-white font-semibold rounded-lg hover:bg-gray-800 transition"),
            class_name="flex flex-col items-center justify-center py-20 text-center"
        )
    )

app.set_not_found(not_found)

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "dist")
    app.build(out_dir=out_dir)
