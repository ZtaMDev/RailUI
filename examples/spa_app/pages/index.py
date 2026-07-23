from railui.all import *
from layout import Layout

def page() -> Component:
    return Layout(
        Head(title="Home | RailUI SPA"),
        
        # Use the hero slot for a nice welcome banner
        SlotFill("hero", Container(
            Text("Welcome to the Future of Python UI!", class_name="text-3xl font-black text-white"),
            class_name="w-full bg-gradient-to-r from-blue-600 to-indigo-600 p-6 shadow-lg text-center"
        )),
        
        # These go to the default Unassigned slot (the body)
        Container(
            Text("Welcome to RailUI Named Slots", class_name="text-4xl font-extrabold text-gray-900 mb-4 block"),
            Text("This app features client-side SPA routing, server actions and Svelte-style slot components.", class_name="text-lg text-gray-600 mb-8 block"),
            Button("Click me for an alert", on_click=alert("Hello from file-based index!"), class_name="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg transition shadow-md"),
            class_name="flex flex-col items-start"
        ),
        
        # Override the default footer slot
        SlotFill("footer", Container(
            Text("Custom Index Footer. Built with RailUI in Python.", class_name="text-sm text-indigo-200 font-bold"),
            class_name="w-full p-6 bg-gray-900 text-center mt-auto"
        ))
    )
