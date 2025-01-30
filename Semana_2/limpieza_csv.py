import pandas as pd
import requests
import numpy as np
from geopy.geocoders import Nominatim

#Lectura del CSV
archivo_cliente = pd.read_csv('clientes.csv')
print(archivo_cliente)

#Lectura de Excel
archivo_inventario = pd.read_excel('inventario_cliente.xlsx')
print(archivo_inventario)


# Leer el archivo CSV existente
archivo_limpieza = pd.read_csv('datos.csv', delimiter=';')

# Mostrar las primeras filas para ver la estructura
print("Datos originales:")
print(archivo_limpieza.head())


archivo_limpieza['Nombre'] = archivo_limpieza['Nombre'].fillna('Inválido')
archivo_limpieza['Apellido'] = archivo_limpieza['Apellido'].fillna('Inválido')

archivo_limpieza = archivo_limpieza[(archivo_limpieza['Nombre'] != 'Inválido') & (archivo_limpieza['Apellido'] != 'Inválido')]

archivo_limpieza['Edad'] = pd.to_numeric(archivo_limpieza['Edad'], errors='coerce')  # Convertir valores no numéricos a NaN
archivo_limpieza['Edad'] = archivo_limpieza['Edad'].apply(lambda x: abs(x) if pd.notna(x) else np.nan)  # Asegurarse de que sea positiva

archivo_limpieza = archivo_limpieza.dropna(subset=['Edad'])

archivo_limpieza['Año_Nacimiento'] = 2025 - archivo_limpieza['Edad']

geolocator = Nominatim(user_agent="city_to_country")

def obtener_pais(ciudad):
    try:
        location = geolocator.geocode(ciudad)
        if location:
            return location.raw.get('address', {}).get('country', 'Desconocido')
        else:
            return 'Desconocido'
    except Exception as e:
        return 'Desconocido'

archivo_limpieza['País'] = archivo_limpieza['Ciudad'].apply(obtener_pais)

# Generar el reporte consolidado (archivo CSV)
archivo_limpieza.to_csv('reporte_consolidado.csv', index=False)

# Mostrar el DataFrame limpio
print("\nDatos después de la limpieza:")
print(archivo_limpieza.head())
