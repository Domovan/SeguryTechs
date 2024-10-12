document.addEventListener('DOMContentLoaded', function() {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    
    var map = L.map('map').setView([21.8853, -102.2916], 12);  // Centrar el mapa en Aguascalientes
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    document.getElementById('search_input').oninput = function() {
        var query = document.getElementById('search_input').value;
        socket.emit('search', query);
    };

    socket.on('search_results', function(results) {
        var resultsDiv = document.getElementById('search_results');
        resultsDiv.innerHTML = '';  // Limpiar los resultados anteriores
        
        if (results.length === 0) {
            resultsDiv.innerHTML = '<p>No se encontraron colonias.</p>';
        } else {
            var ul = document.createElement('ul');
            results.forEach(function(colonia) {
                var li = document.createElement('li');
                li.textContent = colonia.nombre;
                ul.appendChild(li);
                
                // Añadir evento click para mostrar en el mapa
                li.addEventListener('click', function() {
                    var lat = colonia.lat;
                    var lng = colonia.lng;
                    
                    // Centrar el mapa en la colonia buscada
                    map.setView([lat, lng], 16);
                    
                    // Añadir un marcador en la colonia
                    L.marker([lat, lng]).addTo(map)
                        .bindPopup(colonia.nombre)
                        .openPopup();
                });
            });
            resultsDiv.appendChild(ul);
        }
    });
});
