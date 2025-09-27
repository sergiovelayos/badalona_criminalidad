
# ============= CLAUDE ==============
import pandas as pd
import glob
import re
import unicodedata
import numpy as np
import sqlite3
import os


pd.set_option("display.max_columns", None)
pd.set_option('display.max_rows', None)

# Ruta a los ficheros
ruta = "data/descargas_portal_ministerio/*.csv"

# Lista de todos los ficheros
ficheros = glob.glob(ruta)

dfs = []

for fichero in ficheros:
    # Extraer año y trimestre del nombre de fichero con regex
    match = re.search(r"(\d{4})_(\d)_municipios\.csv", fichero)
    if match:
        año, trimestre = int(match.group(1)), int(match.group(2))
    else:
        continue
    
    # Leer CSV (ajusta encoding/sep si hace falta)
    df = pd.read_csv(fichero, sep=";", encoding="utf-8")
    
    # Añadir columnas auxiliares
    df["fichero"] = año * 10 + trimestre  # valor creciente para ordenar
    
    dfs.append(df)

# Unir todos los dataframes
df_total = pd.concat(dfs, ignore_index=True)

# Renombrar columnas
df_total.columns = ["geo", "tipo", "periodo", "valor","fichero"]

# Quitar los periodos de variación
df_total = df_total[~df_total["periodo"].str.contains("Varia", case=False, na=False)]

# Normalizar 'periodo'
df_total["periodo"] = df_total["periodo"].str.strip().str.lower()

# Armonizar periodos
map_periodos = {
    "enero-marzo": "T1",
    "enero-junio": "T2",
    "enero-septiembre": "T3",
    "enero-diciembre": "T4",
    "enero--diciembre": "T4"
}

# 1. Divide la columna 'periodo' en dos partes.
#    La primera parte es el año, la segunda es la descripción.
partes = df_total['periodo'].str.split(' ', expand=True)
periodo_nombre = partes[0]
periodo_año = partes[1]

# 2. Aplica el mapeo a la descripción para obtener un valor armonizado.
descripcion_armonizada = periodo_nombre.map(map_periodos)

# 3. Combina el año con la descripción armonizada para crear la nueva columna.
df_total["periodo"] = descripcion_armonizada + ' ' + periodo_año




# Encontrar el fichero más reciente para cada periodo
fichero_max_por_periodo = df_total.groupby("periodo")["fichero"].max().reset_index()

# Hacer merge para obtener todos los registros del fichero más reciente
df_total_last = df_total.merge(fichero_max_por_periodo, on=["periodo", "fichero"])

df_total_last = df_total_last.copy()

############
#   HARMONIZACIÓN DE GEO
##########

# Municipios que pierden los 20.000 habitantes y que desaparecen de la lista oficial. Los eliminamos.
values_to_remove = ["- Municipio de Santa Eulalia del Río", "-Municipio de Calatayud", "-Municipio de Barañain"]
df_total_last = df_total_last[~df_total_last["geo"].isin(values_to_remove)]

# Arreglar algunos nombres manualmente
replacement_dict = {
    '-Municipo de Villanueva de la Cañada':'28176 Villanueva de la Cañada',
    'Municipo de Villanueva de la Cañada':'28176 Villanueva de la Cañada',
    '-Municipio de Almassora' : '12009 Almazora/Almassora',
    '-Municipio de Almazora/Almassora' : '12009 Almazora/Almassora',
    '-Municipio de Alboraya' : '46013 Alboraia/Alboraya',
    '-Municipio de Alboraia/Alboraya': '46013 Alboraia/Alboraya',
    '-Municipio de Egüés' : '31086 Valle de Egüés/Eguesibar',
    '-Municipio de Valle de Egüés/Eguesibar' : '31086 Valle de Egüés/Eguesibar',
    '-Municipio de Egüés/Eguesibar' : '31086 Valle de Egüés/Eguesibar',
    'Palma de Mallorca': '07040 Palma',
    'València': '46250 Valencia',
    'O Porriño': '36039 Porriño, O',
    'Vila-Real': '12135 Vila-real',
    'San Cristóbal de la Laguna': '38023 San Cristóbal de La Laguna',
    '-Municipio de València' : '46250 Valencia',
    '-Municipio de O Porriño': '36039 Porriño, O',
    '- Municipio de Palma de Mallorca': '07040 Palma',
    '- Municipio de San Cristóbal de la Laguna': '38023 San Cristóbal de La Laguna',
    '- Municipio de Vila-Real' : '12135 Vila-real'
    }

df_total_last['geo'] = df_total_last['geo'].replace(replacement_dict)

df_total_last["geo"] = (
    df_total_last["geo"]
    .str.replace(r"\s+", " ", regex=True)  # colapsar espacios múltiples
    .str.replace(r"^\s*[-–—]\s*", "", regex=True)
)


# Seleccionar columnas relevantes
df_combinaciones = df_total_last[["geo", "periodo", "fichero"]].drop_duplicates()

# Ordenar para más claridad
df_combinaciones = df_combinaciones.sort_values(["geo", "fichero","periodo" ])

# print(df_total_last["geo"].unique())


# Mostrar las primeras filas
# print(df_combinaciones.head(20))

# Guardar a CSV si lo quieres revisar entero
# df_combinaciones.to_csv("data/geo_uniques.csv", index=False, encoding="utf-8")

# print(f"Archivo guardado con {len(df_combinaciones)} combinaciones únicas")

# Este data frame lo dividimos por nivel geográfico en 4: municipios, provincias, CCAA y nacional/otros. Las de municipios, provincias y ccaa las cruzaremos con la población correspondiente a su nivel geográfico y el año.
# Seleccionamos los municipios por su formato (5 dígitos o que contengan "Municipio de")

dic_mun = pd.read_csv("data/diccionarios/municipios.csv", sep=";", dtype={"cp_pk_tab_pob":str})
dic_pro = pd.read_csv("data/diccionarios/provincias.csv", sep=";", dtype={"cp_pk_tab_pro":str})
dic_ccaa = pd.read_csv("data/diccionarios/ccaa.csv", sep=";", dtype={"cp_pk_tab_ccaa":str})

pob_mun = pd.read_csv("data/pob_municipios.csv", sep=";", dtype={"CP":str})
pob_pro = pd.read_csv("data/pob_provincias.csv", sep=";", dtype={"CODPRO":str})
pob_ccaa = pd.read_csv("data/pob_ccaa.csv", sep=";", dtype={"CODCCAA":str})

# # --- Información de 'df_total_last' ---
# print("\n--- 1. Extracto del data frame base 'df_total_last' ---")
# print(df_total_last.head(3))
# df_total_last.info()

# # --- Información de 'dic_ccaa' ---
# print("\n--- 2. Extracto del data frame de diccionario ccaa 'dic_ccaa' ---")
# print(dic_ccaa.head(3))
# dic_ccaa.info()

# --- Información de 'pob_ccaa' ---
# print("\n--- 3. Extracto del data frame de población ccaa 'pob_ccaa' ---")
# print(pob_ccaa.head(3))
# pob_ccaa.info()
# print(df_total_last.head())


# Cruce CCAA
df_cruzado_1 = pd.merge(
    df_total_last, dic_ccaa,
    left_on='geo', right_on='geo_ccaa_unique',
    how='inner'
)


# Cruce 2: con pob_ccaa
if not df_cruzado_1.empty:
    df_cruzado_1[['trimestre', 'año']] = df_cruzado_1['periodo'].str.split(' ', expand=True)
    df_cruzado_1['año'] = df_cruzado_1['año'].astype(int)
    df_cruzado_1['pob_año'] = df_cruzado_1['año'].clip(upper=2024)

    df_cruzado_1['cccaa_pk_tab_ccaa'] = df_cruzado_1['cccaa_pk_tab_ccaa'].astype(str).str.zfill(2)
    pob_ccaa['CODCCAA'] = pob_ccaa['CODCCAA'].astype(str)

    df_cruzado_2 = pd.merge(
        df_cruzado_1, pob_ccaa,
        left_on=['cccaa_pk_tab_ccaa', 'pob_año'],
        right_on=['CODCCAA', 'AÑO'],
        how='inner'
    )
else:
    df_cruzado_2 = pd.DataFrame()



df_cruzado_2 = df_cruzado_2.drop(columns=["geo","fichero","geo_ccaa_unique","cccaa_pk_tab_ccaa","trimestre","año","pob_año","CODCCAA","AÑO"])
nuevo_order = ["periodo", "CCAA", "tipo", "valor", "POB"]
df_cruzado_2 = df_cruzado_2[nuevo_order]
df_cruzado_2["CCAA"] = "CCAA:" + df_cruzado_2["CCAA"].astype(str)
df_cruzado_2 = df_cruzado_2.rename(columns={"CCAA":"geo"})
df_ccaa = df_cruzado_2.copy()

#print(df_cruzado_2["geo"].unique()) # Cat está

#print(df_cruzado_2["periodo"].unique())
# filter = df_ccaa["periodo"].str.contains("T4 2023")
# print(df_ccaa[filter].head(10))



# Cruce Provincias
df_cruzado_1 = pd.merge(
    df_total_last, dic_pro,
    left_on='geo', right_on='geo_pro_unique',
    how='inner'
)

# Cruce 2: con pob_ccaa
if not df_cruzado_1.empty:
    df_cruzado_1[['trimestre', 'año']] = df_cruzado_1['periodo'].str.split(' ', expand=True)
    df_cruzado_1['año'] = df_cruzado_1['año'].astype(int)
    df_cruzado_1['pob_año'] = df_cruzado_1['año'].clip(upper=2024)

    df_cruzado_1['cpro_pk_tab_pro'] = df_cruzado_1['cpro_pk_tab_pro'].astype(str)
    pob_pro['CPRO'] = pob_pro['CPRO'].astype(str)

    df_cruzado_2 = pd.merge(
        df_cruzado_1, pob_pro,
        left_on=['cpro_pk_tab_pro', 'pob_año'],
        right_on=['CPRO', 'AÑO'],
        how='inner'
    )
else:
    df_cruzado_2 = pd.DataFrame()



df_cruzado_2 = df_cruzado_2.drop(columns=["geo","fichero","geo_pro_unique","cpro_pk_tab_pro","trimestre","año","pob_año","CPRO","AÑO"])
nuevo_order = ["periodo", "PROVINCIA", "tipo", "valor", "POB"]
df_cruzado_2 = df_cruzado_2[nuevo_order]
df_cruzado_2["PROVINCIA"] = "PROVINCIA:" + df_cruzado_2["PROVINCIA"].astype(str)
df_cruzado_2 = df_cruzado_2.rename(columns={"PROVINCIA":"geo"})
df_pro = df_cruzado_2.copy()

# print(df_pro["periodo"].unique())
# filter = df_pro["periodo"].str.contains("T4 2023")
# print(df_pro[filter].head(10))



# Cruce Municipios
df_cruzado_1 = pd.merge(
    df_total_last, dic_mun,
    left_on='geo', right_on='geo_mun_unique',
    how='inner'
)

# Cruce 2: con pob_ccaa
if not df_cruzado_1.empty:
    df_cruzado_1[['trimestre', 'año']] = df_cruzado_1['periodo'].str.split(' ', expand=True)
    df_cruzado_1['año'] = df_cruzado_1['año'].astype(int)
    df_cruzado_1['pob_año'] = df_cruzado_1['año'].clip(upper=2024)

    df_cruzado_1['cp_pk_tab_pob'] = df_cruzado_1['cp_pk_tab_pob'].astype(str)
    pob_mun['CP'] = pob_mun['CP'].astype(str)

    df_cruzado_2 = pd.merge(
        df_cruzado_1, pob_mun,
        left_on=['cp_pk_tab_pob', 'pob_año'],
        right_on=['CP', 'AÑO'],
        how='inner'
    )
else:
    df_cruzado_2 = pd.DataFrame()

df_cruzado_2 = df_cruzado_2.drop(columns=["geo","fichero","geo_mun_unique","cp_pk_tab_pob","trimestre","año","pob_año","CP","AÑO"])
nuevo_order = ["periodo", "MUNICIPIO", "tipo", "valor", "POB"]
df_cruzado_2 = df_cruzado_2[nuevo_order]
df_cruzado_2["MUNICIPIO"] = "MUNICIPIO:" + df_cruzado_2["MUNICIPIO"].astype(str)
df_cruzado_2 = df_cruzado_2.rename(columns={"MUNICIPIO":"geo"})
df_mun = df_cruzado_2.copy()

# print(df_mun["periodo"].unique())
# filter = df_mun["periodo"].str.contains("T4 2023")
# print(df_mun[filter].head(10))

# print(f"\n---- Resumen: ------")
# print(f"\nShapes Dataframes: df_ccaa {df_ccaa.shape}, df_pro {df_pro.shape}, df_mun {df_mun.shape}")


df_nac = df_total_last[df_total_last["geo"] == "NACIONAL"].copy()
# print(f"\nRegistros nacionales: {len(df_nac)}")
# print(df_nac.head(3))
# print(df_nac["geo"].unique())

nuevo_order = ["periodo", "geo", "tipo", "valor"]
df_nac = df_nac[nuevo_order]
# print(pob_ccaa.head(3))

# Calcular población total nacional por año
df_pob_nac = pob_ccaa.groupby('AÑO')['POB'].sum().reset_index()
# print(df_pob_nac.head(3))
# print(df_pob_nac["AÑO"].unique())

df_nac[['trimestre', 'año']] = df_nac['periodo'].str.split(' ', expand=True)
df_nac['año'] = df_nac['año'].astype(int)
df_nac['pob_año'] = df_nac['año'].clip(upper=2024)


df_nac_2 = pd.merge(
    df_nac, df_pob_nac,
    left_on=['pob_año'],
    right_on=['AÑO'],
    how='inner'
)

df_nac_2 = df_nac_2.drop(columns=["trimestre","año","pob_año","AÑO"])
nuevo_order = ["periodo", "geo", "tipo", "valor", "POB"]
df_nac_2 = df_nac_2[nuevo_order]


df_ccaa_pro_mun = pd.concat([df_ccaa, df_pro, df_mun,df_nac_2], ignore_index=True)
#print(df_ccaa_pro_mun["geo"].unique()) # Cat ok

# print(f"\nShapes Dataframes: df_ccaa_pro_mun {df_ccaa_pro_mun.shape}")
# print(df_ccaa_pro_mun.head(10))
# print(f"\nRegistros de geo del dataframe resultante:{df_ccaa_pro_mun['geo'].nunique()}")
# print(df_ccaa_pro_mun["geo"].unique()[100:120])
# filter = df_ccaa_pro_mun["geo"].str.contains("CCAA:CATALUÑA")
# print(df_ccaa_pro_mun[filter].head(10))



TIPOLOGIA_NORMALIZAR = {
    # Criminalidad convencional
    "1.-Homicidios dolosos y asesinatos consumados": "1. Homicidios dolosos y asesinatos consumados",
    "2.-HOMICIDIOS DOLOSOS Y ASESINATOS CONSUMADOS (EU)": "1. Homicidios dolosos y asesinatos consumados",

    "2.-Homicidios dolosos y asesinatos en grado tentativa": "2. Homicidios dolosos y asesinatos en grado tentativa",

    "3.-Delitos graves y menos graves de lesiones y riña tumultuaria": "3. Delitos graves y menos graves de lesiones y riña tumultuaria",

    "4.-Secuestro": "4. Secuestro",

    # Libertad sexual
    "5.-Delitos contra la libertad e indemnidad sexual": "5. Delitos contra la libertad sexual",
    "5.-Delitos contra la libertad sexual": "5. Delitos contra la libertad sexual",

    "5.1.-Agresión sexual con penetración": "5.1.-Agresión sexual con penetración",
    "5.2.-Resto de delitos contra la libertad e indemnidad sexual": "5.2.-Resto de delitos contra la libertad sexual",
    "5.2.-Resto de delitos contra la libertad sexual": "5.2.-Resto de delitos contra la libertad sexual",

    # Robos con violencia
    "6.-Robos con violencia e intimidación": "6. Robos con violencia e intimidación",
    "3.-ROBO CON VIOLENCIA E INTIMIDACIÓN (EU)": "6. Robos con violencia e intimidación",

    # Robos con fuerza
    "7.- Robos con fuerza en domicilios, establecimientos y otras instalaciones": "7. Robos con fuerza en domicilios, establecimientos y otras instalaciones",
    "4.-ROBOS CON FUERZA EN DOMICILIOS (EU)": "7.1.-Robos con fuerza en domicilios",

    "7.1.-Robos con fuerza en domicilios": "7.1.-Robos con fuerza en domicilios",

    # Hurtos
    "8.-Hurtos": "8. Hurtos",
    "8.-HURTOS": "8. Hurtos",

    # Sustracciones
    "9.-Sustracciones de vehículos": "9. Sustracciones de vehículos",
    "5.-SUSTRACCIÓN VEHÍCULOS A MOTOR (EU)": "9. Sustracciones de vehículos",

    # Tráfico de drogas
    "10.-Tráfico de drogas": "10. Tráfico de drogas",
    "6.-TRÁFICO DE DROGAS (EU)": "10. Tráfico de drogas",

    # Daños
    "7.-DAÑOS;": "11. Resto de criminalidad convencional",

    # Resto / totales
    "Resto de infracciones penales": "11. Resto de criminalidad convencional",
    "TOTAL INFRACCIONES PENALES": "III. TOTAL INFRACCIONES PENALES",
    "1.-DELITOS Y FALTAS (EU)": "I. CRIMINALIDAD CONVENCIONAL",
}

def normalizar_tipologia(valor: str) -> str:
    """
    Normaliza una tipología antigua al estándar actual.
    Si no hay correspondencia, devuelve el valor original.
    """
    if pd.isna(valor):
        return valor
    valor = valor.strip()
    return TIPOLOGIA_NORMALIZAR.get(valor, valor)


df_ccaa_pro_mun["tipo"] = df_ccaa_pro_mun["tipo"].apply(normalizar_tipologia)

# filtro = (
#     df_ccaa_pro_mun["geo"].str.contains("Cataluña") &
#     (df_ccaa_pro_mun["periodo"] == "T2 2025") &
#     df_ccaa_pro_mun["tipo"].str.contains("Hurtos")
# )

# print("\nPrimer filter:",df_ccaa_pro_mun[filtro])

# Preparar datos
df_ccaa_pro_mun['valor'] = df_ccaa_pro_mun['valor'].str.replace('.', '', regex=False).astype(int)

# Separar periodo en trimestre y año
df_ccaa_pro_mun[['trimestre', 'año']] = df_ccaa_pro_mun['periodo'].str.split(' ', expand=True)
df_ccaa_pro_mun['año'] = df_ccaa_pro_mun['año'].astype(int)

# Crear orden numérico para trimestres
df_ccaa_pro_mun['trim_num'] = df_ccaa_pro_mun['trimestre'].str.replace('T', '').astype(int)

# Ordenar correctamente
df_ccaa_pro_mun = df_ccaa_pro_mun.sort_values(['geo', 'tipo', 'año', 'trim_num']).reset_index(drop=True)


# Crear la desacumulación manualmente para ser más explícito
df_ccaa_pro_mun['valor_original'] = df_ccaa_pro_mun['valor']  # Guardar original para debug

def desacumular_grupo(grupo):
    grupo = grupo.sort_values('trim_num')
    valores_nuevos = []
    
    for i, row in grupo.iterrows():
        if row['trim_num'] == 1:
            # T1 es el valor directo
            valor_trimestre = row['valor_original']
        else:
            # T2, T3, T4: restar el valor acumulado anterior
            valor_anterior = grupo[grupo['trim_num'] == (row['trim_num'] - 1)]['valor_original']
            if len(valor_anterior) > 0:
                valor_trimestre = row['valor_original'] - valor_anterior.iloc[0]
            else:
                valor_trimestre = row['valor_original']
        
        valores_nuevos.append(valor_trimestre)
    
    grupo['valor_desacumulado'] = valores_nuevos
    return grupo

# Aplicar desacumulación
df_ccaa_pro_mun = df_ccaa_pro_mun.groupby(['geo', 'tipo', 'año']).apply(desacumular_grupo).reset_index(drop=True)


# Reemplazar valor original con desacumulado
df_ccaa_pro_mun['valor'] = df_ccaa_pro_mun['valor_desacumulado']

# Limpiar columnas temporales
df_ccaa_pro_mun.drop(columns=['trim_num', 'valor_original', 'valor_desacumulado'], inplace=True)


# filtro = (
#     df_ccaa_pro_mun["geo"].str.contains("Cataluña") &
#     (df_ccaa_pro_mun["periodo"] == "T2 2025") &
#     df_ccaa_pro_mun["tipo"].str.contains("Hurtos")
# )

# print("\nPrimer filter:",df_ccaa_pro_mun[filtro])



#print(df_ccaa_pro_mun[filtro])
# print(df_ccaa_pro_mun.info())
# print(df_ccaa_pro_mun.head(3))


# Guardar resultado intermedio
#df_ccaa_pro_mun.to_csv("data/delitos_borrar.csv", index=False, encoding='utf-8')

# Guardar en SQLite
db_path = "data/delitos.db" 
if os.path.exists(db_path):
    os.remove(db_path)  # Elimina la base de datos si ya existe 

# --- 2. CONEXIÓN Y CARGA DE DATOS ---
try:
    # Conectarse a la base de datos (creará el fichero si no existe)
    conn = sqlite3.connect(db_path)
    #print(f"🔌 Conexión establecida con la nueva base de datos '{db_path}'.")

    # Definir el nombre de la tabla
    table_name = 'delitos'

    # Usar to_sql para insertar el DataFrame en la base de datos
    #print(f"🚀 Insertando {len(df_ccaa_pro_mun)} registros en la tabla '{table_name}'...")
    df_ccaa_pro_mun.to_sql(
        name=table_name,
        con=conn,
        if_exists='replace', # Reemplaza la tabla si ya existe
        index=False          # No escribir el índice del DataFrame
    )

    #print(f"✅ ¡Éxito! Los datos han sido cargados en la base de datos.")

    # Guardar los cambios (commit) y cerrar la conexión
    conn.commit()
    conn.close()
    print("💾 Cambios guardados y conexión cerrada.")

except sqlite3.Error as e:
    print(f"❌ Error de SQLite: {e}")

