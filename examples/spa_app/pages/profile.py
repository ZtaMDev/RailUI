from railui.all import *
from layout import Layout
from store import user_store

def page() -> Component:
    return Layout(
        Head(title="Profile | RailUI SPA"),
        Container(
            Text("User Profile", class_name="text-3xl font-bold text-gray-900 mb-6 block"),
            
            Form(
                Container(
                    Label("Name", class_name="text-sm font-semibold text-gray-700 mb-1 block"),
                    Input(type="text", bind=user_store.name, class_name="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition")
                ),
                Container(
                    Label("Role", class_name="text-sm font-semibold text-gray-700 mb-1 block"),
                    Input(type="text", bind=user_store.role, class_name="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition")
                ),
                Button("Save Settings", type="button", on_click=log("Saved", user_store.name()), class_name="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-lg shadow mt-4 transition"),
                
                class_name="flex flex-col gap-4 max-w-md bg-white p-6 rounded-xl shadow-sm border border-gray-200"
            )
        )
    )
