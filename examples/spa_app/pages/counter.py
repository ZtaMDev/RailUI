from railui.all import *
from layout import Layout

def page() -> Component:
    count, setCount = createSignal(0)
    double_count = useComputed(lambda: count() * 2)

    # on_mount: runs once when this route loads
    on_mount(slide_in_up("counter-card", duration=400))

    return Layout(
        Head(title="Counter | RailUI SPA"),
        Container(
            Text("Reactivity & Animations", class_name="text-3xl font-bold text-gray-900 mb-6 block"),
            
            Container(
                # Count display
                Container(
                    Text("Count", class_name="text-sm font-semibold text-gray-500 uppercase tracking-wide block mb-1"),
                    Text(count(), class_name="text-5xl font-black text-purple-600"),
                    class_name="text-center"
                ),
                Container(
                    Text("Double", class_name="text-sm font-semibold text-gray-500 uppercase tracking-wide block mb-1"),
                    Text(double_count, class_name="text-3xl font-bold text-blue-500"),
                    class_name="text-center"
                ),
                
                # Controls
                Container(
                    Button(
                        "-1",
                        on_click=runSequence(setCount(count() - 1), shake("counter-card")),
                        class_name="px-8 py-3 bg-gray-100 hover:bg-gray-200 rounded-l-xl font-black text-xl transition"
                    ),
                    Button(
                        "Reset",
                        on_click=runSequence(setCount(0), fade_out("counter-card"), set_timeout(slide_in_up("counter-card"), 300)),
                        class_name="px-8 py-3 bg-white hover:bg-gray-50 font-semibold text-gray-600 border-x border-gray-200 transition"
                    ),
                    Button(
                        "+1",
                        on_click=runSequence(setCount(count() + 1), scale_in("counter-card", duration=200)),
                        class_name="px-8 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-r-xl font-black text-xl transition"
                    ),
                    class_name="flex flex-row shadow-sm mt-8"
                ),

                # Demo buttons for more animations
                Container(
                    Text("Animation Demos", class_name="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3 block"),
                    Container(
                        Button("Bounce", on_click=bounce("counter-card", iterations=3), class_name="px-4 py-2 bg-pink-500 hover:bg-pink-600 text-white rounded-lg text-sm font-bold shadow transition"),
                        Button("Spin", on_click=spin("counter-card", duration=600, iterations=2), class_name="px-4 py-2 bg-yellow-400 hover:bg-yellow-500 text-gray-900 rounded-lg text-sm font-bold shadow transition"),
                        Button("Slide Left", on_click=slide_in_left("counter-card", duration=400), class_name="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-bold shadow transition"),
                        Button("Pulse 3x", on_click=pulse("counter-card", iterations=3, duration=400), class_name="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-bold shadow transition"),
                        class_name="flex flex-row gap-3 flex-wrap"
                    ),
                    class_name="mt-6"
                ),

                id="counter-card",
                class_name="flex flex-col items-center gap-6 p-10 bg-white rounded-2xl shadow-md border border-gray-100"
            )
        )
    )
