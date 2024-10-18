# SeguryTechs
var maxMaps = 4; // Máximo de 4 mapas (2x2)

document.getElementById('route_button').onclick = function () {
    if (currentMarker) {
        var latlng = currentMarker.latlng;

        clearMap();

        currentCircle = L.circle(latlng, {
            color: 'red',
            fillColor: '#ff0000',
            fillOpacity: 0.3,
            radius: 1000
        }).addTo(map);

        allCircles.push(currentCircle);

        // Definir 4 destinos de ejemplo para las rutas
        var destinos = [
            {lat: latlng[0] + 0.01, lng: latlng[1] + 0.01},  // Destino 1
            {lat: latlng[0] - 0.01, lng: latlng[1] - 0.01},  // Destino 2
            {lat: latlng[0] + 0.01, lng: latlng[1] - 0.01},  // Destino 3
            {lat: latlng[0] - 0.01, lng: latlng[1] + 0.01}   // Destino 4
        ];

        // Generar las 4 rutas y agregarlas a la tabla
        for (let i = 0; i < destinos.length; i++) {
            generateRoute(latlng, destinos[i], i + 1);
        }
    } else {
        console.log("No hay marcador actual.");
    }
};

// Función para generar una ruta y mostrarla en un mapa en la tabla
function generateRoute(latlng, destino, mapIndex) {
    // Seleccionar la celda correspondiente para el nuevo mapa
    var cellId = "mapCell" + mapIndex;
    var cell = document.getElementById(cellId);

    // Crear un nuevo div para el mapa dentro de la celda
    var newMapDiv = document.createElement('div');
    newMapDiv.id = 'map' + mapIndex;
    newMapDiv.style.width = '200px';  // Ajusta el tamaño según tu preferencia
    newMapDiv.style.height = '200px'; // Ajusta el tamaño según tu preferencia
    cell.appendChild(newMapDiv);

    // Crear un nuevo mapa dentro del div recién creado
    var newMap = L.map(newMapDiv.id).setView([latlng[0], latlng[1]], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(newMap);

    // Agregar una ruta en el nuevo mapa
    var routingControl = L.Routing.control({
        waypoints: [
            L.latLng(latlng[0], latlng[1]), // Punto de origen
            L.latLng(destino.lat, destino.lng) // Punto de destino
        ],
        routeWhileDragging: true
    }).addTo(newMap);

    // Capturar el evento de ruta encontrada y enviar detalles al servidor
    routingControl.on('routesfound', function (e) {
        var routes = e.routes;
        var summary = routes[0].summary;

        // Enviar los detalles de la ruta al servidor mediante WebSocket
        socket.emit('ruta_cambiada', {
            distancia: summary.totalDistance,  // Distancia total en metros
            duracion: summary.totalTime,  // Duración total en segundos
            waypoints: routes[0].coordinates, // Coordenadas de los puntos de la ruta
            calles: routes[0].instructions.map(instruction => instruction.text) // Nombres de las calles
        });
    });
}
<table id="mapTable">
    <tr>
        <td id="mapCell1"></td>
        <td id="mapCell2"></td>
    </tr>
    <tr>
        <td id="mapCell3"></td>
        <td id="mapCell4"></td>
    </tr>
</table>
