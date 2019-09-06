
var mymap = L.map('mapid').setView([-30.110815, -51.21199], 14);

L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
    maxZoom: 18,
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    id: 'mapbox.streets'
}).addTo(mymap);

L.marker([51.5, -0.09]).addTo(mymap);

L.circle([51.508, -0.11], {
    color: 'red',
    fillColor: '#f03',
    fillOpacity: 0.5,
    radius: 500
}).addTo(mymap);

L.polygon([
    [51.509, -0.08],
    [51.503, -0.06],
    [51.51, -0.047]
]).addTo(mymap);

var socket = io.connect('http://127.0.0.1:12345');
socket.on('connect', function () {
    console.log('connected');
});

socket.on('monitor', function (data) {
    console.log(data);

    document.getElementById("step").innerHTML = "Step: " + data['environment']['step'];

    document.getElementById("agentAmount").innerHTML = "Agent amount: " + data['actors'].length;
    /*
    var greenIcon = L.icon({
      iconUrl: 'http://leafletjs.com/examples/custom-icons/leaf-green.png',
      shadowUrl: 'http://leafletjs.com/examples/custom-icons/leaf-shadow.png',

      iconSize: [38, 95], // size of the icon
      shadowSize: [50, 64], // size of the shadow
      iconAnchor: [22, 94], // point of the icon which will correspond to marker's location
      shadowAnchor: [4, 62],  // the same for the shadow
      popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
    });

    L.marker([-30.110815, -51.21199], { icon: greenIcon }).addTo(mymap);
  });
  */
})