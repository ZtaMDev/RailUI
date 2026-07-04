"""
Context states for the compilation engine.
"""

from typing import List, Dict, Any

class SignalContext:
    """Context holding the initialized signals during a render pass."""
    signals: List[Dict[str, Any]] = []

class RenderContext:
    """
    Context holding all JavaScript side effects generated during compilation.

    Three lifecycle buckets exist intentionally:

    - ``effects`` / ``init_scripts``: populated during component ``.render()`` —
      cleared on each compile pass.
    - ``user_effects``: populated by explicit ``createEffect()`` calls — never
      cleared so they survive the render reset.
    - ``user_init_scripts``: populated by ``useFetch`` and similar one-shot hooks
      that must run *once* at page load, not on every reactive update.
    """
    effects: List[str] = []
    init_scripts: List[str] = []
    destroy_scripts: List[str] = []  # Per-route teardown/cleanup scripts
    user_effects: List[str] = []
    user_init_scripts: List[str] = []
    head_styles: List[str] = []   # Per-route <link> stylesheet URLs
    head_scripts: List[str] = []  # Per-route <script src> URLs
    template_mode: bool = False  # When True, DSLExpr children embed inline as ${...}

    @classmethod
    def reset(cls) -> None:
        """Clear per-render state.  Does NOT clear user_effects or user_init_scripts."""
        cls.effects = []
        cls.init_scripts = []
        cls.destroy_scripts = []
        cls.head_styles = []
        cls.head_scripts = []
        cls.template_mode = False
