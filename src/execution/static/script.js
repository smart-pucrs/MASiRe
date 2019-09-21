var mymap = null;
var variablesMarkerGroup = null;
var constantsMarkerGroup = null;
var updateStateFunctionId = null;
var stepSpeed = 1000;
var logId = '#log';
var btnLogId = '#btn-log';
var btnPauseId = '#btn-pause';
var playing = true;
var iconLength = [28, 35];
var iconAncor = [17, 18];

var floodIcon = L.icon({
    iconUrl: '/static/images/flood.png',
    iconSize: iconLength,
    iconAnchor: iconAncor
});

var photoIcon = L.icon({
    iconUrl: '/static/images/photo.png',
    iconSize: iconLength,
    iconAnchor: iconAncor
});

var victimIcon0 = L.icon({
    iconUrl: '/static/images/victim_0.png',
    iconSize: iconLength,
    iconAnchor: iconAncor
});

var victimIcon1 = L.icon({
    iconUrl: '/static/images/victim_1.png',
    iconSize: iconLength,
    iconAnchor: iconAncor
});

var victimIcon2 = L.icon({
    iconUrl: '/static/images/victim_2.png',
    iconSize: iconLength,
    iconAnchor: iconAncor
});

var victimIcon3 = L.icon({
    iconUrl: '/static/images/victim_3.png',
    iconSize: iconLength,
    iconAnchor: iconAncor
});

var waterSampleIcon = L.icon({
    iconUrl: '/static/images/water_sample.png',
    iconSize: iconLength,
    iconAnchor: iconAncor
});

var agentCarIcon = L.icon({
    iconUrl: '/static/images/car.png',
    iconSize: [40, 45],
    iconAnchor: [15, 13]
});

var agentBoatIcon = L.icon({
    iconUrl: '/static/images/boat.png',
    iconSize: [40, 45],
    iconAnchor: [15, 13]
});

var agentDroneIcon = L.icon({
    iconUrl: '/static/images/drone.png',
    iconSize: [40, 45],
    iconAnchor: [15, 13]
});

var socialAssetIcon = L.icon({
    iconUrl: '/static/images/social_asset.png',
    iconSize: [40, 45],
    iconAnchor: [15, 13]
});

var centralIcon = L.icon({
    iconUrl: '/static/images/central.png',
    iconSize: [40, 50],
    iconAnchor: [20, 25]
});


function nextStep() {
    $.getJSON($SCRIPT_ROOT + '/next_step', function (data) {
        if (data['status']) {
            process_simulation_data(data['data']);
        } else {
            logError(data['message']);
        }
    });
}

function prevStep() {
    $.getJSON($SCRIPT_ROOT + '/prev_step', function (data) {
        if (data['status']) {
            process_simulation_data(data['data']);
        } else {
            logError(data['message']);
        }
    });
}

function handle_new_match(data) {
    console.log('Handle ' + data);
    setMatchInfo(data['match_info']);
    setMapConfig(data['map_info']);
    process_simulation_data(data['step_info']);

}

function nextMatch() {
    logNormal('Button NextMatch clicked.');
    $.getJSON($SCRIPT_ROOT + '/next_match', function (data) {
        if (data['status']) {
            handle_new_match(data['data']);
        } else {
            logError(data['message']);
        }
    });
}

function prevMatch() {
    logNormal('Button PrevMatch clicked.');
    $.getJSON($SCRIPT_ROOT + '/prev_match', function (data) {
        if (data['status']) {
            handle_new_match(data['data']);
        }
    });
}

function setMatchInfo(match_info) {
    $('#current-match').text(match_info['current_match'] + ' of ' + match_info['total_matchs']);
}

function setMapConfig(config) {
    if (mymap != null) {
        mymap.remove();
    }

    mymap = L.map('mapid');
    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
        maxZoom: 19,
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
            '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
            'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        id: 'mapbox.streets'
    }).addTo(mymap);

    variablesMarkerGroup = L.layerGroup().addTo(mymap);
    constantsMarkerGroup = L.layerGroup().addTo(mymap);

    let lat = parseFloat(config['centerLat']);
    let lon = parseFloat(config['centerLon']);

    mymap.setView([lat, lon], 17);

    L.marker([lat, lon], { icon: centralIcon }).addTo(constantsMarkerGroup);
    let bounds = [[config['minLat'], config['minLon']], [config['maxLat'], config['maxLon']]];

    L.rectangle(bounds, { color: 'blue', weight: 1 }).on('click', function (e) {
        console.info(e);
    }).addTo(constantsMarkerGroup);
    console.log(config);

    $('#current-map').text(config['osm']);
}

function process_simulation_data(data) {
    console.log(data);
    logNormal('Processing simulation data');

    variablesMarkerGroup.clearLayers();

    $('#step').text(data['current_step'] + ' of ' + data['total_steps']);

    let events = data['step_data']['environment']['events'];
    let old_locations = [];
    for (i in events) {
        event_location = events[i]['location'];

        event_location = format_location(event_location, old_locations);
        old_locations.push(event_location);
        event_location_formated = [events[i]['location']['lat'], events[i]['location']['lon']];

        if (events[i]['type'] == 'flood') {
            L.marker(event_location_formated, { icon: floodIcon }).addTo(variablesMarkerGroup);
            L.circle(event_location_formated, {
                color: 'blue',
                fillColor: 'blue',
                fillOpacity: 0.2,
                radius: events[i]['radius'] * 1000
            }).addTo(variablesMarkerGroup);

        } else if (events[i]['type'] == 'victim') {
            if (events[i]['lifetime'] == 0) {
                L.marker(event_location_formated, { icon: victimIcon3 }).addTo(variablesMarkerGroup);
            }
            else if (events[i]['lifetime'] < 5) {
                L.marker(event_location_formated, { icon: victimIcon2 }).addTo(variablesMarkerGroup);
            } else if (events[i]['lifetime'] < 10) {
                L.marker(event_location_formated, { icon: victimIcon1 }).addTo(variablesMarkerGroup);
            } else {
                L.marker(event_location_formated, { icon: victimIcon0 }).addTo(variablesMarkerGroup);
            }
        } else if (events[i]['type'] == 'photo') {
            L.marker(event_location_formated, { icon: photoIcon }).addTo(variablesMarkerGroup);
        } else {
            L.marker(event_location_formated, { icon: waterSampleIcon }).addTo(variablesMarkerGroup);
        }


    }

    let actors = data['step_data']['actors'];

    $('#active-agents').text(actors.length);

    for (i in actors) {
        agent = actors[i]['agent'];

        agent_location = format_location(agent['location'], old_locations);
        old_locations.push(agent_location);
        agent_location_formated = [agent_location['lat'], agent_location['lon']];

        L.marker(agent_location_formated, { icon: agentDroneIcon }).addTo(variablesMarkerGroup);
        /*
        if (agent['role'] == 'drone') {
            L.marker([agent['location']['lat'], agent['location']['lon']], { icon: agentDroneIcon }).addTo(variablesMarkerGroup);
        } else if (agent['role'] == 'car') {
            L.marker([agent['location']['lat'], agent['location']['lon']], { icon: agentCarIcon }).addTo(variablesMarkerGroup);
        } else if (agent['role'] == 'boat') {
            L.marker([agent['location']['lat'], agent['location']['lon']], { icon: agentBoatIcon }).addTo(variablesMarkerGroup);
        } else if (agent['role'] == 'social_asset') {
            L.marker([agent['location']['lat'], agent['location']['lon']], { icon: socialAssetIcon }).addTo(variablesMarkerGroup);
        } else {
            logError('Role of agent not found: ' + agent['role']);
        }
        */
    }
}

function containsLocation(locations, location){
    for (i in locations){
        if (locations[i]['lat'] == location['lat']){
            if (locations[i]['lon'] == location['lon']) return true;
        }
    }

    return false;
}

function format_location(event_location, old_locations){
    let new_location = event_location;
    let alfa = 0.0001;

    while (containsLocation(old_locations, new_location)){
        new_location['lat'] += alfa;
    }

    return new_location;
}

function init() {
    logNormal('Initializing variables.');

    $.getJSON($SCRIPT_ROOT + '/init',
        function (data) {
            console.log(data)
            if (data['status'] == 0) {
                logCritical(data['message']);

                return;
            }

            setSimulationInfo(data['simulation_info']);
            setMatchInfo(data['match_info']);
            setMapConfig(data['map_info']);
        });
}

function setSimulationInfo(sim_info) {
    $('#simulation-url').text(sim_info['simulation_url']);
    $('#api-url').text(sim_info['api_url']);
    $('#max-agents').text(sim_info['max_agents']);
    $('#first-step-time').text(sim_info['first_step_time']);
    $('#step-time').text(sim_info['step_time']);
    $('#social-asset-timeout').text(sim_info['social_asset_timeout']);
}

function pause() {
    if (playing) {
        logNormal('Paused.');

        clearInterval(updateStateFunctionId);
        $(btnPauseId).text('Play');
        playing = false;
    } else {
        logNormal('Playing.');

        updateStateFunctionId = setInterval(nextStep, stepSpeed);
        $(btnPauseId).text('Pause');
        playing = true;
    }
}

function setLog() {
    if ($(logId).is(':hidden')) {
        logNormal('Hiding Log.');

        $(logId).show();
        $(btnLogId).text('Hide log');
    } else {
        logNormal('Showing Log.');

        $(logId).hide();
        $(btnLogId).text('Show log');
    }
}

function log(tag, message) {
    var oldText = $(logId).val();
    var formattedText = oldText + '\n[ ' + tag + ' ] ## ' + message;
    $(logId).focus().val(formattedText);
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

updateStateFunctionId = setInterval(nextStep, stepSpeed);

window.onload = function () {
    this.init();
};