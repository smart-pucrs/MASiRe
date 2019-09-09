var mymap = L.map('mapid').setView([-30.110815, -51.21199], 14);
var markerGroup = L.layerGroup().addTo(mymap);
var stepSpeed = 1000;

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
    $.getJSON($SCRIPT_ROOT + '/refresh',
        function (data) {
            console.log(data)
            process_simulation_data(data);
        });
}

function process_simulation_data(data) {
    document.getElementById("step").innerHTML = "Step: " + data['environment']['step'];

    markerGroup.clearLayers();

    let events = data['environment']['events'];
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
    }

    let actors = data['actors'];
    var list = document.getElementById('step-speed');
    list.innerHTML = '';

    for (i in actors) {
        agent = actors[i]['agent'];

        L.marker([agent['location']['lat'], agent['location']['lon']], { icon: agentIcon }).addTo(markerGroup);
    }
}


document.getElementById('step-speed').textContent = '1 second'
setInterval(updateData, 1000);
