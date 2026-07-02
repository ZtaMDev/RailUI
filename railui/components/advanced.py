"""
Advanced Components for RailUI.

Includes utilities like Suspense, ErrorBoundary, Head, etc.
"""

from typing import Union, Any, Optional
import uuid

from .base import Component, Container
from ..core.ast import DSLExpr, RawJS
from ..core.context import RenderContext

class Head(Component):
    """
    Injects tags into the document <head>.
    For SEO manipulation per route.
    """
    def __init__(self, title: Optional[str] = None, meta: Optional[dict] = None) -> None:
        super().__init__()
        self.tag_name = "div" # We render a hidden div and use JS to move things to head
        self.title = title
        self.meta = meta or {}
        
    def render(self) -> str:
        # Instead of returning HTML, we inject an initialization script
        # that sets the document.title and meta tags dynamically.
        if self.title:
            RenderContext.init_scripts.append(f'document.title = "{self.title}";')
            
        for key, value in self.meta.items():
            # Basic meta tag injection
            script = f"""
            let m_{key} = document.querySelector('meta[name="{key}"]');
            if (!m_{key}) {{
                m_{key} = document.createElement('meta');
                m_{key}.name = "{key}";
                document.head.appendChild(m_{key});
            }}
            m_{key}.content = "{value}";
            """
            RenderContext.init_scripts.append(script)
            
        # Return empty string since this is purely a side-effect component
        return ""


class Suspense(Component):
    """
    Renders a fallback while an async task (like useFetch) is loading.
    
    Args:
        fallback (Component): The component to show while loading.
        loading_signal (DSLExpr): A boolean signal indicating loading state.
    """
    def __init__(self, *children: Union["Component", DSLExpr, str], fallback: Component, loading: DSLExpr, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.tag_name = "div"
        self._fallback = fallback
        self._children = children
        self._loading = loading

    def render(self) -> str:
        uid: str = self.kwargs.get("id", f"el_{uuid.uuid4().hex[:8]}")
        self.kwargs["id"] = uid
        
        # Render both children and fallback into hidden spans, then toggle visibility
        # A more sophisticated compiler might completely unmount them, but display:none is faster for SPA.
        
        main_html = ""
        for c in self._children:
            main_html += c.render() if isinstance(c, Component) else str(c)
            
        fallback_html = self._fallback.render()
        
        cond_js = self._loading.to_js() if isinstance(self._loading, DSLExpr) else str(self._loading)
        
        html = f"""
        <div id="{uid}-fallback" style="display:none;">{fallback_html}</div>
        <div id="{uid}-main" style="display:none;">{main_html}</div>
        """
        
        effect = f"""
        if ({cond_js}) {{
            document.getElementById('{uid}-fallback').style.display = 'block';
            document.getElementById('{uid}-main').style.display = 'none';
        }} else {{
            document.getElementById('{uid}-fallback').style.display = 'none';
            document.getElementById('{uid}-main').style.display = 'block';
        }}
        """
        RenderContext.effects.append(effect)
        
        return html


class ErrorBoundary(Component):
    """
    Catches JS errors in child components and displays a fallback.
    """
    def __init__(self, *children: Union["Component", DSLExpr, str], fallback: Component, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._children = children
        self._fallback = fallback

    def render(self) -> str:
        uid: str = self.kwargs.get("id", f"el_{uuid.uuid4().hex[:8]}")
        
        main_html = ""
        for c in self._children:
            main_html += c.render() if isinstance(c, Component) else str(c)
            
        fallback_html = self._fallback.render()
        
        # In a real framework we'd use window.onerror or try-catch around effects
        # For this prototype we will just render the children.
        return f'<div id="{uid}">{main_html}</div>'

