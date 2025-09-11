import pandas as pd
import re
import numpy as np

pd.set_option("display.max_columns", None)

# -----------------------
# Rutas
# -----------------------
f_delitos_pob = r"./data/delitos_con_poblacion.csv"

delitos_con_poblacion = pd.read_csv(f_delitos_pob, sep="," , dtype={'codigo_postal': str} )

# -----------------------
# Preparar datos para la webapp
# -----------------------

# Filtrar solo municipios con datos de población
datos_webapp = delitos_con_poblacion[delitos_con_poblacion['tiene_poblacion'] == True].copy()

# Calcular tasa de criminalidad por cada registro
datos_webapp['tasa_criminalidad_x1000'] = (datos_webapp['valor'] * 1000) / datos_webapp['poblacion_2024']

# Crear columna de código de provincia (2 primeros dígitos del código postal)
datos_webapp['codigo_provincia'] = datos_webapp['codigo_postal'].astype(str).str.zfill(5).str[:2]

# Seleccionar y renombrar columnas según especificación
datos_finales = datos_webapp[[
    'geo', 
    'año', 
    'trimestre', 
    'municipio_poblacion',  # renombrar a municipio
    'codigo_postal', 
    'poblacion_2024',       # renombrar a poblacion
    'tipo_normalizado', 
    'valor', 
    'tasa_criminalidad_x1000',
    'codigo_provincia'      # añadir para cálculos de promedio provincial
]].copy()

# Renombrar columnas
datos_finales.rename(columns={
    'municipio_poblacion': 'municipio',
    'poblacion_2024': 'poblacion'
}, inplace=True)

# Crear periodo año-trimestre para ordenamiento temporal
datos_finales['periodo'] = datos_finales['año'].astype(str) + '-' + datos_finales['trimestre']

# -----------------------
# Calcular promedios provinciales
# -----------------------
# Para cada provincia, año, trimestre y tipo de delito, calcular la tasa promedio
promedios_provinciales = datos_finales.groupby([
    'codigo_provincia', 
    'año', 
    'trimestre', 
    'tipo_normalizado'
])['tasa_criminalidad_x1000'].mean().reset_index()

promedios_provinciales.rename(columns={
    'tasa_criminalidad_x1000': 'tasa_promedio_provincial'
}, inplace=True)

# Unir los promedios provinciales con los datos principales
datos_finales = datos_finales.merge(
    promedios_provinciales,
    on=['codigo_provincia', 'año', 'trimestre', 'tipo_normalizado'],
    how='left'
)

print("=== DATOS PREPARADOS PARA WEBAPP ===")
print(f"Total de registros: {len(datos_finales):,}")
print(f"Municipios únicos: {datos_finales['municipio'].nunique():,}")
print(f"Tipos de delito únicos: {datos_finales['tipo_normalizado'].nunique()}")
print(f"Provincias únicas: {datos_finales['codigo_provincia'].nunique()}")
print(f"Rango de años: {datos_finales['año'].min()} - {datos_finales['año'].max()}")

print(f"\nColumnas en el dataset final:")
for col in datos_finales.columns:
    print(f"  - {col}")

print(f"\nPrimeras filas del dataset:")
print(datos_finales[['geo', 'año', 'trimestre', 'municipio', 'tipo_normalizado', 
                    'valor', 'tasa_criminalidad_x1000', 'tasa_promedio_provincial']].head())

# Opcional: Guardar para la webapp
datos_finales.to_csv("./data/datos_criminalidad_webapp.csv", index=False, encoding="utf-8")