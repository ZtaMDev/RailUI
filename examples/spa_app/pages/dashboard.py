from railui.all import *
from layout import Layout

def page() -> Component:
    posts, setPosts = createSignal([])
    loading, setLoading = createSignal(True)

    useFetch(
        url="https://jsonplaceholder.typicode.com/posts?_limit=4",
        on_success=setPosts,
        loading=setLoading
    )

    return Layout(
        Head(title="Dashboard | RailUI SPA"),
        Container(
            Text("Dashboard", class_name="text-3xl font-bold text-gray-900 mb-6 block"),
            
            Suspense(
                Container(
                    Each(
                        items=posts,
                        render_fn=lambda item, index: Container(
                            Text(item.title, class_name="font-bold text-lg text-gray-900 mb-2 block capitalize"),
                            Text(item.body, class_name="text-gray-600 text-sm line-clamp-2"),
                            class_name="p-6 bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition cursor-pointer"
                        )
                    ),
                    class_name="grid grid-cols-2 gap-6 w-full"
                ),
                fallback=Container(
                    Text("Loading async data...", class_name="text-purple-500 font-semibold animate-pulse"),
                    class_name="p-12 border-2 border-dashed border-gray-300 rounded-xl flex justify-center items-center"
                ),
                loading=loading()
            )
        )
    )
