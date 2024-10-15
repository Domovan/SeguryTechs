from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import json
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

socketio = SocketIO(app)


# Función para cargar datos desde un archivo JSON
def cargar_puntos_zonas():
    with open(r'C:\Users\hiram\OneDrive\Desktop\SeguryTechs\ubicaciones.json', 'r') as archivo:
        return json.load(archivo)

# Carga de los puntos de zonas
puntos_zonas = cargar_puntos_zonas()

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
def index():
    return render_template('index.html')

@socketio.on('mostrar_zonas_riesgo')
def handle_mostrar_zonas_riesgo():
    zonas_con_riesgo = []
    for colonia in puntos_zonas:
        nombre = colonia['nombre_colonia']
        lat = colonia['centro'][1]  # Latitud
        lng = colonia['centro'][0]  # Longitud
        riesgo = datos_riesgo.get(nombre, 0)  # Asignar riesgo, 0 si no está en datos_riesgo
        zonas_con_riesgo.append({'nombre': nombre, 'lat': lat, 'lng': lng, 'riesgo': riesgo})
    
    socketio.emit('zonas_riesgo', zonas_con_riesgo)

@socketio.on('search')
def handle_search(query):
    # Aquí va tu lógica de búsqueda
    results = [colonia for colonia in puntos_zonas if query.lower() in colonia['nombre_colonia'].lower()]
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
    print(calles_str + '\n')
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
def estadisticas():
    return render_template('estadisticas.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
