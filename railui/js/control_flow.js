// RailUI Each Helper
// Renders a list of items reactively into a container element.
// The render_fn receives (item, index) and returns an HTML string.
function $renderEach(containerId, items, renderFn, callbacks = {}) {
    const el = document.getElementById(containerId);
    if (!el) return;
    
    items = items || [];
    
    // Memoization to prevent unnecessary renders from global reactivity triggers
    const itemsJson = JSON.stringify(items);
    if (el.getAttribute('data-railui-items-hash') === itemsJson) {
        return;
    }
    el.setAttribute('data-railui-items-hash', itemsJson);
    
    // Check if this is the first render
    const isFirstRender = !el.hasAttribute('data-railui-mounted');
    
    // Trigger unmount if items is empty and it was previously mounted
    if (!isFirstRender && items.length === 0 && callbacks.onUnmount) {
        callbacks.onUnmount();
    }
    
    el.innerHTML = items.map((item, i) => renderFn(item, i)).join('');
    
    if (isFirstRender) {
        el.setAttribute('data-railui-mounted', 'true');
        if (callbacks.onMount && items.length > 0) callbacks.onMount();
    } else {
        if (callbacks.onUpdate) callbacks.onUpdate();
    }
}

// RailUI Show Helper
// Toggles the display of a container element based on a condition.
function $show(elementId, condition, callbacks = {}) {
    const el = document.getElementById(elementId);
    if (!el) return;
    
    const wasVisible = el.style.display !== 'none';
    const isVisible = !!condition;
    
    // Initial mount check
    if (!el.hasAttribute('data-railui-mounted')) {
        el.setAttribute('data-railui-mounted', 'true');
        if (isVisible && callbacks.onMount) {
            callbacks.onMount();
        }
    }
    
    // Only update DOM and trigger lifecycle if state actually changed
    if (wasVisible !== isVisible) {
        el.style.display = isVisible ? '' : 'none';
        
        if (isVisible && callbacks.onUpdate) {
            callbacks.onUpdate();
        } else if (!isVisible && callbacks.onUnmount) {
            callbacks.onUnmount();
        }
    }
}
