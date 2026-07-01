"""
Public API Export Module for RailUI.

Importing from this module provides access to all the common building blocks
needed to create a RailUI application.

Example:
    from railui.all import *
"""

from .core.ast import DSLExpr, RawJS
from .core.signal import createSignal, createEffect, useComputed
from .core.render import compile_app
from .core.utils import log, set_timeout, alert, add_class, remove_class, toggle_class, runSequence
from .components.base import Component, Page, Text, Button, Container, Input

__all__ = [
    "DSLExpr",
    "RawJS",
    "createSignal",
    "createEffect",
    "useComputed",
    "compile_app",
    "log",
    "set_timeout",
    "alert",
    "add_class",
    "remove_class",
    "toggle_class",
    "runSequence",
    "Component",
    "Page",
    "Text",
    "Button",
    "Container",
    "Input"
]
