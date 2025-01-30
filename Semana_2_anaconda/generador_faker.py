# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 09:30:27 2025

@author: RentAdvisor
"""

from faker import Faker
import pandas as pd
import random

# Inicializar Faker
fake = Faker()

# Crear datos de ejemplo con más de 30 filas
data = {
    'Id': list(range(1, 32)),  # Generamos 31 ids
    'Nombre': [fake.first_name() for _ in range(31)],  # Generar 31 nombres
    'Apellido': [fake.last_name() for _ in range(31)],  # Generar 31 apellidos
    'Edad': [random.randint(20, 50) for _ in range(31)],  # Generar 31 edades aleatorias
    'Ciudad': [fake.city() for _ in range(31)],  # Generar 31 ciudades
    'Email': [fake.email() for _ in range(31)]  # Generar 31 correos electrónicos
}

# Crear un DataFrame de Pandas con los datos generados
df = pd.DataFrame(data)

# Guardar el DataFrame en un archivo CSV
df.to_csv('organizacion_faker.csv', index=False)

# Mostrar el DataFrame para ver cómo queda
print(df)