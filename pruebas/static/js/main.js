document.addEventListener('DOMContentLoaded', function () {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // Inicializa el mapa centrado en Aguascalientes
    var map = L.map('map').setView([21.8853, -102.2916], 12);

    // Capa base de OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var currentMarker = null;
    var currentCircle = null;
    var allMarkers = [];
    var allCircles = [];
    var routingControl = null;  // Variable para almacenar el control de rutas

    function clearMap() {
        if (allMarkers.length > 0) {
            allMarkers.forEach(function(marker) {
                map.removeLayer(marker);
            });
            allMarkers = [];
        }

        if (allCircles.length > 0) {
            allCircles.forEach(function(circle) {
                map.removeLayer(circle);
            });
            allCircles = [];
        }

        if (routingControl) {
            map.removeControl(routingControl);
            routingControl = null;
        }
    }

    document.getElementById('search_input').oninput = function () {
        var query = document.getElementById('search_input').value;
        socket.emit('search', query);
    };

    socket.on('search_results', function (results) {
        clearMap();  // Limpiar el mapa antes de mostrar nuevos resultados

        var resultsDiv = document.getElementById('search_results');
        resultsDiv.innerHTML = '';  // Limpiar los resultados anteriores

        if (results.length === 0) {
            resultsDiv.innerHTML = '<p>No se encontraron colonias.</p>';
        } else {
            var ul = document.createElement('ul');
            results.forEach(function (colonia) {
                var li = document.createElement('li');
                li.textContent = colonia.nombre;
                ul.appendChild(li);

                li.addEventListener('click', function () {
                    var lat = colonia.lat;
                    var lng = colonia.lng;

                    clearMap();

                    currentMarker = L.marker([lat, lng]).addTo(map)
                        .bindPopup(colonia.nombre + "<br>Riesgo: " + colonia.riesgo + "%")
                        .openPopup();

                    map.setView([lat, lng], 16);
                    allMarkers.push(currentMarker);

                    document.getElementById('route_button').style.display = 'block';

                    currentMarker.latlng = [lat, lng];
                });
            });
            resultsDiv.appendChild(ul);
        }
    });

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

            routingControl = L.Routing.control({
                waypoints: [
                    L.latLng(latlng[0], latlng[1]),
                    L.latLng(latlng[0] + 0.01, latlng[1] + 0.01) // Ejemplo de destino
                ],
                routeWhileDragging: true
            }).addTo(map);

            // Captura el evento cuando se encuentra una nueva ruta
            routingControl.on('routesfound', function(e) {
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

            // Captura el evento cuando se arrastra un punto de control
            routingControl.on('waypointdragend', function(e) {
                var waypoints = routingControl.getWaypoints();
                var updatedWaypoints = waypoints.map(function(waypoint) {
                    return {
                        lat: waypoint.lat,
                        lng: waypoint.lng
                    };
                });

                // Enviar las nuevas coordenadas de los puntos de control al servidor
                socket.emit('waypoint_dragged', {
                    waypoints: updatedWaypoints
                });

                // Imprimir en la consola de Python
                console.log("Puntos de control actualizados:", updatedWaypoints);
            });
        }
    };

    document.getElementById('show_risk_areas_button').onclick = function () {
        clearMap();
        socket.emit('mostrar_zonas_riesgo');
    };

    socket.on('zonas_riesgo', function (zonas) {
        clearMap();
        zonas.forEach(function (zona) {
            const { nombre, lat, lng, riesgo } = zona;
            const color = obtenerColorRiesgo(riesgo);

            var circle = L.circle([lat, lng], {
                color: color,
                radius: 500,
                fillColor: color,
                fillOpacity: 0.5
            }).addTo(map);

            var marker = L.marker([lat, lng]).addTo(map)
                .bindPopup(`<b>${nombre}</b><br>Riesgo: ${riesgo}%`).openPopup();

            allCircles.push(circle);
            allMarkers.push(marker);
        });
    });

    function obtenerColorRiesgo(riesgo) {
        if (riesgo <= 30) return 'green';
        if (riesgo <= 60) return 'yellow';
        return 'red';
    }
});
