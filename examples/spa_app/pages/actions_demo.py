from railui.all import *
from layout import Layout

@server_action
def save_user(name: str):
    print(f"\n[Backend] Saving user: {name} to the database...\n")
    return {"status": "ok", "message": f"User {name} saved successfully!"}

def page() -> Component:
    username, setUsername = createSignal("")
    status_msg, setStatusMsg = createSignal("")

    return Layout(
        Head(title="Server Actions | RailUI"),
        Container(
            Text("Server Actions Demo", class_name="text-4xl font-black text-gray-900 block mb-4"),
            Text("Call Python functions directly from your frontend components.", class_name="text-gray-500 mb-8 block"),

            Container(
                Input(
                    placeholder="Enter username...",
                    bind=username,
                    class_name="px-4 py-2 border rounded-l-lg w-64"
                ),
                Button(
                    "Save User (RPC)",
                    on_click=save_user(username()).then(lambda res: setStatusMsg(res.message)),
                    class_name="px-4 py-2 bg-blue-600 text-white font-bold rounded-r-lg hover:bg-blue-700"
                ),
                class_name="flex items-center mb-6",
            ),

            Show(
                Text(
                    status_msg(),
                    class_name="p-4 bg-green-100 text-green-800 rounded-lg font-mono text-sm"
                ),
                when=status_msg() != "",
            )
        )
    )
