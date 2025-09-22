# import sqlite3
# import pandas as pd

# # --- CONEXIÓN Y CARGA DE DATOS ---
# conn = sqlite3.connect("data/delitos.db")
# cursor = conn.cursor()

# # --- 1. Tabla de Delitos OPTIMIZADA ---
# print("Cargando y optimizando tabla 'delitos'...")
# df_crimen = pd.read_csv("data/datos_criminalidad_webapp.csv", sep=",")

# # SELECCIONAR SOLO LOS CAMPOS NECESARIOS
# # Eliminamos campos redundantes que se calculan dinámicamente o no se usan
# campos_necesarios = [
#     'año', 'trimestre', 'municipio', 'codigo_postal', 
#     'tipo_normalizado', 'valor'
# ]
# df_crimen_optimizado = df_crimen[campos_necesarios].copy()

# # OPTIMIZAR TIPOS DE DATOS para reducir espacio
# df_crimen_optimizado['año'] = df_crimen_optimizado['año'].astype('int16')  # 2 bytes en lugar de 8
# df_crimen_optimizado['trimestre'] = df_crimen_optimizado['trimestre'].astype('category')  # Más eficiente para valores repetidos
# df_crimen_optimizado['municipio'] = df_crimen_optimizado['municipio'].astype('category')  # Más eficiente para valores repetidos
# df_crimen_optimizado['codigo_postal'] = df_crimen_optimizado['codigo_postal'].astype('int32')  # 4 bytes en lugar de 8
# df_crimen_optimizado['tipo_normalizado'] = df_crimen_optimizado['tipo_normalizado'].astype('category')  # Más eficiente para valores repetidos
# df_crimen_optimizado['valor'] = df_crimen_optimizado['valor'].astype('float32')  # 4 bytes en lugar de 8

# # ELIMINAR DUPLICADOS si existen (antes de cargar a la DB)
# print(f"Registros antes de eliminar duplicados: {len(df_crimen_optimizado)}")
# df_crimen_optimizado = df_crimen_optimizado.drop_duplicates(
#     subset=['año', 'trimestre', 'municipio', 'tipo_normalizado'], 
#     keep='first'
# )
# print(f"Registros después de eliminar duplicados: {len(df_crimen_optimizado)}")

# # Cargar a SQLite
# df_crimen_optimizado.to_sql("delitos", conn, if_exists="replace", index=False)
# print("Tabla 'delitos' optimizada y cargada.")

# # --- 2. Tabla de Población OPTIMIZADA ---
# print("Cargando y optimizando tabla 'poblacion'...")
# df_poblacion = pd.read_csv("data/pobmunanual.csv", sep=";")

# # Optimizar tipos de datos en población también
# if 'AÑO' in df_poblacion.columns:
#     df_poblacion['AÑO'] = df_poblacion['AÑO'].astype('int16')
# if 'cod_mun' in df_poblacion.columns:
#     df_poblacion['cod_mun'] = df_poblacion['cod_mun'].astype('int32')
# if 'POB' in df_poblacion.columns:
#     df_poblacion['POB'] = df_poblacion['POB'].astype('int32')

# df_poblacion.to_sql("poblacion", conn, if_exists="replace", index=False)
# print("Tabla 'poblacion' optimizada y cargada.")

# # --- 3. CREACIÓN DE ÍNDICES PARA OPTIMIZAR CONSULTAS ---
# print("Creando índices para acelerar las búsquedas...")

# # Índice compuesto más eficiente para la consulta principal
# cursor.execute("CREATE INDEX IF NOT EXISTS idx_delitos_municipio_tipo ON delitos (municipio, tipo_normalizado)")

# # Índice para la tabla de población
# cursor.execute("CREATE INDEX IF NOT EXISTS idx_poblacion_cod_mun_ano ON poblacion (cod_mun, AÑO)")

# # Índice adicional para acelerar las consultas por año y trimestre
# cursor.execute("CREATE INDEX IF NOT EXISTS idx_delitos_ano_trimestre ON delitos (año, trimestre)")

# print("Índices creados con éxito.")

# # --- 4. CONFIGURACIÓN DE OPTIMIZACIÓN DE SQLite ---
# print("Aplicando optimizaciones finales de SQLite...")

# # Compactar la base de datos eliminando espacio no utilizado
# cursor.execute("VACUUM")

# # Configurar SQLite para mejor compresión
# cursor.execute("PRAGMA journal_mode = DELETE")
# cursor.execute("PRAGMA synchronous = NORMAL")
# cursor.execute("PRAGMA cache_size = 10000")
# cursor.execute("PRAGMA temp_store = MEMORY")

# print("Optimizaciones de SQLite aplicadas.")

# # --- 5. INFORMACIÓN DE TAMAÑO ---
# cursor.execute("SELECT COUNT(*) FROM delitos")
# total_delitos = cursor.fetchone()[0]
# cursor.execute("SELECT COUNT(*) FROM poblacion") 
# total_poblacion = cursor.fetchone()[0]

# print(f"\n=== RESUMEN ===")
# print(f"Total registros en 'delitos': {total_delitos:,}")
# print(f"Total registros en 'poblacion': {total_poblacion:,}")

# # --- CIERRE DE CONEXIÓN ---
# conn.commit()
# conn.close()
# print("\nBase de datos 'data/delitos.db' creada, optimizada y compactada correctamente.")
# print("Tamaño significativamente reducido manteniendo toda la funcionalidad.")




# =========== CLAUDE
import sqlite3
import pandas as pd
import os

# --- CONEXIÓN Y CARGA DE DATOS ---
conn = sqlite3.connect("data/delitos.db")
cursor = conn.cursor()

# --- 1. Tabla de Delitos OPTIMIZADA ---
print("Cargando y optimizando tabla 'delitos'...")

# Leer el archivo generado por el script anterior
df_delitos = pd.read_csv("data/delitos_armonizado_completo.csv", encoding='utf-8', low_memory=False)

print(f"Registros originales en delitos: {len(df_delitos):,}")

# Verificar las columnas disponibles
print("Columnas disponibles:", df_delitos.columns.tolist())

# Seleccionar campos necesarios basándose en la estructura real
campos_finales = [
    'año', 'trimestre', 'municipio', 'cp', 'valor', 
    'nivel', 'provincia', 'ccaa', 'periodo'
]

# Agregar tipo_normalizado si existe, sino usar 'tipo'
if 'tipo_normalizado' in df_delitos.columns:
    campos_finales.append('tipo_normalizado')
elif 'tipo' in df_delitos.columns:
    campos_finales.append('tipo')

# Verificar qué campos existen realmente
campos_existentes = [campo for campo in campos_finales if campo in df_delitos.columns]
print(f"Campos que se van a usar: {campos_existentes}")

df_delitos_optimizado = df_delitos[campos_existentes].copy()

# Renombrar columnas para consistencia si es necesario
if 'tipo' in df_delitos_optimizado.columns and 'tipo_normalizado' not in df_delitos_optimizado.columns:
    df_delitos_optimizado = df_delitos_optimizado.rename(columns={'tipo': 'tipo_normalizado'})
if 'cp' in df_delitos_optimizado.columns:
    df_delitos_optimizado = df_delitos_optimizado.rename(columns={'cp': 'codigo_postal'})

# OPTIMIZAR TIPOS DE DATOS para reducir espacio
print("Optimizando tipos de datos...")

# Convertir año y trimestre con manejo de errores
df_delitos_optimizado['año'] = pd.to_numeric(df_delitos_optimizado['año'], errors='coerce')
df_delitos_optimizado['trimestre'] = pd.to_numeric(df_delitos_optimizado['trimestre'], errors='coerce')

# Verificar rangos válidos antes de convertir tipos
años_validos = df_delitos_optimizado['año'].between(2000, 2030)
trimestres_validos = df_delitos_optimizado['trimestre'].between(1, 4)

# Contar valores inválidos solo donde no son NaN
años_invalidos = (~años_validos & df_delitos_optimizado['año'].notna()).sum()
trimestres_invalidos = (~trimestres_validos & df_delitos_optimizado['trimestre'].notna()).sum()

print(f"Años inválidos encontrados: {años_invalidos}")
print(f"Trimestres inválidos encontrados: {trimestres_invalidos}")

# Aplicar tipos optimizados con manejo de errores
try:
    df_delitos_optimizado['año'] = df_delitos_optimizado['año'].astype('Int16')
    print("Año convertido a Int16")
except Exception as e:
    print(f"Manteniendo año como float64 debido a: {e}")

try:
    df_delitos_optimizado['trimestre'] = df_delitos_optimizado['trimestre'].astype('Int8')
    print("Trimestre convertido a Int8")
except Exception as e:
    print(f"Manteniendo trimestre como float64 debido a: {e}")

# Resto de optimizaciones
if 'municipio' in df_delitos_optimizado.columns:
    df_delitos_optimizado['municipio'] = df_delitos_optimizado['municipio'].astype('category')

# Manejar código postal con cuidado
if 'codigo_postal' in df_delitos_optimizado.columns:
    try:
        df_delitos_optimizado['codigo_postal'] = pd.to_numeric(df_delitos_optimizado['codigo_postal'], errors='coerce').astype('Int32')
        print("Código postal convertido a Int32")
    except Exception as e:
        print(f"Problemas con codigo_postal: {e}")

if 'tipo_normalizado' in df_delitos_optimizado.columns:
    df_delitos_optimizado['tipo_normalizado'] = df_delitos_optimizado['tipo_normalizado'].astype('category')

df_delitos_optimizado['valor'] = pd.to_numeric(df_delitos_optimizado['valor'], errors='coerce').astype('float32')

if 'nivel' in df_delitos_optimizado.columns:
    df_delitos_optimizado['nivel'] = df_delitos_optimizado['nivel'].astype('category')
if 'provincia' in df_delitos_optimizado.columns:
    df_delitos_optimizado['provincia'] = df_delitos_optimizado['provincia'].astype('category') 
if 'ccaa' in df_delitos_optimizado.columns:
    df_delitos_optimizado['ccaa'] = df_delitos_optimizado['ccaa'].astype('category')
if 'periodo' in df_delitos_optimizado.columns:
    df_delitos_optimizado['periodo'] = df_delitos_optimizado['periodo'].astype('category')

print("Optimización de tipos completada")

# ELIMINAR DUPLICADOS si existen
print(f"Registros antes de eliminar duplicados: {len(df_delitos_optimizado):,}")

# Separar y limpiar duplicados por nivel
df_municipales = df_delitos_optimizado[df_delitos_optimizado['nivel'] == 'Municipal'].copy() if 'nivel' in df_delitos_optimizado.columns else pd.DataFrame()
df_no_municipales = df_delitos_optimizado[df_delitos_optimizado['nivel'] != 'Municipal'].copy() if 'nivel' in df_delitos_optimizado.columns else df_delitos_optimizado.copy()

# Definir subsets para duplicados según la disponibilidad de columnas
subset_municipios = ['año', 'trimestre', 'tipo_normalizado']
if 'codigo_postal' in df_delitos_optimizado.columns:
    subset_municipios.append('codigo_postal')
if 'municipio' in df_delitos_optimizado.columns:
    subset_municipios.append('municipio')

subset_otros = ['año', 'trimestre', 'tipo_normalizado']
if 'nivel' in df_delitos_optimizado.columns:
    subset_otros.append('nivel')
if 'provincia' in df_delitos_optimizado.columns:
    subset_otros.append('provincia')
if 'ccaa' in df_delitos_optimizado.columns:
    subset_otros.append('ccaa')

# Eliminar duplicados
if len(df_municipales) > 0:
    df_municipales = df_municipales.drop_duplicates(subset=subset_municipios, keep='first')

if len(df_no_municipales) > 0:
    df_no_municipales = df_no_municipales.drop_duplicates(subset=subset_otros, keep='first')

# Reunir
if len(df_municipales) > 0:
    df_delitos_optimizado = pd.concat([df_municipales, df_no_municipales], ignore_index=True)
else:
    df_delitos_optimizado = df_no_municipales

print(f"Registros después de eliminar duplicados: {len(df_delitos_optimizado):,}")

# Cargar a SQLite
df_delitos_optimizado.to_sql("delitos", conn, if_exists="replace", index=False)
print("Tabla 'delitos' optimizada y cargada.")

# --- 2. Tabla de Población OPTIMIZADA ---
print("Cargando y optimizando tabla 'poblacion'...")

# Intentar cargar el archivo de población
try:
    # Buscar el archivo de población (ajustar la ruta según tu estructura)
    archivos_poblacion_posibles = [
        "data/geo_master.csv"
    ]
    
    df_poblacion = None
    archivo_encontrado = None
    
    for archivo in archivos_poblacion_posibles:
        if os.path.exists(archivo):
            print(f"Intentando cargar: {archivo}")
            try:
                df_poblacion = pd.read_csv(archivo, sep=";", encoding='utf-8')
                archivo_encontrado = archivo
                break
            except:
                try:
                    df_poblacion = pd.read_csv(archivo, sep=",", encoding='utf-8') 
                    archivo_encontrado = archivo
                    break
                except:
                    continue
    
    if df_poblacion is None:
        print("ADVERTENCIA: No se encontró archivo de población. Creando tabla vacía.")
        # Crear estructura vacía basada en el formato esperado
        df_poblacion = pd.DataFrame(columns=[
            'AÑO', 'NIVEL', 'CODCCAA', 'CCAA', 'CPRO', 'PROVINCIA', 
            'CMUN', 'MUNICIPIO', 'POB'
        ])
    else:
        print(f"Archivo de población cargado: {archivo_encontrado}")
        print(f"Registros en población: {len(df_poblacion):,}")
        
        # Mostrar columnas disponibles en el archivo de población
        print("Columnas disponibles en población:", df_poblacion.columns.tolist())
        
        # Mostrar muestra de los datos
        print("\nPrimeras 5 filas de población:")
        print(df_poblacion.head())
    
    # Optimizar tipos de datos en población
    if len(df_poblacion) > 0:
        print("Optimizando tipos de datos de población...")
        
        # Ya conocemos la estructura exacta del archivo geo_master.csv
        try:
            # Convertir tipos de datos estándar
            df_poblacion['AÑO'] = pd.to_numeric(df_poblacion['AÑO'], errors='coerce').astype('Int16')
            df_poblacion['NIVEL'] = df_poblacion['NIVEL'].astype('category')
            
            # Manejar códigos que pueden estar vacíos
            if 'CODCCAA' in df_poblacion.columns:
                df_poblacion['CODCCAA'] = df_poblacion['CODCCAA'].astype('category')
            if 'CCAA' in df_poblacion.columns:
                df_poblacion['CCAA'] = df_poblacion['CCAA'].astype('category')
            if 'CPRO' in df_poblacion.columns:
                df_poblacion['CPRO'] = df_poblacion['CPRO'].astype('category')
            if 'PROVINCIA' in df_poblacion.columns:
                df_poblacion['PROVINCIA'] = df_poblacion['PROVINCIA'].astype('category')
            if 'CMUN' in df_poblacion.columns:
                df_poblacion['CMUN'] = df_poblacion['CMUN'].astype('category')
            if 'MUNICIPIO' in df_poblacion.columns:
                df_poblacion['MUNICIPIO'] = df_poblacion['MUNICIPIO'].astype('category')
                
            # Población como entero
            df_poblacion['POB'] = pd.to_numeric(df_poblacion['POB'], errors='coerce').astype('Int32')
            
            # Crear código postal para registros municipales
            def crear_cp_poblacion_simple(row):
                if (row['NIVEL'] == 'Municipal' and 
                    pd.notna(row.get('CPRO')) and pd.notna(row.get('CMUN')) and 
                    str(row.get('CPRO', '')).strip() != '' and str(row.get('CMUN', '')).strip() != ''):
                    try:
                        cpro = str(row['CPRO']).split('.')[0] if '.' in str(row['CPRO']) else str(row['CPRO'])
                        cmun = str(row['CMUN']).split('.')[0] if '.' in str(row['CMUN']) else str(row['CMUN'])
                        if cpro.isdigit() and cmun.isdigit():
                            return int(cpro.zfill(2) + cmun.zfill(3))
                    except:
                        pass
                return None
            
            df_poblacion['CODIGO_POSTAL'] = df_poblacion.apply(crear_cp_poblacion_simple, axis=1)
            
            print("Tipos de datos optimizados correctamente")
            
        except Exception as e:
            print(f"Error optimizando tipos de población: {e}")
            print("Continuando con tipos originales...")
        
        # Eliminar duplicados en población
        print(f"Registros población antes de eliminar duplicados: {len(df_poblacion):,}")
        
        try:
            # Separar por nivel para diferentes estrategias de dedup
            df_pob_municipal = df_poblacion[df_poblacion['NIVEL'] == 'Municipal'].copy()
            df_pob_provincial = df_poblacion[df_poblacion['NIVEL'] == 'Provincial'].copy()
            df_pob_autonomico = df_poblacion[df_poblacion['NIVEL'] == 'Autonómico'].copy()
            df_pob_nacional = df_poblacion[df_poblacion['NIVEL'] == 'Nacional'].copy()
            
            # Eliminar duplicados por nivel
            if len(df_pob_municipal) > 0:
                df_pob_municipal = df_pob_municipal.drop_duplicates(
                    subset=['AÑO', 'CPRO', 'CMUN'], keep='first'
                )
            
            if len(df_pob_provincial) > 0:
                df_pob_provincial = df_pob_provincial.drop_duplicates(
                    subset=['AÑO', 'CPRO'], keep='first'
                )
                
            if len(df_pob_autonomico) > 0:
                df_pob_autonomico = df_pob_autonomico.drop_duplicates(
                    subset=['AÑO', 'CODCCAA'], keep='first'
                )
                
            if len(df_pob_nacional) > 0:
                df_pob_nacional = df_pob_nacional.drop_duplicates(
                    subset=['AÑO'], keep='first'
                )
            
            # Reunir todos los dataframes
            dfs_poblacion = [df for df in [df_pob_municipal, df_pob_provincial, df_pob_autonomico, df_pob_nacional] if len(df) > 0]
            if dfs_poblacion:
                df_poblacion = pd.concat(dfs_poblacion, ignore_index=True)
            
        except Exception as e:
            print(f"Error eliminando duplicados: {e}")
            # Fallback básico
            df_poblacion = df_poblacion.drop_duplicates(keep='first')
        
        print(f"Registros población después de eliminar duplicados: {len(df_poblacion):,}")
        print(f"Distribución por nivel: \n{df_poblacion['NIVEL'].value_counts()}")

    # Cargar población a SQLite
    df_poblacion.to_sql("poblacion", conn, if_exists="replace", index=False)
    print("Tabla 'poblacion' optimizada y cargada.")

except Exception as e:
    print(f"Error al procesar población: {e}")
    print("Creando tabla de población vacía...")
    df_poblacion_vacia = pd.DataFrame(columns=[
        'AÑO', 'NIVEL', 'CODCCAA', 'CCAA', 'CPRO', 'PROVINCIA', 
        'CMUN', 'MUNICIPIO', 'POB', 'CODIGO_POSTAL'
    ])
    df_poblacion_vacia.to_sql("poblacion", conn, if_exists="replace", index=False)

# --- 3. CREACIÓN DE ÍNDICES PARA OPTIMIZAR CONSULTAS ---
print("Creando índices para acelerar las búsquedas...")

# Índices para la tabla de delitos
cursor.execute("CREATE INDEX IF NOT EXISTS idx_delitos_codigo_postal_año ON delitos (codigo_postal, año)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_delitos_año_trimestre ON delitos (año, trimestre)")

if 'municipio' in df_delitos_optimizado.columns and 'tipo_normalizado' in df_delitos_optimizado.columns:
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_delitos_municipio_tipo ON delitos (municipio, tipo_normalizado)")
    
if 'nivel' in df_delitos_optimizado.columns:
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_delitos_nivel ON delitos (nivel)")
    
if 'provincia' in df_delitos_optimizado.columns:
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_delitos_nivel_provincia ON delitos (nivel, provincia)")
    
if 'ccaa' in df_delitos_optimizado.columns:
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_delitos_nivel_ccaa ON delitos (nivel, ccaa)")

# Índices para la tabla de población
cursor.execute("CREATE INDEX IF NOT EXISTS idx_poblacion_codigo_postal_año ON poblacion (CODIGO_POSTAL, AÑO)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_poblacion_provincia_año ON poblacion (PROVINCIA, AÑO)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_poblacion_ccaa_año ON poblacion (CCAA, AÑO)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_poblacion_nivel_año ON poblacion (NIVEL, AÑO)")

print("Índices creados con éxito.")

# --- 4. CONFIGURACIÓN DE OPTIMIZACIÓN DE SQLite ---
print("Aplicando optimizaciones finales de SQLite...")

# Compactar la base de datos eliminando espacio no utilizado
cursor.execute("VACUUM")

# Configurar SQLite para mejor rendimiento
cursor.execute("PRAGMA journal_mode = WAL")  # WAL es mejor que DELETE para concurrencia
cursor.execute("PRAGMA synchronous = NORMAL")
cursor.execute("PRAGMA cache_size = 10000")
cursor.execute("PRAGMA temp_store = MEMORY")

print("Optimizaciones de SQLite aplicadas.")

# --- 5. CREAR VISTAS ÚTILES ---
print("Creando vistas útiles para consultas...")

# Vista para delitos con población (solo municipales)
cursor.execute("""
CREATE VIEW IF NOT EXISTS delitos_con_poblacion AS
SELECT 
    d.año,
    d.trimestre,
    d.municipio,
    d.codigo_postal,
    d.provincia,
    d.ccaa,
    d.tipo_normalizado,
    d.valor as delitos,
    p.POB as poblacion,
    CASE 
        WHEN p.POB > 0 THEN (d.valor * 100000.0 / p.POB)
        ELSE NULL 
    END as tasa_por_100k
FROM delitos d
LEFT JOIN poblacion p ON d.codigo_postal = p.CODIGO_POSTAL AND d.año = p.AÑO
WHERE d.nivel = 'Municipal'
""")

# Vista resumen por provincia
cursor.execute("""
CREATE VIEW IF NOT EXISTS resumen_provincial AS
SELECT 
    año,
    trimestre,
    provincia,
    tipo_normalizado,
    SUM(valor) as total_delitos,
    COUNT(DISTINCT municipio) as num_municipios
FROM delitos 
WHERE nivel = 'Municipal' AND provincia IS NOT NULL
GROUP BY año, trimestre, provincia, tipo_normalizado
""")

print("Vistas creadas con éxito.")

# --- 6. INFORMACIÓN DE TAMAÑO ---
cursor.execute("SELECT COUNT(*) FROM delitos")
total_delitos = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM poblacion") 
total_poblacion = cursor.fetchone()[0]

# Estadísticas adicionales
municipios_unicos = 0
if 'municipio' in df_delitos_optimizado.columns:
    cursor.execute("SELECT COUNT(DISTINCT municipio) FROM delitos WHERE nivel = 'Municipal'")
    result = cursor.fetchone()
    municipios_unicos = result[0] if result else 0

tipos_delito = 0
if 'tipo_normalizado' in df_delitos_optimizado.columns:
    cursor.execute("SELECT COUNT(DISTINCT tipo_normalizado) FROM delitos")
    result = cursor.fetchone()
    tipos_delito = result[0] if result else 0

cursor.execute("SELECT MIN(año), MAX(año) FROM delitos WHERE año IS NOT NULL")
rango_años = cursor.fetchone()

print(f"\n=== RESUMEN ===")
print(f"Total registros en 'delitos': {total_delitos:,}")
print(f"Total registros en 'poblacion': {total_poblacion:,}")
print(f"Municipios únicos: {municipios_unicos:,}")
print(f"Tipos de delito: {tipos_delito:,}")
if rango_años[0] and rango_años[1]:
    print(f"Rango de años: {rango_años[0]} - {rango_años[1]}")

# Verificar integridad de las claves de unión
cursor.execute("""
SELECT COUNT(*) as municipios_sin_poblacion 
FROM delitos d 
LEFT JOIN poblacion p ON d.codigo_postal = p.CODIGO_POSTAL AND d.año = p.AÑO
WHERE d.nivel = 'Municipal' AND p.CODIGO_POSTAL IS NULL
""")
sin_poblacion = cursor.fetchone()[0]
print(f"Registros municipales sin datos de población: {sin_poblacion:,}")

# --- CIERRE DE CONEXIÓN ---
conn.commit()
conn.close()

print(f"\nBase de datos 'data/delitos.db' creada y optimizada correctamente.")
print("Tablas creadas: 'delitos' y 'poblacion'")
print("Vistas creadas: 'delitos_con_poblacion' y 'resumen_provincial'")
print("¡Listo para usar en aplicaciones web o análisis!")