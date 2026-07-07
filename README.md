# RailUI

**Python-first, zero-runtime fullstack web framework.**

Write reactive single-page applications entirely in Python. RailUI compiles your Python DSL directly into vanilla JavaScript/HTML/CSS bundles — no Node.js, no JS framework, no runtime interpreter.

```python
from railui.all import *

count, setCount = createSignal(0)

app = App("My App")

@app.route("/")
def home() -> Component:
    return Container(
        Text("Count: ", count()),
        Button("+1", on_click=setCount(count() + 1)),
        class_name="flex gap-4 p-6",
    )

if __name__ == "__main__":
    app.build()
```

---

## Features

|                           |                                                                                                                                       |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **Pure Python DSL**       | Operator overloading compiles `count() + 1` → `sig_1() + 1` in JS — no Python runtime needed                                          |
| **Reactive Signals**      | First-class `createSignal`, `createStore`, `useComputed`, `createEffect`                                                              |
| **Server Actions**        | `@server_action` decorator — call Python functions from the browser via auto-generated `fetch()`                                      |
| **File-Based Routing**    | Drop a `.py` file in `pages/`, get a route. Supports dynamic `[id]` segments                                                          |
| **SPA Router**            | History API client-side navigation with scoped effects and lifecycle                                                                  |
| **Component System**      | 15+ built-in components: `Container`, `Button`, `Input`, `Show`, `Each`, `Form`, `Link`, `Image`, `Head`, `Suspense`, slots, and more |
| **Two-Way Binding**       | `bind=signal` on inputs — reactive form handling in one line                                                                          |
| **Animations**            | 12 pre-built WAAPI animations: `fade_in`, `slide_in_up`, `spin`, `bounce`, `shake`, `pulse` + custom keyframes                        |
| **Conditional Classes**   | `class_list={"bg-red-500": has_error()}`                                                                                              |
| **Tailwind-like CSS**     | 150+ utility classes compiled at build time — zero runtime CSS                                                                        |
| **JS Bridge**             | 30+ utilities: `log`, `alert`, `set_timeout`, `navigate`, `local_storage_set`, `copy_to_clipboard`, `on_mount`, `on_destroy`          |
| **JS Namespace Wrappers** | `Math.floor(x)`, `JSON.stringify()`, `Object.keys()`, `document.getElementById()` — all compile to native JS                          |
| **Named Slots**           | `Slot`/`SlotFill` for composable layouts                                                                                              |
| **HMR**                   | Dev server with file watcher and SSE-based hot reload                                                                                 |
| **Zero Runtime**          | Output is pure vanilla JS (~1KB runtime) — no framework shipped to the browser                                                        |
| **Deploy Anywhere**       | Railway (full-stack with server actions), Vercel (static SPA), or any static host                                                     |

---

## Installation

```bash
pip install railui
```

Requires **Python ≥ 3.12**.

---

## Quick Start

### 1. Create a project

```bash
railui new my-app
cd my-app
```

Or manually create this structure:

```
my-app/
  main.py           # App entry point
  layout.py         # Shared layout (optional)
  pages/
    index.py        # Route: /
    counter.py      # Route: /counter
  public/           # Static assets (copied to build)
  railui.config.json
```

### 2. Define a page

```python
# pages/counter.py
from railui.all import *

def page() -> Component:
    count, setCount = createSignal(0)
    return Container(
        Text("Count: ", count(), class_name="text-2xl font-bold"),
        Button("+1", on_click=setCount(count() + 1), class_name="px-4 py-2 bg-blue-600 text-white rounded"),
    )
```

### 3. Wire it up

```python
# main.py
from railui.all import *

app = App("My Counter App")
app.discover_pages("pages")

if __name__ == "__main__":
    app.build()
```

### 4. Build

```bash
railui build
# Output: dist/index.html + app.{hash}.js + app.{hash}.css
```

### 5. Dev server

```bash
railui dev
# Opens http://127.0.0.1:5173 — HMR enabled
```

---

## Core Concepts

### The DSL — Python that becomes JavaScript

RailUI overloads Python operators so expressions like `count() + 1` produce JavaScript AST nodes instead of executing immediately. This is how you write reactive logic in pure Python.

```python
count, setCount = createSignal(10)

# These compile to JavaScript, they don't run in Python:
count() + 1         # → sig_1() + 1
count() * 2         # → sig_1() * 2
count() > 5         # → sig_1() > 5
count() == 0        # → sig_1() === 0 (=== in JS)
~show_details()     # → !sig_2()
count() + 1 * 2     # → (sig_1() + (1 * 2))

# Property access uses optional chaining:
user_data().name        # → sig_3()?.name
user_data().address.city # → sig_3()?.address?.city

# Index access:
items()[0]              # → sig_4()?.[0]
```

When you need raw JS, use `RawJS`:

```python
RawJS("console.log('hello')")
```

### Signals — Reactive State

```python
# Simple signal
name, setName = createSignal("Alice")
age, setAge = createSignal(30)

# Reading (inside component tree — compiles to JS):
Text(name())           # reactive text node
Text(age() + 1)        # reactive expression

# Writing (inside event handlers — compiles to JS):
Button("Older", on_click=setAge(age() + 1))

# Computed value:
double_age = useComputed(lambda: age() * 2)
Text(double_age)       # reactive computed

# Side effect on every signal change:
createEffect(log("age changed to: ", age()))

# Store (grouped signals):
user = createStore({"name": "Alice", "role": "admin"})
Text(user.name())                    # reactive getter
Button("Reset", on_click=user.set_name(""))  # setter
Input(bind=user.name)                # two-way binding
```

### Components

```python
Container(
    Text("Hello", class_name="text-xl font-bold"),
    Button("Click", on_click=log("clicked"), class_name="px-4 py-2 bg-blue-500 text-white rounded"),
    class_name="flex flex-col gap-4 p-6",
    id="main-container",
)
```

---

## Routing

### File-Based Routing

| File                  | Route        |
| --------------------- | ------------ |
| `pages/index.py`      | `/`          |
| `pages/dashboard.py`  | `/dashboard` |
| `pages/blog/index.py` | `/blog`      |
| `pages/users/[id].py` | `/users/:id` |

Each page module must export a `page()` function returning a `Component`:

```python
# pages/about.py
from railui.all import *

def page() -> Component:
    return Container(
        Text("About Us", class_name="text-3xl font-bold"),
    )
```

### Programmatic Routing

```python
app = App()

@app.route("/hello")
def hello_page() -> Component:
    return Text("Hello!")

@app.route("/user/<name>")
def user_page(name: str) -> Component:
    return Text(f"User: {name}")
```

### 404 Page

```python
def not_found() -> Component:
    return Container(
        Text("404 — Page Not Found"),
        Link("Go home", href="/"),
    )

app.set_not_found(not_found)
```

---

## State Management

### `createSignal`

```python
count, setCount = createSignal(0)
Text(count())                               # reactive display
Button("+", on_click=setCount(count() + 1))  # reactive update
```

### `createStore`

```python
user = createStore({
    "name": "Alice",
    "role": "admin",
    "is_logged_in": True,
})

Text(user.name())           # → sig_1()
Input(bind=user.name)       # two-way binding
Button("Logout", on_click=user.set_is_logged_in(False))
```

### `useFetch`

```python
posts, setPosts = createSignal([])
loading, setLoading = createSignal(True)

useFetch(
    url="https://api.example.com/posts",
    on_success=setPosts,
    loading=setLoading,
    on_error=log("Failed to load posts"),
)

Suspense(
    Each(items=posts, render_fn=lambda post, i: Text(post.title)),
    fallback=Text("Loading..."),
    loading=loading(),
)
```

### `createEffect`

```python
createEffect(log("count changed to: ", count()))
```

---

## Event Handling

```python
Button(
    "Click me",
    on_click=log("clicked!"),
    on_dblclick=setCount(count() + 2),
    on_mouseenter=log("hover!"),
)

Input(
    on_input=setName(event_value()),    # event.target.value
    on_change=log("committed: ", name()),
    on_focus=log("focused"),
    on_blur=log("blurred"),
)

Form(
    on_submit=runSequence(prevent_default(), log("submitted")),
)
```

### Two-Way Binding

```python
username, setUsername = createSignal("")

Input(
    bind=username,                    # two-way binding — one line
    placeholder="Enter username...",
    class_name="px-4 py-2 border rounded",
)
```

---

## Event Utility Functions

```python
prevent_default()      # → event.preventDefault()
stop_propagation()     # → event.stopPropagation()
event_value()          # → event.target.value
```

---

## Conditional Rendering — `Show`

```python
is_visible, setVisible = createSignal(False)

Show(
    Text("This is visible when the signal is truthy"),
    when=is_visible(),
    on_mount=log("BECAME VISIBLE"),
    on_update=log("UPDATED"),
    on_unmount=log("HIDDEN"),
)

# With fallback content:
Show(
    Text("Content loaded!"),
    when=is_loaded(),
    fallback=Text("Loading...", class_name="text-gray-500"),
)
```

---

## List Rendering — `Each`

```python
todos, setTodos = createSignal([
    {"title": "Learn RailUI"},
    {"title": "Build something awesome"},
])

Each(
    items=todos,
    render_fn=lambda item, index: Container(
        Text(index, class_name="text-gray-400 mr-2"),
        Text(item.title, class_name="font-semibold"),
        class_name="p-3 border-b",
    ),
    on_mount=log("List mounted!"),
    on_update=log("List updated!"),
)

# Immutable array operations:
Button("Add", on_click=setTodos(Array.append(todos(), {"title": "New task"})))
Button("Remove", on_click=setTodos(Array.remove(todos(), 0)))
```

---

## Server Actions

Call Python functions from the browser — no API boilerplate.

### Define

```python
# pages/users.py
from railui.all import *

@server_action
def save_user(name: str):
    print(f"Saving {name} to database...")
    return {"status": "ok", "message": f"User {name} saved!"}

def page() -> Component:
    username, setUsername = createSignal("")
    status_msg, setStatusMsg = createSignal("")

    return Container(
        Input(bind=username, placeholder="Enter name..."),
        Button(
            "Save",
            on_click=save_user(username()).then(lambda res: setStatusMsg(res.message)),
        ),
        Show(Text(status_msg()), when=status_msg() != ""),
    )
```

### How it works

1. `@server_action` registers the Python function in `_ACTION_REGISTRY`
2. `save_user(username())` generates a `ServerActionCall` AST node
3. `.then(lambda res: setStatusMsg(res.message))` chains a Promise handler
4. Compiled JS: `fetch('/_railui_action/save_user', {method:'POST', body:JSON.stringify([sig_1()])}).then(r=>r.json()).then(res=>{ set_sig_2(res.message) })`
5. The dev server (or production FastAPI server) receives the POST, deserializes the args, and calls the registered Python function

### Deployment with Server Actions

Server actions require a **Python backend**. Deploy to:

- **Railway** (recommended) — `railui build --platform railway` generates config
- **Any VPS** — run `uvicorn railui.backend.server:create_app --factory`
- **NOT Vercel** — Vercel's serverless functions can't run a persistent Python process

---

## Lifecycle Hooks

```python
on_mount(log("Page mounted!"))
on_destroy(log("Page destroyed — clean up timers!"))

# Alternatively inside Show/Each:
Show(
    Text("Content"),
    when=is_visible(),
    on_mount=log("First time visible"),
    on_update=log("Visibility changed"),
    on_unmount=log("Now hidden"),
)
```

---

## Animations

12 pre-built Web Animations API helpers:

```python
fade_in("element-id")
fade_out("element-id")
slide_in_left("element-id", distance="40px")
slide_in_right("element-id")
slide_in_up("element-id")
slide_out_down("element-id")
spin("element-id", duration=800, iterations="Infinity")
bounce("element-id", height="12px", duration=600)
pulse("element-id", duration=800)
shake("element-id", duration=400)              # form errors
scale_in("element-id", from_scale=0.8)
scale_out("element-id", to_scale=0.8)
```

Chain with `runSequence`:

```python
runSequence(setCount(count() + 1), shake("counter-card"))
runSequence(setCount(0), fade_out("card"), set_timeout(slide_in_up("card"), 300))
```

Custom keyframes:

```python
animate("my-element", [
    {"transform": "translateX(0px)", "opacity": 1},
    {"transform": "translateX(100px)", "opacity": 0},
], duration=500, easing="ease-in-out")
```

---

## Layout System — Named Slots

Define a layout with `Slot` placeholders:

```python
# layout.py
from railui.all import *

def Layout(*children):
    return Container(
        Navbar(),
        Slot("hero", source=children, default=""),
        Container(
            Slot("body", source=children, default=Slot.Unassigned(children)),
        ),
        Slot("footer", source=children,
             default=Text("© 2026", class_name="text-gray-500")),
        class_name="min-h-screen bg-gray-50",
    )
```

Fill slots from pages:

```python
# pages/index.py
def page():
    return Layout(
        SlotFill("hero", Container(
            Text("Welcome!", class_name="text-3xl font-bold text-white"),
            class_name="bg-gradient-to-r from-purple-600 to-blue-500 p-12",
        )),
        Container(
            Text("Main content here"),
            class_name="p-8",
        ),
        SlotFill("footer", Container(
            Text("Custom footer"),
        )),
    )
```

`Slot.Unassigned(children)` returns all children that are not `SlotFill` instances — perfect for default body content.

---

## Head / Meta Tags (Per-Route)

```python
Head(
    title="Dashboard | My App",
    meta={"description": "Dashboard page", "keywords": "python, web"},
    styles=["https://cdn.example.com/styles.css"],
    scripts=["https://cdn.example.com/widget.js"],
)
```

---

## Suspense & Async Loading

```python
Suspense(
    Container(
        Text(user_data().name),
        Text(user_data().email),
    ),
    fallback=Container(
        Text("Loading...", class_name="animate-pulse"),
    ),
    loading=loading(),   # boolean signal from useFetch
)
```

---

## Form Handling

```python
Form(
    Container(
        Label("Name", for_="name-input"),
        Input(
            bind=user_store.name,
            id="name-input",
            class_name="w-full p-3 border rounded",
        ),
    ),
    Container(
        Label("Role", for_="role-input"),
        Input(
            bind=user_store.role,
            id="role-input",
        ),
    ),
    Button("Save", type="submit",
           on_click=log("Saved:", user_store.name(), user_store.role())),
    class_name="flex flex-col gap-4 max-w-md",
)
```

---

## JS Namespace Wrappers

```python
Math.floor(count() / 2)
Math.random()
Math.max(count(), 0)

JSON.stringify(data())
JSON.parse(text())

Object.keys(user_data())
Object.entries(user_data())

String(count())
Number("42")

document.getElementById("my-el")
window.alert("Hello!")

Array.append(tasks(), new_task)
Array.prepend(items(), "first")
Array.remove(items(), index)
Array.concat(list_a(), list_b())
```

---

## DOM Utilities

```python
log("message")                   # console.log
alert("Hello!")                  # window.alert
set_timeout(log("done"), 1000)   # setTimeout
set_interval(log("tick"), 500)   # setInterval

navigate("/dashboard")           # SPA navigation
go_back()
reload()

focus_element("input-id")
scroll_to_element("section-2")

add_class("el", "highlight")
remove_class("el", "highlight")
toggle_class("el", "active")

set_inner_text("output", result())
set_inner_html("container", "<p>HTML</p>")
set_value("input", "new value")
get_value("input")

show_element("loading-spinner")
hide_element("loading-spinner")

local_storage_set("key", data())
local_storage_get("key")
local_storage_remove("key")
local_storage_clear()

copy_to_clipboard(text())
```

---

## Conditional Classes

```python
Container(
    Text("Error message"),
    class_list={
        "bg-red-100 text-red-800": has_error(),
        "bg-green-100 text-green-800": ~has_error(),
    },
)
```

### Hover / Active Classes

```python
Button(
    "Hover me",
    class_name="px-4 py-2 bg-blue-600 text-white rounded",
    hover_class="bg-blue-700 shadow-lg",
    active_class="bg-blue-800 scale-95",
)
```

---

## CSS / Tailwind-like Utilities

RailUI compiles Tailwind-like class names to CSS at build time. 150+ utilities supported:

| Category       | Examples                                                                                     |
| -------------- | -------------------------------------------------------------------------------------------- |
| **Layout**     | `flex`, `grid`, `block`, `hidden`, `flex-row`, `flex-col`, `items-center`, `justify-between` |
| **Grid**       | `grid-cols-3`, `grid-rows-2`, `col-span-2`, `gap-4`                                          |
| **Sizing**     | `w-full`, `w-64`, `h-32`, `max-w-md`, `min-h-screen`                                         |
| **Spacing**    | `p-4`, `px-6`, `py-2`, `m-2`, `mx-auto`, `mt-8`, `-ml-2`                                     |
| **Typography** | `text-sm`, `text-lg`, `text-4xl`, `font-bold`, `font-mono`, `text-center`, `text-red-500`    |
| **Colors**     | `bg-blue-600`, `text-white`, `border-gray-200`, `bg-gradient-to-r`                           |
| **Borders**    | `border`, `border-2`, `border-t`, `rounded`, `rounded-lg`, `rounded-full`                    |
| **Shadows**    | `shadow`, `shadow-sm`, `shadow-md`, `shadow-lg`                                              |
| **Position**   | `static`, `fixed`, `absolute`, `relative`, `sticky`, `z-50`, `top-0`                         |
| **Effects**    | `opacity-50`, `transition`, `outline-none`                                                   |
| **Pseudo**     | `hover:bg-blue-700`, `focus:outline-none`, `focus:ring-2`                                    |
| **Custom**     | `w-[100px]`, `text-[#ff6600]`, `bg-[#1a1a2e]`                                                |

---

## CLI Reference

### `railui dev`

```
railui dev [path] [--host HOST] [--port PORT] [--no-open] [--platform vercel]
```

Starts the dev server with HMR. Builds into `.railui/dev/` — your project stays clean.

- File watcher rebuilds on `.py` changes
- SSE pushes `reload` event to browser
- Serves from `.railui/dev/` with SPA fallback

### `railui build`

```
railui build [path] [--outdir DIR] [--no-bundle] [--platform railway|vercel]
```

Production build. Generates:

- `index.html` — SPA shell
- `app.{hash}.js` — Minified JS bundle
- `app.{hash}.css` — Compiled Tailwind CSS
- Deployment configs (if `--platform` is set)

### `railui new`

```
railui new <project-name> [--dir PARENT_DIR]
```

Scaffolds a new project with `main.py`, `layout.py`, `pages/index.py`, and config.

---

## Configuration

```json
{
  "outdir": "build",
  "port": 5173,
  "open_browser": true,
  "bundle": true,
  "platform": "railway",
  "public_dirs": ["public", "assets"]
}
```

`railui.config.json` in your project root. CLI flags override config values.

---

## Deployment

### Railway (Full-Stack — Server Actions Supported)

```bash
railui build --platform railway
railway up
```

Railway runs the FastAPI backend via `uvicorn`. Server actions work out of the box.

The deployment templates (`railway.toml`, `Procfile`, `requirements.txt`) are auto-generated.

### Vercel (Static SPA — No Server Actions)

```bash
railui build --platform vercel
vercel --prod
```

Vercel **cannot** run Python server actions. The SPA itself works perfectly (routing, signals, animations, etc.), but `@server_action` calls return 404.

Use Vercel for:

- Marketing sites
- Dashboards with client-only data (via `useFetch` on public APIs)
- Prototypes

### Any Static Host

Just upload the `dist/` directory after `railui build`.

### Docker / Custom Server

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install railui && railui build
CMD ["uvicorn", "railui.backend.server:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Architecture Overview

```
Python AST (DSL)          Compile Time              Browser (Runtime)
─────────────────      ──────────────────      ──────────────────────
count + 1              →  sig_1() + 1          →  $signals.sig_1 + 1
setCount(42)           →  set_sig_1(42)        →  $signals.sig_1 = 42
                                                      ↓
Component.render()     →  HTML + Effects       →  runEffects()
                                                      ↓
createSignal(0)        →  createSignal(...)    →  DOM updates
                                                      ↓
@server_action           fetch(...).then(...)  →  FastAPI RPC
```

### Key Design Decisions

| Decision                    | Why                                                                                  |
| --------------------------- | ------------------------------------------------------------------------------------ |
| **Compile-time DSL**        | Zero runtime overhead — no interpreter shipped to browser                            |
| **Direct DOM manipulation** | No virtual DOM — signals update elements directly via `innerText`, `classList`, etc. |
| **Push-based signals**      | `setSignal(val)` triggers `runEffects()` — simple, deterministic                     |
| **Pre-compiled routes**     | All route HTML is inlined in JS — no dynamic server rendering                        |
| **Tailwind-like CSS**       | Regex-based compiler — 150+ rules, zero runtime CSS-in-JS                            |
| **FastAPI backend**         | Async Python server for dev, HMR, and server actions                                 |
| **~1KB runtime JS**         | Minimal client — faster loads, less to debug                                         |

---

## Full API Reference

### Core Types

| Symbol        | Description                        |
| ------------- | ---------------------------------- |
| `DSLExpr`     | Base class for all DSL expressions |
| `RawJS(js)`   | Inject raw JavaScript string       |
| `to_dsl(val)` | Convert Python value to DSLExpr    |

### Signals & State

| Symbol                                       | Description                 |
| -------------------------------------------- | --------------------------- |
| `createSignal(initial)` → `(getter, setter)` | Create a reactive signal    |
| `createStore(dict)` → `Store`                | Create grouped signals      |
| `useComputed(fn)` → `DSLExpr`                | Derived reactive expression |
| `createEffect(expr)`                         | Register side effect        |
| `useFetch(url, on_success, ...)`             | Async data fetching         |

### App

| Symbol                       | Description                |
| ---------------------------- | -------------------------- |
| `App(title)`                 | Application instance       |
| `app.route(path)`            | Decorator — register route |
| `app.discover_pages(dir)`    | File-based routing         |
| `app.set_not_found(factory)` | 404 page                   |
| `app.build(out_dir)`         | Compile bundle             |

### Components

| Component   | Tag          | Key Props                                             |
| ----------- | ------------ | ----------------------------------------------------- |
| `Container` | `<div>`      | `class_name`, `on_click`, ...                         |
| `Text`      | `<span>`     | `class_name`                                          |
| `Button`    | `<button>`   | `type`, `disabled`, `on_click`                        |
| `Input`     | `<input />`  | `type`, `value`, `placeholder`, `bind`, `on_input`    |
| `Textarea`  | `<textarea>` | `rows`, `cols`, `bind`                                |
| `Select`    | `<select>`   | `name`, `bind`, `on_change`                           |
| `Option`    | `<option>`   | `value`, `selected`                                   |
| `Label`     | `<label>`    | `for_`                                                |
| `Form`      | `<form>`     | `action`, `method`, `on_submit`                       |
| `Link`      | `<a>`        | `href` (required), `target`                           |
| `Image`     | `<img />`    | `src`, `alt` (required)                               |
| `Page`      | `<main>`     | semantic main element                                 |
| `Show`      | `<div>`      | `when` (required), `fallback`, lifecycle              |
| `Each`      | `<div>`      | `items` (required), `render_fn` (required), lifecycle |
| `Head`      | —            | `title`, `meta`, `styles`, `scripts`                  |
| `Suspense`  | `<div>`      | `fallback`, `loading`                                 |
| `Slot`      | —            | `name`, `source`, `default`                           |
| `SlotFill`  | —            | `name`                                                |

### Server Actions

| Symbol                            | Description                               |
| --------------------------------- | ----------------------------------------- |
| `@server_action`                  | Decorator — register server-side function |
| `ServerActionCall.then(callback)` | Chain Promise handler                     |

### Animations

| Symbol                           | Description            |
| -------------------------------- | ---------------------- |
| `animate(id, keyframes, **opts)` | Custom WAAPI animation |
| `fade_in(id)` / `fade_out(id)`   | Opacity fade           |
| `slide_in_left/right/up(id)`     | Slide + fade in        |
| `slide_out_down(id)`             | Slide out              |
| `spin(id)`                       | Continuous rotation    |
| `bounce(id)`                     | Vertical bounce        |
| `pulse(id)`                      | Opacity pulse          |
| `shake(id)`                      | Horizontal shake       |
| `scale_in(id)` / `scale_out(id)` | Scale transition       |

### JS Namespaces

`Math`, `JSON`, `Object`, `String`, `Number`, `Boolean`, `window`, `document`, `Array`

### Utility Functions

`log`, `warn`, `error`, `alert`, `confirm_dialog`, `set_timeout`, `set_interval`, `clear_interval`, `clear_timeout`, `navigate`, `go_back`, `go_forward`, `reload`, `open_url`, `focus_element`, `blur_element`, `click_element`, `scroll_to`, `scroll_to_element`, `scroll_to_top`, `set_attribute`, `remove_attribute`, `add_class`, `remove_class`, `toggle_class`, `set_inner_text`, `set_inner_html`, `set_value`, `get_value`, `set_style`, `show_element`, `hide_element`, `local_storage_set`, `local_storage_get`, `local_storage_remove`, `local_storage_clear`, `session_storage_set`, `session_storage_get`, `session_storage_remove`, `copy_to_clipboard`, `on_mount`, `on_destroy`, `runSequence`, `ifelse`, `typeof`, `event_value`, `prevent_default`, `stop_propagation`

---

## Project Structure

```
my-app/
├── main.py              # App entry — App(), discover_pages()
├── layout.py            # Shared layout with Slot system
├── store.py             # Global state (createStore)
├── railui.config.json   # Framework config
├── pages/
│   ├── index.py         # Route: /
│   ├── dashboard.py     # Route: /dashboard
│   └── users/
│       ├── index.py     # Route: /users
│       └── [id].py      # Route: /users/:id
├── public/              # Static assets
│   └── favicon.ico
└── dist/                # Build output (after `railui build`)
    ├── index.html
    ├── app.{hash}.js
    └── app.{hash}.css
```

---

## License

MIT
