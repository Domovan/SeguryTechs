import re

# Texto de ejemplo
text = """
Head northeast on Calle Doctor Alberto del Valle
Turn right onto Avenida Fundición
Make a U-turn and continue on Avenida Fundición
Turn right onto Avenida Convención de 1914 Norte
Turn left onto Calle General Ignacio Zaragoza
You have arrived at your destination, on the right
"""

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

# Separar las calles/avenidas
streets = separate_by_street(text)

print("Calles/Avenidas detectadas:")
for street in streets:
    print(street)
