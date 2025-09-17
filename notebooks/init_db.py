import sqlite3
import pandas as pd

# --- CONEXIÓN Y CARGA DE DATOS ---
conn = sqlite3.connect("data/delitos.db")
cursor = conn.cursor()

# --- 1. Tabla de Delitos ---
print("Cargando tabla 'delitos'...")
df_crimen = pd.read_csv("data/datos_criminalidad_webapp.csv", sep=",")
df_crimen.to_sql("delitos", conn, if_exists="replace", index=False)
print("Tabla 'delitos' cargada.")

# --- 2. Tabla de Población ---
print("Cargando tabla 'poblacion'...")
df_poblacion = pd.read_csv("data/pobmunanual.csv", sep=";")
df_poblacion.to_sql("poblacion", conn, if_exists="replace", index=False)
print("Tabla 'poblacion' cargada.")


# --- 3. CREACIÓN DE ÍNDICES PARA OPTIMIZAR CONSULTAS ---
print("Creando índices para acelerar las búsquedas...")

# Índice en la tabla de delitos para filtrar rápidamente por municipio y tipo
# Esto hace que la cláusula WHERE sea casi instantánea
cursor.execute("CREATE INDEX IF NOT EXISTS idx_delitos_municipio_tipo ON delitos (municipio, tipo_normalizado)")

# Índice en la tabla de población para acelerar el JOIN por código postal y año
# Fundamental para encontrar la población de un año específico rápidamente
cursor.execute("CREATE INDEX IF NOT EXISTS idx_poblacion_cod_mun_ano ON poblacion (cod_mun, AÑO)")

print("Índices creados con éxito.")


# --- CIERRE DE CONEXIÓN ---
conn.commit() # Guardar cambios (importante al ejecutar comandos con cursor)
conn.close()
print("\nBase de datos 'data/delitos.db' creada y optimizada correctamente.")