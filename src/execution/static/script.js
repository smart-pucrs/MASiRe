var mymap = null;
var markerGroup = null;
var stepSpeed = 1000;
var updateStateFunctionId = null;
var logId = '#log';
var btnLogId = '#btn-log';
var btnPauseId = '#btn-pause';
var currentStep = 1;
var playing = true;

var floodIcon = L.icon({
    iconUrl: '/static/images/flood.png',
    iconSize: [25, 23],
    iconAnchor: [15, 13]
});

var photoIcon = L.icon({
    iconUrl: '/static/images/photo.png',
    iconSize: [25, 23],
    iconAnchor: [15, 13]
});

var victimIcon = L.icon({
    iconUrl: '/static/images/victim_0.png',
    iconSize: [25, 23],
    iconAnchor: [15, 13]
});

var waterSampleIcon = L.icon({
    iconUrl: '/static/images/water_sample.png',
    iconSize: [25, 23],
    iconAnchor: [15, 13]
});

var agentIcon = L.icon({
    iconUrl: '/static/images/car.png',
    iconSize: [25, 23],
    iconAnchor: [15, 13]
});

function updateData() {
    logNormal('Request the step data from the simulation.');
    
    $.getJSON($SCRIPT_ROOT + '/next',
        function (data) {
            console.log('DAta: ', data);
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

    $('#step').text((data['step'] + 1) + ' of ' + data['total_steps']);

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
        if (data['status'] == 0){
            logCritical(data['message']);
            
            return;
        }

        sim_info = data['simulation_info']
        map_info = data['map']

        addMatchs(data['total_matchs']);

        $('#simulation-url').text(sim_info['simulation_url']);
        $('#api-url').text(sim_info['api_url']);
        $('#max-agents').text(sim_info['max_agents']);
        $('#first-step-time').text(sim_info['first_step_time']);
        $('#step-time').text(sim_info['step_time']);
        $('#social-asset-timeout').text(sim_info['social_asset_timeout']);

        console.log(data)

        let lat = parseFloat(map_info['centerLat']);
        let lon = parseFloat(map_info['centerLon']);

        mymap = L.map('mapid').setView([lat,lon], 17);
        L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
            maxZoom: 19,
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
                '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
                'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
            id: 'mapbox.streets'
        }).addTo(mymap);

        markerGroup = L.layerGroup().addTo(mymap);
    }
}

function addMatchs(amount){
    if ($('#matchs').children().length == 0){
        for (i=1; i<=amount; i++){
            $('#matchs').append("<button class='btn-match'>"+"Match "+i+"</button>")
        }
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