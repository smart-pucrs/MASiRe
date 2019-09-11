var mymap = L.map('mapid').setView([-30.110815, -51.21199], 14);
var markerGroup = L.layerGroup().addTo(mymap);
var stepSpeed = 1000;
var updateStateFunctionId = null;
var logId = '#log';
var btnLogId = '#btn-log';
var btnPauseId = '#btn-pause';
var currentStep = 1;
var playing = false;


L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
    maxZoom: 18,
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    id: 'mapbox.streets'
}).addTo(mymap);
L.marker([51.5, -0.09]).addTo(mymap);


var floodIcon = L.icon({
    iconUrl: 'flood_icon',
    iconSize: [25, 23],
    iconAnchor: [15, 13]
});

var photoIcon = L.icon({
    iconUrl: 'photo_icon',
    iconSize: [25, 23],
    iconAnchor: [15, 13]
});

var victimIcon = L.icon({
    iconUrl: 'victim_icon',
    iconSize: [25, 23],
    iconAnchor: [15, 13]
});

var waterSampleIcon = L.icon({
    iconUrl: 'water_sample_icon',
    iconSize: [25, 23],
    iconAnchor: [15, 13]
});

var agentIcon = L.icon({
    iconUrl: 'agent_icon',
    iconSize: [25, 23],
    iconAnchor: [15, 13]
});

function updateData() {
    logNormal('Request the step data from the simulation.');
    
    $.getJSON($SCRIPT_ROOT + '/next',
        function (data) {
            process_simulation_data(data);
        });
}

function next(){
    logNormal('Button Next clicked.');
    
    updateData();
}

function prev(){
    logNormal('Button Prev clicked.');

    $.getJSON($SCRIPT_ROOT + '/prev',
        function (data) {
            process_simulation_data(data);
        });
}

function process_simulation_data(data) {
    logNormal('Processing simulation data');

    if (!data['status']){
        logError('Error to update the step: ' + data['message']);
        
        return;
    }

    markerGroup.clearLayers();

    $('#step').text(data['step'] + ' of ' + data['total_steps']);

    let events = data['step_data']['environment']['events'];
    let event_type;
    for (i in events) {
        event_type = events[i]['type'];

        if (event_type == 'flood') {
            L.marker(events[i]['location'], { icon: floodIcon }).addTo(markerGroup);

            L.circle(events[i]['location'], {
                color: 'blue',
                fillColor: 'blue',
                fillOpacity: 0.2,
                radius: events[i]['radius'] * 1000
            }).addTo(markerGroup);

        } else if (event_type == 'victim') {
            L.marker(events[i]['location'], { icon: victimIcon }).addTo(markerGroup);
        } else if (event_type == 'photo') {
            L.marker(events[i]['location'], { icon: photoIcon }).addTo(markerGroup);
        } else {
            L.marker(events[i]['location'], { icon: waterSampleIcon }).addTo(markerGroup);
        }

    let actors = data['step_data']['actors'];

    $('#active-agents').text(actors.length);

    for (i in actors) {
        agent = actors[i]['agent'];

        L.marker([agent['location']['lat'], agent['location']['lon']], { icon: agentIcon }).addTo(markerGroup);
        }
    }
}

function init(){
    logNormal('Initializing variables.');

    $.getJSON($SCRIPT_ROOT + '/init',
        function (data) {
            initInfo(data);
        });

    function initInfo(data){
        $('#simulation-url').text(data['simulation_url']);
        $('#api-url').text(data['api_url']);
        $('#max-agents').text(data['max_agents']);
        $('#first-step-time').text(data['first_step_time']);
        $('#step-time').text(data['step_time']);
        $('#social-asset-timeout').text(data['social_asset_timeout']);
    }
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
    $(logId).text(formattedText);
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

window.onload = function(){
    this.init();
};