"""
railui/core/namespaces.py

Typed, fully-documented stubs for the built-in JavaScript global namespaces available
in the RailUI Python-to-JS DSL. Each class mirrors the actual JavaScript API with
full type signatures, parameter names and docstrings, enabling IDE autocompletion
and in-editor documentation without any runtime overhead.

These objects do NOT generate any JavaScript themselves — they act as compile-time
proxies. When you call a method (e.g. Math.floor(x)), the underlying
JSNativeNamespace.__getattr__ intercepts it and emits a CallOp AST node.

Usage::

    from railui.all import Math, Array, JSON, Object, String, Number, Boolean, window, document

    Text(Math.floor(Math.random() * 100))
    Text(JSON.stringify(my_signal()))
    Text(String(user().age))
"""

from typing import Any, Optional
from .ast import DSLExpr, CallOp, RawJS, to_dsl


# ---------------------------------------------------------------------------
# Helper: shared CallOp factory used by every stub method
# ---------------------------------------------------------------------------
def _call(name: str, *args: Any) -> DSLExpr:
    return CallOp(name, *args)


# ---------------------------------------------------------------------------
# Math
# ---------------------------------------------------------------------------
class _MathNamespace:
    """
    Mirror of the JavaScript global ``Math`` object.

    All methods return a :class:`DSLExpr` that compiles to the corresponding
    ``Math.*`` call in the emitted JavaScript bundle.

    Examples::

        Math.floor(Math.random() * 100)   # -> Math.floor(Math.random() * 100)
        Math.max(a(), b())                # -> Math.max(sig_1(), sig_2())
        Math.abs(offset())                # -> Math.abs(sig_3())
    """

    # Constants (compile to literal JS identifiers)
    @property
    def PI(self) -> DSLExpr:
        """Math.PI — π ≈ 3.14159"""
        return RawJS("Math.PI")

    @property
    def E(self) -> DSLExpr:
        """Math.E — Euler's number ≈ 2.71828"""
        return RawJS("Math.E")

    @property
    def SQRT2(self) -> DSLExpr:
        """Math.SQRT2 — √2 ≈ 1.41421"""
        return RawJS("Math.SQRT2")

    @property
    def LN2(self) -> DSLExpr:
        """Math.LN2 — natural log of 2 ≈ 0.69315"""
        return RawJS("Math.LN2")

    @property
    def LN10(self) -> DSLExpr:
        """Math.LN10 — natural log of 10 ≈ 2.30259"""
        return RawJS("Math.LN10")

    @property
    def INFINITY(self) -> DSLExpr:
        """JavaScript ``Infinity``"""
        return RawJS("Infinity")

    # ---- Rounding -------------------------------------------------------
    def floor(self, x: Any) -> DSLExpr:
        """
        Return the largest integer ≤ x.

        Args:
            x: Any numeric DSL expression.

        Returns:
            DSLExpr: Compiles to ``Math.floor(x)``

        Example::

            Math.floor(3.9)          # -> Math.floor(3.9) -> 3
            Math.floor(score() / 5)  # -> Math.floor(sig_1() / 5)
        """
        return _call("Math.floor", x)

    def ceil(self, x: Any) -> DSLExpr:
        """
        Return the smallest integer ≥ x.

        Args:
            x: Any numeric DSL expression.

        Returns:
            DSLExpr: Compiles to ``Math.ceil(x)``
        """
        return _call("Math.ceil", x)

    def round(self, x: Any) -> DSLExpr:
        """
        Return x rounded to the nearest integer.

        Args:
            x: Any numeric DSL expression.

        Returns:
            DSLExpr: Compiles to ``Math.round(x)``
        """
        return _call("Math.round", x)

    def trunc(self, x: Any) -> DSLExpr:
        """
        Return the integer portion of x (truncates toward zero).

        Args:
            x: Any numeric DSL expression.

        Returns:
            DSLExpr: Compiles to ``Math.trunc(x)``
        """
        return _call("Math.trunc", x)

    # ---- Random ---------------------------------------------------------
    def random(self) -> DSLExpr:
        """
        Return a pseudo-random float in [0, 1).

        Returns:
            DSLExpr: Compiles to ``Math.random()``

        Example::

            Math.floor(Math.random() * 100)   # random int 0-99
        """
        return _call("Math.random")

    # ---- Extremes -------------------------------------------------------
    def max(self, *values: Any) -> DSLExpr:
        """
        Return the largest of the given values.

        Args:
            *values: Two or more numeric DSL expressions.

        Returns:
            DSLExpr: Compiles to ``Math.max(a, b, ...)``

        Example::

            Math.max(score(), best_score())  # -> Math.max(sig_1(), sig_2())
        """
        return _call("Math.max", *values)

    def min(self, *values: Any) -> DSLExpr:
        """
        Return the smallest of the given values.

        Args:
            *values: Two or more numeric DSL expressions.

        Returns:
            DSLExpr: Compiles to ``Math.min(a, b, ...)``
        """
        return _call("Math.min", *values)

    def clamp(self, value: Any, min_val: Any, max_val: Any) -> DSLExpr:
        """
        Clamp value between min_val and max_val. (Compiles to Math.min/max combo.)

        Returns:
            DSLExpr: Compiles to ``Math.min(Math.max(value, min_val), max_val)``
        """
        inner = _call("Math.max", value, min_val)
        return _call("Math.min", inner, max_val)

    # ---- Absolute value / sign ------------------------------------------
    def abs(self, x: Any) -> DSLExpr:
        """
        Return the absolute value of x.

        Args:
            x: Any numeric DSL expression.

        Returns:
            DSLExpr: Compiles to ``Math.abs(x)``
        """
        return _call("Math.abs", x)

    def sign(self, x: Any) -> DSLExpr:
        """
        Return 1, -1 or 0 depending on the sign of x.

        Args:
            x: Any numeric DSL expression.

        Returns:
            DSLExpr: Compiles to ``Math.sign(x)``
        """
        return _call("Math.sign", x)

    # ---- Powers & roots -------------------------------------------------
    def pow(self, base: Any, exponent: Any) -> DSLExpr:
        """
        Return base raised to the power exponent.

        Args:
            base: The base value.
            exponent: The exponent.

        Returns:
            DSLExpr: Compiles to ``Math.pow(base, exponent)``
        """
        return _call("Math.pow", base, exponent)

    def sqrt(self, x: Any) -> DSLExpr:
        """
        Return the square root of x.

        Args:
            x: Any numeric DSL expression.

        Returns:
            DSLExpr: Compiles to ``Math.sqrt(x)``
        """
        return _call("Math.sqrt", x)

    def cbrt(self, x: Any) -> DSLExpr:
        """
        Return the cube root of x.

        Returns:
            DSLExpr: Compiles to ``Math.cbrt(x)``
        """
        return _call("Math.cbrt", x)

    def hypot(self, *values: Any) -> DSLExpr:
        """
        Return the square root of the sum of squares of its arguments.

        Returns:
            DSLExpr: Compiles to ``Math.hypot(a, b, ...)``
        """
        return _call("Math.hypot", *values)

    # ---- Logarithms -----------------------------------------------------
    def log(self, x: Any) -> DSLExpr:
        """
        Return the natural logarithm of x.

        Returns:
            DSLExpr: Compiles to ``Math.log(x)``
        """
        return _call("Math.log", x)

    def log2(self, x: Any) -> DSLExpr:
        """
        Return the base-2 logarithm of x.

        Returns:
            DSLExpr: Compiles to ``Math.log2(x)``
        """
        return _call("Math.log2", x)

    def log10(self, x: Any) -> DSLExpr:
        """
        Return the base-10 logarithm of x.

        Returns:
            DSLExpr: Compiles to ``Math.log10(x)``
        """
        return _call("Math.log10", x)

    def exp(self, x: Any) -> DSLExpr:
        """
        Return E raised to the power x.

        Returns:
            DSLExpr: Compiles to ``Math.exp(x)``
        """
        return _call("Math.exp", x)

    # ---- Trigonometry ---------------------------------------------------
    def sin(self, x: Any) -> DSLExpr:
        """Sine of x (radians). Compiles to ``Math.sin(x)``"""
        return _call("Math.sin", x)

    def cos(self, x: Any) -> DSLExpr:
        """Cosine of x (radians). Compiles to ``Math.cos(x)``"""
        return _call("Math.cos", x)

    def tan(self, x: Any) -> DSLExpr:
        """Tangent of x (radians). Compiles to ``Math.tan(x)``"""
        return _call("Math.tan", x)

    def asin(self, x: Any) -> DSLExpr:
        """Arc-sine of x. Compiles to ``Math.asin(x)``"""
        return _call("Math.asin", x)

    def acos(self, x: Any) -> DSLExpr:
        """Arc-cosine of x. Compiles to ``Math.acos(x)``"""
        return _call("Math.acos", x)

    def atan(self, x: Any) -> DSLExpr:
        """Arc-tangent of x. Compiles to ``Math.atan(x)``"""
        return _call("Math.atan", x)

    def atan2(self, y: Any, x: Any) -> DSLExpr:
        """Arc-tangent of y/x. Compiles to ``Math.atan2(y, x)``"""
        return _call("Math.atan2", y, x)

    def sinh(self, x: Any) -> DSLExpr:
        """Hyperbolic sine. Compiles to ``Math.sinh(x)``"""
        return _call("Math.sinh", x)

    def cosh(self, x: Any) -> DSLExpr:
        """Hyperbolic cosine. Compiles to ``Math.cosh(x)``"""
        return _call("Math.cosh", x)

    def tanh(self, x: Any) -> DSLExpr:
        """Hyperbolic tangent. Compiles to ``Math.tanh(x)``"""
        return _call("Math.tanh", x)


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------
class _JSONNamespace:
    """
    Mirror of the JavaScript global ``JSON`` object.

    Examples::

        JSON.stringify(my_signal())          # -> JSON.stringify(sig_1())
        JSON.parse(raw_string_signal())      # -> JSON.parse(sig_2())
        JSON.stringify(user(), None, 2)      # -> JSON.stringify(sig_1(), null, 2)
    """

    def stringify(self, value: Any, replacer: Any = None, space: Any = None) -> DSLExpr:
        """
        Serialize a value to a JSON string.

        Args:
            value: The DSL expression to serialize.
            replacer: Optional filter function or array of keys (DSL or None).
            space: Optional indentation (number of spaces or string).

        Returns:
            DSLExpr: Compiles to ``JSON.stringify(value[, replacer[, space]])``

        Example::

            JSON.stringify(user())       # -> JSON.stringify(sig_1())
            JSON.stringify(user(), None, 2)  # pretty-print with 2 spaces
        """
        args: list = [value]
        if replacer is not None or space is not None:
            args.append(replacer if replacer is not None else None)
        if space is not None:
            args.append(space)
        return _call("JSON.stringify", *args)

    def parse(self, text: Any) -> DSLExpr:
        """
        Deserialize a JSON string to a JavaScript value.

        Args:
            text: A string DSL expression containing JSON.

        Returns:
            DSLExpr: Compiles to ``JSON.parse(text)``

        Example::

            JSON.parse(raw_json_signal())  # -> JSON.parse(sig_1())
        """
        return _call("JSON.parse", text)


# ---------------------------------------------------------------------------
# Object
# ---------------------------------------------------------------------------
class _ObjectNamespace:
    """
    Mirror of the JavaScript global ``Object`` constructor / namespace.

    Examples::

        Object.keys(user())          # -> Object.keys(sig_1())
        Object.values(config())      # -> Object.values(sig_2())
        Object.entries(params())     # -> Object.entries(sig_3())
        Object.assign({}, base())    # -> Object.assign({}, sig_4())
    """

    def keys(self, obj: Any) -> DSLExpr:
        """
        Return an array of the object's own enumerable property names.

        Args:
            obj: A DSL expression resolving to an object.

        Returns:
            DSLExpr: Compiles to ``Object.keys(obj)``
        """
        return _call("Object.keys", obj)

    def values(self, obj: Any) -> DSLExpr:
        """
        Return an array of the object's own enumerable property values.

        Args:
            obj: A DSL expression resolving to an object.

        Returns:
            DSLExpr: Compiles to ``Object.values(obj)``
        """
        return _call("Object.values", obj)

    def entries(self, obj: Any) -> DSLExpr:
        """
        Return an array of [key, value] pairs for each own property.

        Args:
            obj: A DSL expression resolving to an object.

        Returns:
            DSLExpr: Compiles to ``Object.entries(obj)``
        """
        return _call("Object.entries", obj)

    def assign(self, target: Any, *sources: Any) -> DSLExpr:
        """
        Shallow-copy own enumerable properties from sources into target.

        Args:
            target: The destination object DSL expression.
            *sources: One or more source object DSL expressions.

        Returns:
            DSLExpr: Compiles to ``Object.assign(target, ...sources)``

        Example::

            Object.assign({}, defaults(), overrides())
        """
        return _call("Object.assign", target, *sources)

    def freeze(self, obj: Any) -> DSLExpr:
        """
        Freeze an object so its properties cannot be changed.

        Returns:
            DSLExpr: Compiles to ``Object.freeze(obj)``
        """
        return _call("Object.freeze", obj)

    def create(self, proto: Any) -> DSLExpr:
        """
        Create a new object with proto as its prototype.

        Returns:
            DSLExpr: Compiles to ``Object.create(proto)``
        """
        return _call("Object.create", proto)

    def fromEntries(self, iterable: Any) -> DSLExpr:
        """
        Transform a list of [key, value] entries into an object.

        Returns:
            DSLExpr: Compiles to ``Object.fromEntries(iterable)``
        """
        return _call("Object.fromEntries", iterable)

    def hasOwn(self, obj: Any, key: Any) -> DSLExpr:
        """
        Return true if the object has the specified own property.

        Returns:
            DSLExpr: Compiles to ``Object.hasOwn(obj, key)``
        """
        return _call("Object.hasOwn", obj, key)


# ---------------------------------------------------------------------------
# String  (constructor / static methods)
# ---------------------------------------------------------------------------
class _StringNamespace:
    """
    Mirror of the JavaScript ``String`` constructor.
    
    Calling ``String(val)`` casts a value to a string. Also exposes static helpers.

    Examples::

        String(user().age)       # -> String(sig_1()?.age)
        String.fromCharCode(65)  # -> String.fromCharCode(65)  -> "A"
    """

    def __call__(self, value: Any) -> DSLExpr:
        """
        Convert a value to its string representation.

        Args:
            value: Any DSL expression.

        Returns:
            DSLExpr: Compiles to ``String(value)``
        """
        return _call("String", value)

    def fromCharCode(self, *codes: Any) -> DSLExpr:
        """
        Create a string from Unicode code points.

        Args:
            *codes: One or more integer code values.

        Returns:
            DSLExpr: Compiles to ``String.fromCharCode(code1, code2, ...)``
        """
        return _call("String.fromCharCode", *codes)

    def fromCodePoint(self, *codes: Any) -> DSLExpr:
        """
        Create a string from Unicode code points (full Unicode range).

        Returns:
            DSLExpr: Compiles to ``String.fromCodePoint(...)``
        """
        return _call("String.fromCodePoint", *codes)


# ---------------------------------------------------------------------------
# Number  (constructor / static methods)
# ---------------------------------------------------------------------------
class _NumberNamespace:
    """
    Mirror of the JavaScript ``Number`` constructor.

    Calling ``Number(val)`` casts a value to a number. Also exposes static helpers.

    Examples::

        Number(input_val())          # -> Number(sig_1())
        Number.isInteger(score())    # -> Number.isInteger(sig_2())
        Number.isNaN(result())       # -> Number.isNaN(sig_3())
    """

    # Constants
    @property
    def MAX_SAFE_INTEGER(self) -> DSLExpr:
        """Number.MAX_SAFE_INTEGER (2^53 - 1)"""
        return RawJS("Number.MAX_SAFE_INTEGER")

    @property
    def MIN_SAFE_INTEGER(self) -> DSLExpr:
        """Number.MIN_SAFE_INTEGER (-(2^53 - 1))"""
        return RawJS("Number.MIN_SAFE_INTEGER")

    @property
    def MAX_VALUE(self) -> DSLExpr:
        """Number.MAX_VALUE"""
        return RawJS("Number.MAX_VALUE")

    @property
    def POSITIVE_INFINITY(self) -> DSLExpr:
        """Number.POSITIVE_INFINITY"""
        return RawJS("Number.POSITIVE_INFINITY")

    @property
    def NEGATIVE_INFINITY(self) -> DSLExpr:
        """Number.NEGATIVE_INFINITY"""
        return RawJS("Number.NEGATIVE_INFINITY")

    @property
    def NaN(self) -> DSLExpr:  # noqa: N802
        """Number.NaN"""
        return RawJS("Number.NaN")

    def __call__(self, value: Any) -> DSLExpr:
        """
        Convert a value to a number.

        Args:
            value: Any DSL expression (string signal, boolean, etc.)

        Returns:
            DSLExpr: Compiles to ``Number(value)``
        """
        return _call("Number", value)

    def isInteger(self, value: Any) -> DSLExpr:  # noqa: N802
        """
        Return true if value is an integer.

        Returns:
            DSLExpr: Compiles to ``Number.isInteger(value)``
        """
        return _call("Number.isInteger", value)

    def isFinite(self, value: Any) -> DSLExpr:  # noqa: N802
        """
        Return true if value is a finite number.

        Returns:
            DSLExpr: Compiles to ``Number.isFinite(value)``
        """
        return _call("Number.isFinite", value)

    def isNaN(self, value: Any) -> DSLExpr:  # noqa: N802
        """
        Return true if value is NaN.

        Returns:
            DSLExpr: Compiles to ``Number.isNaN(value)``
        """
        return _call("Number.isNaN", value)

    def isSafeInteger(self, value: Any) -> DSLExpr:  # noqa: N802
        """
        Return true if value is a safe integer (-(2^53-1) <= x <= 2^53-1).

        Returns:
            DSLExpr: Compiles to ``Number.isSafeInteger(value)``
        """
        return _call("Number.isSafeInteger", value)

    def parseFloat(self, string: Any) -> DSLExpr:  # noqa: N802
        """
        Parse a string and return a floating-point number.

        Returns:
            DSLExpr: Compiles to ``Number.parseFloat(string)``
        """
        return _call("Number.parseFloat", string)

    def parseInt(self, string: Any, radix: Any = 10) -> DSLExpr:  # noqa: N802
        """
        Parse a string and return an integer.

        Args:
            string: The string to parse.
            radix: The numeric base (default 10).

        Returns:
            DSLExpr: Compiles to ``Number.parseInt(string, radix)``
        """
        return _call("Number.parseInt", string, radix)


# ---------------------------------------------------------------------------
# Boolean (constructor)
# ---------------------------------------------------------------------------
class _BooleanNamespace:
    """
    Mirror of the JavaScript ``Boolean`` constructor.

    Examples::

        Boolean(user().is_active)    # -> Boolean(sig_1()?.is_active)
    """

    def __call__(self, value: Any) -> DSLExpr:
        """
        Convert a value to a boolean (truthy/falsy coercion).

        Args:
            value: Any DSL expression.

        Returns:
            DSLExpr: Compiles to ``Boolean(value)``
        """
        return _call("Boolean", value)


# ---------------------------------------------------------------------------
# window
# ---------------------------------------------------------------------------
class _WindowNamespace:
    """
    Mirror of the JavaScript ``window`` (global browser) object.

    Useful for accessing timers, navigation, alerts, and other browser APIs.

    Examples::

        window.alert("Hello!")
        window.location.href()       # Note: href is accessed via property chain
    """

    def alert(self, message: Any) -> DSLExpr:
        """Show a browser alert dialog. Compiles to ``window.alert(message)``"""
        return _call("window.alert", message)

    def confirm(self, message: Any) -> DSLExpr:
        """Show a confirm dialog. Compiles to ``window.confirm(message)``"""
        return _call("window.confirm", message)

    def prompt(self, message: Any, default: Any = None) -> DSLExpr:
        """Show a prompt dialog. Compiles to ``window.prompt(message[, default])``"""
        args = [message] if default is None else [message, default]
        return _call("window.prompt", *args)

    def open(self, url: Any, target: Any = "_blank") -> DSLExpr:
        """Open a URL in a new tab/window. Compiles to ``window.open(url, target)``"""
        return _call("window.open", url, target)

    def close(self) -> DSLExpr:
        """Close the current browser window. Compiles to ``window.close()``"""
        return _call("window.close")

    def setTimeout(self, fn: Any, delay: Any) -> DSLExpr:  # noqa: N802
        """
        Execute fn once after delay milliseconds.

        Returns:
            DSLExpr: Compiles to ``window.setTimeout(fn, delay)``

        Note:
            For the ``fn`` argument, pass a ``RawJS`` callback string.
        """
        return _call("window.setTimeout", fn, delay)

    def setInterval(self, fn: Any, interval: Any) -> DSLExpr:  # noqa: N802
        """
        Execute fn repeatedly every interval milliseconds.

        Returns:
            DSLExpr: Compiles to ``window.setInterval(fn, interval)``
        """
        return _call("window.setInterval", fn, interval)

    def clearTimeout(self, id: Any) -> DSLExpr:  # noqa: N802
        """Cancel a timeout previously set with setTimeout."""
        return _call("window.clearTimeout", id)

    def clearInterval(self, id: Any) -> DSLExpr:  # noqa: N802
        """Cancel an interval previously set with setInterval."""
        return _call("window.clearInterval", id)

    def scrollTo(self, x: Any, y: Any) -> DSLExpr:  # noqa: N802
        """Scroll the window to a position. Compiles to ``window.scrollTo(x, y)``"""
        return _call("window.scrollTo", x, y)

    def scrollBy(self, x: Any, y: Any) -> DSLExpr:  # noqa: N802
        """Scroll the window by a delta. Compiles to ``window.scrollBy(x, y)``"""
        return _call("window.scrollBy", x, y)

    def requestAnimationFrame(self, callback: Any) -> DSLExpr:  # noqa: N802
        """Schedule an animation frame callback. Compiles to ``window.requestAnimationFrame(callback)``"""
        return _call("window.requestAnimationFrame", callback)

    def cancelAnimationFrame(self, id: Any) -> DSLExpr:  # noqa: N802
        """Cancel a scheduled animation frame. Compiles to ``window.cancelAnimationFrame(id)``"""
        return _call("window.cancelAnimationFrame", id)

    def dispatchEvent(self, event: Any) -> DSLExpr:  # noqa: N802
        """Dispatch an event on the window. Compiles to ``window.dispatchEvent(event)``"""
        return _call("window.dispatchEvent", event)


# ---------------------------------------------------------------------------
# document
# ---------------------------------------------------------------------------
class _DocumentNamespace:
    """
    Mirror of the JavaScript ``document`` (DOM) object.

    Examples::

        document.getElementById("main")
        document.querySelector(".btn")
        document.title()
    """

    def getElementById(self, id: Any) -> DSLExpr:  # noqa: N802
        """
        Return the element with the given id, or null.

        Args:
            id: String DSL expression for the element id.

        Returns:
            DSLExpr: Compiles to ``document.getElementById(id)``
        """
        return _call("document.getElementById", id)

    def querySelector(self, selector: Any) -> DSLExpr:  # noqa: N802
        """
        Return the first element matching the CSS selector, or null.

        Returns:
            DSLExpr: Compiles to ``document.querySelector(selector)``
        """
        return _call("document.querySelector", selector)

    def querySelectorAll(self, selector: Any) -> DSLExpr:  # noqa: N802
        """
        Return a NodeList of all elements matching the CSS selector.

        Returns:
            DSLExpr: Compiles to ``document.querySelectorAll(selector)``
        """
        return _call("document.querySelectorAll", selector)

    def createElement(self, tag: Any) -> DSLExpr:  # noqa: N802
        """
        Create a new DOM element.

        Returns:
            DSLExpr: Compiles to ``document.createElement(tag)``
        """
        return _call("document.createElement", tag)

    def createTextNode(self, text: Any) -> DSLExpr:  # noqa: N802
        """
        Create a new text node.

        Returns:
            DSLExpr: Compiles to ``document.createTextNode(text)``
        """
        return _call("document.createTextNode", text)

    def getElementById(self, id: Any) -> DSLExpr:  # noqa: N802
        return _call("document.getElementById", id)

    def getElementsByClassName(self, name: Any) -> DSLExpr:  # noqa: N802
        """
        Return all elements with the given class name.

        Returns:
            DSLExpr: Compiles to ``document.getElementsByClassName(name)``
        """
        return _call("document.getElementsByClassName", name)

    def getElementsByTagName(self, tag: Any) -> DSLExpr:  # noqa: N802
        """
        Return all elements with the given tag name.

        Returns:
            DSLExpr: Compiles to ``document.getElementsByTagName(tag)``
        """
        return _call("document.getElementsByTagName", tag)

    def dispatchEvent(self, event: Any) -> DSLExpr:  # noqa: N802
        """Dispatch a DOM event. Compiles to ``document.dispatchEvent(event)``"""
        return _call("document.dispatchEvent", event)

    def title(self) -> DSLExpr:
        """Return the current document title. Compiles to ``document.title``"""
        return RawJS("document.title")


# ---------------------------------------------------------------------------
# Singleton instances  (these are what get exported to railui.all)
# ---------------------------------------------------------------------------
Math = _MathNamespace()
JSON = _JSONNamespace()
Object = _ObjectNamespace()
String = _StringNamespace()
Number = _NumberNamespace()
Boolean = _BooleanNamespace()
window = _WindowNamespace()
document = _DocumentNamespace()
