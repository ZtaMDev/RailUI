"""
Web Animations API Engine for RailUI.

Zero-runtime animation primitives that compile directly to native
Web Animations API (element.animate()) calls. No library needed.

All functions return DSLExpr nodes for use in on_click, on_mount, etc.
"""

import json
from typing import Any, Dict, List, Optional, Union
from .ast import DSLExpr, RawJS


class AnimateOp(DSLExpr):
    """
    Compiles to element.animate(keyframes, options).

    Args:
        target_id (str): The HTML id of the element to animate.
        keyframes (list): List of dicts representing WAAPI keyframe objects.
        duration (int): Duration in milliseconds.
        easing (str): CSS easing function.
        fill (str): WAAPI fill mode ('none', 'forwards', 'backwards', 'both').
        delay (int): Delay before animation starts, in ms.
        iterations (Union[int, str]): Number of iterations or 'Infinity'.
        direction (str): 'normal', 'reverse', 'alternate', 'alternate-reverse'.
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
        self.options = {
            "duration": duration,
            "easing": easing,
            "fill": fill,
            "delay": delay,
            "iterations": iterations,
            "direction": direction,
        }

    def to_js(self) -> str:
        kf_js = json.dumps(self.keyframes)
        opts_js = json.dumps(self.options)
        return f'document.getElementById("{self.target_id}").animate({kf_js}, {opts_js})'


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
    """Custom keyframe animation using the Web Animations API."""
    return AnimateOp(
        target_id, keyframes,
        duration=duration, easing=easing, fill=fill,
        delay=delay, iterations=iterations, direction=direction
    )


# ---------------------------------------------------------------------------
# Pre-built animation helpers
# ---------------------------------------------------------------------------

def fade_in(target_id: str, *, duration: int = 300, delay: int = 0) -> AnimateOp:
    """Fade element in from transparent to opaque."""
    return AnimateOp(
        target_id,
        [{"opacity": 0}, {"opacity": 1}],
        duration=duration, easing="ease-out", fill="forwards", delay=delay
    )

def fade_out(target_id: str, *, duration: int = 300, delay: int = 0) -> AnimateOp:
    """Fade element out from opaque to transparent."""
    return AnimateOp(
        target_id,
        [{"opacity": 1}, {"opacity": 0}],
        duration=duration, easing="ease-in", fill="forwards", delay=delay
    )

def slide_in_left(target_id: str, *, distance: str = "40px", duration: int = 350, delay: int = 0) -> AnimateOp:
    """Slide element in from the left."""
    return AnimateOp(
        target_id,
        [{"transform": f"translateX(-{distance})", "opacity": 0},
         {"transform": "translateX(0)", "opacity": 1}],
        duration=duration, easing="ease-out", fill="forwards", delay=delay
    )

def slide_in_right(target_id: str, *, distance: str = "40px", duration: int = 350, delay: int = 0) -> AnimateOp:
    """Slide element in from the right."""
    return AnimateOp(
        target_id,
        [{"transform": f"translateX({distance})", "opacity": 0},
         {"transform": "translateX(0)", "opacity": 1}],
        duration=duration, easing="ease-out", fill="forwards", delay=delay
    )

def slide_in_up(target_id: str, *, distance: str = "30px", duration: int = 350, delay: int = 0) -> AnimateOp:
    """Slide element in from below."""
    return AnimateOp(
        target_id,
        [{"transform": f"translateY({distance})", "opacity": 0},
         {"transform": "translateY(0)", "opacity": 1}],
        duration=duration, easing="ease-out", fill="forwards", delay=delay
    )

def slide_out_down(target_id: str, *, distance: str = "30px", duration: int = 300, delay: int = 0) -> AnimateOp:
    """Slide element out downwards."""
    return AnimateOp(
        target_id,
        [{"transform": "translateY(0)", "opacity": 1},
         {"transform": f"translateY({distance})", "opacity": 0}],
        duration=duration, easing="ease-in", fill="forwards", delay=delay
    )

def spin(target_id: str, *, duration: int = 800, iterations: Union[int, str] = "Infinity") -> AnimateOp:
    """Spin element continuously."""
    return AnimateOp(
        target_id,
        [{"transform": "rotate(0deg)"}, {"transform": "rotate(360deg)"}],
        duration=duration, easing="linear", fill="none", iterations=iterations
    )

def bounce(target_id: str, *, height: str = "12px", duration: int = 600, iterations: Union[int, str] = "Infinity") -> AnimateOp:
    """Bounce element up and down."""
    return AnimateOp(
        target_id,
        [{"transform": "translateY(0)"}, {"transform": f"translateY(-{height})"}, {"transform": "translateY(0)"}],
        duration=duration, easing="ease-in-out", fill="none", iterations=iterations
    )

def pulse(target_id: str, *, duration: int = 800, iterations: Union[int, str] = "Infinity") -> AnimateOp:
    """Pulse opacity for loading/attention effects."""
    return AnimateOp(
        target_id,
        [{"opacity": 1}, {"opacity": 0.4}, {"opacity": 1}],
        duration=duration, easing="ease-in-out", fill="none", iterations=iterations
    )

def shake(target_id: str, *, duration: int = 400) -> AnimateOp:
    """Shake element horizontally (e.g. for form validation errors)."""
    return AnimateOp(
        target_id,
        [
            {"transform": "translateX(0)"},
            {"transform": "translateX(-8px)"},
            {"transform": "translateX(8px)"},
            {"transform": "translateX(-6px)"},
            {"transform": "translateX(6px)"},
            {"transform": "translateX(0)"},
        ],
        duration=duration, easing="ease-in-out", fill="forwards"
    )

def scale_in(target_id: str, *, from_scale: float = 0.8, duration: int = 250, delay: int = 0) -> AnimateOp:
    """Scale element in from a smaller size."""
    return AnimateOp(
        target_id,
        [{"transform": f"scale({from_scale})", "opacity": 0},
         {"transform": "scale(1)", "opacity": 1}],
        duration=duration, easing="ease-out", fill="forwards", delay=delay
    )

def scale_out(target_id: str, *, to_scale: float = 0.8, duration: int = 200) -> AnimateOp:
    """Scale element out to a smaller size."""
    return AnimateOp(
        target_id,
        [{"transform": "scale(1)", "opacity": 1},
         {"transform": f"scale({to_scale})", "opacity": 0}],
        duration=duration, easing="ease-in", fill="forwards"
    )
