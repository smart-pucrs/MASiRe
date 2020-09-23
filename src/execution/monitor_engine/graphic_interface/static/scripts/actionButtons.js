import { pause, updateStep, updateMatch } from "./script.js";

/** actions for the buttons, when called execute a function */
const actions = {
    'btn-pause': () => pause(),
    'btn-prev': () => updateStep(-1),
    'btn-next': () => updateStep(),
    'btn-next-match': () => updateMatch(),
    'btn-previous-match': () => updateMatch(-1),
};

/** Handles the click, calling the right function */
function handleClick(event) {
    const action = actions[event.target.id];

    return action();
}

/** Add the onClick event for all buttons */
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('click', event => handleClick(event));
});