from railui.all import *
from layout import Layout

# Define server actions (these run on the backend Python server)
@server_action
def save_user(name: str):
    print(f"\n[Backend] Saving user: {name} to the database...\n")
    return {"status": "ok", "message": f"User {name} saved successfully!"}

@server_action
def generate_name():
    import random
    names = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank"]
    return {"name": random.choice(names)}

@server_action
def get_server_time():
    """Returns the current server timestamp — a server-only operation."""
    from datetime import datetime
    return {"time": datetime.now().isoformat(), "source": "backend.py"}

def page() -> Component:
    username, setUsername = createSignal("")
    # --- useAction hook: manages pending/result/error signals automatically ---
    # Returns: (trigger_fn, pending_getter, result_getter, error_getter)
    save_action, saving, save_result, save_error = useAction(save_user)
    gen_action,  gen_pending, gen_result, gen_error = useAction(generate_name)
    server_time_action, server_time_pending, server_time_result, server_time_error = useAction(get_server_time)

    return Layout(
        Head(title="Server Actions | RailUI"),
        Container(
            Text("Server Actions Demo", class_name="text-4xl font-black text-gray-900 block mb-4"),
            Text("useAction() gives you reactive pending/result/error states — no boilerplate.", class_name="text-gray-500 mb-8 block"),

            # --- useAction: save user with reactive loading/result/error ---
            Container(
                Input(
                    placeholder="Enter username...",
                    bind=username,
                    class_name="px-4 py-2 border border-gray-300 rounded-l-lg w-64 focus:outline-none focus:ring-2 focus:ring-blue-500",
                ),
                Button(
                    "Save User",
                    on_click=save_action(username()),
                    disabled=saving(),
                    class_name="px-4 py-2 bg-blue-600 text-white font-bold rounded-r-lg hover:bg-blue-700 disabled:opacity-50 transition",
                ),
                class_name="flex items-center mb-4",
            ),

            # Saving indicator
            Show(
                Text("Saving...", class_name="text-blue-500 text-sm mb-2 block animate-pulse"),
                when=saving(),
            ),

            # Success result
            Show(
                Text(save_result().message, class_name="p-4 bg-green-100 text-green-800 rounded-lg font-mono text-sm block mb-4"),
                when=save_result(),
            ),

            # Error display
            Show(
                Text(save_error(), class_name="p-4 bg-red-100 text-red-800 rounded-lg font-mono text-sm block mb-4"),
                when=save_error(),
            ),

            # --- Divider ---
            Container(class_name="my-8 border-t border-gray-200"),

            # --- useAction: generate random name ---
            Text("Generate Random Name", class_name="text-xl font-bold text-gray-800 block mb-4"),
            Container(
                Button(
                    "Generate",
                    on_click=gen_action(),
                    disabled=gen_pending(),
                    class_name="px-4 py-2 bg-purple-600 text-white font-bold rounded-lg hover:bg-purple-700 disabled:opacity-50 transition",
                ),
                Show(
                    Text(gen_result().name, class_name="ml-4 text-lg font-bold text-purple-700"),
                    when=gen_result(),
                ),
                class_name="flex items-center gap-4",
            ),
            Show(
                Text(gen_error(), class_name="mt-2 text-sm text-red-600 block"),
                when=gen_error(),
            ),
            Button(
                "Get Server Time",
                on_click=server_time_action(),
                class_name="mt-10px px-4 py-2 bg-purple-600 text-white font-bold rounded-lg hover:bg-purple-700 disabled:opacity-50 transition",
            ),
            Show(
                Text(server_time_result().time, class_name="mt-10px ml-4 text-lg font-bold text-purple-700"),
                when=server_time_result(),
            ),

            class_name="max-w-xl mx-auto py-16 px-4"
        )
    )
