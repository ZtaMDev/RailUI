"""
AST Compiler core for RailUI.

This module provides the necessary structures to intercept Python operations and
convert them into a JavaScript Abstract Syntax Tree (AST) string.
"""

import json
from typing import Any, Union, List

class DSLExpr:
    """
    Base class for Domain Specific Language expressions.
    
    This class overloads Python's standard arithmetic and comparison operators
    so that expressions like `count() + 1` yield a BinOp AST node instead of
    executing immediately.
    """
    def __add__(self, other: Any) -> "BinOp": return BinOp(self, "+", other)
    def __sub__(self, other: Any) -> "BinOp": return BinOp(self, "-", other)
    def __mul__(self, other: Any) -> "BinOp": return BinOp(self, "*", other)
    def __truediv__(self, other: Any) -> "BinOp": return BinOp(self, "/", other)
    def __mod__(self, other: Any) -> "BinOp": return BinOp(self, "%", other)
    def __pow__(self, other: Any) -> "BinOp": return BinOp(self, "**", other)
    def __floordiv__(self, other: Any) -> "CallOp": return CallOp("Math.floor", BinOp(self, "/", other))

    def __radd__(self, other: Any) -> "BinOp": return BinOp(other, "+", self)
    def __rsub__(self, other: Any) -> "BinOp": return BinOp(other, "-", self)
    def __rmul__(self, other: Any) -> "BinOp": return BinOp(other, "*", self)
    def __rtruediv__(self, other: Any) -> "BinOp": return BinOp(other, "/", self)
    def __rmod__(self, other: Any) -> "BinOp": return BinOp(other, "%", self)
    def __rpow__(self, other: Any) -> "BinOp": return BinOp(other, "**", self)
    def __rfloordiv__(self, other: Any) -> "CallOp": return CallOp("Math.floor", BinOp(other, "/", self))

    # Bitwise mapped to Logical
    def __and__(self, other: Any) -> "BinOp": return BinOp(self, "&&", other)
    def __rand__(self, other: Any) -> "BinOp": return BinOp(other, "&&", self)
    def __or__(self, other: Any) -> "BinOp": return BinOp(self, "||", other)
    def __ror__(self, other: Any) -> "BinOp": return BinOp(other, "||", self)
    def __invert__(self) -> "UnaryOp": return UnaryOp("!", self)

    # NOTE: __eq__ and __ne__ intentionally return BinOp (a DSL expression node)
    # instead of bool. This is the standard pattern in Python DSLs (SQLAlchemy,
    # Pandas) that overload comparison operators for query/AST building.
    # __hash__ is set to None because __eq__ is overridden (Python requirement).
    __hash__ = None  # type: ignore[assignment]

    def __eq__(self, other: object) -> Any: return BinOp(self, "===", other)  # type: ignore[override]
    def __ne__(self, other: object) -> Any: return BinOp(self, "!==", other)  # type: ignore[override]
    def __lt__(self, other: Any) -> "BinOp": return BinOp(self, "<", other)
    def __le__(self, other: Any) -> "BinOp": return BinOp(self, "<=", other)
    def __gt__(self, other: Any) -> "BinOp": return BinOp(self, ">", other)
    def __ge__(self, other: Any) -> "BinOp": return BinOp(self, ">=", other)

    def __getattr__(self, name: str) -> "PropertyAccess":
        if name.startswith("_"):
            raise AttributeError(name)
        return PropertyAccess(self, name)

    def __getitem__(self, key: Any) -> "PropertyAccess":
        return PropertyAccess(self, key, is_index=True)
        
    def __call__(self, *args: Any) -> "CallOp":
        return CallOp(self.to_js(), *args)

    def to_js(self) -> str:
        """
        Compile the AST node into a valid JavaScript string.
        
        Raises:
            NotImplementedError: If the derived class does not implement this method.
        """
        raise NotImplementedError()

def to_dsl(val: Any) -> DSLExpr:
    """
    Convert a standard Python value into a DSLExpr node if it is not one already.
    
    Args:
        val (Any): The value to convert.
        
    Returns:
        DSLExpr: A DSL expression representation of the value.
    """
    if isinstance(val, DSLExpr):
        return val
    return Literal(val)

class Literal(DSLExpr):
    """Represents a literal JSON-serializable value or a compound dict/list containing DSLExpr nodes."""
    def __init__(self, value: Any) -> None:
        self.value = value
        
    def to_js(self) -> str:
        if isinstance(self.value, dict):
            items = []
            for k, v in self.value.items():
                k_js = json.dumps(k)
                v_js = to_dsl(v).to_js()
                items.append(f"{k_js}: {v_js}")
            return "{" + ", ".join(items) + "}"
        elif isinstance(self.value, list):
            items = [to_dsl(v).to_js() for v in self.value]
            return "[" + ", ".join(items) + "]"
        else:
            return json.dumps(self.value)

class BinOp(DSLExpr):
    """Represents a binary operation in the JavaScript AST."""
    def __init__(self, left: Any, op: str, right: Any) -> None:
        self.left = to_dsl(left)
        self.op = op
        self.right = to_dsl(right)
        
    def to_js(self) -> str:
        return f"({self.left.to_js()} {self.op} {self.right.to_js()})"

class UnaryOp(DSLExpr):
    """Represents a unary operation in the JavaScript AST."""
    def __init__(self, op: str, operand: Any) -> None:
        self.op = op
        self.operand = to_dsl(operand)
        
    def to_js(self) -> str:
        return f"({self.op}{self.operand.to_js()})"

class CallOp(DSLExpr):
    """Represents a function call in the JavaScript AST."""
    def __init__(self, func_name: str, *args: Any) -> None:
        self.func_name = func_name
        self.args: List[DSLExpr] = [to_dsl(a) for a in args]
        
    def to_js(self) -> str:
        args_str = ", ".join(a.to_js() for a in self.args)
        return f"{self.func_name}({args_str})"

class SignalRef(DSLExpr):
    """Represents a reference to a reactive Signal's value."""
    def __init__(self, signal_name: str) -> None:
        self.signal_name = signal_name
        
    def to_js(self) -> str:
        return f"{self.signal_name}()"

class SetOp(DSLExpr):
    """Represents a call to a reactive Signal's setter."""
    def __init__(self, setter_name: str, value: Any) -> None:
        self.setter_name = setter_name
        self.value = to_dsl(value)
        
    def to_js(self) -> str:
        return f"{self.setter_name}({self.value.to_js()})"

class RawJS(DSLExpr):
    """Represents raw JavaScript code injected into the AST."""
    def __init__(self, js_code: str) -> None:
        self.js_code = js_code
        
    def to_js(self) -> str:
        return self.js_code

class MethodCallOp(DSLExpr):
    """Represents calling a method on a JS object."""
    def __init__(self, target: Any, func_name: str, *args: Any) -> None:
        self.target = to_dsl(target)
        self.func_name = func_name
        self.args: List[DSLExpr] = [to_dsl(a) for a in args]
        
    def to_js(self) -> str:
        target_js = self.target.to_js()
        args_str = ", ".join(a.to_js() for a in self.args)
        return f"{target_js}.{self.func_name}({args_str})"

class PropertyAccess(DSLExpr):
    """Represents a property or index access on a JS object."""
    def __init__(self, target: Any, prop: Any, is_index: bool = False) -> None:
        self.target = to_dsl(target)
        self.prop = prop if is_index else str(prop)
        self.is_index = is_index

    def __call__(self, *args: Any) -> MethodCallOp:
        if self.is_index:
            raise TypeError("Cannot call an indexed property directly as a method.")
        return MethodCallOp(self.target, self.prop, *args)
        
    def to_js(self) -> str:
        target_js = self.target.to_js()
        if self.is_index:
            prop_js = to_dsl(self.prop).to_js()
            return f"{target_js}?.[{prop_js}]"
        return f"{target_js}?.{self.prop}"



class ItemProxy(DSLExpr):
    """
    A compile-time proxy representing one item in an ``Each`` list.

    Passed as the first argument to ``Each``'s ``render_fn``.  Attribute access
    on the proxy returns ``RawJS`` nodes that compile to ``${item.prop}``
    template-literal interpolations in the generated JavaScript.

    The proxy itself (without attribute access) compiles to ``${item}``,
    useful when list items are plain primitives (strings, numbers).

    Args:
        var_name (str): The JavaScript variable name to use inside the template
            (``"item"`` for items, ``"index"`` for the loop index).

    Example::

        Each(
            items=todos,
            render_fn=lambda item, i: Container(
                Text(item.title, class_name="font-bold"),
                Text(item.body, class_name="text-sm text-gray-500"),
                class_name="p-4 border-b",
            )
        )
    """

    def __init__(self, var_name: str) -> None:
        self._var_name = var_name

    def __call__(self) -> "ItemProxy":
        """Make the proxy callable so it works where SignalGetters are expected."""
        return self

    def to_js(self) -> str:
        return self._var_name


# ===========================================================================
# JS DOM Utility Functions
# All return DSLExpr nodes for use in on_click, on_mount, createEffect, etc.
# ===========================================================================

# --- Console ---
def log(*args: Any) -> DSLExpr:
    """Logs text to browser console. part of the JS API"""
    parts = ", ".join(to_dsl(a).to_js() for a in args)
    return RawJS(f"console.log({parts})")

def warn(*args: Any) -> DSLExpr:
    """console.warn(...)"""
    parts = ", ".join(to_dsl(a).to_js() for a in args)
    return RawJS(f"console.warn({parts})")

def error(*args: Any) -> DSLExpr:
    """console.error(...)"""
    parts = ", ".join(to_dsl(a).to_js() for a in args)
    return RawJS(f"console.error({parts})")

def alert(message: Any) -> DSLExpr:
    """window.alert(...)"""
    return RawJS(f"alert({to_dsl(message).to_js()})")

def confirm_dialog(message: Any) -> DSLExpr:
    """window.confirm(...) — returns bool"""
    return RawJS(f"confirm({to_dsl(message).to_js()})")

# --- Timers ---
def set_timeout(expr: DSLExpr, delay_ms: int) -> DSLExpr:
    """setTimeout(fn, ms)"""
    return RawJS(f"setTimeout(() => {{ {expr.to_js()} }}, {delay_ms})")

def set_interval(expr: DSLExpr, interval_ms: int) -> DSLExpr:
    """setInterval(fn, ms) — returns the interval id"""
    return RawJS(f"setInterval(() => {{ {expr.to_js()} }}, {interval_ms})")

def clear_interval(interval_id: Any) -> DSLExpr:
    """clearInterval(id)"""
    return RawJS(f"clearInterval({to_dsl(interval_id).to_js()})")

def clear_timeout(timeout_id: Any) -> DSLExpr:
    """clearTimeout(id)"""
    return RawJS(f"clearTimeout({to_dsl(timeout_id).to_js()})")

# --- Navigation ---
def navigate(path: str) -> DSLExpr:
    """SPA navigation using the RailUI router."""
    return RawJS(f"$navigate('{path}')")

def go_back() -> DSLExpr:
    """window.history.back()"""
    return RawJS("window.history.back()")

def go_forward() -> DSLExpr:
    """window.history.forward()"""
    return RawJS("window.history.forward()")

def reload() -> DSLExpr:
    """window.location.reload()"""
    return RawJS("window.location.reload()")

def open_url(url: str, target: str = "_blank") -> DSLExpr:
    """window.open(url, target)"""
    return RawJS(f"window.open('{url}', '{target}')")

# --- DOM Interaction ---
def focus_element(element_id: str) -> DSLExpr:
    """Focus an element by id."""
    return RawJS(f"document.getElementById('{element_id}').focus()")

def blur_element(element_id: str) -> DSLExpr:
    """Blur an element by id."""
    return RawJS(f"document.getElementById('{element_id}').blur()")

def click_element(element_id: str) -> DSLExpr:
    """Programmatically click an element by id."""
    return RawJS(f"document.getElementById('{element_id}').click()")

def scroll_to(x: int = 0, y: int = 0, smooth: bool = True) -> DSLExpr:
    """Scroll the window to specific coordinates."""
    behavior = "smooth" if smooth else "instant"
    return RawJS(f"window.scrollTo({{ top: {y}, left: {x}, behavior: '{behavior}' }})")

def scroll_to_element(element_id: str, smooth: bool = True) -> DSLExpr:
    """Scroll an element into view."""
    behavior = "smooth" if smooth else "instant"
    return RawJS(f"document.getElementById('{element_id}').scrollIntoView({{ behavior: '{behavior}' }})")

def scroll_to_top(smooth: bool = True) -> DSLExpr:
    """Scroll window to top."""
    return scroll_to(0, 0, smooth)

# --- Attributes & Classes ---
def set_attribute(element_id: str, attr: str, value: Any) -> DSLExpr:
    """Set an attribute on an element by id."""
    val_js = to_dsl(value).to_js()
    return RawJS(f"document.getElementById('{element_id}').setAttribute('{attr}', {val_js})")

def remove_attribute(element_id: str, attr: str) -> DSLExpr:
    """Remove an attribute from an element by id."""
    return RawJS(f"document.getElementById('{element_id}').removeAttribute('{attr}')")

def add_class(element_id: str, class_name: str) -> DSLExpr:
    """Add a CSS class to an element by id."""
    return RawJS(f"document.getElementById('{element_id}').classList.add('{class_name}')")

def remove_class(element_id: str, class_name: str) -> DSLExpr:
    """Remove a CSS class from an element by id."""
    return RawJS(f"document.getElementById('{element_id}').classList.remove('{class_name}')")

def toggle_class(element_id: str, class_name: str) -> DSLExpr:
    """Toggle a CSS class on an element by id."""
    return RawJS(f"document.getElementById('{element_id}').classList.toggle('{class_name}')")

# --- Content ---
def set_inner_text(element_id: str, text: Any) -> DSLExpr:
    """Set innerText of an element."""
    val_js = to_dsl(text).to_js()
    return RawJS(f"document.getElementById('{element_id}').innerText = {val_js}")

def set_inner_html(element_id: str, html: str) -> DSLExpr:
    """Set innerHTML of an element (use with caution)."""
    return RawJS(f"document.getElementById('{element_id}').innerHTML = `{html}`")

def set_value(element_id: str, value: Any) -> DSLExpr:
    """Set the value property of an input element."""
    val_js = to_dsl(value).to_js()
    return RawJS(f"document.getElementById('{element_id}').value = {val_js}")

def get_value(element_id: str) -> DSLExpr:
    """Get the value of an input element."""
    return RawJS(f"document.getElementById('{element_id}').value")

# --- Style ---
def set_style(element_id: str, prop: str, value: str) -> DSLExpr:
    """Set an inline style property on an element."""
    return RawJS(f"document.getElementById('{element_id}').style['{prop}'] = '{value}'")

def show_element(element_id: str) -> DSLExpr:
    """Set element display to '' (restores to stylesheet value)."""
    return RawJS(f"document.getElementById('{element_id}').style.display = ''")

def hide_element(element_id: str) -> DSLExpr:
    """Set element display to 'none'."""
    return RawJS(f"document.getElementById('{element_id}').style.display = 'none'")

# --- Local Storage ---
def local_storage_set(key: str, value: Any) -> DSLExpr:
    """localStorage.setItem(key, JSON.stringify(value))"""
    val_js = to_dsl(value).to_js()
    return RawJS(f"localStorage.setItem('{key}', JSON.stringify({val_js}))")

def local_storage_get(key: str) -> DSLExpr:
    """JSON.parse(localStorage.getItem(key))"""
    return RawJS(f"JSON.parse(localStorage.getItem('{key}'))")

def local_storage_remove(key: str) -> DSLExpr:
    """localStorage.removeItem(key)"""
    return RawJS(f"localStorage.removeItem('{key}')")

def local_storage_clear() -> DSLExpr:
    """localStorage.clear()"""
    return RawJS("localStorage.clear()")

# --- Session Storage ---
def session_storage_set(key: str, value: Any) -> DSLExpr:
    """sessionStorage.setItem(key, JSON.stringify(value))"""
    val_js = to_dsl(value).to_js()
    return RawJS(f"sessionStorage.setItem('{key}', JSON.stringify({val_js}))")

def session_storage_get(key: str) -> DSLExpr:
    """JSON.parse(sessionStorage.getItem(key))"""
    return RawJS(f"JSON.parse(sessionStorage.getItem('{key}'))")

def session_storage_remove(key: str) -> DSLExpr:
    """sessionStorage.removeItem(key)"""
    return RawJS(f"sessionStorage.removeItem('{key}')")

# --- Clipboard ---
def copy_to_clipboard(text: Any) -> DSLExpr:
    """navigator.clipboard.writeText(text)"""
    val_js = to_dsl(text).to_js()
    return RawJS(f"navigator.clipboard.writeText({val_js})")

# --- Lifecycle ---
def on_mount(expr: "DSLExpr") -> None:
    """
    Register an expression to run ONCE when the current route mounts.
    Unlike createEffect, this runs in the route's init function, not the effect loop.
    """
    from .context import RenderContext
    RenderContext.init_scripts.append(expr.to_js() + ";")

def on_destroy(expr: "DSLExpr") -> None:
    """
    Register an expression to run ONCE when navigating away from the current route.
    Used for cleaning up intervals, event listeners, or other persistent state.
    """
    from .context import RenderContext
    RenderContext.destroy_scripts.append(expr.to_js() + ";")

# --- Sequences and Control Flow ---
def runSequence(*exprs: "DSLExpr") -> DSLExpr:
    """Run multiple expressions in sequence (comma expression)."""
    return RawJS(", ".join(e.to_js() for e in exprs))

def ifelse(condition: Any, true_val: Any, false_val: Any) -> DSLExpr:
    """Ternary operator: condition ? true_val : false_val"""
    cond_js = to_dsl(condition).to_js()
    true_js = to_dsl(true_val).to_js()
    false_js = to_dsl(false_val).to_js()
    return RawJS(f"({cond_js} ? {true_js} : {false_js})")

def typeof(expr: Any) -> DSLExpr:
    """typeof expr"""
    return RawJS(f"typeof {to_dsl(expr).to_js()}")

# --- Clipboard / Misc ---
def event_value() -> DSLExpr:
    """Returns ``event.target.value`` for use in ``on_input`` handlers."""
    return RawJS("event.target.value")

def prevent_default() -> DSLExpr:
    """event.preventDefault()"""
    return RawJS("event.preventDefault()")

def stop_propagation() -> DSLExpr:
    """event.stopPropagation()"""
    return RawJS("event.stopPropagation()")

# --- JS API Namespaces ---
class JSNativeNamespace:
    """
    A magic namespace class that intercepts Python method calls and translates them 
    directly into JavaScript method calls in the Abstract Syntax Tree (AST).

    This allows you to write Python code that calls native Web APIs or JS objects 
    without needing to use `RawJS` or write custom wrappers.

    How it works:
    -------------
    When you access a property (e.g., `Math.floor`), this class intercepts the `__getattr__` 
    call and returns a callable. When you invoke that callable (`Math.floor(x)`), it 
    generates a `CallOp` AST node: `Math.floor(x)`.

    Examples:
    ---------
    ```python
    from railui.all import Math, JSON, document
    
    # Compiles to: Math.floor(Math.random() * 100)
    random_num = Math.floor(Math.random() * 100)
    
    # Compiles to: JSON.stringify(my_signal())
    json_str = JSON.stringify(my_signal())
    
    # Compiles to: document.getElementById('my-id')
    el = document.getElementById('my-id')
    ```
    """
    def __init__(self, name: str) -> None:
        self._name = name

    def __getattr__(self, prop: str) -> Any:
        if prop.startswith("_"):
            raise AttributeError(prop)
        
        # Returns a callable that generates a CallOp
        def method_wrapper(*args: Any) -> CallOp:
            return CallOp(f"{self._name}.{prop}", *args)
        
        return method_wrapper

from .namespaces import (
    Math, JSON, Object, String, Number, Boolean, window, document
)


class JSArrayNamespace:
    """
    Provides immutable array operations for updating RailUI signals natively.

    RailUI relies on signals (e.g., `setTasks(...)`) to trigger reactivity. 
    Mutating an array directly using native JS methods like `.push()` or `.splice()` 
    will not trigger UI updates.

    This namespace provides static helper methods that perform **immutable** array 
    transformations directly in the JavaScript AST, allowing you to easily update 
    array signals.

    Examples:
    ---------
    ```python
    tasks, setTasks = createSignal(["Task A", "Task B"])

    # Append: Adds item to the end of the array.
    # Compiles to JS: setTasks([...(sig_1() || []), "Task C"])
    Button("Add", on_click=setTasks(Array.append(tasks(), "Task C")))

    # Prepend: Adds item to the beginning of the array.
    # Compiles to JS: setTasks(["Task C", ...(sig_1() || [])])
    Button("Prepend", on_click=setTasks(Array.prepend(tasks(), "Task C")))

    # Remove: Filters out the item at the given index.
    # Compiles to JS: setTasks((sig_1() || []).filter((_, i) => i !== 0))
    Button("Remove First", on_click=setTasks(Array.remove(tasks(), 0)))
    ```
    """
    @staticmethod
    def append(arr: Any, item: Any) -> DSLExpr:
        """
        Return an AST expression representing the addition of an item to the end of the array.
        
        Args:
            arr (Any): The array expression (e.g., `tasks()`).
            item (Any): The item to append.
            
        Returns:
            DSLExpr: Immutable append expression (spread syntax).
        """
        arr_js = to_dsl(arr).to_js()
        item_js = to_dsl(item).to_js()
        return RawJS(f"[...({arr_js} || []), {item_js}]")

    @staticmethod
    def prepend(arr: Any, item: Any) -> DSLExpr:
        """
        Return an AST expression representing the addition of an item to the start of the array.
        
        Args:
            arr (Any): The array expression (e.g., `tasks()`).
            item (Any): The item to prepend.
            
        Returns:
            DSLExpr: Immutable prepend expression (spread syntax).
        """
        arr_js = to_dsl(arr).to_js()
        item_js = to_dsl(item).to_js()
        return RawJS(f"[{item_js}, ...({arr_js} || [])]")

    @staticmethod
    def remove(arr: Any, index: Any) -> DSLExpr:
        """
        Return an AST expression representing the removal of an item at the given index.
        
        Args:
            arr (Any): The array expression (e.g., `tasks()`).
            index (Any): The index to remove.
            
        Returns:
            DSLExpr: Immutable removal expression (using Array.filter).
        """
        arr_js = to_dsl(arr).to_js()
        idx_js = to_dsl(index).to_js()
        return RawJS(f"({arr_js} || []).filter((_, i) => i !== {idx_js})")

    @staticmethod
    def concat(arr1: Any, arr2: Any) -> DSLExpr:
        """
        Return an AST expression combining two arrays into a new array.
        
        Args:
            arr1 (Any): The first array expression.
            arr2 (Any): The second array expression.
            
        Returns:
            DSLExpr: Immutable concat expression (spread syntax).
        """
        arr1_js = to_dsl(arr1).to_js()
        arr2_js = to_dsl(arr2).to_js()
        return RawJS(f"[...({arr1_js} || []), ...({arr2_js} || [])]")

Array = JSArrayNamespace()
