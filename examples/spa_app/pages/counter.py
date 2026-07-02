from railui.all import *
from layout import Layout

def page() -> Component:
    count, setCount = createSignal(0)
    
    # Example of a computed signal
    double_count = useComputed(lambda: count() * 2)

    return Layout(
        Head(title="Counter | RailUI SPA"),
        Container(
            Text("Reactivity Test", class_name="text-3xl font-bold text-gray-900 mb-6 block"),
            
            Container(
                Text("Count: ", class_name="font-semibold text-gray-600"),
                Text(count(), class_name="text-4xl font-black text-purple-600"),
                class_name="mb-2"
            ),
            
            Container(
                Text("Double: ", class_name="font-semibold text-gray-600"),
                Text(double_count, class_name="text-2xl font-bold text-blue-500"),
                class_name="mb-6"
            ),
            
            Container(
                Button("-1", on_click=setCount(count() - 1), class_name="px-6 py-2 bg-gray-200 hover:bg-gray-300 rounded-l-lg font-bold text-lg transition"),
                Button("+1", on_click=setCount(count() + 1), class_name="px-6 py-2 bg-gray-200 hover:bg-gray-300 rounded-r-lg border-l border-white font-bold text-lg transition"),
                class_name="flex flex-row shadow-sm"
            )
        )
    )
