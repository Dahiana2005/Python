import pandas as pd

# Crear una Serie
prueba_siere = pd.Series([10, 20, 30, 40])
print(prueba_siere)

# Crear un DataFrame
datos = {
    "Nombre": ["Ana", "Carlos", "Luisa", "Pedro"],
    "Edad": [23, 45, 34, 28],
    "Ciudad": ["Madrid", "Barcelona", "Sevilla", "Valencia"]
}
print(datos)

#Procesar CSV con Pandas
procesar_archivo = pd.read_csv('datos_prueba.csv')

print(procesar_archivo.head(10)) 