"""
Public API Export Module for RailUI.

Importing from this module provides access to all the common building blocks
needed to create a RailUI application.

Example:
    from railui.all import *
"""

from .core.ast import (
    DSLExpr, RawJS,
    # Console
    log, warn, error, alert, confirm_dialog,
    # Timers
    set_timeout, set_interval, clear_interval, clear_timeout,
    # Navigation
    navigate, go_back, go_forward, reload, open_url,
    # DOM
    focus_element, blur_element, click_element,
    scroll_to, scroll_to_element, scroll_to_top,
    set_attribute, remove_attribute,
    add_class, remove_class, toggle_class,
    set_inner_text, set_inner_html, set_value, get_value,
    set_style, show_element, hide_element,
    # Storage
    local_storage_set, local_storage_get, local_storage_remove, local_storage_clear,
    session_storage_set, session_storage_get, session_storage_remove,
    # Clipboard
    copy_to_clipboard,
    # Lifecycle
    on_mount, on_destroy,
    # Sequences / misc
    runSequence, prevent_default, stop_propagation,
    ifelse, typeof,
    # Arrays
    Array,
    # JS Namespaces
    Math, JSON, Object, window, document,
    String, Number, Boolean,
)
from .core.animations import (
    animate,
    fade_in, fade_out,
    slide_in_left, slide_in_right, slide_in_up, slide_out_down,
    spin, bounce, pulse, shake,
    scale_in, scale_out,
)
from .core.signal import createSignal, createEffect, useComputed, createStore, useFetch, Store
from .core.app import App
from .components.base import (
    Component, Page, Text, Button, Container, Input,
    Textarea, Select, Option, Label, Form, Link, Image,
    Show, Each,
)
from .components.advanced import Suspense, ErrorBoundary, Head
from .components.slots import Slot, SlotFill

__all__ = [
    # Core types
    "DSLExpr", "RawJS",
    # Signals & State
    "createSignal", "createEffect", "useComputed", "createStore", "useFetch", "Store",
    # App
    "App",
    # Console
    "log", "warn", "error", "alert", "confirm_dialog",
    # Timers
    "set_timeout", "set_interval", "clear_interval", "clear_timeout",
    # Navigation
    "navigate", "go_back", "go_forward", "reload", "open_url",
    # DOM
    "focus_element", "blur_element", "click_element",
    "scroll_to", "scroll_to_element", "scroll_to_top",
    "set_attribute", "remove_attribute",
    "add_class", "remove_class", "toggle_class",
    "set_inner_text", "set_inner_html", "set_value", "get_value",
    "set_style", "show_element", "hide_element",
    # Storage
    "local_storage_set", "local_storage_get", "local_storage_remove", "local_storage_clear",
    "session_storage_set", "session_storage_get", "session_storage_remove",
    # Clipboard
    "copy_to_clipboard",
    # Lifecycle
    "on_mount", "on_destroy",
    # Misc
    "runSequence", "prevent_default", "stop_propagation",
    "ifelse", "typeof",
    "Array",
    "Math", "JSON", "Object", "window", "document",
    "String", "Number", "Boolean",
    # Animations
    "animate",
    "fade_in", "fade_out",
    "slide_in_left", "slide_in_right", "slide_in_up", "slide_out_down",
    "spin", "bounce", "pulse", "shake",
    "scale_in", "scale_out",
    # Components
    "Component", "Page", "Text", "Button", "Container", "Input",
    "Textarea", "Select", "Option", "Label", "Form", "Link", "Image",
    "Show", "Each",
    "Suspense", "ErrorBoundary", "Head",
    "Slot", "SlotFill",
]
