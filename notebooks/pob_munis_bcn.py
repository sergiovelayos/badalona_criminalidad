import pandas as pd

# Define el nombre del archivo de entrada y salida
filename_in = r"./data/poblacion_municipios_bcn_24.csv"
filename_out = './data/poblacion_municipios_bcn_24_limpiado.csv'

# 1. LEER EL CSV: Cambia la codificación a 'utf-8'
# El error original ('Ã³') es un síntoma claro de que un archivo UTF-8 se está leyendo como 'latin-1'
try:
    df = pd.read_csv(filename_in, encoding='utf-8', sep=';', header=0) # <<< CORREGIDO
except FileNotFoundError:
    print(f"Error: No se encontró el archivo en la ruta '{filename_in}'")
    exit()

# Asigna los nombres de las columnas. Asegúrate de que tu CSV original tiene 4 columnas sin nombre.
# Si la primera fila ya son los headers, puedes saltarte este paso o usar header=0 y luego df.rename()
df.columns = ['Municipios', 'Sexo', 'Periodo', 'Total']

# Convierte la columna 'Total' a numérica
# Tu lógica para limpiar los números es correcta (quitar puntos de miles, cambiar coma decimal)
df['Total'] = pd.to_numeric(
    df['Total'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False),
    errors='coerce'
)

# Filtra para quedarte solo con los datos totales del año 2024
df_filtered = df[(df['Sexo'] == 'Total') & (df['Periodo'] == 2024)].copy()

# Divide la columna 'Municipios' en código y nombre
# Usar .loc para asignar nuevas columnas es la forma correcta de evitar advertencias
df_filtered.loc[:, 'cod_mun'] = df_filtered['Municipios'].str.extract(r'(\b\d{5}\b)')
df_filtered.loc[:, 'nombre_mun'] = df_filtered['Municipios'].str.replace(r'^\d{5}\s*', '', regex=True).str.strip()

# 2. GUARDAR EL CSV: Usa 'utf-8-sig' para asegurar la compatibilidad
# 'utf-8-sig' añade una marca (BOM) al inicio del archivo que ayuda a programas como Excel
# a reconocer automáticamente que la codificación es UTF-8 y mostrar los acentos correctamente.
df_filtered.to_csv(filename_out, index=False, encoding='utf-8-sig') # <<< CORREGIDO

print(f"¡Proceso completado! Archivo guardado como '{filename_out}'")
print("\nPrimeras filas del resultado:")
print(df_filtered.head())