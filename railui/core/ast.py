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
    def __eq__(self, other: Any) -> "BinOp": return BinOp(self, "===", other)
    def __ne__(self, other: Any) -> "BinOp": return BinOp(self, "!==", other)
    def __lt__(self, other: Any) -> "BinOp": return BinOp(self, "<", other)
    def __le__(self, other: Any) -> "BinOp": return BinOp(self, "<=", other)
    def __gt__(self, other: Any) -> "BinOp": return BinOp(self, ">", other)
    def __ge__(self, other: Any) -> "BinOp": return BinOp(self, ">=", other)

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
    """Represents a literal JSON-serializable value in the JavaScript AST."""
    def __init__(self, value: Any) -> None:
        self.value = value
        
    def to_js(self) -> str:
        return json.dumps(self.value)

class BinOp(DSLExpr):
    """Represents a binary operation in the JavaScript AST."""
    def __init__(self, left: Any, op: str, right: Any) -> None:
        self.left = to_dsl(left)
        self.op = op
        self.right = to_dsl(right)
        
    def to_js(self) -> str:
        return f"({self.left.to_js()} {self.op} {self.right.to_js()})"

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
