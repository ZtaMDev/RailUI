"""
Signal implementation for RailUI.

Signals are the primary reactivity primitive. They hold state and trigger
effects when their values change.
"""

from typing import Any, Tuple, List, Dict, Callable, Optional
from .ast import SignalRef, SetOp, DSLExpr
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


def useFetch(
    url: str,
    on_success: "SignalSetter",
    *,
    loading: Optional["SignalSetter"] = None,
    on_error: Optional[DSLExpr] = None,
    method: str = "GET",
    body: Optional[str] = None,
) -> None:
    """
    Register an async ``fetch()`` call that runs once on page load and updates
    reactive signals with the response data.

    The generated JavaScript performs a standard ``fetch`` call inside an async
    IIFE, parses the response as JSON, and calls the signal setter with the result.
    An optional ``loading`` setter is toggled before and after the request.

    Args:
        url (str): The URL to fetch.
        on_success (SignalSetter): The signal setter to call with the parsed JSON
            response body (e.g. ``setPosts``).
        loading (SignalSetter, optional): A boolean signal setter that is set to
            ``true`` before the request and ``false`` after (in ``finally``).
        on_error (DSLExpr, optional): A DSL expression executed in the ``catch``
            block (e.g. ``log("Failed to load")``).  Defaults to
            ``console.error``.
        method (str): HTTP method — ``"GET"`` (default), ``"POST"``, etc.
        body (str, optional): Raw JSON body string for ``POST`` requests.

    Example::

        posts, setPosts = createSignal([])
        loading, setLoading = createSignal(True)

        useFetch(
            url="https://jsonplaceholder.typicode.com/posts?_limit=5",
            on_success=setPosts,
            loading=setLoading,
            on_error=log("Failed to load posts"),
        )
    """
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
