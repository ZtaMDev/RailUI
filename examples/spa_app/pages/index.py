from railui.all import *
from layout import Layout

def page() -> Component:
    return Layout(
        Head(title="Home | RailUI SPA"),
        Container(
            Text("Welcome to RailUI File-Based Routing", class_name="text-4xl font-extrabold text-gray-900 mb-4 block"),
            Text("This app features client-side SPA routing automatically generated from the pages directory.", class_name="text-lg text-gray-600 mb-8 block"),
            Button("Click me for an alert", on_click=alert("Hello from file-based index!"), class_name="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg transition shadow-md"),
            class_name="flex flex-col items-start"
        )
    )
