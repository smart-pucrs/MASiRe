import { pause, updateStep, goToLastStep, updateMatch, updateSpeed } from "./script.js";

/** actions for the buttons, when called execute a function */
const actions = {
    'btn-pause': () => pause(),
    'btn-prev-10': () => updateStep(-10),
    'btn-prev': () => updateStep(-1),
    'btn-next': () => updateStep(),
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

function animateButton() {
    const button = document.getElementById('expandButton');
    if (button.classList.contains('animate-open')) {
        button.classList.remove('animate-open');
        button.classList.add('animate-close');
    } else {
        button.classList.remove('animate-close');
        button.classList.add('animate-open');
    }
}

/** Add the onClick event for all buttons */
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('click', event => handleClick(event));
});

document.getElementById('expandButton').addEventListener('click', event => animateButton());
/** Add the onChange event for the step input */
document.querySelector('#exact-step').addEventListener('change', event => onChange(event));