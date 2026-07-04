from typing import Dict, Any, Optional

def build_router_js(compiled_routes: Dict[str, Dict[str, Any]], not_found_data: Optional[Dict[str, Any]], trailing_slash: bool) -> str:
    """
    Generates the Client-Side SPA Router JavaScript code.
    This JS intercepts link clicks, manages the browser History API, and swaps
    DOM components and reactive effects dynamically without a full page reload.
    """
    js_code = [
        "const $routes = {};",
        "const $routeInit = {};",
        "const $routeDestroy = {};",
        "const $routeEffects = {};"
    ]
    
    for path, data in compiled_routes.items():
        safe_html = data["html"].replace("\\", "\\\\").replace("`", "\\`")
        
        js_code.append(f"$routes['{path}'] = `{safe_html}`;")
        
        init_scripts = "\n".join(data["init"])
        destroy_scripts = "\n".join(data["destroy"])
        effects_scripts = "\n".join(data["effects"])
        
        js_code.append(f"$routeInit['{path}'] = () => {{ {init_scripts} }};")
        js_code.append(f"$routeDestroy['{path}'] = () => {{ {destroy_scripts} }};")
        if effects_scripts.strip():
            js_code.append(f"$routeEffects['{path}'] = () => {{ $effects.push(() => {{ {effects_scripts} }}); }};")
        else:
            js_code.append(f"$routeEffects['{path}'] = () => {{ }};")
        
    if not_found_data:
        safe_html = not_found_data["html"].replace("\\", "\\\\").replace("`", "\\`")
        js_code.append(f"const $notFoundHtml = `{safe_html}`;")
        js_code.append(f"const $notFoundInit = () => {{ {''.join(not_found_data['init'])} }};")
        js_code.append(f"const $notFoundDestroy = () => {{ {''.join(not_found_data['destroy'])} }};")
        effects_scripts = ''.join(not_found_data['effects'])
        if effects_scripts.strip():
            js_code.append(f"const $notFoundEffects = () => {{ $effects.push(() => {{ {effects_scripts} }}); }};")
        else:
            js_code.append(f"const $notFoundEffects = () => {{ }};")
    else:
        js_code.append("const $notFoundHtml = `<div style='text-align:center;padding:50px;'><h1>404 Not Found</h1><p>The page you are looking for does not exist.</p></div>`;")
        js_code.append("const $notFoundInit = () => {};")
        js_code.append("const $notFoundDestroy = () => {};")
        js_code.append("const $notFoundEffects = () => {};")

    # The History API Engine
    slash_logic = ""
    if not trailing_slash:
        slash_logic = "if (path.length > 1 && path.endsWith('/')) path = path.slice(0, -1);"
        
    js_code.append(f"""
let $currentPath = null;

function $navigate(path, replace = false) {{
    if (path === $currentPath) return;
    
    if (replace) {{
        window.history.replaceState({{}}, '', path);
    }} else {{
        window.history.pushState({{}}, '', path);
    }}
    $renderRoute();
}}

function $renderRoute() {{
    // Run teardown of current route BEFORE replacing DOM
    if ($currentPath) {{
        // Strip query params to find the correct route script
        let oldBase = $currentPath.split('?')[0].split('#')[0];
        let destroyFn = $routeDestroy[oldBase] || $notFoundDestroy;
        destroyFn();
    }}

    let path = window.location.pathname;
    {slash_logic}
    $currentPath = path + window.location.search + window.location.hash;
    
    let html = $routes[path];
    let initFn = $routeInit[path];
    let effectsFn = $routeEffects[path];
    
    if (!html) {{
        // Dynamic route matching could go here
        html = $notFoundHtml;
        initFn = $notFoundInit;
        effectsFn = $notFoundEffects;
    }}
    
    const root = document.getElementById('railui-root');
    root.innerHTML = html;
    
    // Scoped effects cleanup (mutating the array in-place to avoid const assignment errors)
    if (typeof $effects !== 'undefined') {{
        const globals = $effects.filter(e => e._isGlobal);
        $effects.length = 0;
        $effects.push(...globals);
    }} else {{
        window.$effects = [];
    }}
    
    if (initFn) initFn();
    
    if (effectsFn) {{
        // Wrap effects pushed during route load to mark them as route-specific
        const originalPush = $effects.push;
        $effects.push = function(fn) {{
            fn._isRoute = true;
            originalPush.call(this, fn);
        }};
        
        effectsFn();
        
        $effects.push = originalPush;
    }}
    
    // Trigger signal re-eval for the new route
    $effects.forEach(effect => {{
        if (effect._isRoute || effect._isGlobal) {{
            effect();
        }}
    }});
}}

// Intercept local anchor clicks for SPA navigation
document.addEventListener('click', e => {{
    const link = e.target.closest('a');
    if (link && link.href && link.href.startsWith(window.location.origin)) {{
        if (link.target !== '_blank' && !link.hasAttribute('download')) {{
            e.preventDefault();
            $navigate(link.pathname + link.search + link.hash);
        }}
    }}
}});

window.addEventListener('popstate', () => {{
    $renderRoute();
}});

// Mark existing global effects so they persist
if (typeof $effects !== 'undefined') {{
    $effects.forEach(e => e._isGlobal = true);
}}

// Boot the router
document.addEventListener('DOMContentLoaded', () => {{
    $renderRoute();
}});
    """)
    
    return "\n".join(js_code)
