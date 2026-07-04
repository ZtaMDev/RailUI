"""
Named Slot Components for layout composition.
"""

from typing import Union, Any, Tuple
from .base import Component

class SlotFill(Component):
    """
    Component used to fill a specific named Slot.
    Should be passed as a child to a Component that defines Slots in its layout.
    
    Args:
        name (str): The name of the slot this fill targets.
    """
    def __init__(self, name: str, *children: Union["Component", str, Any], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.slot_name = name
        self.tag_name = "div" # Renders as a wrapper div, or could be transparent

    def render(self) -> str:
        # Transparently render children without the wrapper if no kwargs
        if not self.kwargs:
            html = ""
            for c in self.children:
                html += c.render() if isinstance(c, Component) else str(c)
            return html
        return super().render()


class Slot(Component):
    """
    Defines a named slot in a layout component.
    Searches the provided source tuple for a matching SlotFill.
    
    Args:
        name (str): The name of the slot.
        source (tuple): The children tuple of the layout component to search in.
        default (Union[Component, str, Any], optional): Default content if no SlotFill is found.
    """
    def __init__(self, name: str, source: tuple, default: Union["Component", str, Any] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.slot_name = name
        self.source = source
        self.default = default

    def render(self) -> str:
        for c in self.source:
            if isinstance(c, SlotFill) and c.slot_name == self.slot_name:
                return c.render()
        
        if self.default is not None:
            if isinstance(self.default, Component):
                return self.default.render()
            elif isinstance(self.default, tuple) or isinstance(self.default, list):
                html = ""
                for child in self.default:
                    html += child.render() if isinstance(child, Component) else str(child)
                return html
            return str(self.default)
        return ""

    @staticmethod
    def Unassigned(source: tuple) -> tuple:
        """
        Helper to get all children from a source tuple that are NOT SlotFills.
        This represents the "default" slot body content.
        """
        return tuple(c for c in source if not isinstance(c, SlotFill))
