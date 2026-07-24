"""
RailUI

A pure-Python UI framework that compiles directly into dependency-free Javascript/HTML SPA bundles.
"""

__version__ = "0.1.3"

__all__ = [
    "DSLExpr", "RawJS",
    "log", "warn", "error", "alert", "confirm_dialog",
    "set_timeout", "set_interval", "clear_interval", "clear_timeout",
    "navigate", "go_back", "go_forward", "reload", "open_url",
    "add_class", "remove_class", "toggle_class",
    "runSequence", "prevent_default", "stop_propagation", "event_value", "ifelse", "typeof",
    "createSignal", "createEffect", "useComputed", "createStore", "useFetch", "Store", "useAction",
    "App",
    "Component", "Container", "Text", "Button", "Input", "Textarea", "Select", "Option", "Label", "Form", "Link", "Image", "Page", "Show", "Each",
    "Suspense", "ErrorBoundary", "Head",
    "Slot", "SlotFill",
    "server_action", "ServerActionCall",
    "Math", "JSON", "Object", "window", "document",
    "animate", "fade_in", "fade_out", "slide_in_left", "slide_in_right", "slide_in_up", "slide_out_down",
    "spin", "bounce", "pulse", "shake", "scale_in", "scale_out",
]

from .all import *
