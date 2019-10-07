var mymap = null;
var variablesMarkerGroup = null;
var constantsMarkerGroup = null;
var startMatchFunctionId = null;
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
    iconSize: [50, 55],
    iconAnchor: [25, 27]
});

var agentBoatIcon = L.icon({
    iconUrl: '/static/images/boat.png',
    iconSize: [50, 55],
    iconAnchor: [25, 27]
});

var agentDroneIcon = L.icon({
    iconUrl: '/static/images/drone.png',
    iconSize: [50, 55],
    iconAnchor: [25, 27]
});

var doctorIcon = L.icon({
    iconUrl: '/static/images/doctor.png',
    iconSize: [40, 45],
    iconAnchor: [15, 13]
});

var nurseIcon = L.icon({
    iconUrl: '/static/images/nurse.png',
    iconSize: [40, 45],
    iconAnchor: [15, 13]
});

var pharmacistIcon = L.icon({
    iconUrl: '/static/images/pharmacist.png',
    iconSize: [40, 45],
    iconAnchor: [15, 13]
});

var photographerIcon = L.icon({
    iconUrl: '/static/images/photographer.png',
    iconSize: [40, 45],
    iconAnchor: [15, 13]
});

var teacherIcon = L.icon({
    iconUrl: '/static/images/teacher.png',
    iconSize: [40, 45],
    iconAnchor: [15, 13]
});

var centralIcon = L.icon({
    iconUrl: '/static/images/central.png',
    iconSize: [40, 50],
    iconAnchor: [20, 25]
});

function startMatch(){
    $.getJSON($SCRIPT_ROOT + '/current_match', function (data) {
        if (data['status']) {
            handle_new_match(data['data']);
            
            clearInterval(startMatchFunctionId);
            updateStateFunctionId = setInterval(nextStep, stepSpeed);
        } else {
            logError(data['message']);
        }
    });
}

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
    $('#current-match').text((match_info['current_match'] + 1) + ' of ' + match_info['total_matchs']);
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

    $('#step').text(data['environment']['step'] + ' of ' + data['total_steps']);

    let events = data['environment']['events'];
    let old_locations = [];
    for (let i=0; i < events.length; i++) {
        event_location = events[i]['location'];

        event_location = format_location(event_location, old_locations);
        old_locations.push(event_location);
        event_location_formatted = [events[i]['location']['lat'], events[i]['location']['lon']];

        if (events[i]['type'] == 'flood') {
            L.marker(event_location_formatted, { icon: floodIcon }).addTo(variablesMarkerGroup);
            L.circle(event_location_formatted, {
                color: 'blue',
                fillColor: 'blue',
                fillOpacity: 0.2,
                radius: events[i]['radius'] * 1000
            }).addTo(variablesMarkerGroup);

        } else if (events[i]['type'] == 'victim') {
            if (events[i]['lifetime'] == 0) {
                L.marker(event_location_formatted, { icon: victimIcon3 }).addTo(variablesMarkerGroup);
            }
            else if (events[i]['lifetime'] < 5) {
                L.marker(event_location_formatted, { icon: victimIcon2 }).addTo(variablesMarkerGroup);
            } else if (events[i]['lifetime'] < 10) {
                L.marker(event_location_formatted, { icon: victimIcon1 }).addTo(variablesMarkerGroup);
            } else {
                L.marker(event_location_formatted, { icon: victimIcon0 }).addTo(variablesMarkerGroup);
            }
        } else if (events[i]['type'] == 'photo') {
            L.marker(event_location_formatted, { icon: photoIcon }).addTo(variablesMarkerGroup);
        } else {
            L.marker(event_location_formatted, { icon: waterSampleIcon }).addTo(variablesMarkerGroup);
        }


    }

    let actors = data['actors'];

    $('#active-agents').text(actors.length);

    for (let i=0; i < actors.length; i++) {
        type = actors[i]['type'];

        agent_location = format_location(actors[i]['location'], old_locations);
        old_locations.push(agent_location);
        agent_location_formated = [agent_location['lat'], agent_location['lon']];
        if (type == 'agent'){
            switch(actors[i]['role']){
                case 'drone':
                    L.marker(agent_location_formated, { icon: agentDroneIcon }).addTo(variablesMarkerGroup);
                    break;
                case 'car':
                    L.marker(agent_location_formated, { icon: agentCarIcon }).addTo(variablesMarkerGroup);
                    break;
                case 'boat':
                    L.marker(agent_location_formated, { icon: agentBoatIcon }).addTo(variablesMarkerGroup);
                    break;
                default:
                    logError('Role not found.');
            }
        }else{
            switch(actors[i]['profession']){
                case 'doctor':
                    L.marker(agent_location_formated, { icon: doctorIcon }).addTo(variablesMarkerGroup);
                    break;
                case 'nurse':
                    L.marker(agent_location_formated, { icon: nurseIcon }).addTo(variablesMarkerGroup);
                    break;
                case 'pharmacist':
                    L.marker(agent_location_formated, { icon: pharmacistIcon }).addTo(variablesMarkerGroup);
                    break;
                case 'teacher':
                    L.marker(agent_location_formated, { icon: teacherIcon }).addTo(variablesMarkerGroup);
                    break;
                case 'photographer':
                    L.marker(agent_location_formated, { icon: photographerIcon }).addTo(variablesMarkerGroup);
                    break;
                default:
                    logError('Profession not found.');
            }
        }
    }
}

function containsLocation(locations, location){
    for (let i=0; i < locations.length; i++){
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

            setSimulationInfo(data['sim_information']);
            startMatchFunctionId = setInterval(startMatch, stepSpeed);
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

$(function () {
    $('#speed input[type=radio]').change(function(){
        stepSpeed = parseInt(this.value);
        
        if (playing){
            clearInterval(updateStateFunctionId);
            updateStateFunctionId = setInterval(nextStep, stepSpeed);
        }

        logNormal("Step speed change to " + $(this).val() + " ms");
  
    })
})

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

window.onload = function () {
    this.init();
};