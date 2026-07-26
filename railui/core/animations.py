"""
Web Animations API Engine for RailUI.

Zero-runtime animation primitives that compile directly to native
`Web Animations API <https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API>`_
(``element.animate()``) calls. No external library needed — the keyframes
and options you express in Python are serialised directly to JSON and
embedded into the generated JavaScript bundle.

All functions return :class:`AnimateOp` instances — a special
:class:`~railui.core.ast.DSLExpr` subclass — so they can be used
anywhere a DSLExpr is accepted:

- ``on_click``
- ``on_mount``
- :func:`~railui.core.ast.runSequence`
- :func:`~railui.core.ast.on_mount`

Quick start::

    Button(
        "Appear!",
        id="my-btn",
        on_click=scale_in("my-btn"),
    )

    # Or chain animations
    Button(
        "Go!",
        id="hero",
        on_click=runSequence(
            fade_out("hero", duration=200),
            slide_in_up("hero", duration=400, delay=210),
        ),
    )
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Union

from .ast import DSLExpr, RawJS


# ---------------------------------------------------------------------------
# Core WAAPI DSL node
# ---------------------------------------------------------------------------

class AnimateOp(DSLExpr):
    """
    A :class:`~railui.core.ast.DSLExpr` that compiles to a native
    `Web Animations API <https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API>`_
    call: ``element.animate(keyframes, options)``.

    You typically don't construct this directly — use the pre-built helpers
    (:func:`fade_in`, :func:`slide_in_up`, etc.) or the generic :func:`animate`
    factory instead.

    Args:
        target_id: The HTML ``id`` of the element to animate.  Must match the
            ``id`` prop on the component (set it explicitly via ``id="my-id"``).
        keyframes: A list of CSS keyframe dictionaries following the WAAPI
            ``KeyframeEffect`` spec. Property names use camelCase
            (e.g. ``"backgroundColor"``, ``"transform"``).
            The list must contain **at least two** keyframes.
        duration: Total animation duration in milliseconds. Defaults to ``300``.
        easing: CSS easing function — any valid
            ``<easing-function>`` value such as ``"ease"``, ``"ease-in-out"``,
            ``"linear"``, or ``"cubic-bezier(0.4, 0, 0.2, 1)"``.
            Defaults to ``"ease"``.
        fill: WAAPI fill mode that controls the element's state after the
            animation completes. One of ``"none"``, ``"forwards"`` (default),
            ``"backwards"``, or ``"both"``.
        delay: Delay before the animation starts, in milliseconds.
            Defaults to ``0``.
        iterations: Number of times to repeat.  Use ``"Infinity"`` (as a
            string) for a continuous loop.  Defaults to ``1``.
        direction: Playback direction.  One of ``"normal"`` (default),
            ``"reverse"``, ``"alternate"``, or ``"alternate-reverse"``.

    Example::

        # Custom keyframe animation
        AnimateOp(
            "card",
            [
                {"transform": "rotate(-5deg) scale(0.95)", "opacity": 0},
                {"transform": "rotate(0deg) scale(1)", "opacity": 1},
            ],
            duration=500,
            easing="cubic-bezier(0.34, 1.56, 0.64, 1)",
            fill="forwards",
        )
    """

    def __init__(
        self,
        target_id: str,
        keyframes: List[Dict[str, Any]],
        *,
        duration: int = 300,
        easing: str = "ease",
        fill: str = "forwards",
        delay: int = 0,
        iterations: Union[int, str] = 1,
        direction: str = "normal",
    ) -> None:
        self.target_id = target_id
        self.keyframes = keyframes
        self.options: Dict[str, Any] = {
            "duration": duration,
            "easing": easing,
            "fill": fill,
            "delay": delay,
            "iterations": iterations,
            "direction": direction,
        }

    def to_js(self) -> str:
        """Compile the animation to a JavaScript ``element.animate(...)`` call."""
        kf_js = json.dumps(self.keyframes)
        opts_js = json.dumps(self.options)
        return f'document.getElementById("{self.target_id}").animate({kf_js}, {opts_js})'

    def then(self, callback_js: str) -> "RawJS":
        """
        Chain a callback to run when the animation finishes.

        Args:
            callback_js: Raw JavaScript to execute when the animation's
                ``finished`` promise resolves, e.g. ``"el.remove()"``
                or ``"navigate('/next')"``

        Returns:
            :class:`~railui.core.ast.RawJS` — a DSL node representing the
            chained promise expression.

        Example::

            # Remove an element after fading it out
            Button(
                "Delete",
                id="item-card",
                on_click=fade_out("item-card", duration=200).then("document.getElementById('item-card').remove()"),
            )
        """
        return RawJS(f"{self.to_js()}.finished.then(() => {{ {callback_js} }})")


# ---------------------------------------------------------------------------
# Generic factory
# ---------------------------------------------------------------------------

def animate(
    target_id: str,
    keyframes: List[Dict[str, Any]],
    *,
    duration: int = 300,
    easing: str = "ease",
    fill: str = "forwards",
    delay: int = 0,
    iterations: Union[int, str] = 1,
    direction: str = "normal",
) -> AnimateOp:
    """
    Create a fully-customisable Web Animations API animation.

    This is the generic escape hatch when the pre-built helpers don't cover
    your use-case. Supply your own keyframes as plain Python dicts.

    Args:
        target_id: HTML ``id`` of the target element.
        keyframes: List of WAAPI keyframe dicts (CSS property names in camelCase).
            Must have at least two entries.
        duration: Animation duration in milliseconds. Defaults to ``300``.
        easing: CSS easing function (e.g. ``"ease-out"``,
            ``"cubic-bezier(0.4, 0, 0.2, 1)"``). Defaults to ``"ease"``.
        fill: Post-animation fill mode (``"none"``, ``"forwards"``,
            ``"backwards"``, ``"both"``). Defaults to ``"forwards"``.
        delay: Delay before start in milliseconds. Defaults to ``0``.
        iterations: Repeat count, or the string ``"Infinity"`` for a loop.
            Defaults to ``1``.
        direction: Playback direction — ``"normal"``, ``"reverse"``,
            ``"alternate"``, or ``"alternate-reverse"``. Defaults to
            ``"normal"``.

    Returns:
        :class:`AnimateOp` — a DSLExpr node ready to be passed to any
        event handler or lifecycle hook.

    Example::

        animate(
            "hero",
            [
                {"opacity": 0, "transform": "scale(0.9) translateY(20px)"},
                {"opacity": 1, "transform": "scale(1)  translateY(0px)"},
            ],
            duration=600,
            easing="cubic-bezier(0.16, 1, 0.3, 1)",
            fill="forwards",
            delay=100,
        )
    """
    return AnimateOp(
        target_id, keyframes,
        duration=duration, easing=easing, fill=fill,
        delay=delay, iterations=iterations, direction=direction,
    )


# ---------------------------------------------------------------------------
# CSS Transitions helper
# ---------------------------------------------------------------------------

def transition(
    target_id: str,
    to: Dict[str, str],
    *,
    duration: int = 300,
    easing: str = "ease",
    fill: str = "forwards",
    delay: int = 0,
) -> AnimateOp:
    """
    Animate an element from its **current computed style** to new CSS values.

    Unlike :func:`animate` (which requires explicit ``from`` keyframes),
    ``transition`` only needs the *destination* state. The browser reads
    the element's live computed styles as the implicit starting frame,
    making it ideal for "toggle" effects where the starting state isn't
    known at compile time.

    This function compiles to a two-keyframe WAAPI call:
    ``element.animate([{}, toKeyframe], options)`` where the first empty
    keyframe causes the browser to snapshot the element's current style.

    Args:
        target_id: HTML ``id`` of the target element.
        to: A dict of CSS properties (camelCase) and their target values.
            For example ``{"opacity": "0", "transform": "translateX(100px)"}``.
        duration: Duration in milliseconds. Defaults to ``300``.
        easing: CSS easing. Defaults to ``"ease"``.
        fill: Post-animation fill mode. Defaults to ``"forwards"``.
        delay: Delay in milliseconds. Defaults to ``0``.

    Returns:
        :class:`AnimateOp` ready for use in any event handler.

    Example::

        sidebar, setSidebar = createSignal(False)

        Button(
            "Toggle Sidebar",
            id="sidebar-panel",
            on_click=runSequence(
                setSidebar(True),
                transition("sidebar-panel", {"transform": "translateX(0)", "opacity": "1"}),
            ),
        )

        # Colour transition on hover
        Container(
            id="card",
            on_mouseenter=transition("card", {"backgroundColor": "#f0f9ff", "boxShadow": "0 8px 32px rgba(0,0,0,.12)"}),
            on_mouseleave=transition("card", {"backgroundColor": "#ffffff", "boxShadow": "0 1px 3px rgba(0,0,0,.1)"}),
        )
    """
    return AnimateOp(
        target_id,
        [
            {},           # empty first keyframe → browser snapshots current style
            dict(to),     # destination state
        ],
        duration=duration,
        easing=easing,
        fill=fill,
        delay=delay,
    )


# ---------------------------------------------------------------------------
# Pre-built animation presets
# ---------------------------------------------------------------------------

def fade_in(
    target_id: str,
    *,
    duration: int = 300,
    delay: int = 0,
    easing: str = "ease-out",
) -> AnimateOp:
    """
    Fade an element in from fully transparent to fully opaque.

    Args:
        target_id: HTML ``id`` of the element to animate.
        duration: Duration in milliseconds. Defaults to ``300``.
        delay: Start delay in milliseconds. Defaults to ``0``.
        easing: CSS easing. Defaults to ``"ease-out"``.

    Returns:
        :class:`AnimateOp` — use in ``on_click``, ``on_mount``, etc.

    Example::

        Container(id="alert-box", on_mount=fade_in("alert-box"))
    """
    return AnimateOp(
        target_id,
        [{"opacity": 0}, {"opacity": 1}],
        duration=duration, easing=easing, fill="forwards", delay=delay,
    )


def fade_out(
    target_id: str,
    *,
    duration: int = 300,
    delay: int = 0,
    easing: str = "ease-in",
) -> AnimateOp:
    """
    Fade an element out from fully opaque to fully transparent.

    Args:
        target_id: HTML ``id`` of the element to animate.
        duration: Duration in milliseconds. Defaults to ``300``.
        delay: Start delay in milliseconds. Defaults to ``0``.
        easing: CSS easing. Defaults to ``"ease-in"``.

    Returns:
        :class:`AnimateOp`.

    Example::

        Button("Close", id="modal", on_click=fade_out("modal", duration=200))
    """
    return AnimateOp(
        target_id,
        [{"opacity": 1}, {"opacity": 0}],
        duration=duration, easing=easing, fill="forwards", delay=delay,
    )


def slide_in_left(
    target_id: str,
    *,
    distance: str = "40px",
    duration: int = 350,
    delay: int = 0,
    easing: str = "ease-out",
) -> AnimateOp:
    """
    Slide an element in from the left while fading in.

    Args:
        target_id: HTML ``id`` of the element.
        distance: How far off-screen to start, e.g. ``"60px"`` or ``"100%"``.
            Defaults to ``"40px"``.
        duration: Duration in milliseconds. Defaults to ``350``.
        delay: Start delay in milliseconds. Defaults to ``0``.
        easing: CSS easing. Defaults to ``"ease-out"``.

    Returns:
        :class:`AnimateOp`.

    Example::

        Nav(id="drawer", on_mount=slide_in_left("drawer", distance="300px"))
    """
    return AnimateOp(
        target_id,
        [
            {"transform": f"translateX(-{distance})", "opacity": 0},
            {"transform": "translateX(0)", "opacity": 1},
        ],
        duration=duration, easing=easing, fill="forwards", delay=delay,
    )


def slide_in_right(
    target_id: str,
    *,
    distance: str = "40px",
    duration: int = 350,
    delay: int = 0,
    easing: str = "ease-out",
) -> AnimateOp:
    """
    Slide an element in from the right while fading in.

    Args:
        target_id: HTML ``id`` of the element.
        distance: How far off-screen to start. Defaults to ``"40px"``.
        duration: Duration in milliseconds. Defaults to ``350``.
        delay: Start delay in milliseconds. Defaults to ``0``.
        easing: CSS easing. Defaults to ``"ease-out"``.

    Returns:
        :class:`AnimateOp`.
    """
    return AnimateOp(
        target_id,
        [
            {"transform": f"translateX({distance})", "opacity": 0},
            {"transform": "translateX(0)", "opacity": 1},
        ],
        duration=duration, easing=easing, fill="forwards", delay=delay,
    )


def slide_in_up(
    target_id: str,
    *,
    distance: str = "30px",
    duration: int = 350,
    delay: int = 0,
    easing: str = "ease-out",
) -> AnimateOp:
    """
    Slide an element in from below while fading in.

    Args:
        target_id: HTML ``id`` of the element.
        distance: How far below to start. Defaults to ``"30px"``.
        duration: Duration in milliseconds. Defaults to ``350``.
        delay: Start delay in milliseconds. Defaults to ``0``.
        easing: CSS easing. Defaults to ``"ease-out"``.

    Returns:
        :class:`AnimateOp`.

    Example::

        # Staggered list entrance
        Each(
            items=posts,
            render_fn=lambda post, i: Container(
                Text(post.title),
                id=f"post-{i}",
                on_mount=slide_in_up(f"post-{i}", delay=i * 80),
            ),
        )
    """
    return AnimateOp(
        target_id,
        [
            {"transform": f"translateY({distance})", "opacity": 0},
            {"transform": "translateY(0)", "opacity": 1},
        ],
        duration=duration, easing=easing, fill="forwards", delay=delay,
    )


def slide_out_down(
    target_id: str,
    *,
    distance: str = "30px",
    duration: int = 300,
    delay: int = 0,
    easing: str = "ease-in",
) -> AnimateOp:
    """
    Slide an element out downwards while fading out.

    Args:
        target_id: HTML ``id`` of the element.
        distance: How far below to end. Defaults to ``"30px"``.
        duration: Duration in milliseconds. Defaults to ``300``.
        delay: Start delay in milliseconds. Defaults to ``0``.
        easing: CSS easing. Defaults to ``"ease-in"``.

    Returns:
        :class:`AnimateOp`.
    """
    return AnimateOp(
        target_id,
        [
            {"transform": "translateY(0)", "opacity": 1},
            {"transform": f"translateY({distance})", "opacity": 0},
        ],
        duration=duration, easing=easing, fill="forwards", delay=delay,
    )


def spin(
    target_id: str,
    *,
    duration: int = 800,
    iterations: Union[int, str] = "Infinity",
) -> AnimateOp:
    """
    Spin an element continuously (or a set number of times).

    Useful for loading spinners and loaders.

    Args:
        target_id: HTML ``id`` of the element.
        duration: One full rotation duration in milliseconds. Defaults to ``800``.
        iterations: Number of rotations, or ``"Infinity"`` for continuous.
            Defaults to ``"Infinity"``.

    Returns:
        :class:`AnimateOp`.

    Example::

        Img(src="/spinner.svg", alt="Loading", id="loader", on_mount=spin("loader"))
    """
    return AnimateOp(
        target_id,
        [{"transform": "rotate(0deg)"}, {"transform": "rotate(360deg)"}],
        duration=duration, easing="linear", fill="none", iterations=iterations,
    )


def bounce(
    target_id: str,
    *,
    height: str = "12px",
    duration: int = 600,
    iterations: Union[int, str] = "Infinity",
) -> AnimateOp:
    """
    Bounce an element up and down rhythmically.

    Args:
        target_id: HTML ``id`` of the element.
        height: Bounce height (upward). Defaults to ``"12px"``.
        duration: One full bounce cycle in milliseconds. Defaults to ``600``.
        iterations: Number of bounces, or ``"Infinity"`` for a loop.
            Defaults to ``"Infinity"``.

    Returns:
        :class:`AnimateOp`.
    """
    return AnimateOp(
        target_id,
        [
            {"transform": "translateY(0)"},
            {"transform": f"translateY(-{height})"},
            {"transform": "translateY(0)"},
        ],
        duration=duration, easing="ease-in-out", fill="none", iterations=iterations,
    )


def pulse(
    target_id: str,
    *,
    min_opacity: float = 0.4,
    duration: int = 800,
    iterations: Union[int, str] = "Infinity",
) -> AnimateOp:
    """
    Pulse an element's opacity for loading / attention effects.

    Args:
        target_id: HTML ``id`` of the element.
        min_opacity: Minimum opacity during the pulse. Defaults to ``0.4``.
        duration: One full pulse cycle in milliseconds. Defaults to ``800``.
        iterations: Number of pulses, or ``"Infinity"`` for continuous.
            Defaults to ``"Infinity"``.

    Returns:
        :class:`AnimateOp`.

    Example::

        # Skeleton / loading placeholder
        Container(id="skeleton", class_name="h-4 bg-gray-200 rounded", on_mount=pulse("skeleton"))
    """
    return AnimateOp(
        target_id,
        [{"opacity": 1}, {"opacity": min_opacity}, {"opacity": 1}],
        duration=duration, easing="ease-in-out", fill="none", iterations=iterations,
    )


def shake(
    target_id: str,
    *,
    amplitude: str = "8px",
    duration: int = 400,
) -> AnimateOp:
    """
    Shake an element horizontally — ideal for form validation errors.

    Args:
        target_id: HTML ``id`` of the element.
        amplitude: Maximum horizontal displacement. Defaults to ``"8px"``.
        duration: Total shake duration in milliseconds. Defaults to ``400``.

    Returns:
        :class:`AnimateOp`.

    Example::

        Input(
            id="email-input",
            type="email",
            on_blur=runSequence(
                shake("email-input"),
            ),
        )
    """
    a = amplitude
    # Quick amplitude for inner frames
    try:
        val = float(amplitude.rstrip("px"))
        inner = f"{val * 0.75:.0f}px"
    except ValueError:
        inner = amplitude

    return AnimateOp(
        target_id,
        [
            {"transform": "translateX(0)"},
            {"transform": f"translateX(-{a})"},
            {"transform": f"translateX({a})"},
            {"transform": f"translateX(-{inner})"},
            {"transform": f"translateX({inner})"},
            {"transform": "translateX(0)"},
        ],
        duration=duration, easing="ease-in-out", fill="forwards",
    )


def scale_in(
    target_id: str,
    *,
    from_scale: float = 0.8,
    duration: int = 250,
    delay: int = 0,
    easing: str = "cubic-bezier(0.34, 1.56, 0.64, 1)",
) -> AnimateOp:
    """
    Scale an element in from a smaller size while fading it in.

    Uses a slight spring easing by default for a natural, polished feel.

    Args:
        target_id: HTML ``id`` of the element.
        from_scale: Starting scale factor (0–1). Defaults to ``0.8``.
        duration: Duration in milliseconds. Defaults to ``250``.
        delay: Start delay in milliseconds. Defaults to ``0``.
        easing: CSS easing. Defaults to a subtle spring
            ``"cubic-bezier(0.34, 1.56, 0.64, 1)"``.

    Returns:
        :class:`AnimateOp`.

    Example::

        # Modal entrance
        Dialog(
            ...,
            id="modal",
            on_mount=scale_in("modal"),
        )
    """
    return AnimateOp(
        target_id,
        [
            {"transform": f"scale({from_scale})", "opacity": 0},
            {"transform": "scale(1)", "opacity": 1},
        ],
        duration=duration, easing=easing, fill="forwards", delay=delay,
    )


def scale_out(
    target_id: str,
    *,
    to_scale: float = 0.8,
    duration: int = 200,
    easing: str = "ease-in",
) -> AnimateOp:
    """
    Scale an element out to a smaller size while fading it out.

    Args:
        target_id: HTML ``id`` of the element.
        to_scale: Ending scale factor (0–1). Defaults to ``0.8``.
        duration: Duration in milliseconds. Defaults to ``200``.
        easing: CSS easing. Defaults to ``"ease-in"``.

    Returns:
        :class:`AnimateOp`.

    Example::

        Button("Dismiss", id="toast", on_click=scale_out("toast", duration=150))
    """
    return AnimateOp(
        target_id,
        [
            {"transform": "scale(1)", "opacity": 1},
            {"transform": f"scale({to_scale})", "opacity": 0},
        ],
        duration=duration, easing=easing, fill="forwards",
    )


def flip_in(
    target_id: str,
    *,
    axis: str = "Y",
    duration: int = 500,
    delay: int = 0,
) -> AnimateOp:
    """
    Flip an element into view along the X or Y axis.

    Args:
        target_id: HTML ``id`` of the element.
        axis: Rotation axis — ``"X"`` or ``"Y"``. Defaults to ``"Y"``.
        duration: Duration in milliseconds. Defaults to ``500``.
        delay: Start delay in milliseconds. Defaults to ``0``.

    Returns:
        :class:`AnimateOp`.

    Example::

        Container(id="card", on_mount=flip_in("card", axis="Y"))
    """
    start = f"rotate{axis}(90deg)" if axis.upper() == "X" else f"rotate{axis}(-90deg)"
    return AnimateOp(
        target_id,
        [
            {"transform": f"{start} scale(0.9)", "opacity": 0},
            {"transform": "rotateX(0) rotateY(0) scale(1)", "opacity": 1},
        ],
        duration=duration, easing="ease-out", fill="forwards", delay=delay,
    )


def highlight(
    target_id: str,
    *,
    color: str = "#fef08a",
    duration: int = 1200,
) -> AnimateOp:
    """
    Flash a background highlight on an element to draw attention to a change.

    Args:
        target_id: HTML ``id`` of the element.
        color: Highlight colour in any CSS format. Defaults to a soft yellow
            ``"#fef08a"``.
        duration: Total duration in milliseconds. Defaults to ``1200``.

    Returns:
        :class:`AnimateOp`.

    Example::

        # Flash a row when a value updates
        Tr(
            ...,
            id="row-1",
            on_mount=highlight("row-1"),
        )
    """
    return AnimateOp(
        target_id,
        [
            {"backgroundColor": color},
            {"backgroundColor": color, "offset": 0.3},
            {"backgroundColor": "transparent"},
        ],
        duration=duration, easing="ease-out", fill="forwards",
    )
