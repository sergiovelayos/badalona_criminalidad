import pandas as pd
import re

# --- Datos de relación CCAA <-> Provincia ---
mapping_data = """
CODAUTO Comunidad Autónoma CPRO Provincia
01 Andalucía 04 Almería
01 Andalucía 11 Cádiz
01 Andalucía 14 Córdoba
01 Andalucía 18 Granada
01 Andalucía 21 Huelva
01 Andalucía 23 Jaén
01 Andalucía 29 Málaga
01 Andalucía 41 Sevilla
02 Aragón 22 Huesca
02 Aragón 44 Teruel
02 Aragón 50 Zaragoza
03 Asturias, Principado de 33 Asturias
04 Balears, Illes 07 Balears, Illes
05 Canarias 35 Palmas, Las
05 Canarias 38 Santa Cruz de Tenerife
06 Cantabria 39 Cantabria
07 Castilla y León 05 Ávila
07 Castilla y León 09 Burgos
07 Castilla y León 24 León
07 Castilla y León 34 Palencia
07 Castilla y León 37 Salamanca
07 Castilla y León 40 Segovia
07 Castilla y León 42 Soria
07 Castilla y León 47 Valladolid
07 Castilla y León 49 Zamora
08 Castilla-La Mancha 02 Albacete
08 Castilla-La Mancha 13 Ciudad Real
08 Castilla-La Mancha 16 Cuenca
08 Castilla-La Mancha 19 Guadalajara
08 Castilla-La Mancha 45 Toledo
09 Cataluña 08 Barcelona
09 Cataluña 17 Girona
09 Cataluña 25 Lleida
09 Cataluña 43 Tarragona
10 Comunitat Valenciana 03 Alicante/Alacant
10 Comunitat Valenciana 12 Castellón/Castelló
10 Comunitat Valenciana 46 Valencia/València
11 Extremadura 06 Badajoz
11 Extremadura 10 Cáceres
12 Galicia 15 Coruña, A
12 Galicia 27 Lugo
12 Galicia 32 Ourense
12 Galicia 36 Pontevedra
13 Madrid, Comunidad de 28 Madrid
14 Murcia, Región de 30 Murcia
15 Navarra, Comunidad Foral de 31 Navarra
16 País Vasco 01 Araba/Álava
16 País Vasco 48 Bizkia
16 País Vasco 20 Gipuzkoa
17 Rioja, La 26 Rioja, La
18 Ceuta 51 Ceuta
19 Melilla 52 Melilla
"""

# Parsear manualmente con regex
rows = []
for line in mapping_data.strip().splitlines()[1:]:
    match = re.match(r"(\d{2})\s+(.*?)\s+(\d{2})\s+(.*)", line)
    if match:
        rows.append(match.groups())

df_relaciones = pd.DataFrame(rows, columns=["CODCCAA", "CCAA", "CPRO", "PROVINCIA"])
df_relaciones['CPRO'] = df_relaciones['CPRO'].str.strip().str.zfill(2)

# --- Leer Excel con población ---
excel_file = r"./data/pobmun/pobmunanual.xlsx"
df = pd.read_excel(excel_file, dtype={'CPRO': str, 'CMUN': str})

# --- CORRECCIÓN ---
# Normalizar los nombres de columna del Excel ANTES del merge
# Así nos aseguramos de que la columna de provincia se llame 'PROVINCIA'
df.rename(columns={
    'NOMBRE': 'MUNICIPIO',
    'NOM_MUN': 'MUNICIPIO',
    'Nombre': 'MUNICIPIO',
    'Provincia': 'PROVINCIA' # Estandarizar nombre si viene en mayúscula/minúscula
}, inplace=True)

# Limpiar y estandarizar la columna CPRO
df['CPRO'] = df['CPRO'].str.strip().str.zfill(2)

# --- SOLUCIÓN DEFINITIVA: Eliminar la columna de provincia del Excel ANTES del merge ---
if 'PROVINCIA' in df.columns:
    df = df.drop(columns=['PROVINCIA'])

# Crear CP (CPRO + CMUN)
df['CP'] = df['CPRO'] + df['CMUN']

# Eliminar columnas innecesarias si existen
for col in ['HOMBRES', 'MUJERES']:
    if col in df.columns:
        df = df.drop(columns=[col])

# Merge con info de CCAA y Provincia
# Ahora ya no habrá conflicto y se creará una única columna 'PROVINCIA'
df_final = pd.merge(
    df,
    df_relaciones[['CODCCAA', 'CCAA', 'CPRO', 'PROVINCIA']],
    on='CPRO',
    how='left'
)

# Reordenar columnas (esta línea ya funcionará)
df_final = df_final[['CODCCAA', 'CCAA', 'CPRO', 'PROVINCIA', 'CMUN','CP', 'MUNICIPIO', 'POB', 'AÑO']]

# --- Cálculo adicional: población por provincia ---
poblacion_por_prov = df_final.groupby(['AÑO', 'CPRO', 'PROVINCIA'])['POB'].sum().reset_index()

# --- Cálculo adicional: población por comunidad autónoma ---
poblacion_por_ccaa = df_final.groupby(['AÑO', 'CODCCAA', 'CCAA'])['POB'].sum().reset_index()

# --- Cálculo adicional: población nacional ---
poblacion_nacional = df_final.groupby('AÑO')['POB'].sum().reset_index()

# # Mostrar tablas
# print("\n=== DataFrame completo (municipios) ===")
# print(df_final.head())

# print("\n=== Población por Provincia ===")
# print(poblacion_por_prov.head())

# print("\n=== Población por CCAA ===")
# print(poblacion_por_ccaa.head())

# print("\n=== Población Nacional ===")
# print(poblacion_nacional.head())




# --- 2. Creación del DataFrame Consolidado ---

# Preparar cada DataFrame para la unión, añadiendo la columna 'NIVEL'

# Nivel Municipal
df_municipal = df_final.copy()
df_municipal['NIVEL'] = 'Municipal'

# Nivel Provincial (necesitamos añadirle la info de CCAA que le falta)
df_provincial = poblacion_por_prov.copy()
df_provincial['NIVEL'] = 'Provincial'
# Usamos el df_relaciones para obtener el código y nombre de la CCAA para cada provincia
mapa_ccaa = df_relaciones[['CPRO', 'CODCCAA', 'CCAA']].drop_duplicates()
df_provincial = pd.merge(df_provincial, mapa_ccaa, on='CPRO', how='left')


# Nivel Autonómico
df_autonomico = poblacion_por_ccaa.copy()
df_autonomico['NIVEL'] = 'Autonómico'

# Nivel Nacional
df_nacional = poblacion_nacional.copy()
df_nacional['NIVEL'] = 'Nacional'

# Concatenar (apilar) todos los DataFrames en uno solo
df_consolidado = pd.concat([
    df_municipal,
    df_provincial,
    df_autonomico,
    df_nacional
], ignore_index=True)


# --- 3. Limpieza y Ordenación del DataFrame Final ---

# Definir el orden final y lógico de las columnas
columnas_ordenadas = [
    'AÑO',
    'NIVEL',
    'CODCCAA',
    'CCAA',
    'CPRO',
    'PROVINCIA',
    'CMUN',
    'MUNICIPIO',
    'POB'
]
df_consolidado = df_consolidado[columnas_ordenadas]

# Ordenar los datos para una mejor visualización
# (Por año y luego por población de mayor a menor para ver los totales primero)
df_consolidado.sort_values(by=['AÑO', 'POB'], ascending=[True, False], inplace=True)


# # --- 4. Mostrar Resultados del DataFrame Consolidado ---
# print("\n\n=============================================")
# print("=== DATAFRAME CONSOLIDADO (TODO JUNTO) ===")
# print("=============================================")
# print("Mostrando las primeras filas (que corresponden al total Nacional y CCAA más pobladas):")
# print(df_consolidado.head(10))

# print("\nEjemplo: Filtrando para ver la población de la provincia de Barcelona en 2023:")
# print(df_consolidado[(df_consolidado['AÑO'] == 2023) & (df_consolidado['PROVINCIA'] == 'Barcelona') & (df_consolidado['NIVEL'] == 'Provincial')])

# print("\nEjemplo: Filtrando para ver la población del municipio de Badalona en 2023:")
# print(df_consolidado[(df_consolidado['AÑO'] == 2023) & (df_consolidado['MUNICIPIO'] == 'Badalona')])

# print(len(df_consolidado)) # 81999

# Exportar a CSV si lo necesitas
df_consolidado.to_csv('./data/geo_master.csv', index=False, sep=';')

## Imprimir lista de valores únicos de provincias y comunidades autónomas
# print("\nProvincias únicas en el DataFrame final:")
# print(df_consolidado['PROVINCIA'].dropna().unique())
# print("\nComunidades Autónomas únicas en el DataFrame final:")
# print(df_consolidado['CCAA'].dropna().unique())
