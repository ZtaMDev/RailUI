from railui.all import *
from layout import Layout
from railui.core.namespaces import Math
def page() -> Component:
    # 1. Test useFetch Property Access
    user_data, setUserData = createSignal({})
    loading, setLoading = createSignal(True)

    useFetch(
        url="https://jsonplaceholder.typicode.com/users/1",
        on_success=setUserData,
        loading=setLoading
    )

    # 2. Test Component Lifecycle hooks (Show)
    show_details, setShowDetails = createSignal(False)

    # 3. Test Each Component Lifecycle hooks
    tasks, setTasks = createSignal([{"title": "Learn RailUI"}, {"title": "Build a SPA"}])

    # 4. Test Route Teardown (on_destroy)
    on_mount(log("Dashboard route mounted!"))
    on_destroy(log("Dashboard route destroyed! Cleaning up..."))

    return Layout(
        Head(title="Dashboard | RailUI SPA"),
        Container(
            Text("Advanced Data & Lifecycle", class_name="text-3xl font-bold text-gray-900 mb-6 block"),
            
            Suspense(
                Container(
                    # Demonstrating deep property access directly in Python thanks to AST enhancement
                    Text(user_data().name, class_name="text-xl font-bold block mb-1"),
                    Text(user_data().email, class_name="text-gray-500 mb-4 block"),
                    Text(user_data().company.name, class_name="text-sm font-mono bg-gray-100 p-1 rounded"),
                    
                    Button(
                        "Toggle Details",
                        on_click=setShowDetails(~show_details()),
                        class_name="mt-6 px-4 py-2 bg-purple-600 text-white rounded shadow hover:bg-purple-700 block"
                    ),
                    
                    Show(
                        Container(
                            Text("City: ", class_name="font-bold"),
                            Text(user_data().address.city),
                            class_name="p-4 mt-4 bg-purple-50 rounded-lg text-purple-900 border border-purple-100"
                        ),
                        when=show_details(),
                        # The new lifecycle hooks for control-flow components!
                        on_mount=log("Details MOUNTED (first render)"),
                        on_update=log("Details UPDATED (visibility toggled)"),
                        on_unmount=log("Details UNMOUNTED (hidden)")
                    ),
                    class_name="p-8 bg-white rounded-2xl shadow-sm border border-gray-100"
                ),
                
                # Each List Test
                Container(
                    Text("Tasks List (Each Lifecycle Test)", class_name="text-xl font-bold block mb-4 text-gray-800"),
                    Button(
                        "Add Task",
                        on_click=setTasks(Array.append(tasks(), {"title": "New Task " + Math.floor(Math.random() * 100)})),
                        class_name="mb-4 px-4 py-2 bg-blue-600 text-white rounded shadow hover:bg-blue-700 block"
                    ),
                    Each(
                        items=tasks,
                        render_fn=lambda item, index: Container(
                            Text(index, class_name="font-mono text-gray-400 mr-2"),
                            Text(item.title, class_name="font-semibold"),
                            class_name="p-3 mb-2 bg-gray-50 rounded border border-gray-200"
                        ),
                        on_mount=log("Each list MOUNTED!"),
                        on_update=log("Each list UPDATED! (item added)")
                    ),
                    class_name="p-8 bg-white rounded-2xl shadow-sm border border-gray-100 mt-6"
                ),
                fallback=Container(
                    Text("Fetching user data...", class_name="text-purple-500 font-semibold animate-pulse"),
                    class_name="p-12 border-2 border-dashed border-gray-300 rounded-xl flex justify-center items-center"
                ),
                loading=loading()
            )
        )
    )
