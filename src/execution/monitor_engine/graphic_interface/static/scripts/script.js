import ApiController from './services/ApiController.js';
import { defineEventIcon, defineActorIcon } from './utils/marker/defineMarkerIcon.js';
import defineRouteRadius from './utils/route/defineRouteRadius.js';
import getSpeedMultiplier from './utils/getSpeedMultiplier.js';
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
let selectedMarker = null;
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
 * @param {Number} stepValue -> increment or decrement the step, default (updateStep) is 1, to prevStep use -1
 * @param {Number} exactStep -> Go to the desired step, default is null
 */
async function updateStep(stepValue = 1, exactStep = null) {
    if (exactStep && exactStep <= 0) {
        currentStep = stepValue;
    } else {
        currentStep = exactStep ? parseInt(exactStep) - 1 : currentStep + stepValue;
    }

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
 * @param {object} data data to initialize the next match
 */
function handle_new_match(data) {
    setMatchInfo(data['match_info']);
    setMapConfig(data['map_info']);
    process_simulation_data(data['step_info']);
}

/**
 * Update Match and refresh the graphic interface.
 * @param {Number} matchValue -> increment or decrement the currentMatch, default (nextMatch) is 1, to prevMatch use -1
 */
async function updateMatch(matchValue = 1) {
    if (currentMatch === 0 && matchValue === -1) {
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
 * @param {object} match_info information of the current match
 */
function setMatchInfo(match_info) {
    totalSteps = match_info['total_steps'];

    $('#step').text(`${currentStep + 1} of ${totalSteps}`);
    $('#current-match').text(`${currentMatch + 1} of ${match_info['total_matches']}`);

}

/**
 * Set information in Map fields.
 * @param {object} config the map config 
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
        resetMarker();
    }).addTo(constantsMarkerGroup);

    mymap.addEventListener('mousemove', (e) => {
        pos_lat = e.latlng.lat;
        pos_lon = e.latlng.lng;
    });

    $('#current-map').text(config['osm']);
}

/**
 * Handle the step data drawing all markers in map.
 * @param {object} data - api data to processed
 */
function process_simulation_data(data) {
    logNormal('Processing simulation data');

    variablesMarkerGroup.clearLayers();

    const events = data['environment']['events'];

    const old_locations = [];

    events.map(event => {
        const event_location = format_location(event['location'], old_locations);

        old_locations.push(event_location);

        const event_location_formatted = [event['location']['lat'], event['location']['lon']];

        const icon = selectedMarker && selectedMarker.id === event.identifier ? selectedMarker.icon : defineEventIcon(event);

        const marker = L.marker(event_location_formatted, { icon, id: event.identifier });

        if (event['type'] === 'flood') {
            L.circle(event_location_formatted, {
                color: '#504E0F',
                fillColor: '#504E0F',
                fillOpacity: 0.65,
                radius: event['radius'] * 109000
            }).addTo(variablesMarkerGroup);
        }

        marker.info = event;
        marker.on('click', () => setCurrentEntity(event));
        marker.bindTooltip(event.type);
        marker.addTo(variablesMarkerGroup);

        checkIfIsSelected(event);
        updateMetrics(data['partial_report']);
    });

    const actors = data['actors'];
    $('#active-agents').text(actors.length);

    actors.map(actor => {
        const agentInfo = actor['agent'];

        const agent_location = format_location(agentInfo['location'], old_locations);

        old_locations.push(agent_location);

        const agent_location_formated = [agent_location['lat'], agent_location['lon']];

        const icon = selectedMarker && selectedMarker.id === agentInfo.token ? selectedMarker.icon : defineActorIcon(agentInfo);

        const marker = L.marker(agent_location_formated, { icon, id: agentInfo.token });

        const socialName = agentInfo.role ? agentInfo.role : agentInfo.profession;

        marker.info = agentInfo;
        marker.on('click', () => setCurrentEntity(agentInfo));
        marker.bindTooltip(socialName);
        marker.addTo(variablesMarkerGroup);

        checkIfIsSelected(agentInfo);

        if (agentInfo['route']) {
            printRoute(agentInfo['route']);
        };
    });
}

/**
 * Checks if the agent/event is active and calls updateEntityInfo to update information on screen in step time
 * @param {info} info from the agent/event to check if is the active one
 */
function checkIfIsSelected(info) {
    if (currentEntity['id'] === info['token'] || currentEntity['id'] === info['identifier']) {
        updateEntityInfo(info);
        moveMap(info.location);
    };
}

/**
 * Set information in entity info fields and highlights the marker.
 * @param {object} info the agent/event info
 * @param {object} marker marker to be highlighted
 */
function setCurrentEntity(info) {
    const id = typesWithTokens.includes(info.type) ? info.token : info.identifier;

    if (selectedMarker && id === selectedMarker.id) {
        return resetMarker();
    }

    highlightMarker(id);

    currentEntity['type'] = info['type'];
    currentEntity['active'] = true;
    currentEntity['id'] = id;

    updateEntityInfo(info);
}

/** Highlight the marker and set the selectedMarker object
 * @param {object} id identifier of the marker to be highlighted
 */
function highlightMarker(id) {
    resetMarker();

    variablesMarkerGroup.eachLayer((layer) => {
        const layerId = layer.options.id;

        if (layerId === id) {
            const oldIconObjCopy = JSON.parse(JSON.stringify(layer.getIcon()));
            const oldIcon = L.icon(oldIconObjCopy.options);

            const { iconSize: defaultSize, iconAnchor: defaultAnchor } = oldIcon.options;

            const { _latlng } = layer;

            const newLayer = L.marker(_latlng, { icon: oldIcon, id: layerId });
            newLayer.info = layer.info;
            newLayer.on('click', () => setCurrentEntity(newLayer.info));

            const options = newLayer.options.icon.options;
            options.iconSize = [70, 75];
            options.iconAnchor = [45, 47];

            selectedMarker = {
                id,
                defaultSize,
                defaultAnchor,
                icon: L.icon(options),
                _latlng
            }

            updateLayer(layer, newLayer);
            moveMap(_latlng);
        }
    });
}

/**
 *  Resets the last highlighted Marker size and cleans the selectedMarker object
 */
function resetMarker() {
    if (selectedMarker) {
        const { id, defaultSize, defaultAnchor } = selectedMarker;

        variablesMarkerGroup.eachLayer((layer) => {
            const layerId = layer.options.id;

            if (layerId === id) {
                const { _latlng } = layer;

                const oldIconObjCopy = JSON.parse(JSON.stringify(layer.getIcon()));
                const oldIcon = L.icon(oldIconObjCopy.options);

                const newLayer = L.marker(_latlng, { icon: oldIcon, id: layerId });
                newLayer.info = layer.info;
                newLayer.on('click', () => setCurrentEntity(newLayer.info));

                const options = newLayer.options.icon.options;
                options.iconSize = defaultSize;
                options.iconAnchor = defaultAnchor;

                selectedMarker = null;

                currentEntity['active'] = false;
                currentEntity['type'] = null;
                currentEntity['id'] = null;

                updateEntityInfo();

                updateLayer(layer, newLayer);
            }
        });
    }
}

/**
 * Moves the map to a specific parameter
 * @param {Object | Array} _latlng 
 */
function moveMap(_latlng) {
    mymap.flyTo(_latlng);
}

/**
 * Updates the variablesMarkerGroup layer information
 * @param {Object} layer the layer to be updated
 * @param {Object} newLayer the new layer to be add
 */
function updateLayer(layer, newLayer) {
    variablesMarkerGroup.removeLayer(layer);
    variablesMarkerGroup.addLayer(newLayer);
}

/**
 * Updates the entity info on the screen
 * @param {object} info information to be updated in the screen, default is null to show 'no agent selected'
 */
function updateEntityInfo(info = null) {
    $("#entity-list-info").empty();

    if (info) {
        $(noEntityTextId).hide();

        let value = null;
        for (let key in info) {
            switch (key) {
                case 'location':
                    value = `[${info[key]['lat']}, ${info[key]['lon']}]`;
                    break;
                case 'route':
                    value = [];
                    info[key].map(nextRoute => {
                        value.push(`[${nextRoute.lat}, ${nextRoute.lon}]`);
                    });
                    break;
                case 'destination_distance':
                case 'radius':
                    value = `${(info[key] * 100).toFixed(2).toString()} km`;
                    break;
                case 'social_assets':
                    value = [];
                    info[key].map(item => {
                        const temp = item;
                        delete temp.location;
                        if (temp instanceof Object) {
                            value.push(temp.profession || temp.type);
                        } else {
                            value.push(temp);
                        }
                    });
                    break;
                case 'physical_storage_vector':
                    value = '';
                    info[key].map((item, index) => {
                        if (item instanceof Object) {
                            value += item.type;
                        }

                        if (index !== info[key].length - 1) value += ", ";
                    });
                    break;
                default:
                    value = info[key];
            }

            $("#entity-list-info").append(`<li><b>${key}:</b> ${value}</li>`);
        }
    } else {
        $(noEntityTextId).show();
    }
}

/**
 * Check whether the entered location is within the array given.
 * @param {Array<object>} locations the array of objects to be checked
 * @param {object} location the location to be checked within the array
 */
function containsLocation(locations, location) {
    if (locations.some(item => item['lat'] === location['lat'] && item['lon'] === location['lon'])) {
        return true;
    }

    return false;
}

/**
 * Format the location incrementing the lat coordination by 1/10000.
 * @param {Array<object>} old_locations the array of old locations
 * @param {object} event_location the new location of the event
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
 * @param {object} data -> the partial_info with the metrics from that step
 */
function updateMetrics(data) {
    const formattedData = JSON.parse(data);
    let str = '';

    for (const item in formattedData) {
        const obj = formattedData[item];
        str += `<li><b>${item}: </b>`;

        if (obj instanceof Object) {
            str += "<ul>";

            for (const props in obj) {
                const key = props.replace(/_/g, " ");
                str += `<li>${key}: ${obj[props]}</li>`;
            }

            str += "</ul>";
        } else {
            str += obj;
        }

        str += "</li>";
    }

    $("#metrics").html(str);
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
 * @param {Number} speed The speed value, default is 250. To increase the simulation speed use -250
 */
function updateSpeed(speed = 250) {
    const newSpeed = stepSpeed + speed;

    if (newSpeed < 250) {
        stepSpeed = 250;
    } else if (newSpeed > 1750) {
        stepSpeed = 1750;
    } else {
        stepSpeed = newSpeed;
    }

    clearInterval(updateStateFunctionId);
    updateStateFunctionId = setInterval(updateStep, stepSpeed);

    if (!playing) {
        playing = true;
        pause();
    }

    const speedMultiplier = getSpeedMultiplier(stepSpeed);

    let str = `${speedMultiplier}x`;

    if (stepSpeed === 1750) {
        str += " (min)";
    } else if (stepSpeed === 250) {
        str += " (max)";
    }

    $('#speed').text(str);
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

window.onload = () => {
    init();
};

// Export functions
export { pause, updateStep, goToLastStep, updateMatch, updateSpeed, expandMenu };