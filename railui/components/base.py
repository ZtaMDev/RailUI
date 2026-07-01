"""
Core Component system for RailUI.

This module defines the Base Component and standard HTML elements like Container,
Text, Button, and Input.
"""

import uuid
from typing import Any, Union, Dict, Callable
from ..core.ast import DSLExpr, to_dsl
from ..core.context import RenderContext
from ..core.css import register_classes

class Component:
    """
    Base class for all RailUI UI elements.
    """
    def __init__(self, *children: Union["Component", DSLExpr, str], **kwargs: Any) -> None:
        self.tag_name: str = "div"
        self.children = children
        self.kwargs = kwargs

    def render(self) -> str:
        attrs = []
        uid = self.kwargs.get("id", f"el_{uuid.uuid4().hex[:8]}")
        has_id_in_kwargs = "id" in self.kwargs
        
        # We might need an ID for reactive bindings
        has_events = any(k.startswith("on_") for k in self.kwargs)
        needs_id = not has_id_in_kwargs and (
            "bind" in self.kwargs or "class_list" in self.kwargs or has_events
        )
        if needs_id or has_id_in_kwargs:
            attrs.append(f'id="{uid}"')

        # Process CSS classes
        base_classes = []
        if "class_name" in self.kwargs:
            cls_str = self.kwargs.pop("class_name")
            base_classes.append(cls_str)
            register_classes(cls_str)
            
        if "hover_class" in self.kwargs:
            h_cls = self.kwargs.pop("hover_class")
            base_classes.append(h_cls)
            register_classes(h_cls, pseudo=":hover")
            
        if "active_class" in self.kwargs:
            a_cls = self.kwargs.pop("active_class")
            base_classes.append(a_cls)
            register_classes(a_cls, pseudo=":active")
            
        if "class_list" in self.kwargs:
            cl_dict = self.kwargs.pop("class_list")
            for cls_names, condition in cl_dict.items():
                register_classes(cls_names)
                # Register JS effect for toggle
                # condition should be a DSLExpr
                cond_js = to_dsl(condition).to_js()
                for individual_cls in cls_names.split():
                    if not individual_cls.strip(): continue
                    effect_js = f'document.getElementById("{uid}").classList.toggle("{individual_cls}", {cond_js});'
                    RenderContext.effects.append(effect_js)

        if base_classes:
            attrs.append(f'class="{" ".join(base_classes)}"')

        for k, v in self.kwargs.items():
            if k == "id":
                pass # Handled above
            elif k.startswith("on_"):
                event_name = k[3:]
                if isinstance(v, DSLExpr):
                    js_code = v.to_js()
                else:
                    js_code = str(v)
                RenderContext.init_scripts.append(f'document.getElementById("{uid}").addEventListener("{event_name}", function(event) {{ {js_code} }});')
            elif k == "style":
                attrs.append(f'style="{v}"')
            elif k == "bind":
                js_code = f"{v.setter_name}(event.target.value)"
                RenderContext.init_scripts.append(f'document.getElementById("{uid}").addEventListener("input", function(event) {{ {js_code} }});')
                RenderContext.effects.append(f'document.getElementById("{uid}").value = {v.sid}();')
            else:
                attrs.append(f'{k}="{v}"')
        
        attr_str = " " + " ".join(attrs) if attrs else ""
        
        child_html = ""
        for c in self.children:
            if isinstance(c, Component):
                child_html += c.render()
            elif isinstance(c, DSLExpr):
                child_uid = f"el_{uuid.uuid4().hex[:8]}"
                child_html += f'<span id="{child_uid}"></span>'
                RenderContext.effects.append(f'document.getElementById("{child_uid}").innerText = {c.to_js()};')
            else:
                child_html += str(c)
                
        if self.tag_name in ["input", "img", "br", "hr", "meta", "link"]:
            return f"<{self.tag_name}{attr_str} />"
            
        return f"<{self.tag_name}{attr_str}>{child_html}</{self.tag_name}>"

class Container(Component):
    """A generic div container element."""
    def __init__(self, *children: Union["Component", DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "div"

class Text(Component):
    """An inline span text element."""
    def __init__(self, *children: Union["Component", DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "span"

class Button(Component):
    """A clickable button element."""
    def __init__(self, *children: Union["Component", DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "button"

class Input(Component):
    """An input field. Use `bind=signal` to create a two-way binding."""
    def __init__(self, *children: Union["Component", DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "input"

class Page(Component):
    """A semantic main element, typically used as the root of a view."""
    def __init__(self, *children: Union["Component", DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "main"
