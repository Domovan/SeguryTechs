from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import json
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

i=0
socketio = SocketIO(app)
# Datos de las colonias con coordenadas
puntos_zonas = {
    "Centro": (21.8853, -102.2920),
    "San Marcos Barrio": (21.8785, -102.2920),
    "Américas Las Fracc.": (21.8838, -102.2880),
    "Municipio Libre Fracc.": (21.8950, -102.3090),
    "Haciendas de Aguascalientes Fracc.": (21.8670, -102.3050),
    "Morelos I Fracc.": (21.8900, -102.2840),
    "Gremial Col.": (21.8840, -102.3070),
    "Ojocaliente I Fracc.": (21.8735, -102.2970),
    "Flores Las Col.": (21.8830, -102.2750),
    "Pilar Blanco Infonavit": (21.8930, -102.2920),
    "San Cayetano Fracc.": (21.8790, -102.2980),
    "Insurgentes Col. (Las Huertas)": (21.8795, -102.3080),
    "Guadalupe de Barrio": (21.8820, -102.3010),
    "Morelos Infonavit": (21.8890, -102.2900),
    "Circunvalación Norte Fracc.": (21.8955, -102.3055),
    "San Marcos Col.": (21.8770, -102.2870),
    "Rodolfo Landeros Fracc.": (21.8630, -102.3070),
    "Obraje Col.": (21.8845, -102.2760),
    "Santa Anita 1era Secc. Fracc.": (21.8820, -102.3030),
    "Trabajo del Col.": (21.8885, -102.2960),
    "José Guadalupe Peralta Fracc.": (21.8615, -102.3080),
    "Dorado El 1era Secc. Fracc.": (21.8620, -102.2950),
    "Purísima La Barrio": (21.8650, -102.3000),
    "Ojocaliente III Fracc.": (21.8730, -102.3075),
    "Colinas del Río Fracc.": (21.8690, -102.2875),
    "España Fracc.": (21.8850, -102.2950),
    "Industrial Col.": (21.8700, -102.2950),
    "Arboledas Las Fracc.": (21.8820, -102.2880),
    "Villas de Ntra. Sra. de la Asunción Sec Estacion Fracc.": (21.8920, -102.3095),
    "Bosques del Prado Sur Fracc.": (21.8925, -102.3010)
}

# Datos de riesgo
datos_riesgo = {
    "Centro": 60,
    "San Marcos Barrio": 50,
    "Américas Las Fracc.": 45,
    "Municipio Libre Fracc.": 70,
    "Haciendas de Aguascalientes Fracc.": 30,
    "Morelos I Fracc.": 40,
    "Gremial Col.": 35,
    "Ojocaliente I Fracc.": 65,
    "Flores Las Col.": 25,
    "Pilar Blanco Infonavit": 50,
    "San Cayetano Fracc.": 40,
    "Insurgentes Col. (Las Huertas)": 60,
    "Guadalupe de Barrio": 35,
    "Morelos Infonavit": 55,
    "Circunvalación Norte Fracc.": 50,
    "San Marcos Col.": 45,
    "Rodolfo Landeros Fracc.": 70,
    "Obraje Col.": 40,
    "Santa Anita 1era Secc. Fracc.": 55,
    "Trabajo del Col.": 35,
    "José Guadalupe Peralta Fracc.": 65,
    "Dorado El 1era Secc. Fracc.": 45,
    "Purísima La Barrio": 25,
    "Ojocaliente III Fracc.": 55,
    "Colinas del Río Fracc.": 30,
    "España Fracc.": 60,
    "Industrial Col.": 50,
    "Arboledas Las Fracc.": 55,
    "Villas de Ntra. Sra. de la Asunción Sec Estacion Fracc.": 35,
    "Bosques del Prado Sur Fracc.": 35
}

# Ruta principal para servir la página
@app.route('/')
def index():#valiendo verga
    return render_template('index.html')



@socketio.on('mostrar_zonas_riesgo')
def handle_mostrar_zonas_riesgo():
    zonas_con_riesgo = [{'nombre': k, 'lat': v[0], 'lng': v[1], 'riesgo': datos_riesgo[k]} 
                        for k, v in puntos_zonas.items()]
    socketio.emit('zonas_riesgo', zonas_con_riesgo)

@socketio.on('search')
def handle_search(query):
    results = []
    
    # Busca la colonia exacta en el diccionario
    if query in puntos_zonas:
        lat, lng = puntos_zonas[query]
        riesgo = datos_riesgo[query]
        results.append({'nombre': query, 'lat': lat, 'lng': lng, 'riesgo': riesgo})
    else:
        # Búsqueda por coincidencia parcial
        results = [{'nombre': k, 'lat': v[0], 'lng': v[1], 'riesgo': datos_riesgo[k]} 
                   for k, v in puntos_zonas.items() if query.lower() in k.lower()]

    socketio.emit('search_results', results)
    
    
@socketio.on('ruta_cambiada')
def handle_ruta_cambiada(data):
    distancia = data.get('distancia')
    duracion = data.get('duracion')
    waypoints = data.get('waypoints')
    calles = data.get('calles')  # Recibimos las calles

    # Crear una cadena vacía para almacenar las calles
    calles_str = "Calles por las que pasa la ruta:\n"

    print("Ruta recibida:")
    print(f"Distancia total: {distancia} metros")
    print(f"Duración total: {duracion} segundos")
    print("Waypoints (coordenadas):")
    # Para cada calle, añadirla al string
    for calle in calles:
        calles_str += calle + '\n'  # Añadir cada calle al string con salto de línea

    # Imprimir el resultado (si es necesario para debug)
    print(calles_str+ '\n')
    print(separate_by_street(calles_str))
    
    

# Función para separar las instrucciones de las calles/avenidas
def separate_by_street(text):
    lines = text.strip().split('\n')  # Dividir el texto por renglones
    streets = []
    
    for line in lines:
        # Encontrar las frases que empiezan con 'C' o 'A'
        match = re.search(r'\b(C|A)\w+.*', line)
        if match:
            street = match.group(0)  # Extraer la calle o avenida
            streets.append(street)
    
    return streets
    
    
@socketio.on('waypoint_dragged')
def handle_waypoint_dragged(data):
    waypoints = data['waypoints']
    print("Puntos de control actualizados:", waypoints)



# Ruta principal para servir la página
@app.route('/estadisticas')
def estadisticas():#valiendo verga
    return render_template('estadisticas.html')


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
