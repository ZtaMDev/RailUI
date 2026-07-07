from railui.all import *
from layout import Layout

@server_action
def save_user(name: str):
    """A backend Python function that saves a user."""
    # This runs purely on the server!
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
            #TODO: FIX THIS BECAUSE ITS NOT WORKING, BAD VALUE PROSESSING AND ALSO THE ACTIONS API ITS BROKEN
            Container(
                Input(
                    placeholder="Enter username...", 
                    value=username(),
                    on_input=setUsername(username.value),
                    class_name="px-4 py-2 border rounded-l-lg w-64"
                ),
                Button(
                    "Save User (RPC)", 
                    # The magic: Call the python function directly!
                    # We wrap it in a custom JS snippet just to handle the Promise result
                    on_click=RawJS(
                        save_user(username()).to_js() + 
                        f".then(res => {{ {setStatusMsg(RawJS('res.message')).to_js()} }})"
                    ),
                    class_name="px-4 py-2 bg-blue-600 text-white font-bold rounded-r-lg hover:bg-blue-700"
                ),
                class_name="flex items-center mb-6",
            ),
            
            # Show the success message from the backend
            Show(
                when=status_msg() != "",
                fallback=None,
                children=Text(
                    status_msg(),
                    class_name="p-4 bg-green-100 text-green-800 rounded-lg font-mono text-sm"
                )
            )
        )
    )
