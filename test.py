from railui.all import *

def main():
    # Define state
    count, setCount = createSignal(0)
    name, setName = createSignal("World")
    
    # Derived state
    double_count = useComputed(lambda: count() * 2)
    
    # Side effects
    createEffect(log('Counter updated! New value:', count()))
    
    # Build page component
    app_page = Page(
        Container(
            Text("RailUI Demo", class_name="text-4xl font-extrabold text-center mb-[20px] text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600"),
            
            # Counter Example
            Container(
                Container(
                    Text("Counter: "),
                    Text(count(), class_name="font-bold text-blue-600"),
                    Text(" | Double: "),
                    Text(double_count, class_name="font-bold text-green-600"),
                    class_name="text-2xl mb-4"
                ),
                Container(
                    Button(
                        "+", 
                        on_click=runSequence(setCount(count() + 1), log("Incremented to:", count())),
                        class_name="px-6 py-2 bg-blue-500 text-white rounded-lg shadow mr-2 transition",
                        hover_class="bg-blue-600"
                    ),
                    Button(
                        "-", 
                        on_click=runSequence(setCount(count() - 1), log("Decremented to:", count())),
                        class_name="px-6 py-2 bg-red-500 text-white rounded-lg shadow transition",
                        hover_class="bg-red-600"
                    ),
                    class_name="flex"
                ),
                class_name="p-6 border border-gray-200 rounded-xl shadow-sm mb-6 bg-white transition",
                class_list={
                    "border-red-500 bg-red-50": count() < 0
                }
            ),
            
            # Two-way binding Example
            Container(
                Container(
                    Text("Greeting: Hello, "),
                    Text(name(), class_name="font-bold text-purple-600"),
                    Text("!"),
                    class_name="text-2xl mb-4"
                ),
                Input(bind=name, type="text", class_name="border border-gray-300 p-3 rounded-lg w-full focus:outline-none transition", placeholder="Enter your name"),
                class_name="p-6 border border-gray-200 rounded-xl shadow-sm bg-white"
            ),
            
            class_name="max-w-2xl mx-auto p-12 bg-gray-50 min-h-screen font-sans"
        )
    )
    
    # Compile the app
    compile_app(app_page, output_dir="test")

if __name__ == "__main__":
    main()
