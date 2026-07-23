"""
Signal implementation for RailUI.

Signals are the primary reactivity primitive. They hold state and trigger
effects when their values change.
"""

from typing import Any, Tuple, List, Dict, Callable, Optional
from .ast import SignalRef, SetOp, DSLExpr, on_mount
from .context import SignalContext, RenderContext

_signal_counter: int = 0

class SignalGetter(DSLExpr):
    """
    A getter for a reactive signal.
    
    Acts as a DSLExpr so it can be seamlessly used in the Python DSL AST.
    Calling it returns a SignalRef AST node.
    """
    def __init__(self, sid: str, setter_name: str) -> None:
        self.sid = sid
        self.setter_name = setter_name
        
    def __call__(self) -> SignalRef:
        """Get the AST reference to the signal's value."""
        return SignalRef(self.sid)
        
    def to_js(self) -> str:
        """
        Compile the getter to JavaScript.
        Serves as a fallback when printed directly in text nodes.
        """
        return f"{self.sid}()"

class SignalSetter:
    """
    A setter for a reactive signal.
    
    Calling this with a value returns a SetOp AST node.
    """
    def __init__(self, setter_name: str) -> None:
        self.setter_name = setter_name
        
    def __call__(self, new_val: Any) -> SetOp:
        """
        Generate an AST node representing setting the signal.
        
        Args:
            new_val (Any): The new value for the signal.
            
        Returns:
            SetOp: The AST operation for setting the signal.
        """
        return SetOp(self.setter_name, new_val)

def createSignal(initial_value: Any) -> Tuple[SignalGetter, SignalSetter]:
    """
    Create a new reactive signal.
    
    Args:
        initial_value (Any): The initial value of the signal.
        
    Returns:
        Tuple[SignalGetter, SignalSetter]: A pair containing the signal getter and setter.
    """
    global _signal_counter
    _signal_counter += 1
    signal_id = f"sig_{_signal_counter}"
    setter_name = f"set_{signal_id}"
    
    # Store initialization context for rendering JS later
    SignalContext.signals.append({
        "id": signal_id,
        "initial": initial_value
    })
    
    from .ast import to_dsl
    js_val = to_dsl(initial_value).to_js()
    RenderContext.user_init_scripts.append(f"createSignal('{signal_id}', {js_val});")
    
    return SignalGetter(signal_id, setter_name), SignalSetter(setter_name)

def useComputed(compute_fn: Callable[[], DSLExpr]) -> DSLExpr:
    """
    Create a computed reactive value based on other signals.
    
    This function evaluates the given callable during the component build phase
    to construct a derived AST expression. The resulting expression will automatically
    reflect changes to any underlying signals it depends on when executed in the browser.
    
    Args:
        compute_fn (Callable[[], DSLExpr]): A function returning a DSL expression.
        
    Returns:
        DSLExpr: The computed AST expression.
    """
    return compute_fn()

def createEffect(expr: DSLExpr) -> None:
    """
    Register a user-defined side-effect that runs on every reactive update.

    Unlike DOM effects generated automatically by components, ``createEffect``
    results are stored in ``RenderContext.user_effects`` which is intentionally
    never cleared between render passes, ensuring user-declared effects always
    survive ``compile_app``'s internal reset and appear in the final JS bundle.

    Args:
        expr (DSLExpr): The DSL expression representing the javascript effect to run.
    """
    RenderContext.user_effects.append(expr.to_js())


class Store:
    """
    An accessor object returned by ``createStore``.

    Each key in the initial dict becomes an attribute on this object:

    - ``store.<key>`` — the ``SignalGetter`` (callable, returns a ``SignalRef``).
    - ``store.set_<key>`` — the ``SignalSetter`` (callable, returns a ``SetOp``).

    Example::

        user = createStore({"name": "Alice", "age": 30})

        Text(user.name())            # reactive text node
        Button("Reset",
               on_click=user.set_name("Alice"))  # setter
    """

    def __init__(self, fields: Dict[str, Tuple["SignalGetter", "SignalSetter"]]) -> None:
        for key, (getter, setter) in fields.items():
            setattr(self, key, getter)
            setattr(self, f"set_{key}", setter)


def createStore(initial_values: Dict[str, Any]) -> Store:
    """
    Create a reactive store grouping multiple named signals.

    This is a convenience wrapper that calls ``createSignal`` for each key in
    ``initial_values`` and bundles the getter/setter pairs into a single ``Store``
    accessor object, keeping related state logically grouped.

    Args:
        initial_values (Dict[str, Any]): A mapping of field names to initial values.

    Returns:
        Store: An object where each key becomes a ``SignalGetter`` attribute and a
            ``set_<key>`` ``SignalSetter`` attribute.

    Example::

        user = createStore({
            "name": "Alice",
            "email": "alice@example.com",
            "role": "admin",
        })

        Text(user.name())  # binds to the "name" signal
        Input(bind=user.name, type="text")  # two-way bind
        user.set_name("Bob")  # returns a SetOp for use in on_click etc.
    """
    fields: Dict[str, Tuple[SignalGetter, SignalSetter]] = {}
    for key, value in initial_values.items():
        getter, setter = createSignal(value)
        fields[key] = (getter, setter)
    return Store(fields)


class UseActionCall(DSLExpr):
    """
    AST Node representing a reactive server action call wrapper (hook invocation).
    This handles setting pending/loading state, tracking output result, and catching errors.
    """
    def __init__(self, action_name: str, args: tuple, kwargs: dict, pending_setter: str, result_setter: str, error_setter: str):
        self.action_name = action_name
        self.args = args
        self.kwargs = kwargs
        self.pending_setter = pending_setter
        self.result_setter = result_setter
        self.error_setter = error_setter

    def to_js(self) -> str:
        from .ast import to_dsl
        js_args = [to_dsl(arg).to_js() for arg in self.args]
        body_js = f"JSON.stringify([{', '.join(js_args)}])"
        url = f"/_railui_action/{self.action_name}"
        # Build the async IIFE expression
        js = (
            f"(async () => {{\n"
            f"  {self.pending_setter}(true);\n"
            f"  {self.result_setter}(null);\n"
            f"  {self.error_setter}(null);\n"
            f"  try {{\n"
            f"    const res = await fetch('{url}', {{ method: 'POST', "
            f"headers: {{ 'Content-Type': 'application/json' }}, "
            f"body: {body_js} }});\n"
            f"    if (!res.ok) {{\n"
            f"      const txt = await res.text();\n"
            f"      throw new Error(txt || 'Action failed');\n"
            f"    }}\n"
            f"    const data = await res.json();\n"
            f"    if (data && typeof data === 'object' && 'error' in data) {{\n"
            f"      throw new Error(data.error);\n"
            f"    }}\n"
            f"    {self.result_setter}(data);\n"
            f"    return data;\n"
            f"  }} catch (e) {{\n"
            f"    {self.error_setter}(e.message || String(e));\n"
            f"    throw e;\n"
            f"  }} finally {{\n"
            f"    {self.pending_setter}(false);\n"
            f"  }}\n"
            f"}})()"
        )
        return js

    def then(self, callback: Callable[[Any], DSLExpr]) -> "DSLExpr":
        from .ast import RawJS
        res_proxy = RawJS("res")
        callback_js = callback(res_proxy).to_js()
        js = f"{self.to_js()}.then(res => {{ {callback_js} }})"
        return RawJS(js)


def useAction(action: Any) -> Tuple[Callable[..., UseActionCall], SignalGetter, SignalGetter, SignalGetter]:
    """
    Hook to wrap a server action with reactive pending, result, and error states.

    Returns:
        Tuple[Callable[..., UseActionCall], SignalGetter, SignalGetter, SignalGetter]:
        - action_trigger: A callable that returns the UseActionCall AST node.
        - pending: A boolean signal indicating if the action is executing.
        - result: A signal holding the response value of the action.
        - error: A signal holding any error message.
    """
    if hasattr(action, "name"):
        action_name = action.name
    elif hasattr(action, "__name__"):
        action_name = action.__name__
    else:
        action_name = str(action)

    pending, set_pending = createSignal(False)
    result, set_result = createSignal(None)
    error, set_error = createSignal(None)

    def trigger(*args: Any, **kwargs: Any) -> UseActionCall:
        return UseActionCall(
            action_name=action_name,
            args=args,
            kwargs=kwargs,
            pending_setter=set_pending.setter_name,
            result_setter=set_result.setter_name,
            error_setter=set_error.setter_name
        )

    return trigger, pending, result, error


def useFetch(
    url: Any,
    on_success: Optional["SignalSetter"] = None,
    *,
    loading: Optional["SignalSetter"] = None,
    on_error: Optional[DSLExpr] = None,
    method: str = "GET",
    body: Optional[str] = None,
) -> Any:
    """
    Fetch hook supporting both:
    1. Hook style (returns trigger, pending, result, error and automatically triggers on mount):
       `fetch_trigger, is_loading, data, error = useFetch(my_action)`
    2. Side-effect style (returns None, triggers request on load and writes to a signal):
       `useFetch("https://api.com/data", set_data)`
    """
    if callable(url) or hasattr(url, "name"):
        # New hook-style signature
        trigger, pending, result, error = useAction(url)
        on_mount(trigger())
        return trigger, pending, result, error

    # Otherwise, fall back to old signature behaviour
    if on_success is None:
        raise ValueError("useFetch requires an on_success callback when fetching from a URL string.")

    loading_start = f"{loading.setter_name}(true);" if loading else ""
    loading_end   = f"{loading.setter_name}(false);" if loading else ""
    success_js    = f"{on_success.setter_name}(data);"

    if on_error is not None:
        error_js = on_error.to_js() + ";"
    else:
        error_js = "console.error('[useFetch] Error:', e);"

    fetch_opts = ""
    if method.upper() != "GET" or body:
        opts = [f'method: "{method.upper()}"']
        if body:
            opts.append(f'body: `{body}`')
            opts.append('headers: { "Content-Type": "application/json" }')
        fetch_opts = ", { " + ", ".join(opts) + " }"

    script = (
        f"(async () => {{\n"
        f"  {loading_start}\n"
        f"  try {{\n"
        f'    const res = await fetch("{url}"{fetch_opts});\n'
        f"    const data = await res.json();\n"
        f"    {success_js}\n"
        f"  }} catch(e) {{\n"
        f"    {error_js}\n"
        f"  }} finally {{\n"
        f"    {loading_end}\n"
        f"  }}\n"
        f"}})();"
    )
    RenderContext.user_init_scripts.append(script)
