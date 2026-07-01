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
