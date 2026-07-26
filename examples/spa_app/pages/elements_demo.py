"""
elements_demo.py — Comprehensive showcase of every RailUI UI component.

Route: /elements_demo
"""
from railui.all import *
from layout import Layout


# ── Server Actions ────────────────────────────────────────────────────────────

@server_action
def echo_message(text: str, repeat: Any = 1):
    """Echo a message back from the Python backend, optionally repeated."""
    if not text or not str(text).strip():
        return {"ok": False, "output": "⚠️ Empty input — type something first!"}
    try:
        repeat_num = int(repeat)
    except (ValueError, TypeError):
        repeat_num = 1
    clean = str(text).strip()
    result = " · ".join([clean] * max(1, min(repeat_num, 10)))
    return {
        "ok": True,
        "output": result,
        "length": len(result),
        "words": len(clean.split()),
    }


@server_action
def generate_table(rows: Any, cols: Any):
    """Generate a dynamic multiplication table on the backend."""
    try:
        r_num = int(rows)
    except (ValueError, TypeError):
        r_num = 4
    try:
        c_num = int(cols)
    except (ValueError, TypeError):
        c_num = 4
    r_num = max(1, min(r_num, 12))
    c_num = max(1, min(c_num, 12))
    table = []
    for r in range(1, r_num + 1):
        row_data = []
        for c in range(1, c_num + 1):
            row_data.append(str(r * c))
        table.append(row_data)
    return {"rows": r_num, "cols": c_num, "table": table}


@server_action
def get_color_palette(theme: str):
    """Return a colour palette for a given theme name."""
    palettes = {
        "ocean":    ["#0ea5e9", "#0284c7", "#0369a1", "#075985", "#0c4a6e"],
        "forest":   ["#22c55e", "#16a34a", "#15803d", "#166534", "#14532d"],
        "sunset":   ["#f97316", "#ea580c", "#dc2626", "#c2410c", "#9a3412"],
        "lavender": ["#a78bfa", "#8b5cf6", "#7c3aed", "#6d28d9", "#5b21b6"],
    }
    colors = palettes.get(theme.lower(), palettes["ocean"])
    return {"theme": theme, "colors": colors}


# ── Page ─────────────────────────────────────────────────────────────────────

def page() -> Component:
    # ── Signals ───────────────────────────────────────────────────────────────
    show_details,   set_show_details   = createSignal(False)
    counter,        set_counter        = createSignal(0)
    text_input,     set_text_input     = createSignal("")
    repeat_count,   set_repeat_count   = createSignal(3)
    selected_tab,   set_selected_tab   = createSignal("typography")
    progress_val,   set_progress_val   = createSignal(40)
    table_rows,     set_table_rows     = createSignal(4)
    table_cols,     set_table_cols     = createSignal(4)
    selected_theme, set_selected_theme = createSignal("ocean")
    items_list,     set_items_list     = createSignal([
        {"id": 1, "name": "Signal-driven Lists", "tag": "reactive", "done": False},
        {"id": 2, "name": "Server Actions",       "tag": "backend",  "done": False},
        {"id": 3, "name": "CSS Animations",       "tag": "ui",       "done": False},
        {"id": 4, "name": "File-based Routing",   "tag": "routing",  "done": False},
        {"id": 5, "name": "Zero JS runtime",      "tag": "perf",     "done": False},
    ])

    # ── useAction hooks ───────────────────────────────────────────────────────
    run_echo,    echo_pending,   echo_result,   echo_error   = useAction(echo_message)
    run_table,   table_pending,  table_result,  table_error  = useAction(generate_table)
    run_palette, pal_pending,    pal_result,    pal_error    = useAction(get_color_palette)

    # ── Helper: section wrapper ───────────────────────────────────────────────
    def Section(title: str, *children, badge: str = "") -> Component:
        return Container(
            Container(
                H2(title, class_name="text-xl font-bold text-gray-900"),
                Badge(badge, variant="info", class_name="ml-3") if badge else Text(""),
                class_name="flex items-center mb-4",
            ),
            *children,
            class_name="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6",
        )

    # ─────────────────────────────────────────────────────────────────────────
    # BUILD PAGE
    # ─────────────────────────────────────────────────────────────────────────
    return Layout(
        Head(
            title="Elements Demo · RailUI",
            meta={"description": "Comprehensive showcase of every RailUI component"},
        ),

        # ── PAGE HERO ────────────────────────────────────────────────────────
        SlotFill("hero",
            Container(
                Img(
                    src="/hero.svg",
                    alt="RailUI hero banner",
                    class_name="w-full max-w-2xl mx-auto rounded-2xl shadow-2xl",
                    loading="eager",
                ),
                H1("Elements Showcase",
                   class_name="text-4xl font-black text-gray-900 mt-6 mb-2 text-center"),
                Paragraph(
                    "Every RailUI component, reactive signal, server action and "
                    "animation — in one place.",
                    class_name="text-gray-500 text-center max-w-xl mx-auto",
                ),
                class_name="w-full bg-gradient-to-b from-purple-50 to-white py-12 px-4 flex flex-col items-center",
            ),
        ),

        # ──────────────────────────────────────────────────────────────────────
        # BODY CONTENT
        # ──────────────────────────────────────────────────────────────────────

        # ── 1. TYPOGRAPHY ────────────────────────────────────────────────────
        Section("Typography",
            H1("Heading Level 1", class_name="text-4xl font-black text-gray-900 mb-1"),
            H2("Heading Level 2", class_name="text-3xl font-bold text-gray-800 mb-1"),
            H3("Heading Level 3", class_name="text-2xl font-semibold text-gray-700 mb-1"),
            H4("Heading Level 4", class_name="text-xl font-medium text-gray-600 mb-4"),
            Paragraph(
                "A ", Strong("strong"), " word, an ", Em("emphasised"), " phrase, "
                "some ", Mark("highlighted text"), ", ", Del("deleted"), " text, "
                "and ", Ins("inserted"), " text. With ",
                Abbr("API", title="Application Programming Interface"),
                " reference.",
                class_name="text-gray-700 leading-relaxed mb-3",
            ),
            Container(
                Code("from railui.all import *",
                     class_name="block bg-gray-900 text-green-400 px-4 py-3 rounded-xl text-sm font-mono"),
                class_name="mb-3",
            ),
            Blockquote(
                Paragraph("Python-first, zero-runtime — just ship.",
                          class_name="text-gray-700 italic"),
                class_name="border-l-4 border-purple-400 pl-4 py-1",
            ),
            Divider(label="More text utilities", class_name="my-4"),
            Container(
                Badge("New",    variant="success"),
                Badge("Beta",   variant="warning", class_name="ml-2"),
                Badge("Stable", variant="info",    class_name="ml-2"),
                Badge("Deprecated", variant="danger", class_name="ml-2"),
                Badge("Default",    class_name="ml-2"),
                class_name="flex flex-wrap gap-2 mt-2",
            ),
            badge="elements",
        ),

        # ── 2. MEDIA ─────────────────────────────────────────────────────────
        Section("Media — Images, SVG & Video",
            Container(
                # Img from public
                Figure(
                    Img(src="/icon.svg", alt="RailUI icon",
                        class_name="w-20 h-20 mx-auto",
                        loading="lazy"),
                    Figcaption("icon.svg — from public/",
                               class_name="text-xs text-gray-400 text-center mt-1"),
                    class_name="text-center",
                ),
                # Picture with multiple sources
                Figure(
                    Picture(
                        Source(srcset="/hero.svg", type="image/svg+xml"),
                        Img(src="/hero.svg", alt="Hero banner",
                            class_name="rounded-xl shadow w-full",
                            loading="lazy"),
                    ),
                    Figcaption("Picture + Source responsive component",
                               class_name="text-xs text-gray-400 mt-1"),
                ),
                class_name="grid grid-cols-1 gap-6",
            ),
            Divider(class_name="my-4"),
            # GIF treated as video-like element
            Container(
                H3("Animated GIF (demo.gif)", class_name="text-base font-semibold text-gray-700 mb-2"),
                Img(
                    src="/demo.gif",
                    alt="RailUI animation demo",
                    class_name="rounded-xl shadow mx-auto block max-w-xs",
                    loading="lazy",
                ),
                class_name="text-center",
            ),
            Divider(class_name="my-4"),
            # Canvas placeholder
            Container(
                H3("Canvas Element", class_name="text-base font-semibold text-gray-700 mb-2"),
                Canvas(
                    id="demo-canvas",
                    width=320, height=80,
                    class_name="rounded-xl border border-gray-200 w-full bg-gray-50",
                ),
                class_name="",
            ),
            badge="public/",
        ),

        # ── 3. SIGNALS & INTERACTIVITY ────────────────────────────────────────
        Section("Reactive Signals & Counter",
            Container(
                # Animated counter display
                Container(
                    id="counter-display",
                    class_name="text-7xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-500 text-center py-4",
                    children=Text(counter()),
                ),
                Container(
                    Button("−", on_click=set_counter(counter() - 1),
                           class_name="w-14 h-14 rounded-full bg-gray-100 hover:bg-gray-200 text-2xl font-bold text-gray-700 transition"),
                    Button("Reset", on_click=set_counter(0),
                           class_name="px-6 h-14 rounded-full bg-white border border-gray-200 hover:border-purple-400 text-gray-600 font-semibold transition mx-3"),
                    Button("+", on_click=set_counter(counter() + 1),
                           class_name="w-14 h-14 rounded-full bg-gradient-to-br from-purple-600 to-blue-500 text-white text-2xl font-bold shadow-lg hover:shadow-purple-200 transition"),
                    class_name="flex items-center justify-center gap-0",
                ),
                # Progress reacting to counter
                Container(
                    Paragraph("Counter → Progress bar (0–20 range):",
                              class_name="text-xs text-gray-400 mb-1"),
                    Progress(value=counter(), max=20,
                             class_name="w-full h-3 rounded-full [&::-webkit-progress-bar]:rounded-full [&::-webkit-progress-bar]:bg-gray-100 [&::-webkit-progress-value]:rounded-full [&::-webkit-progress-value]:bg-gradient-to-r [&::-webkit-progress-value]:from-purple-500 [&::-webkit-progress-value]:to-blue-500"),
                    class_name="mt-4",
                ),
                class_name="",
            ),
            badge="createSignal",
        ),

        # ── 4. SHOW / DETAILS / DIALOG ───────────────────────────────────────
        Section("Show, Details & Conditional UI",
            Button(
                Show("Hide Details", when=show_details(), fallback="Show Details"),
                on_click=set_show_details(~show_details()),
                class_name="px-5 py-2 rounded-lg bg-purple-600 text-white font-semibold hover:bg-purple-700 transition mb-4",
            ),
            Show(
                Container(
                    Paragraph("This panel is conditionally rendered using ",
                              Code("Show(when=signal())"),
                              " and a ", Code("fallback="), " text for the button.",
                              class_name="text-gray-600 mb-3"),
                    Container(
                        Avatar(alt="Alice", size="w-10 h-10"),
                        Avatar(alt="Bob Chen", size="w-10 h-10"),
                        Avatar(src="/icon.svg", alt="RailUI", size="w-10 h-10"),
                        class_name="flex gap-3 mb-3",
                    ),
                    Tooltip(
                        Badge("Hover me!", variant="info"),
                        text="CSS-only tooltip — no JS needed!",
                        position="right",
                    ),
                    class_name="bg-purple-50 rounded-xl p-4 border border-purple-100",
                ),
                when=show_details(),
                on_mount=slide_in_up("show-panel", duration=300),
                id="show-panel",
            ),
            Divider(label="HTML Details / Summary", class_name="my-4"),
            Details(
                Summary("What is RailUI?",
                        class_name="cursor-pointer font-semibold text-gray-800 py-2"),
                Paragraph(
                    "RailUI is a Python-first, zero-runtime fullstack web framework "
                    "that compiles Python DSL code into vanilla JS/HTML/CSS SPAs. "
                    "No Node.js required.",
                    class_name="text-gray-600 pt-2 pb-1",
                ),
                class_name="border border-gray-200 rounded-xl px-4",
            ),
            Details(
                Summary("How do server actions work?",
                        class_name="cursor-pointer font-semibold text-gray-800 py-2"),
                Paragraph(
                    "Decorate any Python function with @server_action. "
                    "RailUI automatically creates a FastAPI endpoint and a "
                    "typed JavaScript fetch() wrapper callable from your UI.",
                    class_name="text-gray-600 pt-2 pb-1",
                ),
                class_name="border border-gray-200 rounded-xl px-4 mt-2",
            ),
            badge="Show",
        ),

        # ── 5. EACH (reactive list) ────────────────────────────────────────────
        Section("Each — Reactive Lists",
            Container(
                H3("Feature Checklist", class_name="text-base font-semibold text-gray-700 mb-3"),
                Each(
                    items=items_list,
                    render_fn=lambda item, i: Container(
                        Container(
                            Badge(item.tag, variant="default",
                                  class_name="text-xs bg-gray-100 text-gray-600"),
                            class_name="",
                        ),
                        Span(item.name, class_name="text-gray-800 font-medium flex-1 ml-3"),
                        class_name="flex items-center bg-white border border-gray-100 rounded-xl px-4 py-3 shadow-sm mb-2 hover:border-purple-200 transition",
                    ),
                    class_name="",
                ),
                class_name="",
            ),
            badge="Each",
        ),

        # ── 6. FORMS & INPUTS ────────────────────────────────────────────────
        Section("Forms, Inputs & Select",
            Form(
                Container(
                    Label("Search / Echo text",
                          class_name="block text-sm font-medium text-gray-700 mb-1"),
                    Container(
                        Input(
                            type="text",
                            placeholder="Type something to echo...",
                            bind=text_input,
                            class_name="flex-1 px-4 py-2 border border-gray-200 rounded-l-xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm",
                        ),
                        Select(
                            Option("1×", value="1"),
                            Option("2×", value="2"),
                            Option("3×", value="3"),
                            Option("5×", value="5"),
                            bind=repeat_count,
                            class_name="border-t border-b border-gray-200 px-2 py-2 text-sm bg-white focus:outline-none",
                        ),
                        Button(
                            Show("Calling...", when=echo_pending(), fallback="Echo →"),
                            on_click=run_echo(text_input(), repeat_count()),
                            disabled=echo_pending(),
                            class_name="px-5 py-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-r-xl transition disabled:opacity-50",
                        ),
                        class_name="flex",
                    ),
                    class_name="mb-4",
                ),
                Container(
                    Label("Textarea", class_name="block text-sm font-medium text-gray-700 mb-1"),
                    Textarea(
                        placeholder="Multi-line input — type anything...",
                        rows=3,
                        class_name="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm resize-none",
                    ),
                    class_name="mb-4",
                ),
                Container(
                    Label("Colour theme", class_name="block text-sm font-medium text-gray-700 mb-1"),
                    Container(
                        Select(
                            Option("Ocean",    value="ocean"),
                            Option("Forest",   value="forest"),
                            Option("Sunset",   value="sunset"),
                            Option("Lavender", value="lavender"),
                            bind=selected_theme,
                            class_name="flex-1 px-4 py-2 border border-gray-200 rounded-l-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-purple-500",
                        ),
                        Button(
                            Show("Loading...", when=pal_pending(), fallback="Get Palette"),
                            on_click=run_palette(selected_theme()),
                            disabled=pal_pending(),
                            class_name="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-r-xl transition disabled:opacity-50",
                        ),
                        class_name="flex",
                    ),
                    class_name="mb-4",
                ),
                Fieldset(
                    Legend("Accessibility Demo", class_name="text-sm font-medium text-gray-700 px-1"),
                    Container(
                        Label("Name", for_="demo-name",
                              class_name="block text-sm text-gray-600 mb-1"),
                        Input(id="demo-name", type="text", placeholder="Your name",
                              class_name="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"),
                        class_name="mb-3",
                    ),
                    Container(
                        Label("Email", for_="demo-email",
                              class_name="block text-sm text-gray-600 mb-1"),
                        Input(id="demo-email", type="email", placeholder="you@example.com",
                              class_name="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"),
                    ),
                    class_name="border border-gray-200 rounded-xl p-4 mt-2",
                ),
                on_submit=prevent_default(),
                class_name="",
            ),

            # Echo result
            Show(
                Container(
                    H3("Echo Result", class_name="text-sm font-semibold text-gray-500 mb-2"),
                    Paragraph(echo_result().output,
                              class_name="font-mono text-purple-700 bg-purple-50 rounded-lg px-4 py-3 text-sm break-all"),
                    class_name="mt-4",
                ),
                when=echo_result(),
            ),
            Show(
                Paragraph(echo_error(),
                          class_name="text-red-600 bg-red-50 rounded-lg px-4 py-3 text-sm mt-4"),
                when=echo_error(),
            ),
            badge="Form",
        ),

        # ── 7. SERVER ACTION — DYNAMIC TABLE GENERATOR ───────────────────────
        Section("Server Action — Dynamic Table Generator",
            Container(
                Container(
                    Container(
                        Label("Rows (1–12):", class_name="text-sm text-gray-600 mr-2"),
                        Input(
                            type="number", value="4",
                            min="1", max="12",
                            bind=table_rows,
                            class_name="w-20 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500",
                        ),
                        Label("Cols (1–12):", class_name="text-sm text-gray-600 mx-3"),
                        Input(
                            type="number", value="4",
                            min="1", max="12",
                            bind=table_cols,
                            class_name="w-20 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500",
                        ),
                        Button(
                            Show("Generating...", when=table_pending(), fallback="Generate Table"),
                            on_click=run_table(table_rows(), table_cols()),
                            disabled=table_pending(),
                            class_name="ml-4 px-5 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-xl transition shadow disabled:opacity-50",
                        ),
                        class_name="flex items-center flex-wrap gap-2",
                    ),
                    class_name="mb-4",
                ),
                Show(
                    Container(
                        Paragraph(
                            "Multiplication table generated by Python backend:",
                            class_name="text-xs text-gray-400 mb-2 font-medium",
                        ),
                        Table(
                            Tbody(
                                Each(
                                    items=table_result().table,
                                    render_fn=lambda row, i: Tr(
                                        Each(
                                            items=row,
                                            render_fn=lambda cell, j: Td(
                                                cell,
                                                class_name="px-4 py-2 border border-gray-200 text-center font-mono text-sm bg-white hover:bg-purple-50 transition"
                                            )
                                        )
                                    )
                                )
                            ),
                            class_name="w-full border-collapse border border-gray-200 rounded-xl overflow-hidden shadow-sm"
                        ),
                        class_name="overflow-x-auto py-2",
                    ),
                    when=table_result(),
                ),
                Show(
                    Paragraph(table_error(),
                              class_name="text-red-600 bg-red-50 rounded-lg px-4 py-2 text-sm"),
                    when=table_error(),
                ),
                class_name="",
            ),
            badge="server_action",
        ),

        # ── 8. COLOUR PALETTE RESULT ─────────────────────────────────────────
        Show(
            Container(
                H3("Generated Palette", class_name="text-lg font-bold text-gray-800 mb-3"),
                Container(
                    Each(
                        items=pal_result().colors,
                        render_fn=lambda color, i: Tooltip(
                            Container(
                                id=f"swatch-{i}",
                                style=f"background-color: ${{color.to_js()}};",
                                class_name="w-16 h-16 rounded-2xl shadow-md cursor-pointer transition transform hover:scale-110 border-2 border-white",
                                on_click=transition(f"swatch-{i}",
                                                    {"transform": "scale(1.15)"},
                                                    duration=200),
                            ),
                            text=color,
                        ),
                        class_name="flex gap-4 flex-wrap",
                    ),
                    class_name="",
                ),
                class_name="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-6",
            ),
            when=pal_result(),
        ),

        # ── 9. LISTS ─────────────────────────────────────────────────────────
        Section("Lists — Ul, Ol, Dl",
            Container(
                Container(
                    H3("Unordered List", class_name="text-base font-semibold text-gray-700 mb-2"),
                    Ul(
                        Li("Zero-runtime JavaScript bundle"),
                        Li("Python ↔ browser type-safe bridge"),
                        Li("Hot module reload with watchdog"),
                        Li("File-based routing (pages/)"),
                        Li("Built-in animation engine (WAAPI)"),
                        class_name="list-disc list-inside space-y-1 text-gray-600 text-sm",
                    ),
                    class_name="",
                ),
                Divider(class_name="my-4"),
                Container(
                    H3("Ordered List", class_name="text-base font-semibold text-gray-700 mb-2"),
                    Ol(
                        Li("Install: pip install railui"),
                        Li("Create: railui new my-app"),
                        Li("Develop: railui dev"),
                        Li("Deploy: railui build"),
                        class_name="list-decimal list-inside space-y-1 text-gray-600 text-sm",
                    ),
                    class_name="",
                ),
                Divider(class_name="my-4"),
                Container(
                    H3("Description List", class_name="text-base font-semibold text-gray-700 mb-2"),
                    Dl(
                        Dt("createSignal", class_name="font-mono font-semibold text-purple-700 text-sm"),
                        Dd("Create a reactive signal with getter/setter pair",
                           class_name="ml-4 text-gray-600 text-sm mb-2"),
                        Dt("useAction", class_name="font-mono font-semibold text-purple-700 text-sm"),
                        Dd("Hook wrapping a server action with pending/result/error states",
                           class_name="ml-4 text-gray-600 text-sm mb-2"),
                        Dt("Each", class_name="font-mono font-semibold text-purple-700 text-sm"),
                        Dd("Reactively render a list from a signal",
                           class_name="ml-4 text-gray-600 text-sm"),
                    ),
                    class_name="",
                ),
                class_name="",
            ),
            badge="elements",
        ),

        # ── 10. TABLE ────────────────────────────────────────────────────────
        Section("Static Table",
            Container(
                Table(
                    Thead(
                        Tr(
                            Th("Component", scope="col",
                               class_name="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider bg-gray-100 rounded-tl-xl"),
                            Th("Tag",        scope="col",
                               class_name="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider bg-gray-100"),
                            Th("Category",   scope="col",
                               class_name="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider bg-gray-100"),
                            Th("Reactive",   scope="col",
                               class_name="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider bg-gray-100 rounded-tr-xl"),
                        ),
                    ),
                    Tbody(
                        *[Tr(
                            Td(name, class_name="px-6 py-3 font-mono text-sm text-purple-700 font-semibold border-t border-gray-100"),
                            Td(tag,  class_name="px-6 py-3 font-mono text-sm text-gray-600 border-t border-gray-100"),
                            Td(cat,  class_name="px-6 py-3 text-sm text-gray-500 border-t border-gray-100"),
                            Td(
                                Badge("Yes", variant="success") if rx else Badge("Static", variant="default"),
                                class_name="px-6 py-3 border-t border-gray-100",
                            ),
                            class_name="hover:bg-purple-50/50 transition",
                        ) for name, tag, cat, rx in [
                            ("H1–H6",    "<h1>–<h6>", "Typography", False),
                            ("Img",      "<img/>",    "Media",      False),
                            ("Video",    "<video>",   "Media",      False),
                            ("Table",    "<table>",   "Layout",     False),
                            ("Show",     "<div>",     "Reactive",   True),
                            ("Each",     "<div>",     "Reactive",   True),
                            ("Progress", "<progress>","Interactive",True),
                            ("Badge",    "<span>",    "Utility",    False),
                            ("Tooltip",  "<div>",     "Utility",    False),
                            ("Fragment", "(none)",    "Utility",    False),
                        ]],
                    ),
                    class_name="w-full border-collapse text-left",
                ),
                class_name="overflow-x-auto rounded-xl border border-gray-200 shadow-sm",
            ),
            badge="Table",
        ),

        # ── 11. SEMANTIC LAYOUT ELEMENTS ─────────────────────────────────────
        Section("Semantic Layout Elements",
            Container(
                Container(
                    Header(
                        H2("Article Header", class_name="text-lg font-bold text-gray-800"),
                        Paragraph("Posted 26 July 2026", class_name="text-xs text-gray-400"),
                        class_name="border-b border-gray-100 pb-3 mb-3",
                    ),
                    Container(
                        Article(
                            H3("RailUI reaches v0.1", class_name="font-semibold text-gray-700 mb-1"),
                            Paragraph(
                                "The framework's initial alpha ships with file-based routing, "
                                "reactive signals, server actions and the full HTML element library.",
                                class_name="text-gray-600 text-sm",
                            ),
                            class_name="flex-1",
                        ),
                        Aside(
                            Badge("Alpha", variant="warning"),
                            Paragraph("v0.1.3", class_name="text-xs text-gray-400 mt-1"),
                            class_name="ml-4 flex flex-col items-end",
                        ),
                        class_name="flex items-start",
                    ),
                    Footer(
                        Paragraph("© 2026 RailUI — MIT License",
                                  class_name="text-xs text-gray-400"),
                        class_name="border-t border-gray-100 pt-3 mt-3",
                    ),
                    class_name="bg-gray-50 rounded-xl p-4 border border-gray-200",
                ),
                class_name="",
            ),
            badge="HTML5",
        ),

        # ── 12. ANIMATIONS ───────────────────────────────────────────────────
        Section("Animations — Web Animations API",
            Container(
                Container(
                    Tooltip(
                        Button("Fade In",
                               on_click=fade_in("anim-target", duration=400),
                               class_name="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-semibold transition"),
                        text="opacity: 0 → 1",
                    ),
                    Tooltip(
                        Button("Slide Up",
                               on_click=slide_in_up("anim-target", duration=400),
                               class_name="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-sm font-semibold transition"),
                        text="translateY(30px) → 0",
                    ),
                    Tooltip(
                        Button("Scale In",
                               on_click=scale_in("anim-target", from_scale=0.7, duration=300),
                               class_name="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-semibold transition"),
                        text="scale(0.7) + fade in",
                    ),
                    Tooltip(
                        Button("Shake",
                               on_click=shake("anim-target"),
                               class_name="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-xl text-sm font-semibold transition"),
                        text="horizontal shake",
                    ),
                    Tooltip(
                        Button("Flip In",
                               on_click=flip_in("anim-target", axis="Y", duration=500),
                               class_name="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-sm font-semibold transition"),
                        text="rotateY(-90deg) → 0",
                    ),
                    Tooltip(
                        Button("Highlight",
                               on_click=highlight("anim-target", color="#fde68a"),
                               class_name="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-xl text-sm font-semibold transition"),
                        text="background flash",
                    ),
                    Tooltip(
                        Button("Pulse ∞",
                               on_click=pulse("anim-target", duration=700),
                               class_name="px-4 py-2 bg-pink-500 hover:bg-pink-600 text-white rounded-xl text-sm font-semibold transition"),
                        text="opacity pulse loop",
                    ),
                    Tooltip(
                        Button("Transition →",
                               on_click=transition("anim-target",
                                                   {"backgroundColor": "#7c3aed",
                                                    "color": "#ffffff",
                                                    "borderRadius": "999px"},
                                                   duration=400),
                               class_name="px-4 py-2 bg-violet-700 hover:bg-violet-800 text-white rounded-xl text-sm font-semibold transition"),
                        text="CSS transition() from current state",
                    ),
                    class_name="flex flex-wrap gap-2 mb-6",
                ),
                # Target element
                Container(
                    id="anim-target",
                    class_name="w-full bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-dashed border-purple-200 rounded-2xl p-8 text-center",
                    children=Container(
                        H3("Animation Target", class_name="text-xl font-bold text-gray-700"),
                        Paragraph("Click any button above to animate this element.",
                                  class_name="text-gray-400 text-sm mt-1"),
                        class_name="",
                    ),
                ),
                class_name="",
            ),
            badge="animate()",
        ),

        # ── 13. PROGRESS & METER ─────────────────────────────────────────────
        Section("Progress & Meter",
            Container(
                H3("Reactive Progress Bar", class_name="text-base font-semibold text-gray-700 mb-2"),
                Progress(value=progress_val(), max=100,
                         class_name="w-full h-4 rounded-full"),
                Container(
                    Button("−10", on_click=set_progress_val(progress_val() - 10),
                           class_name="px-4 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-semibold"),
                    Text(progress_val(), class_name="mx-3 font-mono font-bold text-gray-700"),
                    Text("/ 100", class_name="text-gray-400 text-sm"),
                    Button("+10", on_click=set_progress_val(progress_val() + 10),
                           class_name="px-4 py-1.5 ml-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-semibold"),
                    class_name="flex items-center mt-3",
                ),
                Divider(class_name="my-4"),
                H3("Meter Elements", class_name="text-base font-semibold text-gray-700 mb-2"),
                Container(
                    Paragraph("Disk usage:", class_name="text-sm text-gray-500 w-24"),
                    Meter(value=0.72, min=0, max=1, low=0.3, high=0.8, optimum=0.5,
                          class_name="flex-1 h-4"),
                    Span("72%", class_name="ml-3 text-sm font-mono text-gray-600"),
                    class_name="flex items-center gap-2 mb-2",
                ),
                Container(
                    Paragraph("Battery:", class_name="text-sm text-gray-500 w-24"),
                    Meter(value=0.3, min=0, max=1, low=0.2, high=0.7, optimum=0.9,
                          class_name="flex-1 h-4"),
                    Span("30%", class_name="ml-3 text-sm font-mono text-red-500 font-semibold"),
                    class_name="flex items-center gap-2",
                ),
                class_name="",
            ),
            badge="interactive",
        ),

        # ── 14. IFRAME (embed) ────────────────────────────────────────────────
        Section("Iframe & Canvas",
            H3("Embedded Map (OpenStreetMap)", class_name="text-base font-semibold text-gray-700 mb-3"),
            Iframe(
                src="https://www.openstreetmap.org/export/embed.html?bbox=-74.01,40.71,-73.97,40.73&layer=mapnik",
                title="OpenStreetMap embed",
                width="100%",
                height=260,
                class_name="w-full rounded-xl border border-gray-200",
                loading="lazy",
            ),
            badge="media",
        ),

        # ── 15. DIALOG ───────────────────────────────────────────────────────
        Section("Dialog (Modal)",
            Container(
                Button(
                    "Open Modal",
                    type="button",
                    on_click=RawJS("document.getElementById('demo-dialog').showModal()"),
                    class_name="px-6 py-2.5 bg-gray-900 text-white rounded-xl font-semibold hover:bg-gray-800 transition shadow cursor-pointer",
                ),
                Dialog(
                    H2("RailUI Modal", class_name="text-xl font-bold text-gray-900 mb-2"),
                    Paragraph(
                        "This is a native ",
                        Code("<dialog>"),
                        " element opened via the Web API. "
                        "No third-party modal library needed!",
                        class_name="text-gray-600 mb-4",
                    ),
                    Container(
                        Button(
                            "Close",
                            on_click=RawJS("document.getElementById('demo-dialog').close()"),
                            class_name="px-5 py-2 bg-purple-600 text-white rounded-lg font-semibold",
                        ),
                        class_name="flex justify-end",
                    ),
                    id="demo-dialog",
                    class_name="rounded-2xl shadow-2xl p-8 max-w-md w-full backdrop:bg-black/50",
                ),
                class_name="",
            ),
        ),
        # ── 16. COLOUR PALETTE ───────────────────────────────────────────────
        Show(
            Container(
                H3("Generated Palette", class_name="text-lg font-bold text-gray-800 mb-3"),
                Container(
                    Each(
                        items=pal_result().colors,
                        render_fn=lambda color, i: Tooltip(
                            Container(
                                id=f"swatch-{i}",
                                style=f"background:${{color}}",
                                class_name="w-12 h-12 rounded-xl shadow-md cursor-pointer transition hover:scale-110",
                                on_click=transition(f"swatch-{i}",
                                                    {"transform": "scale(1.2)"},
                                                    duration=200),
                            ),
                            text=color,
                        ),
                        class_name="flex gap-3 flex-wrap",
                    ),
                    class_name="",
                ),
                class_name="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-6",
            ),
            when=pal_result(),
        ),
    )
