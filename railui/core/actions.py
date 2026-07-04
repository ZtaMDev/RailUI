"""
railui/core/actions.py

Server Actions implementation.
Allows developers to decorate standard Python functions with `@server_action`.
These functions can then be called transparently from the frontend via automatically generated `fetch()` wrappers.
"""
from typing import Any, Callable, Dict
import inspect

# Global registry of all registered server actions.
# Key: action_name (string), Value: Python Callable
_ACTION_REGISTRY: Dict[str, Callable] = {}


class ServerAction:
    """
    Represents a registered server action.
    When compiled to AST in the frontend, it turns into an RPC call.
    """
    def __init__(self, name: str, func: Callable):
        self.name = name
        self.func = func

    def __call__(self, *args: Any, **kwargs: Any) -> "ServerActionCall":
        """
        When called inside a frontend component (e.g. `on_click=my_action(123)`),
        it returns an AST node representing the RPC invocation.
        """
        return ServerActionCall(self.name, args, kwargs)


from .ast import DSLExpr, to_dsl

class ServerActionCall(DSLExpr):
    """
    AST Node representing the execution of a server action.
    This will be intercepted by the compiler in `ast.py` to generate the `fetch()` JS code.
    """
    def __init__(self, name: str, args: tuple, kwargs: dict):
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def to_js(self) -> str:
        """
        Compile to a JS fetch() call.
        Uses POST and JSON.stringify to send arguments to the backend.
        We return a Promise that resolves to the JSON response.
        """
        # Convert all arguments to JS strings (they might be DSLExprs like `input_value()`)
        js_args = [to_dsl(arg).to_js() for arg in self.args]
        
        # We pack args in a JSON array. We don't support kwargs from the frontend yet, 
        # as JS doesn't have keyword arguments natively.
        body_js = f"JSON.stringify([{', '.join(js_args)}])"
        
        url = f"/_railui_action/{self.name}"
        
        return (
            f"fetch('{url}', {{ method: 'POST', "
            f"headers: {{ 'Content-Type': 'application/json' }}, "
            f"body: {body_js} }}).then(r => r.json())"
        )


def server_action(func: Callable) -> ServerAction:
    """
    Decorator to register a Python function as a Server Action.
    
    Example::
    
        @server_action
        def save_name(name: str):
            db.save(name)
            return {"status": "ok"}
    """
    name = func.__name__
    if name in _ACTION_REGISTRY:
        raise ValueError(f"A server action named '{name}' is already registered.")
    
    _ACTION_REGISTRY[name] = func
    return ServerAction(name, func)


def get_action_registry() -> Dict[str, Callable]:
    """Return the global server action registry."""
    return _ACTION_REGISTRY
