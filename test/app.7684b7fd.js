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
createSignal('sig_2', "World");
$effects.push(() => { document.getElementById("el_9945f98e").classList.toggle("border-red-500", (sig_1() < 0)); });
$effects.push(() => { document.getElementById("el_9945f98e").classList.toggle("bg-red-50", (sig_1() < 0)); });
$effects.push(() => { document.getElementById("el_fc47c86b").innerText = sig_1(); });
$effects.push(() => { document.getElementById("el_01a8de6f").innerText = (sig_1() * 2); });
$effects.push(() => { document.getElementById("el_2a03365f").innerText = sig_2(); });
$effects.push(() => { document.getElementById("el_9ae9ecef").value = sig_2(); });
$effects.push(() => { console.log("Counter updated! New value:", sig_1()) });
document.getElementById("el_4dcd28fb").addEventListener("click", function(event) { (() => { set_sig_1((sig_1() + 1)); console.log("Incremented to:", sig_1()) })() });
document.getElementById("el_75420944").addEventListener("click", function(event) { (() => { set_sig_1((sig_1() - 1)); console.log("Decremented to:", sig_1()) })() });
document.getElementById("el_9ae9ecef").addEventListener("input", function(event) { set_sig_2(event.target.value) });
runEffects();
