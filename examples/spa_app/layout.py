from railui.all import *

def Navbar() -> Component:
    return Container(
        Container(
            Text("RailUI", class_name="font-black text-2xl text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-500"),
            Container(
                Link("Home", href="/", class_name="text-gray-600 hover:text-purple-600 font-medium transition"),
                Link("Counter", href="/counter", class_name="text-gray-600 hover:text-purple-600 font-medium transition"),
                Link("Dashboard", href="/dashboard", class_name="text-gray-600 hover:text-purple-600 font-medium transition"),
                Link("Profile", href="/profile", class_name="text-gray-600 hover:text-purple-600 font-medium transition"),
                Link("Invalid", href="/nowhere", class_name="text-gray-400 hover:text-red-500 font-medium transition"),
                class_name="flex flex-row items-center gap-6"
            ),
            class_name="flex flex-row justify-between items-center w-full max-w-5xl mx-auto"
        ),
        class_name="w-full bg-white shadow-sm p-4 border-b border-gray-200 sticky top-0 z-50"
    )

def Layout(*children: Component) -> Component:
    return Page(
        Navbar(),
        Container(
            *children,
            class_name="w-full max-w-5xl mx-auto p-8"
        ),
        class_name="min-h-screen bg-gray-50 flex flex-col"
    )
