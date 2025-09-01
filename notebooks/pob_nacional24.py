import pandas as pd

# La ruta a tu archivo CSV
csv_file = r"./data/pobmun24.csv"

# Leemos el archivo directamente desde su ruta.
# OJO: Puede que tu archivo tenga problemas de codificación. Si da error, prueba añadir encoding='latin1' o encoding='utf-8'.
try:
    df = pd.read_csv(csv_file, sep=';', dtype={'CPRO': str, 'CMUN': str})
except Exception as e:
    print(f"Error inicial: {e}")
    print("Intentando leer con codificación 'latin1'...")
    df = pd.read_csv(csv_file, sep=';', dtype={'CPRO': str, 'CMUN': str}, encoding='latin1')


# --- Paso de depuración (muy recomendado) ---
# Imprime las primeras 5 filas y los nombres de las columnas para verificar que todo se ha leído bien.
print("Primeras 5 filas del DataFrame:")
print(df.head())
print("\nNombres de las columnas detectadas:")
print(df.columns)
# ---------------------------------------------


# 1. Creamos la nueva columna 'CP' uniendo 'CPRO' y 'CMUN'
df['cod_mun'] = df['CPRO'] + df['CMUN']

# 2. Eliminamos las columnas que no necesitas
df = df.drop(columns=['CPRO', 'CMUN', 'HOMBRES', 'MUJERES'])

# # Mostramos el DataFrame resultante
# print("\nDataFrame final:")
# print(df)

# Exportamos el DataFrame final a un nuevo archivo CSV
df.to_csv('./data/pobmun24_limpio.csv', index=False, sep=';')
print("Archivo CSV exportado correctamente a './data/pobmun24_limpio.csv'")