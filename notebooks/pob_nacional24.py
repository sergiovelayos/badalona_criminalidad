import pandas as pd

# La ruta a tu archivo CSV
# csv_file = r"./data/pobmun24.csv"

# Leer Excel File
excel_file = r"./data/pobmun/pobmunanual.xlsx"

df = pd.read_excel(excel_file, dtype={'CPRO': str, 'CMUN': str})

# print(f"Datos de población: {df.shape}", 
#       f"\n{df.head(3)}\n",
#       f"\n{df.info()}\n")

# Comprobar un municipio específico (opcional)
#  filtro = df['NOMBRE'] == 'Barberà del Vallès'
# print(df[filtro])


# --- Paso de depuración (muy recomendado) ---
# Imprime las primeras 5 filas y los nombres de las columnas para verificar que todo se ha leído bien.
# print("Primeras 5 filas del DataFrame:")
# print(df.head())
# print("\nNombres de las columnas detectadas:")
# print(df.columns)
# ---------------------------------------------


# 1. Creamos la nueva columna 'CP' uniendo 'CPRO' y 'CMUN'
df['cod_mun'] = df['CPRO'] + df['CMUN']

# 2. Eliminamos las columnas que no necesitas
df = df.drop(columns=['CPRO', 'CMUN', 'HOMBRES', 'MUJERES'])

# # Mostramos el DataFrame resultante
# print("\nDataFrame final:")
# print(df)

# Exportamos el DataFrame final a un nuevo archivo CSV
df.to_csv('./data/pobmunanual.csv', index=False, sep=';')
