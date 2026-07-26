"""
elements.py — Extended HTML component library for RailUI.

Provides typed Python wrappers for the full spectrum of HTML elements,
organized into the following groups:

- **Typography**: Heading, Paragraph, Strong, Em, Code, Pre, Blockquote, Hr, Br
- **Media**: Img, Video, Audio, Source, Picture, Canvas, Iframe, Figure, Figcaption
- **Lists**: Ul, Ol, Li, Dl, Dt, Dd
- **Tables**: Table, Thead, Tbody, Tfoot, Tr, Th, Td, Caption, Colgroup, Col
- **Layout / Semantic**: Header, Footer, Nav, Section, Article, Aside, Main, Div, Span
- **Interactive**: Details, Summary, Dialog, Progress, Meter
- **Forms & Inputs**: Fieldset, Legend, Datalist, Output, Search
- **Scripting helpers**: Portal, Fragment

All components accept the same base props as :class:`~railui.components.base.Component`
(``class_name``, ``style``, ``id``, event handlers, etc.).
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional, Union

from .base import Component
from ..core.ast import DSLExpr
from ..core.context import RenderContext


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _filter_none(**kwargs: Any) -> Dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}


# ===========================================================================
# Typography
# ===========================================================================

class Heading(Component):
    """
    A semantic heading element (``<h1>`` through ``<h6>``).

    Args:
        *children: Heading text or nested components.
        level: Heading level between 1 and 6. Defaults to ``1``.
        class_name: Tailwind / CSS class string.
        style: Inline CSS string.

    Example::

        Heading("Welcome to RailUI", level=1, class_name="text-5xl font-black")
        Heading("Section Title", level=2, class_name="text-3xl font-bold mb-4")
    """
    def __init__(
        self,
        *children: Union[Component, DSLExpr, str],
        level: int = 1,
        id: Optional[str] = None,
        class_name: Optional[str] = None,
        hover_class: Optional[str] = None,
        class_list: Optional[Dict[str, DSLExpr]] = None,
        style: Optional[str] = None,
        on_click: Optional[DSLExpr] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            *children, id=id, class_name=class_name, hover_class=hover_class,
            class_list=class_list, style=style, on_click=on_click, **kwargs
        )
        self.tag_name = f"h{max(1, min(6, level))}"


# Convenience aliases
class H1(Heading):
    """``<h1>`` — top-level page heading."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, level=1, **kwargs)

class H2(Heading):
    """``<h2>`` — section heading."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, level=2, **kwargs)

class H3(Heading):
    """``<h3>`` — subsection heading."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, level=3, **kwargs)

class H4(Heading):
    """``<h4>`` — minor heading."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, level=4, **kwargs)

class H5(Heading):
    """``<h5>`` — sub-minor heading."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, level=5, **kwargs)

class H6(Heading):
    """``<h6>`` — fine-print heading."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, level=6, **kwargs)


class Paragraph(Component):
    """
    A ``<p>`` paragraph element.

    Args:
        *children: Text or inline components.
        class_name: Tailwind / CSS class string.

    Example::

        Paragraph("This is a paragraph of text.", class_name="text-gray-600 leading-relaxed")
    """
    def __init__(
        self,
        *children: Union[Component, DSLExpr, str],
        id: Optional[str] = None,
        class_name: Optional[str] = None,
        hover_class: Optional[str] = None,
        class_list: Optional[Dict[str, DSLExpr]] = None,
        style: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*children, id=id, class_name=class_name, hover_class=hover_class,
                         class_list=class_list, style=style, **kwargs)
        self.tag_name = "p"


class Strong(Component):
    """
    A ``<strong>`` element for bold, semantically important text.

    Example::

        Strong("Important!", class_name="text-red-600")
    """
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "strong"


class Em(Component):
    """
    An ``<em>`` element for italicized, semantically emphasized text.

    Example::

        Em("Note: this is important.", class_name="text-gray-500 italic")
    """
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "em"


class Small(Component):
    """``<small>`` — side-comments, fine print, legal text."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "small"


class Mark(Component):
    """``<mark>`` — highlighted / marked text (yellow highlight by default)."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "mark"


class Del(Component):
    """``<del>`` — deleted / strikethrough text."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "del"


class Ins(Component):
    """``<ins>`` — inserted / underlined text."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "ins"


class Sub(Component):
    """``<sub>`` — subscript text (e.g. chemical formulas)."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "sub"


class Sup(Component):
    """``<sup>`` — superscript text (e.g. footnote markers)."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "sup"


class Code(Component):
    """
    An inline ``<code>`` element for monospace code snippets.

    Example::

        Code("railui dev", class_name="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono")
    """
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "code"


class Pre(Component):
    """
    A ``<pre>`` element preserving whitespace, commonly wraps ``Code``.

    Example::

        Pre(Code("def hello():\\n    print('Hello!')"), class_name="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto")
    """
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "pre"


class Blockquote(Component):
    """
    A ``<blockquote>`` element for long quotations.

    Args:
        *children: Quote content.
        cite: URL of the source document.

    Example::

        Blockquote(
            Paragraph("The only way to do great work is to love what you do."),
            cite="https://example.com",
            class_name="border-l-4 border-blue-400 pl-4 italic text-gray-600",
        )
    """
    def __init__(
        self,
        *children: Union[Component, DSLExpr, str],
        cite: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*children, cite=cite, **kwargs)
        self.tag_name = "blockquote"


class Abbr(Component):
    """``<abbr>`` — abbreviation with optional tooltip via ``title``."""
    def __init__(
        self,
        *children: Union[Component, DSLExpr, str],
        title: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*children, title=title, **kwargs)
        self.tag_name = "abbr"


class Cite(Component):
    """``<cite>`` — title of a creative work."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "cite"


class Hr(Component):
    """
    A ``<hr />`` horizontal rule (thematic break).

    Example::

        Hr(class_name="my-8 border-gray-200")
    """
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.tag_name = "hr"


class Br(Component):
    """A ``<br />`` line break."""
    def __init__(self) -> None:
        super().__init__()
        self.tag_name = "br"


class Span(Component):
    """
    A generic inline ``<span>`` wrapper.

    Example::

        Span("hello", class_name="text-blue-500 font-semibold")
    """
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "span"


# ===========================================================================
# Media
# ===========================================================================

class Img(Component):
    """
    An ``<img />`` element with relative-path support.

    Place images in the ``public/`` directory (or any directory listed in
    ``public_dirs`` inside ``railui.config.json``). Paths starting with
    ``/`` are served relative to the SPA root; paths without a leading
    slash are resolved relative to the current route.

    Args:
        src: Image path (e.g. ``"/images/logo.png"``) or external URL.
        alt: Descriptive alt text — required for accessibility.
        width: Intrinsic width in pixels or CSS string.
        height: Intrinsic height in pixels or CSS string.
        loading: ``"lazy"`` (default) or ``"eager"``.
        decoding: ``"async"``, ``"sync"``, or ``"auto"``.
        crossorigin: CORS setting (``"anonymous"`` or ``"use-credentials"``).
        on_load: DSL expression fired when the image finishes loading.
        on_error: DSL expression fired when the image fails to load.

    Example::

        # The file must exist at public/images/hero.jpg
        Img(
            src="/images/hero.jpg",
            alt="Hero banner",
            loading="lazy",
            class_name="w-full h-64 object-cover rounded-xl",
        )

        # External URL
        Img(src="https://picsum.photos/400/300", alt="Placeholder")
    """
    def __init__(
        self,
        src: str,
        alt: str = "",
        *,
        id: Optional[str] = None,
        class_name: Optional[str] = None,
        class_list: Optional[Dict[str, DSLExpr]] = None,
        style: Optional[str] = None,
        width: Optional[Union[int, str]] = None,
        height: Optional[Union[int, str]] = None,
        loading: Optional[str] = "lazy",
        decoding: Optional[str] = None,
        crossorigin: Optional[str] = None,
        on_load: Optional[DSLExpr] = None,
        on_error: Optional[DSLExpr] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            src=src, alt=alt, id=id, class_name=class_name, class_list=class_list,
            style=style, width=width, height=height, loading=loading,
            decoding=decoding, crossorigin=crossorigin,
            on_load=on_load, on_error=on_error, **kwargs
        )
        self.tag_name = "img"


class Video(Component):
    """
    A ``<video>`` element.

    Place video files in ``public/`` or a directory listed in ``public_dirs``
    in ``railui.config.json``.

    Args:
        *children: ``Source`` components or fallback text.
        src: Direct video URL (alternative to ``Source`` children).
        controls: Show native browser controls.
        autoplay: Autoplay the video on load.
        loop: Loop the video.
        muted: Mute audio (required for autoplay in most browsers).
        playsinline: Prevent full-screen on iOS.
        poster: URL of a preview image shown before play.
        width: Player width.
        height: Player height.
        preload: ``"auto"``, ``"metadata"``, or ``"none"``.
        crossorigin: CORS setting.
        on_play: DSL expression fired on play.
        on_pause: DSL expression fired on pause.
        on_ended: DSL expression fired when playback ends.

    Example::

        Video(
            Source(src="/videos/demo.mp4", type="video/mp4"),
            controls=True,
            muted=True,
            autoplay=True,
            loop=True,
            class_name="w-full rounded-xl",
        )
    """
    def __init__(
        self,
        *children: Union[Component, DSLExpr, str],
        src: Optional[str] = None,
        controls: Optional[bool] = None,
        autoplay: Optional[bool] = None,
        loop: Optional[bool] = None,
        muted: Optional[bool] = None,
        playsinline: Optional[bool] = None,
        poster: Optional[str] = None,
        width: Optional[Union[int, str]] = None,
        height: Optional[Union[int, str]] = None,
        preload: Optional[str] = None,
        crossorigin: Optional[str] = None,
        id: Optional[str] = None,
        class_name: Optional[str] = None,
        style: Optional[str] = None,
        on_play: Optional[DSLExpr] = None,
        on_pause: Optional[DSLExpr] = None,
        on_ended: Optional[DSLExpr] = None,
        **kwargs: Any,
    ) -> None:
        # Boolean HTML attributes — only add when True
        bools: Dict[str, Any] = {}
        if controls:
            bools["controls"] = "controls"
        if autoplay:
            bools["autoplay"] = "autoplay"
        if loop:
            bools["loop"] = "loop"
        if muted:
            bools["muted"] = "muted"
        if playsinline:
            bools["playsinline"] = "playsinline"
        super().__init__(
            *children,
            src=src, id=id, class_name=class_name, style=style,
            poster=poster, width=width, height=height, preload=preload,
            crossorigin=crossorigin,
            on_play=on_play, on_pause=on_pause, on_ended=on_ended,
            **bools, **kwargs
        )
        self.tag_name = "video"


class Audio(Component):
    """
    An ``<audio>`` element.

    Args:
        *children: ``Source`` components or fallback text.
        src: Direct audio URL (alternative to ``Source`` children).
        controls: Show native browser controls.
        autoplay: Autoplay on load.
        loop: Loop.
        muted: Mute.
        preload: ``"auto"``, ``"metadata"``, or ``"none"``.
        on_play: DSL expression on play.
        on_ended: DSL expression when playback ends.

    Example::

        Audio(
            Source(src="/audio/bg.mp3", type="audio/mpeg"),
            controls=True,
            class_name="w-full",
        )
    """
    def __init__(
        self,
        *children: Union[Component, DSLExpr, str],
        src: Optional[str] = None,
        controls: Optional[bool] = None,
        autoplay: Optional[bool] = None,
        loop: Optional[bool] = None,
        muted: Optional[bool] = None,
        preload: Optional[str] = None,
        id: Optional[str] = None,
        class_name: Optional[str] = None,
        style: Optional[str] = None,
        on_play: Optional[DSLExpr] = None,
        on_pause: Optional[DSLExpr] = None,
        on_ended: Optional[DSLExpr] = None,
        **kwargs: Any,
    ) -> None:
        bools: Dict[str, Any] = {}
        if controls:
            bools["controls"] = "controls"
        if autoplay:
            bools["autoplay"] = "autoplay"
        if loop:
            bools["loop"] = "loop"
        if muted:
            bools["muted"] = "muted"
        super().__init__(
            *children,
            src=src, id=id, class_name=class_name, style=style,
            preload=preload, on_play=on_play, on_pause=on_pause, on_ended=on_ended,
            **bools, **kwargs
        )
        self.tag_name = "audio"


class Source(Component):
    """
    A ``<source />`` element — child of ``Video``, ``Audio``, or ``Picture``.

    Args:
        src: Media URL.
        type: MIME type (e.g. ``"video/mp4"`` or ``"image/webp"``).
        media: Media query for ``Picture`` source selection.
        srcset: Responsive image srcset (for ``Picture``).
        sizes: Responsive sizes hint (for ``Picture``).

    Example::

        Video(
            Source(src="/video/demo.webm", type="video/webm"),
            Source(src="/video/demo.mp4", type="video/mp4"),
            controls=True,
        )
    """
    def __init__(
        self,
        src: Optional[str] = None,
        type: Optional[str] = None,
        media: Optional[str] = None,
        srcset: Optional[str] = None,
        sizes: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(src=src, type=type, media=media, srcset=srcset, sizes=sizes, **kwargs)
        self.tag_name = "source"

    def render(self) -> str:
        # <source> is void
        return super().render()


class Picture(Component):
    """
    A ``<picture>`` responsive image container.

    Wrap ``Source`` elements and a fallback ``Img`` (required) for art direction
    or format switching.

    Example::

        Picture(
            Source(srcset="/images/hero.webp", type="image/webp"),
            Source(srcset="/images/hero.jpg", type="image/jpeg"),
            Img(src="/images/hero.jpg", alt="Hero", class_name="w-full"),
            class_name="block",
        )
    """
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "picture"


class Figure(Component):
    """
    A ``<figure>`` element — wraps self-contained content like images or code.

    Example::

        Figure(
            Img(src="/charts/sales.png", alt="Sales chart"),
            Figcaption("Figure 1: Q4 Sales Data"),
            class_name="my-6 text-center",
        )
    """
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "figure"


class Figcaption(Component):
    """``<figcaption>`` — caption for a ``Figure``."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "figcaption"


class Canvas(Component):
    """
    A ``<canvas>`` element for 2D/WebGL drawing.

    Args:
        width: Canvas width in pixels.
        height: Canvas height in pixels.
        id: Required to access from JavaScript via ``document.getElementById``.

    Example::

        Canvas(id="my-chart", width=600, height=400, class_name="rounded shadow")
    """
    def __init__(
        self,
        *,
        id: Optional[str] = None,
        class_name: Optional[str] = None,
        style: Optional[str] = None,
        width: Optional[Union[int, str]] = None,
        height: Optional[Union[int, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(id=id, class_name=class_name, style=style, width=width, height=height, **kwargs)
        self.tag_name = "canvas"


class Iframe(Component):
    """
    An ``<iframe>`` inline frame.

    Args:
        src: URL of the embedded content.
        title: Accessibility title (required for screen readers).
        width: Frame width.
        height: Frame height.
        allow: Feature policy string.
        sandbox: Sandbox attribute value.
        loading: ``"lazy"`` (default) or ``"eager"``.
        allowfullscreen: Allow fullscreen mode.

    Example::

        Iframe(
            src="https://www.youtube.com/embed/dQw4w9WgXcQ",
            title="RailUI demo",
            width=560,
            height=315,
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope",
            allowfullscreen=True,
            class_name="rounded-xl shadow-lg",
        )
    """
    def __init__(
        self,
        *,
        src: str,
        title: str = "",
        id: Optional[str] = None,
        class_name: Optional[str] = None,
        style: Optional[str] = None,
        width: Optional[Union[int, str]] = None,
        height: Optional[Union[int, str]] = None,
        allow: Optional[str] = None,
        sandbox: Optional[str] = None,
        loading: str = "lazy",
        allowfullscreen: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        bools: Dict[str, Any] = {}
        if allowfullscreen:
            bools["allowfullscreen"] = "allowfullscreen"
        super().__init__(
            src=src, title=title, id=id, class_name=class_name, style=style,
            width=width, height=height, allow=allow, sandbox=sandbox,
            loading=loading, **bools, **kwargs
        )
        self.tag_name = "iframe"


# ===========================================================================
# Lists
# ===========================================================================

class Ul(Component):
    """
    An ``<ul>`` unordered list.

    Example::

        Ul(
            Li("Item 1"),
            Li("Item 2"),
            Li("Item 3"),
            class_name="list-disc list-inside space-y-1 text-gray-700",
        )
    """
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "ul"


class Ol(Component):
    """
    An ``<ol>`` ordered list.

    Args:
        type: Marker type: ``"1"`` (default), ``"a"``, ``"A"``, ``"i"``, ``"I"``.
        start: Starting number.
        reversed: Reverse the list order.
    """
    def __init__(
        self,
        *children: Union[Component, DSLExpr, str],
        type: Optional[str] = None,
        start: Optional[int] = None,
        reversed: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        bools: Dict[str, Any] = {}
        if reversed:
            bools["reversed"] = "reversed"
        super().__init__(*children, type=type, start=start, **bools, **kwargs)
        self.tag_name = "ol"


class Li(Component):
    """
    A ``<li>`` list item.

    Example::

        Li("First item", class_name="py-1 border-b")
    """
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "li"


class Dl(Component):
    """``<dl>`` — description list (contains ``Dt`` / ``Dd`` pairs)."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "dl"


class Dt(Component):
    """``<dt>`` — description term."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "dt"


class Dd(Component):
    """``<dd>`` — description details."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "dd"


# ===========================================================================
# Tables
# ===========================================================================

class Table(Component):
    """
    A ``<table>`` element.

    Example::

        Table(
            Thead(Tr(Th("Name"), Th("Age"), Th("City"))),
            Tbody(
                Tr(Td("Alice"), Td("30"), Td("New York")),
                Tr(Td("Bob"),   Td("25"), Td("London")),
            ),
            class_name="w-full border-collapse text-sm",
        )
    """
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "table"


class Caption(Component):
    """``<caption>`` — table caption (must be first child of ``Table``)."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "caption"


class Colgroup(Component):
    """``<colgroup>`` — group of columns for styling."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "colgroup"


class Col(Component):
    """``<col>`` — individual column in a ``Colgroup``."""
    def __init__(self, *, span: Optional[int] = None, **kwargs: Any) -> None:
        super().__init__(span=span, **kwargs)
        self.tag_name = "col"


class Thead(Component):
    """``<thead>`` — table head section."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "thead"


class Tbody(Component):
    """``<tbody>`` — table body section."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "tbody"


class Tfoot(Component):
    """``<tfoot>`` — table foot section."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "tfoot"


class Tr(Component):
    """``<tr>`` — table row."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "tr"


class Th(Component):
    """
    ``<th>`` — table header cell.

    Args:
        colspan: Number of columns to span.
        rowspan: Number of rows to span.
        scope: ``"col"``, ``"row"``, ``"colgroup"``, or ``"rowgroup"``.
    """
    def __init__(
        self,
        *children: Union[Component, DSLExpr, str],
        colspan: Optional[int] = None,
        rowspan: Optional[int] = None,
        scope: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*children, colspan=colspan, rowspan=rowspan, scope=scope, **kwargs)
        self.tag_name = "th"


class Td(Component):
    """
    ``<td>`` — table data cell.

    Args:
        colspan: Number of columns to span.
        rowspan: Number of rows to span.
    """
    def __init__(
        self,
        *children: Union[Component, DSLExpr, str],
        colspan: Optional[int] = None,
        rowspan: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*children, colspan=colspan, rowspan=rowspan, **kwargs)
        self.tag_name = "td"


# ===========================================================================
# Semantic Layout
# ===========================================================================

class Header(Component):
    """
    A ``<header>`` semantic element — page or section header.

    Example::

        Header(
            H1("My App"),
            Nav(Link("Home", href="/"), Link("About", href="/about")),
            class_name="flex items-center justify-between px-8 py-4 bg-white shadow",
        )
    """
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "header"


class Footer(Component):
    """
    A ``<footer>`` semantic element — page or section footer.

    Example::

        Footer(
            Paragraph("© 2025 My Company", class_name="text-gray-400 text-sm"),
            class_name="py-8 text-center bg-gray-900",
        )
    """
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "footer"


class Nav(Component):
    """
    A ``<nav>`` semantic element for navigation links.

    Example::

        Nav(
            Link("Home", href="/", class_name="mr-4"),
            Link("About", href="/about", class_name="mr-4"),
            class_name="flex items-center gap-4",
        )
    """
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "nav"


class Section(Component):
    """``<section>`` — thematic grouping of content with a heading."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "section"


class Article(Component):
    """``<article>`` — self-contained content (blog post, news article, etc.)."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "article"


class Aside(Component):
    """``<aside>`` — content tangentially related to the main content (sidebar)."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "aside"


class Main(Component):
    """
    ``<main>`` — the primary content of the document.

    .. note::
        There should be only one ``<main>`` per page. For pages within a layout,
        prefer using RailUI's ``Page`` (which also renders as ``<main>``) or
        a regular ``Container``.
    """
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "main"


class Div(Component):
    """
    A plain ``<div>`` container — alias of ``Container``.

    Prefer ``Container`` in most cases; use ``Div`` when you want to be
    explicit about the element name.
    """
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "div"


# ===========================================================================
# Interactive Elements
# ===========================================================================

class Details(Component):
    """
    A ``<details>`` disclosure widget (accordion).

    Args:
        *children: Must contain a ``Summary`` and the hidden content.
        open: Whether the disclosure is open by default.

    Example::

        Details(
            Summary("Click to expand"),
            Paragraph("Hidden content revealed on click."),
            class_name="border rounded-lg p-4",
        )
    """
    def __init__(
        self,
        *children: Union[Component, DSLExpr, str],
        open: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        bools: Dict[str, Any] = {}
        if open:
            bools["open"] = "open"
        super().__init__(*children, **bools, **kwargs)
        self.tag_name = "details"


class Summary(Component):
    """
    ``<summary>`` — visible label for a ``Details`` disclosure widget.

    Example::

        Summary("FAQ: What is RailUI?", class_name="cursor-pointer font-semibold")
    """
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "summary"


class Dialog(Component):
    """
    A ``<dialog>`` modal element.

    Requires JavaScript to open (``HTMLDialogElement.showModal()``).
    Use the ``id`` prop and a RailUI ``RawJS`` expression to trigger it.

    Args:
        *children: Dialog content.
        open: Start in open state.

    Example::

        Dialog(
            H2("Confirm Action"),
            Paragraph("Are you sure?"),
            Button("Yes", on_click=RawJS("document.getElementById('confirm-dlg').close()")),
            id="confirm-dlg",
            class_name="rounded-2xl shadow-2xl p-6 backdrop:bg-black/50",
        )
    """
    def __init__(
        self,
        *children: Union[Component, DSLExpr, str],
        open: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        bools: Dict[str, Any] = {}
        if open:
            bools["open"] = "open"
        super().__init__(*children, **bools, **kwargs)
        self.tag_name = "dialog"


class Progress(Component):
    """
    A ``<progress>`` loading / progress bar.

    Args:
        value: Current progress value (numeric or reactive DSLExpr).
        max: Maximum value (default 100).

    Example::

        Progress(value=75, max=100, class_name="w-full h-2 accent-blue-500")

        # Reactive
        upload_pct, _ = createSignal(0)
        Progress(value=upload_pct(), max=100)
    """
    def __init__(
        self,
        *,
        value: Optional[Union[int, float, DSLExpr]] = None,
        max: Optional[Union[int, float]] = None,
        id: Optional[str] = None,
        class_name: Optional[str] = None,
        style: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(value=value, max=max, id=id, class_name=class_name, style=style, **kwargs)
        self.tag_name = "progress"


class Meter(Component):
    """
    A ``<meter>`` gauge element for a scalar measurement within a known range.

    Args:
        value: Current value.
        min: Minimum value.
        max: Maximum value.
        low: Upper bound of the low range.
        high: Lower bound of the high range.
        optimum: Optimal value.

    Example::

        Meter(value=0.7, min=0, max=1, low=0.3, high=0.8, optimum=0.9)
    """
    def __init__(
        self,
        *,
        value: Union[int, float],
        min: Optional[Union[int, float]] = None,
        max: Optional[Union[int, float]] = None,
        low: Optional[Union[int, float]] = None,
        high: Optional[Union[int, float]] = None,
        optimum: Optional[Union[int, float]] = None,
        id: Optional[str] = None,
        class_name: Optional[str] = None,
        style: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            value=value, min=min, max=max, low=low, high=high, optimum=optimum,
            id=id, class_name=class_name, style=style, **kwargs
        )
        self.tag_name = "meter"


# ===========================================================================
# Forms & Inputs
# ===========================================================================

class Fieldset(Component):
    """
    ``<fieldset>`` — groups related form controls.

    Args:
        *children: Form controls and a ``Legend``.
        disabled: Disable all controls inside.

    Example::

        Fieldset(
            Legend("Personal Information"),
            Label("Name", for_="name"),
            Input(type="text", id="name"),
            class_name="border rounded-lg p-4",
        )
    """
    def __init__(
        self,
        *children: Union[Component, DSLExpr, str],
        disabled: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        bools: Dict[str, Any] = {}
        if disabled:
            bools["disabled"] = "disabled"
        super().__init__(*children, **bools, **kwargs)
        self.tag_name = "fieldset"


class Legend(Component):
    """``<legend>`` — caption for a ``Fieldset``."""
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "legend"


class Datalist(Component):
    """
    ``<datalist>`` — pre-defined options for an ``Input`` with ``list`` attribute.

    Example::

        Datalist(
            Option(value="Python"),
            Option(value="JavaScript"),
            Option(value="Rust"),
            id="languages",
        )
        Input(type="text", list="languages")
    """
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "datalist"


class Output(Component):
    """
    ``<output>`` — result of a calculation or user action.

    Args:
        for_: Space-separated IDs of input elements it relates to.
        name: Name of the output element.
    """
    def __init__(
        self,
        *children: Union[Component, DSLExpr, str],
        for_: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if for_ is not None:
            kwargs["for"] = for_
        super().__init__(*children, name=name, **kwargs)
        self.tag_name = "output"


# ===========================================================================
# Utility / Composition helpers
# ===========================================================================

class Fragment(Component):
    """
    A transparent wrapper that renders its children with **no** surrounding element.

    Useful for returning multiple root-level components from a function without
    introducing a spurious ``<div>`` into the DOM.

    Example::

        def page() -> Component:
            return Fragment(
                Header(...),
                Main(...),
                Footer(...),
            )
    """
    def __init__(self, *children: Union[Component, DSLExpr, str], **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.tag_name = "__fragment__"

    def render(self) -> str:
        from .base import Component as BaseComp
        html = ""
        for c in self.children:
            if isinstance(c, BaseComp):
                html += c.render()
            elif isinstance(c, DSLExpr):
                from ..core.context import RenderContext
                if RenderContext.template_mode:
                    html += f"${{{c.to_js()}}}"
                else:
                    cuid = f"el_{uuid.uuid4().hex[:8]}"
                    html += f'<span id="{cuid}"></span>'
                    RenderContext.effects.append(
                        f'document.getElementById("{cuid}").innerText = {c.to_js()};'
                    )
            else:
                html += str(c)
        return html


class Badge(Component):
    """
    A styled inline badge / pill (renders as ``<span>``).

    A convenient high-level component for status indicators, tags, labels, etc.
    Applies sensible default classes on top of any ``class_name`` you provide.

    Args:
        *children: Badge text or icon.
        variant: Preset color variant — ``"default"`` | ``"success"`` | ``"warning"``
            | ``"danger"`` | ``"info"``. Ignored when ``class_name`` is supplied.
        class_name: Override with custom Tailwind classes.

    Example::

        Badge("New", variant="success")
        Badge("Deprecated", variant="warning")
        Badge(status(), class_name="bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full text-xs")
    """
    _VARIANTS = {
        "default": "bg-gray-100 text-gray-700",
        "success": "bg-green-100 text-green-700",
        "warning": "bg-yellow-100 text-yellow-800",
        "danger":  "bg-red-100 text-red-700",
        "info":    "bg-blue-100 text-blue-700",
    }

    def __init__(
        self,
        *children: Union[Component, DSLExpr, str],
        variant: str = "default",
        class_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        base = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
        if class_name is None:
            color = self._VARIANTS.get(variant, self._VARIANTS["default"])
            class_name = f"{base} {color}"
        super().__init__(*children, class_name=class_name, **kwargs)
        self.tag_name = "span"


class Avatar(Component):
    """
    A circular avatar image or initials fallback (renders as ``<div>``).

    Args:
        src: Image path (from ``public/`` dir) or external URL.
        alt: Alt text / initials for the fallback.
        size: Tailwind size class, e.g. ``"w-10 h-10"`` (default ``"w-8 h-8"``).
        class_name: Extra CSS classes.

    Example::

        Avatar(src="/avatars/alice.jpg", alt="Alice", size="w-12 h-12")
        Avatar(alt="JD")   # initials fallback
    """
    def __init__(
        self,
        *,
        src: Optional[str] = None,
        alt: str = "",
        size: str = "w-8 h-8",
        class_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        wrapper_cls = f"{size} rounded-full overflow-hidden bg-gray-200 flex items-center justify-center text-gray-600 font-semibold text-sm"
        if class_name:
            wrapper_cls += f" {class_name}"

        if src:
            content: Component = Img(src=src, alt=alt, class_name="w-full h-full object-cover")
        else:
            initials = "".join(w[0].upper() for w in alt.split() if w)[:2] or "?"
            content = Span(initials)

        super().__init__(content, class_name=wrapper_cls, **kwargs)
        self.tag_name = "div"


class Divider(Component):
    """
    A styled horizontal divider (renders as ``<hr />``).

    Args:
        label: Optional centered label text.
        class_name: Custom Tailwind classes.

    Example::

        Divider()
        Divider(label="OR", class_name="my-6 border-gray-300")
    """
    def __init__(
        self,
        *,
        label: Optional[str] = None,
        class_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self._label = label
        self._custom_cls = class_name
        super().__init__(**kwargs)
        self.tag_name = "div"

    def render(self) -> str:
        if self._label:
            cls = self._custom_cls or "my-6"
            return (
                f'<div class="relative flex items-center {cls}">'
                f'<div class="flex-grow border-t border-gray-300"></div>'
                f'<span class="mx-4 text-sm text-gray-400">{self._label}</span>'
                f'<div class="flex-grow border-t border-gray-300"></div>'
                f'</div>'
            )
        cls = self._custom_cls or "my-6 border-gray-200"
        return f'<hr class="{cls}" />'


class Tooltip(Component):
    """
    Wraps children in a ``<div>`` with a hover tooltip (CSS-only, no JS).

    Args:
        *children: The element that triggers the tooltip on hover.
        text: The tooltip text to display.
        position: ``"top"`` (default), ``"bottom"``, ``"left"``, ``"right"``.
        class_name: Extra classes on the outer wrapper.

    Example::

        Tooltip(
            Button("Save", class_name="px-4 py-2 bg-blue-600 text-white rounded"),
            text="Save your changes (Ctrl+S)",
        )
    """
    _POS = {
        "top":    "bottom-full left-1/2 -translate-x-1/2 mb-2",
        "bottom": "top-full left-1/2 -translate-x-1/2 mt-2",
        "left":   "right-full top-1/2 -translate-y-1/2 mr-2",
        "right":  "left-full top-1/2 -translate-y-1/2 ml-2",
    }

    def __init__(
        self,
        *children: Union[Component, DSLExpr, str],
        text: str,
        position: str = "top",
        class_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self._tip_text = text
        self._tip_pos = position
        self._custom_cls = class_name
        super().__init__(*children, class_name=class_name, **kwargs)
        self.tag_name = "div"

    def render(self) -> str:
        from .base import Component as BaseComp
        inner_html = ""
        for c in self.children:
            inner_html += c.render() if isinstance(c, BaseComp) else str(c)

        pos_cls = self._POS.get(self._tip_pos, self._POS["top"])
        wrapper_cls = "relative inline-block group"
        if self._custom_cls:
            wrapper_cls += f" {self._custom_cls}"

        return (
            f'<div class="{wrapper_cls}">'
            f'{inner_html}'
            f'<div class="pointer-events-none absolute {pos_cls} z-50 hidden group-hover:block '
            f'bg-gray-900 text-white text-xs rounded py-1 px-2 whitespace-nowrap shadow-lg">'
            f'{self._tip_text}'
            f'</div>'
            f'</div>'
        )
