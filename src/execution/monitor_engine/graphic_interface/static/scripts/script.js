import ApiController from './services/ApiController.js';
import { defineEventIcon, defineActorIcon } from './utils/marker/defineMarkerIcon.js';
import defineRouteRadius from './utils/route/defineRouteRadius.js';
import icons from './utils/icons.js';

let mymap = null;
let variablesMarkerGroup = null;
let constantsMarkerGroup = null;
let startMatchFunctionId = null;
let updateStateFunctionId = null;
let stepSpeed = 1000;
let playing = true;
let currentStep = 0;
let totalSteps = 0;
let currentMatch = 0;
let selectedMarker = {};
let pos_lat, pos_lon;

const api = new ApiController();
const btnPauseId = '#btn-pause';
const noEntityTextId = '#no-entity-text';
const extendMenuId = '#extend-menu';
const invalidStartError = 'Error: Invalid LatLng object: (NaN, NaN)';
const invalidStepError = 'The current match dont have this step yet.';
const typesWithTokens = ['agent', 'social_asset'];
const currentEntity = {
    'type': null, 
    'id': null, 
    'active': false
};

/**
 * Handle error in Json Requests
 */
function handleError(error) {
    logError(error);
}

/**
 * Start draw the current match.
 */
async function startMatch() {
    currentStep = 0;
    currentMatch = 0;

    try {
        const matchInfo = await api.getMatchInfo($SCRIPT_ROOT);
        setMatchInfo(matchInfo);

        try {
            const mapInfo = await api.getMapInfo($SCRIPT_ROOT, currentMatch);
            setMapConfig(mapInfo);

            clearInterval(startMatchFunctionId);
            updateStateFunctionId = setInterval(updateStep, stepSpeed);
        } catch (err) {
            if (err.toString() !== invalidStartError) {
                handleError(`[START MATCH | MAP INFO]: ${err}`);
            }
        }
    } catch (err) {
        handleError(`[START MATCH | MATCH INFO]: ${err}`);
    }
}

document.getElementById("mapid").addEventListener("contextmenu", (e) => {
    e.preventDefault();

    alert(`Lat: ${pos_lat} \nLon: ${pos_lon}`);
    
    return false;
});

/**
 * Get next step from the Flask and refresh the graphic interface.
 * @param stepValue -> increment or decrement the step, default (updateStep) is 1, to prevStep use -1
 * @param exactStep -> Go to the desired step, default is null
 */
async function updateStep(stepValue = 1, exactStep = null) {
    currentStep = exactStep ? parseInt(exactStep) - 1 : currentStep + stepValue;

    if (currentStep > totalSteps) {
        goToLastStep();
    }

    try {
        const simulationData = await api.getSimulationData($SCRIPT_ROOT, currentMatch, currentStep);
        
        if (simulationData.message === invalidStepError) {
            currentStep -= stepValue;
            return;
        }

        process_simulation_data(simulationData);
        
        try {
            const matchInfo = await api.getMatchInfo($SCRIPT_ROOT);
            setMatchInfo(matchInfo);
        } catch (err) {
            handleError(`[UPDATE STEP | MATCH INFO]: ${err}`);
        }
    } catch (err) {
        if (!(err instanceof TypeError)) {
            handleError(`[UPDATE STEP | SIMULATION DATA]: ${err}`);
            currentStep -= stepValue;
        }
    }
}

function goToLastStep() {
    updateStep(0, totalSteps - 1);
}

/**
 * Set the information of the match, the map and all events.
 */
function handle_new_match(data) {
    setMatchInfo(data['match_info']);
    setMapConfig(data['map_info']);
    process_simulation_data(data['step_info']);
}

/**
 * Update Match and refresh the graphic interface.
 * @param matchValue -> increment or decrement the currentMatch, default (nextMatch) is 1, to prevMatch use -1
 */
async function updateMatch(matchValue = 1) {
    if(currentMatch === 0 && matchValue === -1) {
        return logError("Already in the first step.");
    }

    currentMatch += matchValue;
    
    const oldStepValue = currentStep;
    currentStep = -1;

    try {
        const mapInfo = await api.getMapInfo($SCRIPT_ROOT, currentMatch);
        setMapConfig(mapInfo);

        updateStep();
    } catch (err) {
        handleError(`[NEXT MATCH | MAP INFO]: ${err}`);
        currentMatch -= matchValue;
        currentStep = oldStepValue;
    }
}

/**
 * Set information in match fields.
 */
function setMatchInfo(match_info) {
    totalSteps = match_info['total_steps'];

    $('#step').text(`${currentStep + 1} of ${totalSteps}`);
    $('#current-match').text(`${currentMatch + 1} of ${match_info['total_matches']}`);
}

/**
 * Set information in Map fields.
 */
function setMapConfig(config) {
    if (mymap !== null) {
        mymap.remove();
    }

    mymap = L.map('mapid', {
        zoomControl: false,
        attributionControl: false
    });
    
    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
        maxZoom: 19,
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
            '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
            'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        id: 'mapbox.streets',
    }).addTo(mymap);

    variablesMarkerGroup = L.layerGroup().addTo(mymap);
    constantsMarkerGroup = L.layerGroup().addTo(mymap);

    const lat = parseFloat(config['centerLat']);
    const lon = parseFloat(config['centerLon']);

    mymap.setView([lat, lon], 17);

    L.marker([lat, lon], { icon: icons.centralIcon }).addTo(constantsMarkerGroup);

    const bounds = [[config['minLat'], config['minLon']], [config['maxLat'], config['maxLon']]];

    L.rectangle(bounds, { weight: 1 }).on('click', (e) => {
        console.info(e);
        resetMarkerSize();
    }).addTo(constantsMarkerGroup);

    mymap.addEventListener('mousemove', (e) => {
        pos_lat = e.latlng.lat;
        pos_lon = e.latlng.lng;
    });

    $('#current-map').text(config['osm']);
}

/**
 * Handle the step data drawing all markers in map.
 */
function process_simulation_data(data) {    
    logNormal('Processing simulation data');

    variablesMarkerGroup.clearLayers();
    currentEntity['active'] = false;

    const events = data['environment']['events'];
    
    const old_locations = [];

    events.map(event => {
        const event_location = format_location(event['location'], old_locations);
        
        old_locations.push(event_location);

        const event_location_formatted = [event['location']['lat'], event['location']['lon']];
        
        const marker = L.marker(event_location_formatted, { icon: defineEventIcon(event) });

        const type = event['type'];

        if (type === 'flood') {
            L.circle(event_location_formatted, {
                color: '#504E0F',
                fillColor: '#504E0F',
                fillOpacity: 0.65,
                radius: event['radius'] * 109000
            }).addTo(variablesMarkerGroup);
        }
        
        marker.info = event;
        marker.on('click', () => setCurrentEntity(event, marker));  
        marker.addTo(variablesMarkerGroup);
        marker.bindTooltip(event.type);

        updateMetrics(data['partial_report']);
    });

    const actors = data['actors'];
    $('#active-agents').text(actors.length);

    actors.map(actor => {
        const agentInfo = actor['agent'];

        const agent_location = format_location(agentInfo['location'], old_locations);

        old_locations.push(agent_location);

        const agent_location_formated = [agent_location['lat'], agent_location['lon']];

        const marker = L.marker(agent_location_formated, { icon: defineActorIcon(agentInfo) });

        marker.info = agentInfo;
        marker.on('click', () => setCurrentEntity(agentInfo, marker));  
        marker.addTo(variablesMarkerGroup);

        const socialName = agentInfo.role ? agentInfo.role : agentInfo.profession

        marker.bindTooltip(socialName);
        
        if (agentInfo['route']) {
            printRoute(agentInfo['route']);
        }
    });

    if (currentEntity['active']) {
        $(noEntityTextId).hide();
    }
}

/**
 * Set information in entity info fields and highlights the marker.
 */
function setCurrentEntity(info, marker) {
    $("#entity-list-info").empty();
    $(noEntityTextId).hide();
    
    const token = typesWithTokens.includes(info.type) ? info.token : info.identifier;

    if (token === selectedMarker.token) {
        resetMarkerSize();
    } else {
        highlightMarker(marker);
    }

    let value = null;
    for (let key in info) {
        switch (key) {
            case 'location':
                value = `[${info[key]['lat']}, ${info[key]['lon']}]`;
                break;
            case 'route':
                value = [];
                for (let i = 0; i < info[key].length; i++) {
                    value.push(`[${info[key][i]['lat']}, ${info[key][i]['lon']}]`);
                }
                break;
            case 'destination_distance':
            case 'radius':
                value = `${(info[key] * 100).toFixed(2).toString()} km`;
                break;
            case 'social_assets':
                value = [];
                for (let i = 0; i < info[key].length; i++) {
                    const temp = info[key][i];
                    delete temp['location'];
                    value.push(temp);
                }
                break;
            default:
                value = info[key];
        }

        $("#entity-list-info").append(`<li><b>${key}:</b> ${value}</li>`);
    }

    currentEntity['type'] = info['type'];
    currentEntity['active'] = true;

    if (info['type'] === 'agent' || info['type'] === 'social_asset') {
        currentEntity['id'] = info['token'];
    } else {
        currentEntity['id'] = info['identifier'];
    }
}

/**
 * Check whether the entered location is within the array given.
 */
function containsLocation(locations, location) {
    if (locations.some(item => item['lat'] === location['lat'] && item['lon'] === location['lon'])) {
        return true;
    }

    return false;
}

/**
 * Format the location incrementing the lat coordination by 1/10000.
 */
function format_location(event_location, old_locations) {
    const new_location = event_location;
    const alfa = 0.0001;

    while (containsLocation(old_locations, new_location)) {
        new_location['lat'] += alfa;
    }

    return new_location;
}

/**
 * Update the metric list in index.html
 * @param data -> the partial_info with the metrics from that step
 */
function updateMetrics(data) {
    const formattedData = JSON.parse(data);
    let str = '';

    for (const item in formattedData) {
        const obj = formattedData[item];
        for (const props in obj) {
            str += `<li><b>${item} ${props}:</b> ${formattedData[item][props]}</li>`;
        }
    }

    $("#metrics").html(str);
}

/** Hightlight the marker and set the selectedMarker object
 * @param marker -> THe marker to be highlighted
 */
function highlightMarker(marker) {
        resetMarkerSize();
        const { iconSize: defaultSize, iconAnchor: defaultAnchor } = marker.options.icon.options;

        const newIcon = marker.getIcon();
        newIcon.options.iconSize = [85, 92];
        newIcon.options.iconAnchor = [73, 74];
        marker.setIcon(newIcon);

        const token = typesWithTokens.includes(marker.info.type) ? marker.info.token : marker.info.identifier;

        selectedMarker = {
            marker,
            token
        }

        selectedMarker.marker.defaultSize = defaultSize;
        selectedMarker.marker.defaultAnchor = defaultAnchor;
}

/**
 *  Resets the last highlighted Marker size and cleans the object
 */
function resetMarkerSize() {
    const oldMarker = selectedMarker.marker;

    if (oldMarker) {
        const oldIcon = oldMarker.getIcon();
        oldIcon.options.iconSize = oldMarker.defaultSize;
        oldIcon.options.iconAnchor = oldMarker.defaultAnchor;
        oldMarker.setIcon(oldIcon);
    }

    selectedMarker = {};
}

/**
 * Initialize the simulator info fields.
 */
async function init() {
    logNormal('Initializing the simulation');

    try {
        const simulationInfo = await api.getSimulationConfig($SCRIPT_ROOT);
        setSimulationInfo(simulationInfo);

        startMatchFunctionId = setInterval(startMatch, stepSpeed);
    } catch (err) {
        handleError(`[INIT]: ${err}`);
    }
}

/**
 * Draw the route given with red circles.
 */
function printRoute(route) {
    const radius = defineRouteRadius(mymap.getZoom());

    route.map(item => L.circle([item['lat'], item['lon']], {
        color: 'red',
        radius,
    }).addTo(variablesMarkerGroup));
}

/**
 * Set simulation info fields.
 */
function setSimulationInfo(sim_info) {
    $('#simulation-url').text(sim_info['simulation_url']);
    $('#api-url').text(sim_info['api_url']);
    $('#max-agents').text(sim_info['max_agents']);
    $('#first-step-time').text(sim_info['first_step_time']);
    $('#step-time').text(sim_info['step_time']);
    $('#social-asset-timeout').text(sim_info['social_asset_timeout']);
}

/**
 * Pause the next step interval.
 */
function pause() {
    if (playing) {
        logNormal('Paused.');

        clearInterval(updateStateFunctionId);
        $(btnPauseId).html('<img src="static/images/play_button.svg" height="13" width="13" alt="Resume Match" />');
        playing = false;
    } else {
        logNormal('Playing.');

        updateStateFunctionId = setInterval(updateStep, stepSpeed);
        $(btnPauseId).html('<img src="static/images/pause_button.svg" height="14" width="14" alt="Pause Match" />');
        playing = true;
    }
}

/**
 * Event handler for the speed options.
 * @param speed The speed value, default is 250. To increase the simulation speed use -250
 */
function updateSpeed(speed = 250) {
    stepSpeed += speed;
    
    if (playing) {
        clearInterval(updateStateFunctionId);
        updateStateFunctionId = setInterval(updateStep, stepSpeed);
    }

    logNormal(`Step speed changed to ${stepSpeed}ms`);
}

function animateButton() {
    const button = document.getElementById('expand-button');
    if (button.classList.contains('animate-open')) {
        button.classList.remove('animate-open');
        button.classList.add('animate-close');
    } else {
        button.classList.remove('animate-close');
        button.classList.add('animate-open');
    }
}

function expandMenu() {
    if ($(extendMenuId).css('display') === 'none') {
        $(extendMenuId).css('display', 'flex');
        if (playing) pause();
    } else {
        $(extendMenuId).css('display', 'none');
        if (!playing) pause();
    }

    return animateButton();
}

/**
 * Add log in text area.
 */
function log(tag, message) {
    const formattedText = `[${tag}]: ${message}`;
    console.log(formattedText);
}

function logNormal(message) {
    log('NORMAL', message);
}

function logError(message) {
    log('ERROR', message);
}

function logCritical(message) {
    log('CRITICAL', message);
}

$(noEntityTextId).show();

window.onload = () => {
    init();
};

// Export functions
export { pause, updateStep, goToLastStep, updateMatch, updateSpeed, expandMenu };