// RailUI Each Helper
// Renders a list of items reactively into a container element.
// The render_fn receives (item, index) and returns an HTML string.
function $renderEach(containerId, items, renderFn) {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = items.map((item, i) => renderFn(item, i)).join('');
}

// RailUI Show Helper
// Toggles the display of a container element based on a condition.
function $show(elementId, condition) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.style.display = condition ? '' : 'none';
}
