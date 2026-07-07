
// RailUI Minimal Runtime
const $signals = {};
const $effects = [];

function createSignal(id, initial) {
    $signals[id] = initial;
    window[id] = () => $signals[id];
    window["set_" + id] = (val) => {
        $signals[id] = val;
        runEffects();
    };
}

function runEffects() {
    for (let effect of $effects) {
        effect();
    }
}

// -- DOM & Storage Utilities (Auth / JWT Prep) --

function $setCookie(name, value, days = 7) {
    let expires = "";
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/; SameSite=Lax";
}

function $getCookie(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for(let i=0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

function $removeCookie(name) {
    document.cookie = name + '=; Max-Age=-99999999;';
}

function $getJWT() {
    return $getCookie("jwt_token") || localStorage.getItem("jwt_token");
}

function $setJWT(token) {
    $setCookie("jwt_token", token, 7);
    localStorage.setItem("jwt_token", token);
}

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


// -- Global State Initialization --
createSignal('sig_1', "Alice Developer");
createSignal('sig_2', "Admin");
createSignal('sig_3', true);
createSignal('sig_4', "");
createSignal('sig_5', "");
createSignal('sig_6', 0);
createSignal('sig_7', {});
createSignal('sig_8', true);
(async () => {
  set_sig_8(true);
  try {
    const res = await fetch("https://jsonplaceholder.typicode.com/users/1");
    const data = await res.json();
    set_sig_7(data);
  } catch(e) {
    console.error('[useFetch] Error:', e);
  } finally {
    set_sig_8(false);
  }
})();
createSignal('sig_9', false);
createSignal('sig_10', [{"title": "Learn RailUI"}, {"title": "Build a SPA"}]);

// -- Global Effects --
$effects.push(() => {

});

// -- SPA Router --
const $routes = {};
const $routeInit = {};
const $routeDestroy = {};
const $routeEffects = {};
$routes['/actions_demo'] = `<main class="min-h-screen bg-gray-50 flex flex-col"><div class="w-full bg-white shadow-sm p-4 border-b border-gray-200 sticky top-0 z-50"><div class="flex flex-row justify-between items-center w-full max-w-5xl mx-auto"><span class="font-black text-2xl text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-500">RailUI</span><div class="flex flex-row items-center gap-6"><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/">Home</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/counter">Counter</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/dashboard">Dashboard</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/profile">Profile</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/actions_demo">Actions Demo</a><a class="text-gray-400 hover:text-red-500 font-medium transition" href="/nowhere">Invalid</a></div></div></div><div class="w-full max-w-5xl mx-auto p-8 flex-grow"><div><span class="text-4xl font-black text-gray-900 block mb-4">Server Actions Demo</span><span class="text-gray-500 mb-8 block">Call Python functions directly from your frontend components.</span><div class="flex items-center mb-6"><input id="el_b838fbcb" class="px-4 py-2 border rounded-l-lg w-64" type="text" value="<railui.core.ast.SignalRef object at 0x000001F79E40D160>" placeholder="Enter username..." /><button id="el_81d78b22" class="px-4 py-2 bg-blue-600 text-white font-bold rounded-r-lg hover:bg-blue-700" type="button">Save User (RPC)</button></div><div id="el_93065c4e" children="<railui.components.base.Text object at 0x000001F79E356990>"></div></div></div><div class="w-full p-4 border-t border-gray-200 mt-auto text-center bg-white"><span class="text-sm text-gray-500">© 2026 RailUI Framework. All rights reserved.</span></div></main>`;
$routeInit['/actions_demo'] = () => { document.title = "Server Actions | RailUI";
document.getElementById("el_b838fbcb").addEventListener("input", function(event) { set_sig_4(sig_4()?.value) });
document.getElementById("el_81d78b22").addEventListener("click", function(event) { fetch('/_railui_action/save_user', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify([sig_4()]) }).then(r => r.json()).then(res => { set_sig_5(res.message) }) }); };
$routeDestroy['/actions_demo'] = () => {  };
$routeEffects['/actions_demo'] = () => { $effects.push(() => { $show("el_93065c4e", (sig_5() !== ""), {}); }); };
$routes['/counter'] = `<main class="min-h-screen bg-gray-50 flex flex-col"><div class="w-full bg-white shadow-sm p-4 border-b border-gray-200 sticky top-0 z-50"><div class="flex flex-row justify-between items-center w-full max-w-5xl mx-auto"><span class="font-black text-2xl text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-500">RailUI</span><div class="flex flex-row items-center gap-6"><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/">Home</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/counter">Counter</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/dashboard">Dashboard</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/profile">Profile</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/actions_demo">Actions Demo</a><a class="text-gray-400 hover:text-red-500 font-medium transition" href="/nowhere">Invalid</a></div></div></div><div class="w-full max-w-5xl mx-auto p-8 flex-grow"><div><span class="text-3xl font-bold text-gray-900 mb-6 block">Reactivity & Animations</span><div id="counter-card" class="flex flex-col items-center gap-6 p-10 bg-white rounded-2xl shadow-md border border-gray-100"><div class="text-center"><span class="text-sm font-semibold text-gray-500 uppercase tracking-wide block mb-1">Count</span><span class="text-5xl font-black text-purple-600"><span id="el_89390102"></span></span></div><div class="text-center"><span class="text-sm font-semibold text-gray-500 uppercase tracking-wide block mb-1">Double</span><span class="text-3xl font-bold text-blue-500"><span id="el_490be813"></span></span></div><div class="flex flex-row shadow-sm mt-8"><button id="el_e6e21279" class="px-8 py-3 bg-gray-100 hover:bg-gray-200 rounded-l-xl font-black text-xl transition" type="button">-1</button><button id="el_75c8f632" class="px-8 py-3 bg-white hover:bg-gray-50 font-semibold text-gray-600 border-x border-gray-200 transition" type="button">Reset</button><button id="el_731f1a7e" class="px-8 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-r-xl font-black text-xl transition" type="button">+1</button></div><div class="mt-6"><span class="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3 block">Animation Demos</span><div class="flex flex-row gap-3 flex-wrap"><button id="el_d3ae78a2" class="px-4 py-2 bg-pink-500 hover:bg-pink-600 text-white rounded-lg text-sm font-bold shadow transition" type="button">Bounce</button><button id="el_e8ba4229" class="px-4 py-2 bg-yellow-400 hover:bg-yellow-500 text-gray-900 rounded-lg text-sm font-bold shadow transition" type="button">Spin</button><button id="el_2f611e15" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-bold shadow transition" type="button">Slide Left</button><button id="el_653b5b45" class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-bold shadow transition" type="button">Pulse 3x</button></div></div></div></div></div><div class="w-full p-4 border-t border-gray-200 mt-auto text-center bg-white"><span class="text-sm text-gray-500">© 2026 RailUI Framework. All rights reserved.</span></div></main>`;
$routeInit['/counter'] = () => { document.getElementById("counter-card").animate([{"transform": "translateY(30px)", "opacity": 0}, {"transform": "translateY(0)", "opacity": 1}], {"duration": 400, "easing": "ease-out", "fill": "forwards", "delay": 0, "iterations": 1, "direction": "normal"});
document.title = "Counter | RailUI SPA";
document.getElementById("el_e6e21279").addEventListener("click", function(event) { set_sig_6((sig_6() - 1)), document.getElementById("counter-card").animate([{"transform": "translateX(0)"}, {"transform": "translateX(-8px)"}, {"transform": "translateX(8px)"}, {"transform": "translateX(-6px)"}, {"transform": "translateX(6px)"}, {"transform": "translateX(0)"}], {"duration": 400, "easing": "ease-in-out", "fill": "forwards", "delay": 0, "iterations": 1, "direction": "normal"}) });
document.getElementById("el_75c8f632").addEventListener("click", function(event) { set_sig_6(0), document.getElementById("counter-card").animate([{"opacity": 1}, {"opacity": 0}], {"duration": 300, "easing": "ease-in", "fill": "forwards", "delay": 0, "iterations": 1, "direction": "normal"}), setTimeout(() => { document.getElementById("counter-card").animate([{"transform": "translateY(30px)", "opacity": 0}, {"transform": "translateY(0)", "opacity": 1}], {"duration": 350, "easing": "ease-out", "fill": "forwards", "delay": 0, "iterations": 1, "direction": "normal"}) }, 300) });
document.getElementById("el_731f1a7e").addEventListener("click", function(event) { set_sig_6((sig_6() + 1)), document.getElementById("counter-card").animate([{"transform": "scale(0.8)", "opacity": 0}, {"transform": "scale(1)", "opacity": 1}], {"duration": 200, "easing": "ease-out", "fill": "forwards", "delay": 0, "iterations": 1, "direction": "normal"}) });
document.getElementById("el_d3ae78a2").addEventListener("click", function(event) { document.getElementById("counter-card").animate([{"transform": "translateY(0)"}, {"transform": "translateY(-12px)"}, {"transform": "translateY(0)"}], {"duration": 600, "easing": "ease-in-out", "fill": "none", "delay": 0, "iterations": 3, "direction": "normal"}) });
document.getElementById("el_e8ba4229").addEventListener("click", function(event) { document.getElementById("counter-card").animate([{"transform": "rotate(0deg)"}, {"transform": "rotate(360deg)"}], {"duration": 600, "easing": "linear", "fill": "none", "delay": 0, "iterations": 2, "direction": "normal"}) });
document.getElementById("el_2f611e15").addEventListener("click", function(event) { document.getElementById("counter-card").animate([{"transform": "translateX(-40px)", "opacity": 0}, {"transform": "translateX(0)", "opacity": 1}], {"duration": 400, "easing": "ease-out", "fill": "forwards", "delay": 0, "iterations": 1, "direction": "normal"}) });
document.getElementById("el_653b5b45").addEventListener("click", function(event) { document.getElementById("counter-card").animate([{"opacity": 1}, {"opacity": 0.4}, {"opacity": 1}], {"duration": 400, "easing": "ease-in-out", "fill": "none", "delay": 0, "iterations": 3, "direction": "normal"}) }); };
$routeDestroy['/counter'] = () => {  };
$routeEffects['/counter'] = () => { $effects.push(() => { document.getElementById("el_89390102").innerText = sig_6();
document.getElementById("el_490be813").innerText = (sig_6() * 2); }); };
$routes['/dashboard'] = `<main class="min-h-screen bg-gray-50 flex flex-col"><div class="w-full bg-white shadow-sm p-4 border-b border-gray-200 sticky top-0 z-50"><div class="flex flex-row justify-between items-center w-full max-w-5xl mx-auto"><span class="font-black text-2xl text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-500">RailUI</span><div class="flex flex-row items-center gap-6"><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/">Home</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/counter">Counter</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/dashboard">Dashboard</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/profile">Profile</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/actions_demo">Actions Demo</a><a class="text-gray-400 hover:text-red-500 font-medium transition" href="/nowhere">Invalid</a></div></div></div><div class="w-full max-w-5xl mx-auto p-8 flex-grow"><div><span class="text-3xl font-bold text-gray-900 mb-6 block">Advanced Data & Lifecycle</span>
        <div id="el_99fc0a84-fallback" style="display:none;"><div class="p-12 border-2 border-dashed border-gray-300 rounded-xl flex justify-center items-center"><span class="text-purple-500 font-semibold animate-pulse">Fetching user data...</span></div></div>
        <div id="el_99fc0a84-main" style="display:none;"><div class="p-8 bg-white rounded-2xl shadow-sm border border-gray-100"><span class="text-xl font-bold block mb-1"><span id="el_edd57e1e"></span></span><span class="text-gray-500 mb-4 block"><span id="el_fb14383c"></span></span><span class="text-sm font-mono bg-gray-100 p-1 rounded"><span id="el_934f1588"></span></span><button id="el_90e55dd2" class="mt-6 px-4 py-2 bg-purple-600 text-white rounded shadow hover:bg-purple-700 block" type="button">Toggle Details</button><div id="el_ef8872f5"><div class="p-4 mt-4 bg-purple-50 rounded-lg text-purple-900 border border-purple-100"><span class="font-bold">City: </span><span><span id="el_9913931b"></span></span></div></div></div><div class="p-8 bg-white rounded-2xl shadow-sm border border-gray-100 mt-6"><span class="text-xl font-bold block mb-4 text-gray-800">Tasks List (Each Lifecycle Test)</span><button id="el_3cbdb311" class="mb-4 px-4 py-2 bg-blue-600 text-white rounded shadow hover:bg-blue-700 block" type="button">Add Task</button><div id="el_38354e8e"></div></div></div>
        </div></div><div class="w-full p-4 border-t border-gray-200 mt-auto text-center bg-white"><span class="text-sm text-gray-500">© 2026 RailUI Framework. All rights reserved.</span></div></main>`;
$routeInit['/dashboard'] = () => { console.log("Dashboard route mounted!");
document.title = "Dashboard | RailUI SPA";
document.getElementById("el_90e55dd2").addEventListener("click", function(event) { set_sig_9((!sig_9())) });
document.getElementById("el_3cbdb311").addEventListener("click", function(event) { set_sig_10([...(sig_10() || []), {"title": ("New Task " + Math.floor((Math.random() * 100)))}]) }); };
$routeDestroy['/dashboard'] = () => { console.log("Dashboard route destroyed! Cleaning up..."); };
$routeEffects['/dashboard'] = () => { $effects.push(() => { document.getElementById("el_edd57e1e").innerText = sig_7()?.name;
document.getElementById("el_fb14383c").innerText = sig_7()?.email;
document.getElementById("el_934f1588").innerText = sig_7()?.company?.name;
$show("el_ef8872f5", sig_9(), {onMount: () => { console.log("Details MOUNTED (first render)") }, onUnmount: () => { console.log("Details UNMOUNTED (hidden)") }, onUpdate: () => { console.log("Details UPDATED (visibility toggled)") }});
document.getElementById("el_9913931b").innerText = sig_7()?.address?.city;
$renderEach("el_38354e8e", sig_10(), (item, index) => `<div class="p-3 mb-2 bg-gray-50 rounded border border-gray-200"><span class="font-mono text-gray-400 mr-2">${index}</span><span class="font-semibold">${item?.title}</span></div>`, {onMount: () => { console.log("Each list MOUNTED!") }, onUpdate: () => { console.log("Each list UPDATED! (item added)") }});

        if (sig_8()) {
            document.getElementById('el_99fc0a84-fallback').style.display = 'block';
            document.getElementById('el_99fc0a84-main').style.display = 'none';
        } else {
            document.getElementById('el_99fc0a84-fallback').style.display = 'none';
            document.getElementById('el_99fc0a84-main').style.display = 'block';
        }
         }); };
$routes['/'] = `<main class="min-h-screen bg-gray-50 flex flex-col"><div class="w-full bg-white shadow-sm p-4 border-b border-gray-200 sticky top-0 z-50"><div class="flex flex-row justify-between items-center w-full max-w-5xl mx-auto"><span class="font-black text-2xl text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-500">RailUI</span><div class="flex flex-row items-center gap-6"><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/">Home</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/counter">Counter</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/dashboard">Dashboard</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/profile">Profile</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/actions_demo">Actions Demo</a><a class="text-gray-400 hover:text-red-500 font-medium transition" href="/nowhere">Invalid</a></div></div></div><div class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 p-6 shadow-lg text-center"><span class="text-3xl font-black text-white">🎉 Welcome to the Future of Python UI!</span></div><div class="w-full max-w-5xl mx-auto p-8 flex-grow"><div class="flex flex-col items-start"><span class="text-4xl font-extrabold text-gray-900 mb-4 block">Welcome to RailUI Named Slots</span><span class="text-lg text-gray-600 mb-8 block">This app features client-side SPA routing and Svelte-style slot components.</span><button id="el_e98460d2" class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg transition shadow-md" type="button">Click me for an alert</button></div></div><div class="w-full p-6 bg-gray-900 text-center mt-auto"><span class="text-sm text-indigo-200 font-bold">Custom Index Footer. Built with RailUI in Python.</span></div></main>`;
$routeInit['/'] = () => { document.title = "Home | RailUI SPA";
document.getElementById("el_e98460d2").addEventListener("click", function(event) { alert("Hello from file-based index!") }); };
$routeDestroy['/'] = () => {  };
$routeEffects['/'] = () => { };
$routes['/profile'] = `<main class="min-h-screen bg-gray-50 flex flex-col"><div class="w-full bg-white shadow-sm p-4 border-b border-gray-200 sticky top-0 z-50"><div class="flex flex-row justify-between items-center w-full max-w-5xl mx-auto"><span class="font-black text-2xl text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-500">RailUI</span><div class="flex flex-row items-center gap-6"><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/">Home</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/counter">Counter</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/dashboard">Dashboard</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/profile">Profile</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/actions_demo">Actions Demo</a><a class="text-gray-400 hover:text-red-500 font-medium transition" href="/nowhere">Invalid</a></div></div></div><div class="w-full max-w-5xl mx-auto p-8 flex-grow"><div><span class="text-3xl font-bold text-gray-900 mb-6 block">User Profile</span><form class="flex flex-col gap-4 max-w-md bg-white p-6 rounded-xl shadow-sm border border-gray-200"><div><label class="text-sm font-semibold text-gray-700 mb-1 block">Name</label><input id="el_7f9663b5" class="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition" type="text" /></div><div><label class="text-sm font-semibold text-gray-700 mb-1 block">Role</label><input id="el_bac6be71" class="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition" type="text" /></div><button id="el_85a5c57c" class="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-lg shadow mt-4 transition" type="button">Save Settings</button></form></div></div><div class="w-full p-4 border-t border-gray-200 mt-auto text-center bg-white"><span class="text-sm text-gray-500">© 2026 RailUI Framework. All rights reserved.</span></div></main>`;
$routeInit['/profile'] = () => { document.title = "Profile | RailUI SPA";
document.getElementById("el_7f9663b5").addEventListener("input", function(event) { set_sig_1(event.target.value) });
document.getElementById("el_bac6be71").addEventListener("input", function(event) { set_sig_2(event.target.value) });
document.getElementById("el_85a5c57c").addEventListener("click", function(event) { console.log("Saved", sig_1()) }); };
$routeDestroy['/profile'] = () => {  };
$routeEffects['/profile'] = () => { $effects.push(() => { document.getElementById("el_7f9663b5").value = sig_1();
document.getElementById("el_bac6be71").value = sig_2(); }); };
const $notFoundHtml = `<main class="min-h-screen bg-gray-50 flex flex-col"><div class="w-full bg-white shadow-sm p-4 border-b border-gray-200 sticky top-0 z-50"><div class="flex flex-row justify-between items-center w-full max-w-5xl mx-auto"><span class="font-black text-2xl text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-500">RailUI</span><div class="flex flex-row items-center gap-6"><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/">Home</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/counter">Counter</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/dashboard">Dashboard</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/profile">Profile</a><a class="text-gray-600 hover:text-purple-600 font-medium transition" href="/actions_demo">Actions Demo</a><a class="text-gray-400 hover:text-red-500 font-medium transition" href="/nowhere">Invalid</a></div></div></div><div class="w-full max-w-5xl mx-auto p-8 flex-grow"><div class="flex flex-col items-center justify-center py-20 text-center"><span class="text-8xl font-black text-gray-200 block mb-4">404</span><span class="text-2xl font-bold text-gray-800 block mb-6">Page Not Found</span><a class="px-6 py-3 bg-gray-900 text-white font-semibold rounded-lg hover:bg-gray-800 transition" href="/">Go back home</a></div></div><div class="w-full p-4 border-t border-gray-200 mt-auto text-center bg-white"><span class="text-sm text-gray-500">© 2026 RailUI Framework. All rights reserved.</span></div></main>`;
const $notFoundInit = () => { document.title = "404 Not Found"; };
const $notFoundDestroy = () => {  };
const $notFoundEffects = () => { };

let $currentPath = null;

function $navigate(path, replace = false) {
    if (path === $currentPath) return;
    
    if (replace) {
        window.history.replaceState({}, '', path);
    } else {
        window.history.pushState({}, '', path);
    }
    $renderRoute();
}

function $renderRoute() {
    // Run teardown of current route BEFORE replacing DOM
    if ($currentPath) {
        // Strip query params to find the correct route script
        let oldBase = $currentPath.split('?')[0].split('#')[0];
        let destroyFn = $routeDestroy[oldBase] || $notFoundDestroy;
        destroyFn();
    }

    let path = window.location.pathname;
    if (path.length > 1 && path.endsWith('/')) path = path.slice(0, -1);
    $currentPath = path + window.location.search + window.location.hash;
    
    let html = $routes[path];
    let initFn = $routeInit[path];
    let effectsFn = $routeEffects[path];
    
    if (!html) {
        // Dynamic route matching could go here
        html = $notFoundHtml;
        initFn = $notFoundInit;
        effectsFn = $notFoundEffects;
    }
    
    const root = document.getElementById('railui-root');
    root.innerHTML = html;
    
    // Scoped effects cleanup (mutating the array in-place to avoid const assignment errors)
    if (typeof $effects !== 'undefined') {
        const globals = $effects.filter(e => e._isGlobal);
        $effects.length = 0;
        $effects.push(...globals);
    } else {
        window.$effects = [];
    }
    
    if (initFn) initFn();
    
    if (effectsFn) {
        // Wrap effects pushed during route load to mark them as route-specific
        const originalPush = $effects.push;
        $effects.push = function(fn) {
            fn._isRoute = true;
            originalPush.call(this, fn);
        };
        
        effectsFn();
        
        $effects.push = originalPush;
    }
    
    // Trigger signal re-eval for the new route
    $effects.forEach(effect => {
        if (effect._isRoute || effect._isGlobal) {
            effect();
        }
    });
}

// Intercept local anchor clicks for SPA navigation
document.addEventListener('click', e => {
    const link = e.target.closest('a');
    if (link && link.href && link.href.startsWith(window.location.origin)) {
        if (link.target !== '_blank' && !link.hasAttribute('download')) {
            e.preventDefault();
            $navigate(link.pathname + link.search + link.hash);
        }
    }
});

window.addEventListener('popstate', () => {
    $renderRoute();
});

// Mark existing global effects so they persist
if (typeof $effects !== 'undefined') {
    $effects.forEach(e => e._isGlobal = true);
}

// Boot the router
document.addEventListener('DOMContentLoaded', () => {
    $renderRoute();
});
    
        