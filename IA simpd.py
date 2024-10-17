from flask import Flask, render_template_string, request
import pandas as pd
import folium
import matplotlib.pyplot as plt
import io
import base64
import mysql.connector

# Inicializar la aplicación Flask
app = Flask(__name__)

# Configuración de la conexión a la base de datos
db_config = {
    'host': 'localhost',  # Cambiado a 'localhost' ya que es tu usuario
    'user': 'root',       # Cambiado a 'root' ya que es tu usuario
    'password': '',  # Manteniendo tu contraseña
    'database': 'zona_de_riesgo'  # Cambia esto por tu nombre de base de datos
}

# Crear la conexión a la base de datos
def obtener_conexion():
    return mysql.connector.connect(**db_config)

def crear_base_de_datos():
    """Crea la base de datos y las tablas si no existen."""
    conexion = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password']
    )
    cursor = conexion.cursor()
    
    # Crear base de datos
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
    cursor.execute(f"USE {db_config['database']}")

    # Crear tabla 'zonas'
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS zonas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            riesgo INT NOT NULL,
            latitud FLOAT NOT NULL,
            longitud FLOAT NOT NULL
        )
    ''')

    # Crear tabla 'graficas' con columna imagen como TEXT
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS graficas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            opcion INT NOT NULL,
            imagen TEXT NOT NULL  -- Cambiado a TEXT para almacenar imágenes en base64
        )
    ''')
    
    cursor.close()
    conexion.close()

def cargar_zonas_a_db():
    """Carga las zonas de riesgo en la base de datos."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    PUNTOS_ZONAS = {
        "centro": (21.8842637, -102.3134514),
        "san marcos barrio": (21.8818817, -102.3122746),
        "americas las fracc.": (21.8173776, -102.1151153),
        "municipio libre fracc.": (21.8954463, -102.2689912),
        "haciendas de aguascalientes fracc.": (21.8883146, -102.2533752),
        "morelos i fracc.": (21.8559395, -102.269382),
        "gremial col.": (21.8953131, -102.2984856),
        "ojocaliente i fracc.": (21.8851666, -102.2591437),
        "flores las col.": (21.8965786, -102.2835921),
        "pilar blanco infonavit": (21.8501643, -102.3074635),
        "san cayetano fracc.": (21.8989515, -102.3144822),
        "insurgentes col. (las huertas)": (21.851145, -102.315225),
        "guadalupe de barrio": (21.8860278, -102.3089169),
        "morelos infonavit": (21.862874, -102.2654909),
        "circunvalación norte fracc.": (21.8992303, -102.3053105),
        "san marcos col.": (21.8787032, -102.3307405),
        "rodolfo landeros fracc.": (21.9015364, -102.2580932),
        "obraje col.": (21.8734586, -102.3032229),
        "santa anita 1era secc. fracc.": (21.896521, -102.2824202),
        "trabajo del col.": (21.8696268, -102.2471416),
        "jose guadalupe peralta fracc.": (21.8695216, -102.2423444),
        "dorado el 1era secc. fracc.": (21.8615633, -102.3105411),
        "purisima la barrio": (21.8837164, -102.2900327),
        "ojocaliente iii fracc.": (21.8783716, -102.2513738),
        "colinas del rio fracc.": (21.8952314, -102.3261915),
        "espana fracc.": (21.8655335, -102.316369),
        "industrial col.": (21.896001, -102.2994408),
        "arboledas las fracc.": (21.962825, -102.305393),
        "villas de ntra. sra. de la asuncion sec estacion fracc.": (21.9287349, -102.2689383),
        "bosques del prado sur fracc.": (21.9172782, -102.3142545)
    }

    # Puedes ajustar los niveles de riesgo según tus necesidades
    DATOS_RIESGO = {
        "centro": 60,
        "san marcos barrio": 55,
        "americas las fracc.": 45,
        "municipio libre fracc.": 50,
        "haciendas de aguascalientes fracc.": 40,
        "morelos i fracc.": 35,
        "gremial col.": 30,
        "ojocaliente i fracc.": 30,
        "flores las col.": 20,
        "pilar blanco infonavit": 25,
        "san cayetano fracc.": 45,
        "insurgentes col. (las huertas)": 35,
        "guadalupe de barrio": 50,
        "morelos infonavit": 30,
        "circunvalación norte fracc.": 40,
        "san marcos col.": 55,
        "rodolfo landeros fracc.": 65,
        "obraje col.": 40,
        "santa anita 1era secc. fracc.": 50,
        "trabajo del col.": 35,
        "jose guadalupe peralta fracc.": 30,
        "dorado el 1era secc. fracc.": 20,
        "purisima la barrio": 25,
        "ojocaliente iii fracc.": 40,
        "colinas del rio fracc.": 60,
        "espana fracc.": 55,
        "industrial col.": 35,
        "arboledas las fracc.": 45,
        "villas de ntra. sra. de la asuncion sec estacion fracc.": 50,
        "bosques del prado sur fracc.": 35
    }

    # Limpiar la tabla antes de insertar datos
    cursor.execute("DELETE FROM zonas")

    for zona, coords in PUNTOS_ZONAS.items():
        riesgo = DATOS_RIESGO[zona]
        query = "INSERT INTO zonas (nombre, riesgo, latitud, longitud) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (zona, riesgo, coords[0], coords[1]))

    conexion.commit()
    cursor.close()
    conexion.close()

@app.route('/')
def index():
    return render_template_string(''' 
        <html>
            <head>
                <title>SIMPD - Mapa de Riesgo</title>
                <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
                <style>
                    body {
                        font-family: 'Roboto', sans-serif;
                        background-color: #f0f4f8;
                        color: #333;
                        text-align: center;
                        padding: 30px;
                        margin: 0;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }
                    h1 {
                        color: #4A90E2;
                        font-size: 2.5em;
                        margin-bottom: 10px;
                        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
                    }
                    h2 {
                        color: #E94E77;
                        font-size: 1.5em;
                        margin-bottom: 20px;
                    }
                    select, button {
                        padding: 12px;
                        margin: 10px 0;
                        border: 2px solid #4A90E2;
                        border-radius: 5px;
                        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
                        font-size: 1em;
                        transition: background-color 0.3s, border-color 0.3s;
                    }
                    button {
                        background-color: #4A90E2;
                        color: white;
                        cursor: pointer;
                    }
                    button:hover {
                        background-color: #357ABD;
                        border-color: #357ABD;
                    }
                    a {
                        color: #4A90E2;
                        text-decoration: none;
                    }
                    a:hover {
                        text-decoration: underline;
                    }
                </style>
            </head>
            <body>
                <h1>Sistema de Monitoreo de Puntos de Riesgo</h1>
                <h2><a href="/mapa" target="_blank">Ver Mapa de Riesgo</a></h2>
                <h2>Seleccionar Gráfica</h2>
                <form action="/grafica" method="POST">
                    <select name="opcion">
                        <option value="1">Gráfica 1: Nivel de Riesgo por Zona</option>
                        <option value="2">Gráfica 2: Proporción de Zonas en Diferentes Niveles de Riesgo</option>
                        <option value="3">Gráfica 3: Histograma de Niveles de Riesgo</option>
                    </select>
                    <button type="submit">Ver Gráfica</button>
                </form>
            </body>
        </html>
    ''')

@app.route('/mapa')
def mapa():
    """Visualiza un mapa con las zonas de riesgo y lo devuelve como HTML."""
    mapa = folium.Map(location=[21.8853, -102.2920], zoom_start=13)

    # Conectar a la base de datos y obtener zonas
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre, riesgo, latitud, longitud FROM zonas")
    zonas = cursor.fetchall()
    cursor.close()
    conexion.close()

    # Añadir marcadores al mapa
    for zona in zonas:
        nombre, riesgo, latitud, longitud = zona
        color, nivel_riesgo = asignar_color_riesgo(riesgo)

        folium.CircleMarker(
            location=(latitud, longitud),
            radius=8,
            color=color,
            fill=True,
            fill_opacity=0.6,
            popup=f"<strong>{nombre.capitalize()}</strong><br>Nivel de Riesgo: {nivel_riesgo} (Riesgo: {riesgo})",
            fill_color=color
        ).add_to(mapa)

    # Generar el mapa como HTML
    mapa_html = mapa._repr_html_()
    return render_template_string(''' 
        <html>
            <head>
                <title>Mapa de Riesgo</title>
                <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
                <style>
                    body {
                        font-family: 'Roboto', sans-serif;
                        background-color: #f0f4f8;
                        color: #333;
                        text-align: center;
                        padding: 20px;
                    }
                    h1 {
                        color: #4A90E2;
                    }
                    a {
                        color: #4A90E2;
                    }
                    a:hover {
                        text-decoration: underline;
                    }
                </style>
            </head>
            <body>
                <h1>Mapa de Riesgo</h1>
                {{ mapa_html | safe }}
                <br>
                <a href="/">Volver al Menú</a>
            </body>
        </html>
    ''', mapa_html=mapa_html)

def asignar_color_riesgo(riesgo):
    """Asigna un color y nivel de riesgo basado en el valor del riesgo."""
    if riesgo >= 60:
        return 'red', 'Alto'
    elif 40 <= riesgo < 60:
        return 'orange', 'Moderado'
    else:
        return 'green', 'Bajo'

@app.route('/grafica', methods=['POST'])
def grafica():
    opcion = int(request.form.get('opcion'))
    img = graficar_datos(opcion)
    
    # Guardar la imagen en la base de datos
    guardar_grafica(opcion, img)
    
    return render_template_string(''' 
        <html>
            <head>
                <title>Gráfica {{ opcion }}</title>
                <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
                <style>
                    body {
                        font-family: 'Roboto', sans-serif;
                        background-color: #f0f4f8;
                        color: #333;
                        text-align: center;
                        padding: 20px;
                    }
                    h1 {
                        color: #4A90E2;
                    }
                    img {
                        max-width: 90%;
                        height: auto;
                        border: 2px solid #E94E77;
                        border-radius: 5px;
                        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
                    }
                    a {
                        color: #4A90E2;
                        text-decoration: none;
                    }
                    a:hover {
                        text-decoration: underline;
                    }
                </style>
            </head>
            <body>
                <h1>Gráfica {{ opcion }}</h1>
                <img src="data:image/png;base64,{{ img }}" alt="Gráfica">
                <br>
                <a href="/">Volver al Menú</a>
            </body>
        </html>
    ''', img=img, opcion=opcion)

def graficar_datos(opcion):
    """Genera gráficas basadas en la opción seleccionada y devuelve la imagen en base64."""
    plt.clf()  # Limpiar la figura actual
    
    # Conectar a la base de datos y obtener zonas
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre, riesgo FROM zonas")
    datos = cursor.fetchall()
    cursor.close()
    conexion.close()
    
    nombres = [d[0] for d in datos]
    riesgos = [d[1] for d in datos]

    if opcion == 1:
        # Gráfica 1: Nivel de Riesgo por Zona
        plt.figure(figsize=(10, 5))
        plt.bar(nombres, riesgos, color='lightblue')
        plt.axhline(y=50, color='red', linestyle='--', label='Umbral de Riesgo')
        plt.title('Nivel de Riesgo por Zona - Gráfica 1')
        plt.xlabel('Zonas')
        plt.ylabel('Nivel de Riesgo')
        plt.xticks(rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
    elif opcion == 2:
        # Gráfica 2: Proporción de Zonas en Diferentes Niveles de Riesgo
        niveles_riesgo = pd.cut(riesgos, bins=[0, 40, 60, 100], labels=['Bajo', 'Moderado', 'Alto'])
        conteo_niveles = niveles_riesgo.value_counts()
        plt.figure(figsize=(8, 6))
        plt.pie(conteo_niveles, labels=conteo_niveles.index, autopct='%1.1f%%', startangle=90)
        plt.title('Proporción de Zonas en Diferentes Niveles de Riesgo - Gráfica 2')
        plt.axis('equal')  # Para que el pie sea un círculo
    elif opcion == 3:
        # Gráfica 3: Histogramas de Niveles de Riesgo
        plt.figure(figsize=(10, 5))
        plt.hist(riesgos, bins=[0, 20, 40, 60, 80, 100], color='blue', alpha=0.7)
        plt.title('Histograma de Niveles de Riesgo - Gráfica 3')
        plt.xlabel('Nivel de Riesgo')
        plt.ylabel('Frecuencia')
        plt.xticks([0, 20, 40, 60, 80, 100])
        plt.grid(axis='y')
    
    # Guardar la imagen en un objeto BytesIO
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()  # Cerrar la figura
    buf.seek(0)
    img = base64.b64encode(buf.getvalue()).decode('utf8')  # Convertir a base64
    return img

def guardar_grafica(opcion, img_base64):
    """Guarda la gráfica en la base de datos."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    query = "INSERT INTO graficas (opcion, imagen) VALUES (%s, %s)"
    cursor.execute(query, (opcion, img_base64))
    conexion.commit()
    cursor.close()
    conexion.close()

if __name__ == "__main__":
    crear_base_de_datos()  # Crear base de datos y tablas al iniciar la app
    cargar_zonas_a_db()  # Cargar zonas en la base de datos al iniciar la app
    app.run(debug=True)

