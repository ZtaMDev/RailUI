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
    
    Two buckets exist intentionally:
    - ``effects``/``init_scripts``: populated during component ``.render()`` — cleared on each compile pass.
    - ``user_effects``: populated by explicit ``createEffect()`` calls in user code before ``compile_app()`` — 
      never cleared so they survive the render reset and always make it into the final bundle.
    """
    effects: List[str] = []
    init_scripts: List[str] = []
    user_effects: List[str] = []
    
    @classmethod
    def reset(cls) -> None:
        """Clear per-render state. Does NOT clear user_effects — those are declared once at the module level."""
        cls.effects = []
        cls.init_scripts = []
