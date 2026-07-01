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

createSignal('sig_1', 0);
createSignal('sig_2', "Alice Dev");
createSignal('sig_3', "alice@railui.dev");
createSignal('sig_4', "developer");
createSignal('sig_5', "Building the future with RailUI.");
createSignal('sig_6', []);
createSignal('sig_7', true);
$effects.push(() => { document.getElementById("el_6372135f").classList.toggle("border-red-500", (sig_1() < 0)); });
$effects.push(() => { document.getElementById("el_6372135f").classList.toggle("bg-red-50", (sig_1() < 0)); });
$effects.push(() => { document.getElementById("el_5e5342c2").innerText = sig_1(); });
$effects.push(() => { document.getElementById("el_fccf01b8").innerText = (sig_1() * 2); });
$effects.push(() => { document.getElementById("inp-name").value = sig_2(); });
$effects.push(() => { document.getElementById("inp-email").value = sig_3(); });
$effects.push(() => { document.getElementById("sel-role").value = sig_4(); });
$effects.push(() => { document.getElementById("ta-bio").value = sig_5(); });
$effects.push(() => { document.getElementById("el_661e1a49").innerText = sig_2(); });
$effects.push(() => { document.getElementById("el_afceb8e1").innerText = sig_3(); });
$effects.push(() => { document.getElementById("el_12a7aa0d").innerText = sig_4(); });
$effects.push(() => { $show("el_ca187ddc", sig_7()); });
$effects.push(() => { $show("el_4ccc1a01", !(sig_7())); });
$effects.push(() => { $renderEach("el_33a42d08", sig_6(), (item, index) => `<div class="p-4 border-b border-gray-100 last:border-b-0 hover:bg-gray-50 transition cursor-pointer"><span class="font-semibold mb-1 block text-gray-900">${item.title}</span><span class="text-sm text-gray-500 block line-clamp-2">${item.body}</span></div>`); });
$effects.push(() => { console.log("Counter changed \u2192", sig_1()) });
document.getElementById("el_bb50710a").addEventListener("click", function(event) { (() => { set_sig_1((sig_1() + 1)); console.log("+ click") })() });
document.getElementById("el_c8628ca6").addEventListener("click", function(event) { set_sig_1((sig_1() - 1)) });
document.getElementById("el_63c95361").addEventListener("click", function(event) { set_sig_1(0) });
document.getElementById("inp-name").addEventListener("input", function(event) { set_sig_2(event.target.value) });
document.getElementById("inp-email").addEventListener("input", function(event) { set_sig_3(event.target.value) });
document.getElementById("sel-role").addEventListener("input", function(event) { set_sig_4(event.target.value) });
document.getElementById("ta-bio").addEventListener("input", function(event) { set_sig_5(event.target.value) });
document.getElementById("el_06101697").addEventListener("click", function(event) { console.log("Saved:", sig_2(), sig_3()) });
(async () => {
  set_sig_7(true);
  try {
    const res = await fetch("https://jsonplaceholder.typicode.com/posts?_limit=6");
    const data = await res.json();
    set_sig_6(data);
  } catch(e) {
    console.log("Failed to load posts");
  } finally {
    set_sig_7(false);
  }
})();
runEffects();
