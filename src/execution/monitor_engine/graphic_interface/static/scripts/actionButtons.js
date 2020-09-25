import { pause, updateStep, goToLastStep, updateMatch, updateSpeed } from "./script.js";

/** actions for the buttons, when called execute a function */
const actions = {
    'btn-pause': () => pause(),
    'btn-prev': () => updateStep(-1),
    'btn-next-1': () => updateStep(),
    'btn-next-10': () => updateStep(+10),
    'exact-step': (exactStep) => updateStep(0, exactStep),
    'go-to-last-step': () => goToLastStep(),
    'btn-next-match': () => updateMatch(),
    'btn-previous-match': () => updateMatch(-1),
    'inc-speed': () => updateSpeed(-250),
    'dec-speed': () => updateSpeed(),
};

/** Handles the click, calling the right function */
function handleClick(event) {
    const action = actions[event.target.id];

    return action();
}

function onChange(event) {
    const { id, value } = event.target;

    return actions[id](value);
}

/** Add the onClick event for all buttons */
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('click', event => handleClick(event));
});

/** Add the onChange event for the step input */
document.querySelector('#exact-step').addEventListener('change', event => onChange(event));