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
        socket.emit('search', query); // Envía la consulta al servidor
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
                li.textContent = colonia.nombre_colonia; // Actualiza para acceder al nombre correcto
                ul.appendChild(li);

                li.addEventListener('click', function () {
                    var lat = colonia.centro[1]; // Accede a la latitud
                    var lng = colonia.centro[0]; // Accede a la longitud
                    var riesgo =colonia.riesgo;

                    clearMap();
                    let randomNumber = Math.floor(Math.random() * 101);
                    currentMarker = L.marker([lat, lng]).addTo(map)
                    
                        .bindPopup(colonia.nombre_colonia + "<br>Riesgo: " + riesgo + "%")
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

    var maxMaps = 4; // Máximo de 4 mapas (2x2)

    document.getElementById('route_button').onclick = function () {
        if (currentMarker) {
            var latlng = currentMarker.getLatLng(); // Cambiado de latlng a getLatLng()
    
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
                {lat: latlng.lat + 0.01, lng: latlng.lng + 0.01},  // Destino 1
                {lat: latlng.lat - 0.01, lng: latlng.lng - 0.01},  // Destino 2
                {lat: latlng.lat + 0.01, lng: latlng.lng - 0.01},  // Destino 3
                {lat: latlng.lat - 0.01, lng: latlng.lng + 0.01}   // Destino 4
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
        var mapDivId = "map" + mapIndex;
        var directionsDivId = "directions" + mapIndex;
        
        var mapDiv = document.getElementById(mapDivId);
        var directionsDiv = document.getElementById(directionsDivId);
        var tabla = document.getElementById('mapTable');
    
           
        // Limpiar la celda para asegurarse de que esté vacía
        mapDiv.innerHTML = '';
        directionsDiv.innerHTML = '';
    
        // Crear un nuevo mapa dentro del div
        var newMap = L.map(mapDivId).setView([latlng.lat, latlng.lng], 13);
    
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(newMap);
    
        // Crear un control de ruta con las direcciones movidas al div correspondiente
        var routingControl = L.Routing.control({
            waypoints: [
                L.latLng(latlng.lat, latlng.lng), // Punto de origen
                L.latLng(destino.lat, destino.lng) // Punto de destino
            ],
            routeWhileDragging: true,
            createMarker: function() { return null; }, // Deshabilitar los marcadores predeterminados
        }).addTo(newMap);
    
        // Mover las direcciones al div correspondiente
        routingControl.on('routesfound', function (e) {
            var routes = e.routes;
            var instructions = routes[0].instructions;
    
            // Limpiar direcciones previas
            directionsDiv.innerHTML = '';
    
            // Mostrar las instrucciones de la ruta
            instructions.forEach(instruction => {
                var directionItem = document.createElement('div');
                directionItem.innerText = instruction.text;
                directionsDiv.appendChild(directionItem);
            });
    
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
    
    

    document.getElementById('show_risk_areas_button').onclick = function () {
        clearMap();
        socket.emit('mostrar_zonas_riesgo');
    };

    socket.on('zonas_riesgo', function (zonas) {
        clearMap();
        zonas.forEach(function (zona) {
            
            let randomNumber = Math.floor(Math.random() * 101);//generar un numero aleatorio
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
