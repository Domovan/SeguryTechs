import json
import random

# Leer el archivo JSON original
with open(r'C:\Users\hiram\OneDrive\Desktop\SeguryTechs\ubicaciones.json', 'r') as file:
    data = json.load(file)

# Agregar un nuevo parámetro "riesgo" con un número aleatorio entre 0 y 100
for colonia in data:
    colonia['riesgo'] = random.randint(0, 100)

# Guardar los datos modificados en un nuevo archivo
with open('colonias_modificado.json', 'w') as file:
    json.dump(data, file, indent=4)

print("El archivo con las modificaciones ha sido guardado como 'colonias_modificado.json'.")
