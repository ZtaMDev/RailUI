"""
Core Component system for RailUI.

This module defines the base ``Component`` class and all built-in HTML elements.
All components provide type hints for their standard HTML properties and events
to enable rich IDE autocomplete.
"""

import uuid
from typing import Any, Callable, Dict, Optional, Union
from ..core.ast import DSLExpr, to_dsl
from ..core.context import RenderContext
from ..core.css import register_classes, register_hover_for_element, register_active_for_element


def _filter_none(**kwargs: Any) -> Dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}


class Component:
    """
    Base class for all RailUI UI elements.

    Provides shared props like ``class_name``, ``style``, all DOM event handlers,
    and two-way data binding via ``bind``.

    Args:
        *children: Nested ``Component``, ``DSLExpr``, or plain ``str`` content.
        id: HTML ``id`` attribute. Auto-generated when required by reactivity.
        class_name: Static Tailwind/CSS class string.
        hover_class: Extra classes added on ``:hover`` (JavaScript-driven).
        active_class: Extra classes added on ``:active`` (JavaScript-driven).
        class_list: Dict of ``{class_str: DSLExpr}`` for conditional classes.
        style: Inline CSS string.
        bind: A ``SignalGetter`` for two-way reactive binding (input value).
        on_click: DSL expression executed on the ``click`` event.
        on_input: DSL expression executed on the ``input`` event.
        on_change: DSL expression executed on the ``change`` event.
        on_keydown: DSL expression executed on the ``keydown`` event.
        on_keyup: DSL expression executed on the ``keyup`` event.
        on_submit: DSL expression executed on the ``submit`` event.
        on_focus: DSL expression executed on the ``focus`` event.
        on_blur: DSL expression executed on the ``blur`` event.
        on_mouseenter: DSL expression executed on the ``mouseenter`` event.
        on_mouseleave: DSL expression executed on the ``mouseleave`` event.
        on_dblclick: DSL expression executed on the ``dblclick`` event.
        on_scroll: DSL expression executed on the ``scroll`` event.
        on_load: DSL expression executed on the ``load`` event.
    """
    def __init__(
        self,
        *children: Union["Component", DSLExpr, str],
        id: Optional[str] = None,
        class_name: Optional[str] = None,
        hover_class: Optional[str] = None,
        active_class: Optional[str] = None,
        class_list: Optional[Dict[str, DSLExpr]] = None,
        style: Optional[str] = None,
        bind: Optional[Any] = None,
        on_click: Optional[DSLExpr] = None,
        on_input: Optional[DSLExpr] = None,
        on_change: Optional[DSLExpr] = None,
        on_keydown: Optional[DSLExpr] = None,
        on_keyup: Optional[DSLExpr] = None,
        on_keypress: Optional[DSLExpr] = None,
        on_submit: Optional[DSLExpr] = None,
        on_focus: Optional[DSLExpr] = None,
        on_blur: Optional[DSLExpr] = None,
        on_mouseenter: Optional[DSLExpr] = None,
        on_mouseleave: Optional[DSLExpr] = None,
        on_mousedown: Optional[DSLExpr] = None,
        on_mouseup: Optional[DSLExpr] = None,
        on_dblclick: Optional[DSLExpr] = None,
        on_contextmenu: Optional[DSLExpr] = None,
        on_scroll: Optional[DSLExpr] = None,
        on_load: Optional[DSLExpr] = None,
        **kwargs: Any
    ) -> None:
        self.tag_name: str = "div"
        children_kw = kwargs.pop("children", None)
        if children_kw is not None:
            if isinstance(children_kw, Component):
                children = children + (children_kw,)
            elif isinstance(children_kw, (list, tuple)):
                children = children + tuple(children_kw)
        self.children = children
        self.kwargs: Dict[str, Any] = _filter_none(
            id=id, class_name=class_name, hover_class=hover_class,
            active_class=active_class, class_list=class_list, style=style,
            bind=bind, on_click=on_click, on_input=on_input, on_change=on_change,
            on_keydown=on_keydown, on_keyup=on_keyup, on_keypress=on_keypress,
            on_submit=on_submit, on_focus=on_focus, on_blur=on_blur,
            on_mouseenter=on_mouseenter, on_mouseleave=on_mouseleave,
            on_mousedown=on_mousedown, on_mouseup=on_mouseup,
            on_dblclick=on_dblclick, on_contextmenu=on_contextmenu,
            on_scroll=on_scroll, on_load=on_load,
            **kwargs
        )

    def render(self) -> str:
        attrs = []
        uid: str = self.kwargs.get("id", f"el_{uuid.uuid4().hex[:8]}")
        has_id_in_kwargs = "id" in self.kwargs

        has_events = any(k.startswith("on_") for k in self.kwargs)
        has_reactive_kwargs = any(
            isinstance(v, DSLExpr) and not k.startswith("on_")
            for k, v in self.kwargs.items()
        )
        needs_id = not has_id_in_kwargs and (
            "bind" in self.kwargs or "class_list" in self.kwargs or
            "hover_class" in self.kwargs or "active_class" in self.kwargs or has_events or has_reactive_kwargs
        )
        if needs_id or has_id_in_kwargs:
            attrs.append(f'id="{uid}"')

        base_classes = []
        if "class_name" in self.kwargs:
            cls_str: str = self.kwargs.pop("class_name")
            base_classes.append(cls_str)
            register_classes(cls_str)

        if "hover_class" in self.kwargs:
            register_hover_for_element(uid, self.kwargs.pop("hover_class"))

        if "active_class" in self.kwargs:
            register_active_for_element(uid, self.kwargs.pop("active_class"))

        if "class_list" in self.kwargs:
            cl_dict: dict = self.kwargs.pop("class_list")
            for cls_names, condition in cl_dict.items():
                register_classes(cls_names)
                cond_js = to_dsl(condition).to_js()
                for individual_cls in cls_names.split():
                    if not individual_cls.strip(): continue
                    if RenderContext.template_mode:
                        base_classes.append(f"${{{cond_js} ? '{individual_cls}' : ''}}")
                    else:
                        RenderContext.effects.append(
                            f'document.getElementById("{uid}").classList.toggle("{individual_cls}", {cond_js});'
                        )

        if base_classes:
            attrs.append(f'class="{" ".join(base_classes)}"')

        for k, v in list(self.kwargs.items()):
            if k == "id": pass
            elif k.startswith("on_"):
                event_name = k[3:]
                js_code = v.to_js() if isinstance(v, DSLExpr) else str(v)
                RenderContext.init_scripts.append(
                    f'document.getElementById("{uid}").addEventListener("{event_name}", function(event) {{ {js_code} }});'
                )
            elif k == "style":
                attrs.append(f'style="{v}"')
            elif k == "bind":
                setter_js = f"{v.setter_name}(event.target.value)"
                RenderContext.init_scripts.append(
                    f'document.getElementById("{uid}").addEventListener("input", function(event) {{ {setter_js} }});'
                )
                RenderContext.effects.append(f'document.getElementById("{uid}").value = {v.sid}();')
            elif isinstance(v, DSLExpr):
                RenderContext.effects.append(
                    f'document.getElementById("{uid}").{k} = {v.to_js()};'
                )
            elif k == "children":
                pass
            else:
                attr_name = k.replace("_", "-") if k.startswith("data_") or k.startswith("aria_") else k
                attrs.append(f'{attr_name}="{v}"')

        attr_str = " " + " ".join(attrs) if attrs else ""

        child_html = ""
        for c in self.children:
            if isinstance(c, Component):
                child_html += c.render()
            elif isinstance(c, DSLExpr):
                if RenderContext.template_mode:
                    child_html += f"${{{c.to_js()}}}"
                else:
                    child_uid = f"el_{uuid.uuid4().hex[:8]}"
                    child_html += f'<span id="{child_uid}"></span>'
                    RenderContext.effects.append(f'document.getElementById("{child_uid}").innerText = {c.to_js()};')
            else:
                child_html += str(c)

        if self.tag_name in ("input", "img", "br", "hr", "meta", "link"):
            return f"<{self.tag_name}{attr_str} />"
        return f"<{self.tag_name}{attr_str}>{child_html}</{self.tag_name}>"


class Container(Component):
    """
    A generic ``<div>`` container element.

    Args:
        *children: Nested components or strings.
        class_name: CSS/Tailwind class string.
        on_click: DSL expression for click events.
        **kwargs: Any other standard HTML attribute.

    Example::

        Container(
            Text("Hello"),
            Text("World"),
            class_name="flex gap-4 p-6",
        )
    """
    def __init__(
        self, *children: Union["Component", DSLExpr, str],
        id: Optional[str] = None, class_name: Optional[str] = None,
        hover_class: Optional[str] = None, active_class: Optional[str] = None,
        class_list: Optional[Dict[str, DSLExpr]] = None, style: Optional[str] = None,
        on_click: Optional[DSLExpr] = None, **kwargs: Any
    ) -> None:
        super().__init__(
            *children, id=id, class_name=class_name, hover_class=hover_class,
            active_class=active_class, class_list=class_list, style=style,
            on_click=on_click, **kwargs
        )
        self.tag_name = "div"


class Text(Component):
    """
    An inline ``<span>`` text node.

    Can accept a plain string, a signal ref (reactive), or a DSL expression.

    Args:
        *children: Text content — string literals or reactive ``signal()`` calls.
        class_name: CSS/Tailwind class string.

    Example::

        Text("Hello World", class_name="text-lg font-bold")
        Text(user().name, class_name="text-gray-500")  # reactive
        Text(score() * 2, class_name="font-mono")       # DSL expression
    """
    def __init__(
        self, *children: Union["Component", DSLExpr, str],
        id: Optional[str] = None, class_name: Optional[str] = None,
        hover_class: Optional[str] = None, class_list: Optional[Dict[str, DSLExpr]] = None,
        style: Optional[str] = None, **kwargs: Any
    ) -> None:
        super().__init__(
            *children, id=id, class_name=class_name, hover_class=hover_class,
            class_list=class_list, style=style, **kwargs
        )
        self.tag_name = "span"


class Button(Component):
    """
    A ``<button>`` element.

    Args:
        *children: Button label — string or nested components.
        type: HTML button type (``"button"``, ``"submit"``, ``"reset"``).
        disabled: Disable the button (static bool or reactive DSLExpr string).
        on_click: DSL expression executed on click.
        on_dblclick: DSL expression executed on double-click.
        class_name: CSS/Tailwind class string.

    Example::

        Button(
            "Save",
            on_click=setCount(count() + 1),
            class_name="px-4 py-2 bg-blue-600 text-white rounded",
        )
    """
    def __init__(
        self, *children: Union["Component", DSLExpr, str],
        id: Optional[str] = None, class_name: Optional[str] = None,
        hover_class: Optional[str] = None, active_class: Optional[str] = None,
        class_list: Optional[Dict[str, DSLExpr]] = None, style: Optional[str] = None,
        type: str = "button", disabled: Optional[Union[bool, str]] = None,
        on_click: Optional[DSLExpr] = None, on_dblclick: Optional[DSLExpr] = None,
        on_mouseenter: Optional[DSLExpr] = None, on_mouseleave: Optional[DSLExpr] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(
            *children, id=id, class_name=class_name, hover_class=hover_class,
            active_class=active_class, class_list=class_list, style=style,
            type=type, disabled=disabled, on_click=on_click, on_dblclick=on_dblclick,
            on_mouseenter=on_mouseenter, on_mouseleave=on_mouseleave, **kwargs
        )
        self.tag_name = "button"


class Input(Component):
    """
    An ``<input />`` element with optional two-way data binding.

    Args:
        type: Input type (``"text"``, ``"password"``, ``"email"``, ``"number"``, etc.).
        placeholder: Placeholder text.
        value: Static initial value.
        name: HTML name attribute.
        disabled: Disable the input.
        readonly: Make the input read-only.
        bind: A ``SignalGetter`` to bind the input value reactively (two-way).
        on_input: DSL expression on each keystroke.
        on_change: DSL expression when value is committed.

    Example::

        name_input, setName = createSignal("")
        Input(
            type="text",
            placeholder="Enter name...",
            bind=name_input,
        )
    """
    def __init__(
        self,
        id: Optional[str] = None, class_name: Optional[str] = None,
        hover_class: Optional[str] = None, active_class: Optional[str] = None,
        class_list: Optional[Dict[str, DSLExpr]] = None, style: Optional[str] = None,
        type: str = "text", value: Optional[str] = None, placeholder: Optional[str] = None,
        name: Optional[str] = None, disabled: Optional[Union[bool, str]] = None,
        readonly: Optional[Union[bool, str]] = None, checked: Optional[Union[bool, str]] = None,
        min: Optional[str] = None, max: Optional[str] = None, step: Optional[str] = None,
        bind: Optional[Any] = None,
        on_input: Optional[DSLExpr] = None, on_change: Optional[DSLExpr] = None,
        on_focus: Optional[DSLExpr] = None, on_blur: Optional[DSLExpr] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(
            id=id, class_name=class_name, hover_class=hover_class, active_class=active_class,
            class_list=class_list, style=style, type=type, value=value, placeholder=placeholder,
            name=name, disabled=disabled, readonly=readonly, checked=checked, min=min, max=max,
            step=step, bind=bind, on_input=on_input, on_change=on_change,
            on_focus=on_focus, on_blur=on_blur, **kwargs
        )
        self.tag_name = "input"


class Textarea(Component):
    """A ``<textarea>`` element."""
    def __init__(
        self, *children: Union["Component", DSLExpr, str],
        id: Optional[str] = None, class_name: Optional[str] = None,
        hover_class: Optional[str] = None, active_class: Optional[str] = None,
        class_list: Optional[Dict[str, DSLExpr]] = None, style: Optional[str] = None,
        rows: Optional[Union[int, str]] = None, cols: Optional[Union[int, str]] = None,
        placeholder: Optional[str] = None, name: Optional[str] = None,
        disabled: Optional[Union[bool, str]] = None, readonly: Optional[Union[bool, str]] = None,
        bind: Optional[Any] = None,
        on_input: Optional[DSLExpr] = None, on_change: Optional[DSLExpr] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(
            *children, id=id, class_name=class_name, hover_class=hover_class,
            active_class=active_class, class_list=class_list, style=style,
            rows=rows, cols=cols, placeholder=placeholder, name=name,
            disabled=disabled, readonly=readonly, bind=bind,
            on_input=on_input, on_change=on_change, **kwargs
        )
        self.tag_name = "textarea"


class Select(Component):
    """A ``<select>`` element."""
    def __init__(
        self, *children: Union["Component", DSLExpr, str],
        id: Optional[str] = None, class_name: Optional[str] = None,
        hover_class: Optional[str] = None, class_list: Optional[Dict[str, DSLExpr]] = None,
        style: Optional[str] = None, name: Optional[str] = None,
        multiple: Optional[Union[bool, str]] = None, disabled: Optional[Union[bool, str]] = None,
        bind: Optional[Any] = None, on_change: Optional[DSLExpr] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(
            *children, id=id, class_name=class_name, hover_class=hover_class,
            class_list=class_list, style=style, name=name, multiple=multiple,
            disabled=disabled, bind=bind, on_change=on_change, **kwargs
        )
        self.tag_name = "select"


class Option(Component):
    """An ``<option>`` element."""
    def __init__(
        self, *children: Union["Component", DSLExpr, str],
        value: Optional[str] = None, selected: Optional[Union[bool, str]] = None,
        disabled: Optional[Union[bool, str]] = None, **kwargs: Any
    ) -> None:
        super().__init__(*children, value=value, selected=selected, disabled=disabled, **kwargs)
        self.tag_name = "option"


class Label(Component):
    """A ``<label>`` element."""
    def __init__(
        self, *children: Union["Component", DSLExpr, str],
        for_: Optional[str] = None, id: Optional[str] = None,
        class_name: Optional[str] = None, hover_class: Optional[str] = None,
        class_list: Optional[Dict[str, DSLExpr]] = None, style: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        if for_ is not None:
            kwargs["for"] = for_
        super().__init__(
            *children, id=id, class_name=class_name, hover_class=hover_class,
            class_list=class_list, style=style, **kwargs
        )
        self.tag_name = "label"


class Form(Component):
    """A ``<form>`` element."""
    def __init__(
        self, *children: Union["Component", DSLExpr, str],
        id: Optional[str] = None, class_name: Optional[str] = None,
        class_list: Optional[Dict[str, DSLExpr]] = None, style: Optional[str] = None,
        action: Optional[str] = None, method: Optional[str] = None,
        enctype: Optional[str] = None, on_submit: Optional[DSLExpr] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(
            *children, id=id, class_name=class_name, class_list=class_list,
            style=style, action=action, method=method, enctype=enctype,
            on_submit=on_submit, **kwargs
        )
        self.tag_name = "form"


class Link(Component):
    """
    An ``<a>`` anchor element.

    Args:
        *children: Link label — string or nested components.
        href: The URL to navigate to. Supports SPA client-side routing paths.
        target: HTML target attribute (e.g. ``"_blank"``).
        rel: Relationship attribute (e.g. ``"noopener noreferrer"``).
        on_click: DSL expression executed on click (e.g. to prevent default).
        class_name: CSS/Tailwind class string.

    Example::

        Link("Go to Dashboard", href="/dashboard", class_name="underline text-blue-500")
        Link("Open Docs", href="https://example.com", target="_blank")
    """
    def __init__(
        self, *children: Union["Component", DSLExpr, str],
        href: str, target: Optional[str] = None, rel: Optional[str] = None,
        id: Optional[str] = None, class_name: Optional[str] = None,
        hover_class: Optional[str] = None, class_list: Optional[Dict[str, DSLExpr]] = None,
        style: Optional[str] = None, on_click: Optional[DSLExpr] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(
            *children, href=href, target=target, rel=rel, id=id, class_name=class_name,
            hover_class=hover_class, class_list=class_list, style=style, on_click=on_click,
            **kwargs
        )
        self.tag_name = "a"


class Image(Component):
    """An ``<img />`` element."""
    def __init__(
        self, src: str, alt: str,
        id: Optional[str] = None, class_name: Optional[str] = None,
        class_list: Optional[Dict[str, DSLExpr]] = None, style: Optional[str] = None,
        width: Optional[Union[int, str]] = None, height: Optional[Union[int, str]] = None,
        loading: Optional[str] = None, on_load: Optional[DSLExpr] = None,
        on_error: Optional[DSLExpr] = None, **kwargs: Any
    ) -> None:
        super().__init__(
            src=src, alt=alt, id=id, class_name=class_name, class_list=class_list,
            style=style, width=width, height=height, loading=loading,
            on_load=on_load, on_error=on_error, **kwargs
        )
        self.tag_name = "img"


class Page(Component):
    """A semantic ``<main>`` element."""
    def __init__(
        self, *children: Union["Component", DSLExpr, str],
        id: Optional[str] = None, class_name: Optional[str] = None,
        style: Optional[str] = None, **kwargs: Any
    ) -> None:
        super().__init__(*children, id=id, class_name=class_name, style=style, **kwargs)
        self.tag_name = "main"


class Show(Component):
    """
    Conditionally render children based on a reactive signal expression.

    The component wraps its children in a ``<div>`` that is shown or hidden
    by toggling CSS ``display`` via a reactive JavaScript effect.

    Args:
        *children: Content to render when the condition is truthy.
        when: A ``DSLExpr`` (e.g. ``is_logged_in()``) that controls visibility.
        on_mount: DSL expression executed once when the component first becomes visible.
        on_update: DSL expression executed each time visibility changes to visible.
        on_unmount: DSL expression executed when the component becomes hidden.
        class_name: CSS/Tailwind class string for the wrapper div.

    Example::

        is_admin, _ = createSignal(False)

        Show(
            Text("Admin Panel"),
            when=is_admin(),
            on_mount=log("Admin panel mounted"),
            on_unmount=log("Admin panel hidden"),
        )
    """
    def __init__(
        self, *children: Union["Component", DSLExpr, str],
        when: DSLExpr, id: Optional[str] = None, class_name: Optional[str] = None,
        style: Optional[str] = None, fallback: Optional[Union["Component", str]] = None,
        on_mount: Optional[DSLExpr] = None,
        on_unmount: Optional[DSLExpr] = None,
        on_update: Optional[DSLExpr] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(*children, id=id, class_name=class_name, style=style, **kwargs)
        self.tag_name = "div"
        self._when = when
        self._fallback = fallback
        self._on_mount = on_mount
        self._on_unmount = on_unmount
        self._on_update = on_update

    def render(self) -> str:
        uid: str = self.kwargs.get("id", f"el_{uuid.uuid4().hex[:8]}")
        self.kwargs["id"] = uid
        cond_js = self._when.to_js() if isinstance(self._when, DSLExpr) else str(self._when)
        
        if self._fallback:
            main_html = ""
            for c in self.children:
                main_html += c.render() if isinstance(c, Component) else str(c)
            fallback_html = self._fallback.render() if isinstance(self._fallback, Component) else self._fallback
            html = f"""
            <div id="{uid}-show-main">{main_html}</div>
            <div id="{uid}-show-fallback">{fallback_html}</div>
            """
            RenderContext.effects.append(
                f"(function() {{ "
                f"const show = {cond_js}; "
                f"document.getElementById('{uid}-show-main').style.display = show ? '' : 'none'; "
                f"document.getElementById('{uid}-show-fallback').style.display = show ? 'none' : ''; "
                f"}})();"
            )
            return html
        
        # Build callbacks object
        cb_parts = []
        if self._on_mount: cb_parts.append(f"onMount: () => {{ {self._on_mount.to_js()} }}")
        if self._on_unmount: cb_parts.append(f"onUnmount: () => {{ {self._on_unmount.to_js()} }}")
        if self._on_update: cb_parts.append(f"onUpdate: () => {{ {self._on_update.to_js()} }}")
        callbacks = "{" + ", ".join(cb_parts) + "}"
        
        RenderContext.effects.append(f'$show("{uid}", {cond_js}, {callbacks});')
        return super().render()


class Each(Component):
    """
    Reactively render a list of items from a signal.

    Automatically re-renders the list whenever the signal changes. Uses an
    optional ``render_fn`` lambda to template each item. The lambda receives
    the current ``item`` and its ``index`` as DSL-compatible proxy objects.

    Args:
        items: A ``SignalGetter`` holding the list to iterate.
        render_fn: A ``lambda item, index: Component`` that templates each item.
        on_mount: DSL expression executed once when the list first renders.
        on_update: DSL expression executed each time items change.
        on_unmount: DSL expression executed when the list becomes empty.
        class_name: CSS/Tailwind class string for the wrapper div.

    Example::

        posts, setPosts = createSignal([])

        Each(
            items=posts,
            render_fn=lambda post, i: Container(
                Text(post.title, class_name="font-bold"),
                Text(post.body, class_name="text-gray-500 text-sm"),
                class_name="p-4 border rounded mb-2",
            ),
            on_update=log("Posts list updated"),
        )
    """
    def __init__(
        self, items: DSLExpr, render_fn: Callable[[Any, Any], Union["Component", str]],
        id: Optional[str] = None, class_name: Optional[str] = None,
        style: Optional[str] = None, 
        on_mount: Optional[DSLExpr] = None,
        on_unmount: Optional[DSLExpr] = None,
        on_update: Optional[DSLExpr] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(id=id, class_name=class_name, style=style, **kwargs)
        self._items = items
        self._render_fn = render_fn
        self._on_mount = on_mount
        self._on_unmount = on_unmount
        self._on_update = on_update

    def render(self) -> str:
        uid: str = self.kwargs.get("id", f"el_{uuid.uuid4().hex[:8]}")
        self.kwargs["id"] = uid

        from ..core.ast import ItemProxy
        old_mode = RenderContext.template_mode
        old_effects_len = len(RenderContext.effects)
        old_init_scripts_len = len(RenderContext.init_scripts)
        RenderContext.template_mode = True

        try:
            item_proxy = ItemProxy("item")
            index_proxy = ItemProxy("index")
            component_tree = self._render_fn(item_proxy, index_proxy)
            template_html = component_tree.render() if isinstance(component_tree, Component) else component_tree
        finally:
            RenderContext.template_mode = old_mode
            if len(RenderContext.effects) > old_effects_len:
                RenderContext.effects = RenderContext.effects[:old_effects_len]
            if len(RenderContext.init_scripts) > old_init_scripts_len:
                RenderContext.init_scripts = RenderContext.init_scripts[:old_init_scripts_len]

        safe_html = template_html.replace("\\", "\\\\").replace("`", "\\`")
        items_js = self._items.to_js() if isinstance(self._items, DSLExpr) else str(self._items)
        
        cb_parts = []
        if self._on_mount: cb_parts.append(f"onMount: () => {{ {self._on_mount.to_js()} }}")
        if self._on_unmount: cb_parts.append(f"onUnmount: () => {{ {self._on_unmount.to_js()} }}")
        if self._on_update: cb_parts.append(f"onUpdate: () => {{ {self._on_update.to_js()} }}")
        callbacks = "{" + ", ".join(cb_parts) + "}"
        
        effect = f'$renderEach("{uid}", {items_js}, (item, index) => `{safe_html}`, {callbacks});'
        RenderContext.effects.append(effect)
        return super().render()
