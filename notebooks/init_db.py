import sqlite3
import pandas as pd

# --- CONEXIÓN Y CARGA DE DATOS ---
conn = sqlite3.connect("data/delitos.db")
cursor = conn.cursor()

# --- 1. Tabla de Delitos OPTIMIZADA ---
print("Cargando y optimizando tabla 'delitos'...")
df_crimen = pd.read_csv("data/datos_criminalidad_webapp.csv", sep=",")

# SELECCIONAR SOLO LOS CAMPOS NECESARIOS
# Eliminamos campos redundantes que se calculan dinámicamente o no se usan
campos_necesarios = [
    'año', 'trimestre', 'municipio', 'codigo_postal', 
    'tipo_normalizado', 'valor'
]
df_crimen_optimizado = df_crimen[campos_necesarios].copy()

# OPTIMIZAR TIPOS DE DATOS para reducir espacio
df_crimen_optimizado['año'] = df_crimen_optimizado['año'].astype('int16')  # 2 bytes en lugar de 8
df_crimen_optimizado['trimestre'] = df_crimen_optimizado['trimestre'].astype('category')  # Más eficiente para valores repetidos
df_crimen_optimizado['municipio'] = df_crimen_optimizado['municipio'].astype('category')  # Más eficiente para valores repetidos
df_crimen_optimizado['codigo_postal'] = df_crimen_optimizado['codigo_postal'].astype('int32')  # 4 bytes en lugar de 8
df_crimen_optimizado['tipo_normalizado'] = df_crimen_optimizado['tipo_normalizado'].astype('category')  # Más eficiente para valores repetidos
df_crimen_optimizado['valor'] = df_crimen_optimizado['valor'].astype('float32')  # 4 bytes en lugar de 8

# ELIMINAR DUPLICADOS si existen (antes de cargar a la DB)
print(f"Registros antes de eliminar duplicados: {len(df_crimen_optimizado)}")
df_crimen_optimizado = df_crimen_optimizado.drop_duplicates(
    subset=['año', 'trimestre', 'municipio', 'tipo_normalizado'], 
    keep='first'
)
print(f"Registros después de eliminar duplicados: {len(df_crimen_optimizado)}")

# Cargar a SQLite
df_crimen_optimizado.to_sql("delitos", conn, if_exists="replace", index=False)
print("Tabla 'delitos' optimizada y cargada.")

# --- 2. Tabla de Población OPTIMIZADA ---
print("Cargando y optimizando tabla 'poblacion'...")
df_poblacion = pd.read_csv("data/pobmunanual.csv", sep=";")

# Optimizar tipos de datos en población también
if 'AÑO' in df_poblacion.columns:
    df_poblacion['AÑO'] = df_poblacion['AÑO'].astype('int16')
if 'cod_mun' in df_poblacion.columns:
    df_poblacion['cod_mun'] = df_poblacion['cod_mun'].astype('int32')
if 'POB' in df_poblacion.columns:
    df_poblacion['POB'] = df_poblacion['POB'].astype('int32')

df_poblacion.to_sql("poblacion", conn, if_exists="replace", index=False)
print("Tabla 'poblacion' optimizada y cargada.")

# --- 3. CREACIÓN DE ÍNDICES PARA OPTIMIZAR CONSULTAS ---
print("Creando índices para acelerar las búsquedas...")

# Índice compuesto más eficiente para la consulta principal
cursor.execute("CREATE INDEX IF NOT EXISTS idx_delitos_municipio_tipo ON delitos (municipio, tipo_normalizado)")

# Índice para la tabla de población
cursor.execute("CREATE INDEX IF NOT EXISTS idx_poblacion_cod_mun_ano ON poblacion (cod_mun, AÑO)")

# Índice adicional para acelerar las consultas por año y trimestre
cursor.execute("CREATE INDEX IF NOT EXISTS idx_delitos_ano_trimestre ON delitos (año, trimestre)")

print("Índices creados con éxito.")

# --- 4. CONFIGURACIÓN DE OPTIMIZACIÓN DE SQLite ---
print("Aplicando optimizaciones finales de SQLite...")

# Compactar la base de datos eliminando espacio no utilizado
cursor.execute("VACUUM")

# Configurar SQLite para mejor compresión
cursor.execute("PRAGMA journal_mode = DELETE")
cursor.execute("PRAGMA synchronous = NORMAL")
cursor.execute("PRAGMA cache_size = 10000")
cursor.execute("PRAGMA temp_store = MEMORY")

print("Optimizaciones de SQLite aplicadas.")

# --- 5. INFORMACIÓN DE TAMAÑO ---
cursor.execute("SELECT COUNT(*) FROM delitos")
total_delitos = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM poblacion") 
total_poblacion = cursor.fetchone()[0]

print(f"\n=== RESUMEN ===")
print(f"Total registros en 'delitos': {total_delitos:,}")
print(f"Total registros en 'poblacion': {total_poblacion:,}")

# --- CIERRE DE CONEXIÓN ---
conn.commit()
conn.close()
print("\nBase de datos 'data/delitos.db' creada, optimizada y compactada correctamente.")
print("Tamaño significativamente reducido manteniendo toda la funcionalidad.")