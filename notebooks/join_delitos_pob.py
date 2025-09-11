import pandas as pd
import re
# import os
# import seaborn as sns
# import matplotlib.pyplot as plt
# from io import StringIO

pd.set_option("display.max_columns", None)

# -----------------------
# Rutas
# -----------------------
f_delitos = r"./data/esp_geo_normalized.csv"               # separador ';', salta 1 fila
file_poblacion  = r"./data/pobmun24_limpio.csv"     # separador desconocido (auto)


# print(f"Población: {pob.shape}", 
#       f"\n{pob.head(3)}\n",
#       f"\n{pob.info()}\n")

delitos = pd.read_csv(f_delitos, sep="," )


# print(f"Población: {delitos.shape}", 
#       f"\n{delitos.head(3)}\n",
#       f"\n{delitos.info()}\n")



# -----------------------
# Lectura de datos
# -----------------------
# Leer el dataset de población
poblacion = pd.read_csv(file_poblacion, sep=";")

# # Mostrar información inicial
# print("=== INFORMACIÓN INICIAL ===")
# print(f"Registros de delitos: {len(delitos)}")
# print(f"Registros de población: {len(poblacion)}")
# print(f"Códigos postales únicos en población: {poblacion['cod_mun'].nunique()}")

# -----------------------
# Preparar datos de población para el mapeo
# -----------------------
# Crear diccionario código postal -> datos de población
# Convertir cod_mun a string con 5 dígitos (añadir ceros a la izquierda si es necesario)
poblacion['codigo_postal'] = poblacion['cod_mun'].astype(str).str.zfill(5)

# Crear el diccionario de mapeo
codigo_a_poblacion = {}
for _, row in poblacion.iterrows():
    codigo = row['codigo_postal']
    if codigo not in codigo_a_poblacion:  # Evitar duplicados
        codigo_a_poblacion[codigo] = {
            'provincia': row['PROVINCIA'],
            'municipio': row['municipios'], 
            'poblacion': row['POB24']
        }

# print(f"Se crearon {len(codigo_a_poblacion)} mapeos código postal -> población")

# -----------------------
# Función para extraer código postal de la columna geo
# -----------------------
def extraer_codigo_postal(geo_value):
    """Extrae el código postal de la columna geo si existe"""
    if pd.isna(geo_value):
        return None
    
    geo_str = str(geo_value)
    # Buscar patrón de 5 dígitos al inicio
    match = re.match(r"^(\d{5})", geo_str)
    if match:
        return match.group(1)
    else:
        return None

# -----------------------
# Aplicar el mapeo
# -----------------------
def mapear_poblacion(row):
    """Mapea los datos de población basándose en el código postal"""
    codigo_postal = extraer_codigo_postal(row['geo'])
    
    if codigo_postal and codigo_postal in codigo_a_poblacion:
        datos_poblacion = codigo_a_poblacion[codigo_postal]
        return pd.Series({
            'provincia': datos_poblacion['provincia'],
            'municipio_poblacion': datos_poblacion['municipio'],
            'poblacion_2024': datos_poblacion['poblacion'],
            'codigo_postal': codigo_postal,
            'tiene_poblacion': True
        })
    else:
        return pd.Series({
            'provincia': None,
            'municipio_poblacion': None,
            'poblacion_2024': None,
            'codigo_postal': codigo_postal,  # Puede ser None si no hay CP
            'tiene_poblacion': False
        })

# Aplicar el mapeo
# print("\n=== APLICANDO MAPEO ===")
datos_poblacion = delitos.apply(mapear_poblacion, axis=1)

# Unir con el dataframe original
delitos_con_poblacion = pd.concat([delitos, datos_poblacion], axis=1)

# # -----------------------
# # Verificaciones y estadísticas
# # -----------------------
# print("\n=== RESULTADOS ===")
# print(f"Registros finales: {len(delitos_con_poblacion)}")
# print(f"¿Se mantuvieron todos los registros?: {len(delitos_con_poblacion) == len(delitos)}")

# # Estadísticas del mapeo
# registros_con_poblacion = delitos_con_poblacion['tiene_poblacion'].sum()
# registros_sin_poblacion = len(delitos_con_poblacion) - registros_con_poblacion

# print(f"Registros con datos de población: {registros_con_poblacion}")
# print(f"Registros sin datos de población: {registros_sin_poblacion}")
# print(f"Porcentaje mapeado: {registros_con_poblacion/len(delitos_con_poblacion)*100:.1f}%")

# # Análisis de los registros sin mapear
# print(f"\n=== ANÁLISIS DE REGISTROS SIN MAPEAR ===")
# sin_poblacion = delitos_con_poblacion[~delitos_con_poblacion['tiene_poblacion']]

# # Tipos de registros sin mapear
# sin_cp = sin_poblacion[sin_poblacion['codigo_postal'].isna()]
# con_cp_sin_mapear = sin_poblacion[sin_poblacion['codigo_postal'].notna()]

# print(f"Registros sin código postal: {len(sin_cp)}")
# print(f"Registros con CP pero sin mapear: {len(con_cp_sin_mapear)}")

# # Ejemplos de registros sin código postal (provincias, comunidades, etc.)
# print(f"\nEjemplos de registros sin código postal (primeros 10):")
# ejemplos_sin_cp = sin_cp['geo'].value_counts().head(10)
# for geo, count in ejemplos_sin_cp.items():
#     print(f"  '{geo}': {count} registros")

# # Códigos postales que no se pudieron mapear
# if len(con_cp_sin_mapear) > 0:
#     print(f"\nCódigos postales sin mapear (primeros 10):")
#     cp_sin_mapear = con_cp_sin_mapear['codigo_postal'].value_counts().head(10)
#     for cp, count in cp_sin_mapear.items():
#         ejemplo_geo = con_cp_sin_mapear[con_cp_sin_mapear['codigo_postal'] == cp]['geo'].iloc[0]
#         print(f"  {cp} ('{ejemplo_geo}'): {count} registros")

# # -----------------------
# # Ejemplos de uniones exitosas
# # -----------------------
# print(f"\n=== EJEMPLOS DE UNIONES EXITOSAS ===")
# con_poblacion = delitos_con_poblacion[delitos_con_poblacion['tiene_poblacion']]
# ejemplos_exitosos = con_poblacion.groupby(['codigo_postal', 'geo', 'provincia', 'poblacion_2024']).size().head(5)

# for (cp, geo, provincia, pob), count in ejemplos_exitosos.items():
#     print(f"  CP {cp}: '{geo}' -> {provincia}, población: {pob:,.0f} ({count} registros)")

# # -----------------------
# # Verificación específica (ejemplo con un municipio conocido)
# # -----------------------
# print(f"\n=== VERIFICACIÓN ESPECÍFICA ===")
# # Buscar un ejemplo específico como Motril
# motril_filter = delitos_con_poblacion['geo'].str.contains('Motril', na=False)
# if motril_filter.any():
#     motril_example = delitos_con_poblacion[motril_filter].iloc[0]
#     print(f"Ejemplo Motril:")
#     print(f"  Geo: {motril_example['geo']}")
#     print(f"  Código Postal: {motril_example['codigo_postal']}")
#     print(f"  Provincia: {motril_example['provincia']}")
#     print(f"  Población 2024: {motril_example['poblacion_2024']}")
#     print(f"  Tiene población: {motril_example['tiene_poblacion']}")

# # Mostrar las columnas finales
# print(f"\n=== COLUMNAS FINALES ===")
# print("Columnas en el dataset final:")
# for col in delitos_con_poblacion.columns:
#     print(f"  - {col}")

# Opcional: guardar resultado
delitos_con_poblacion.to_csv("./data/delitos_con_poblacion.csv", index=False, encoding="utf-8")
# print(f"\n¡Proceso completado! Dataset listo para análisis.")
