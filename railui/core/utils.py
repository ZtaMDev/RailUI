"""
Utility DSL functions for JavaScript interactions.

These functions provide a clean, Pythonic wrapper around common JavaScript
and DOM APIs, preventing the need for raw JS strings in the frontend code.
"""

from typing import Any
from .ast import CallOp, RawJS, DSLExpr, to_dsl

def log(*args: Any) -> CallOp:
    """
    Generate a console.log statement in the compiled Javascript.
    
    This acts as a transparent bridge, passing Python arguments to the JS console.
    
    Args:
        *args: Values, strings, or DSLExpr (Signals) to log.
        
    Returns:
        CallOp: The AST node representing the console.log action.
    """
    return CallOp("console.log", *args)

def set_timeout(callback: DSLExpr, delay_ms: int) -> CallOp:
    """
    Generate a setTimeout call in the compiled Javascript.
    
    Args:
        callback (DSLExpr): A Javascript expression or arrow function to execute.
        delay_ms (int): The delay in milliseconds before the callback is executed.
        
    Returns:
        CallOp: The AST node representing the setTimeout action.
    """
    return CallOp("setTimeout", callback, delay_ms)

def alert(message: Any) -> CallOp:
    """
    Generate an alert dialog in the browser.
    
    Args:
        message (Any): The message to display in the alert window.
        
    Returns:
        CallOp: The AST node for the alert.
    """
    return CallOp("alert", message)

def add_class(element_id: str, class_name: str) -> RawJS:
    """
    Generate Javascript to add a CSS class to a specific DOM element by ID.
    
    Args:
        element_id (str): The HTML ID of the target element.
        class_name (str): The class to add.
        
    Returns:
        RawJS: The compiled Javascript action.
    """
    return RawJS(f"document.getElementById({to_dsl(element_id).to_js()}).classList.add({to_dsl(class_name).to_js()})")

def remove_class(element_id: str, class_name: str) -> RawJS:
    """
    Generate Javascript to remove a CSS class from a specific DOM element by ID.
    
    Args:
        element_id (str): The HTML ID of the target element.
        class_name (str): The class to remove.
        
    Returns:
        RawJS: The compiled Javascript action.
    """
    return RawJS(f"document.getElementById({to_dsl(element_id).to_js()}).classList.remove({to_dsl(class_name).to_js()})")

def toggle_class(element_id: str, class_name: str, force: Any = None) -> RawJS:
    """
    Generate Javascript to toggle a CSS class on an element by ID.
    
    Args:
        element_id (str): The HTML ID of the target element.
        class_name (str): The class to toggle.
        force (Any, optional): If provided (e.g. a Signal), the class is explicitly added if truthy, 
                               and removed if falsy.
                               
    Returns:
        RawJS: The compiled Javascript action.
    """
    if force is not None:
        return RawJS(f"document.getElementById({to_dsl(element_id).to_js()}).classList.toggle({to_dsl(class_name).to_js()}, {to_dsl(force).to_js()})")
    return RawJS(f"document.getElementById({to_dsl(element_id).to_js()}).classList.toggle({to_dsl(class_name).to_js()})")

def runSequence(*actions: Any) -> RawJS:
    """
    Chain multiple Javascript actions together in a single execution block.
    
    This is extremely useful for event handlers (like `on_click`) that need to perform
    multiple tasks sequentially, such as updating a signal and logging a value.
    
    Args:
        *actions (Any): A sequence of DSLExpr objects representing the actions to execute.
        
    Returns:
        RawJS: A block of executed Javascript code (an IIFE).
    """
    js_statements = "; ".join(to_dsl(a).to_js() for a in actions)
    return RawJS(f"(() => {{ {js_statements} }})()")
