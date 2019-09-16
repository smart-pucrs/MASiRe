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

var agentIcon = L.icon({
    iconUrl: '/static/images/car.png',
    iconSize: [40, 45],
    iconAnchor: [15, 13]
});

var centralIcon = L.icon({
    iconUrl: '/static/images/central.png',
    iconSize: [40, 50],
    iconAnchor: [20, 25]
});

function updateData() {
    logNormal('Request the step data from the simulation.');
    
    $.getJSON($SCRIPT_ROOT + '/next_step',
        function (data) {
            if (data['status'] == 0){
                logError('Error to update the step data: ' + data['message']);
            }else{
                process_simulation_data(data);
            }     
        });
}

function nextStep(){
    logNormal('Button Next clicked.');
    updateData();
}

function prevStep(){
    logNormal('Button Prev clicked.');

    $.getJSON($SCRIPT_ROOT + '/prev_step',
        function (data) {
            if (data['status']){
                process_simulation_data(data);
            
            }else{
                logError('Error to get the previous step: ' + data['message']);
            }     
        });
}

function nextMatch(){
    logNormal('Button NextMatch clicked.');
    
    $.getJSON($SCRIPT_ROOT + '/next_match',
        function (data) {
            if (data['status']){
                console.log(data);
                setMatchInfo(data['current_match'], data['total_macths']);
                setMapConfig(data['map']);
                process_simulation_data(data);

            }else{
                logError('Error to get the next match: ' + data['message']);
            }     
        });
}

function prevMatch(){
    logNormal('Button PrevMatch clicked.');
    
    $.getJSON($SCRIPT_ROOT + '/prev_match',
        function (data) {
            if (data['status']){
                console.log(data);
                setMatchInfo(data['current_match'], data['total_macths']);
                setMapConfig(data['map']);
                process_simulation_data(data);
                
            }else{
                logError('Error to get the previous match: ' + data['message']);
            }     
        });
}

function setMatchInfo(match, tMatch){
    $('#current-match').text(match + ' of ' + tMatch);
}

function setMapConfig(config){
    if (mymap != null){
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

    L.rectangle(bounds, {color: 'blue', weight: 1}).on('click', function (e) {
        console.info(e);
    }).addTo(constantsMarkerGroup);
    console.log(config);

    $('#current-map').text(config['osm']);
}

function process_simulation_data(data) {
    logNormal('Processing simulation data');

    variablesMarkerGroup.clearLayers();

    $('#step').text((data['step'] + 1) + ' of ' + data['total_steps']);

    let events = data['step_data']['environment']['events'];
    let event_type;
    for (i in events) {
        event_type = events[i]['type'];

        if (event_type == 'flood') {
            L.marker(events[i]['location'], { icon: floodIcon }).addTo(variablesMarkerGroup);

            L.circle(events[i]['location'], {
                color: 'blue',
                fillColor: 'blue',
                fillOpacity: 0.2,
                radius: events[i]['radius'] * 1000
            }).addTo(variablesMarkerGroup);

        } else if (event_type == 'victim') {
            if (events[i]['lifetime']  == 0){
                L.marker(events[i]['location'], { icon: victimIcon3 }).addTo(variablesMarkerGroup);
            }
            else if (events[i]['lifetime'] < 5){
                L.marker(events[i]['location'], { icon: victimIcon2 }).addTo(variablesMarkerGroup);
            }else if (events[i]['lifetime'] < 10){
                L.marker(events[i]['location'], { icon: victimIcon1 }).addTo(variablesMarkerGroup);
            }else{
                L.marker(events[i]['location'], { icon: victimIcon0 }).addTo(variablesMarkerGroup);
            }
        } else if (event_type == 'photo') {
            L.marker(events[i]['location'], { icon: photoIcon }).addTo(variablesMarkerGroup);
        } else {
            L.marker(events[i]['location'], { icon: waterSampleIcon }).addTo(variablesMarkerGroup);
        }

    let actors = data['step_data']['actors'];

    $('#active-agents').text(actors.length);

    for (i in actors) {
        agent = actors[i]['agent'];

        L.marker([agent['location']['lat'], agent['location']['lon']], { icon: agentIcon }).addTo(variablesMarkerGroup);
        }
    }
}

function init(){
    logNormal('Initializing variables.');

    $.getJSON($SCRIPT_ROOT + '/init',
        function (data){
            if (data['status'] == 0){
                logCritical(data['message']);
                
                return;
            }
            console.log(data);

            sim_info = data['simulation_info']
            map_info = data['map']

            $('#simulation-url').text(sim_info['simulation_url']);
            $('#api-url').text(sim_info['api_url']);
            $('#max-agents').text(sim_info['max_agents']);
            $('#first-step-time').text(sim_info['first_step_time']);
            $('#step-time').text(sim_info['step_time']);
            $('#social-asset-timeout').text(sim_info['social_asset_timeout']);

            setMatchInfo(data['current_match'], data['total_matchs']);
            setMapConfig(map_info);
    });    
}

function pause(){
    if (playing){
        logNormal('Paused.');

        clearInterval(updateStateFunctionId);
        $(btnPauseId).text('Play');
        playing = false;
    }else{
        logNormal('Playing.');

        updateStateFunctionId = setInterval(updateData, stepSpeed);
        $(btnPauseId).text('Pause');
        playing = true;
    }
}

function setLog(){
    if ($(logId).is(':hidden')){
        logNormal('Hiding Log.');

        $(logId).show();
        $(btnLogId).text('Hide log');
    }else{
        logNormal('Showing Log.');

        $(logId).hide();
        $(btnLogId).text('Show log');
    }
}

function log(tag, message){
    var oldText = $(logId).val();
    var formattedText = oldText + '\n[ ' + tag + ' ] ## ' + message;
    $(logId).focus().val(formattedText);
}

function logNormal(message){
    log('NORMAL', message);
}

function logError(message){
    log('ERROR', message);
}

function logCritical(message){
    log('CRITICAL', message);
}

updateStateFunctionId = setInterval(updateData, stepSpeed);

window.onload = function(){
    this.init();
};