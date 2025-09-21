import pandas as pd
import glob
import re

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

# print("\nValores únicos por columna\n", df_total.nunique(),"\n registros totales antes de cualquier proceso:", len(df_total))
# Renombrar columnas
df_total.columns = ["geo", "tipo", "periodo", "valor","fichero"]

# Número de periodos distintos
# print(df_total["periodo"].nunique()) # 60

# Quitar los periodos de variación
df_total = df_total[~df_total["periodo"].str.contains("Varia", case=False, na=False)]
# print(df_total["periodo"].nunique()) # Bajamos a 49

# print("\n registros totales después de quitar 'Variaciones':", len(df_total)) # 484405

# Normalizar 'periodo'
df_total["periodo"] = df_total["periodo"].str.strip().str.lower()
# print(df_total["periodo"].nunique()) # 43

# Agrupación de periodos por fichero
resultado = df_total.groupby(['fichero', 'periodo']).size().sort_index()
# print(resultado)

df_total_last = df_total.loc[
    df_total.groupby("periodo")["fichero"].idxmax()
].copy()
# print(df_total_last)
# print(f"Total registros tras quedarnos con último fichero: {len(df_total_last)}")
# print(df_geo_last[["fichero", "periodo"]].sort_values("periodo").head(20))

# Encontrar el fichero más reciente para cada periodo
fichero_max_por_periodo = df_total.groupby("periodo")["fichero"].max().reset_index()

# Hacer merge para obtener todos los registros del fichero más reciente
df_total_last = df_total.merge(fichero_max_por_periodo, on=["periodo", "fichero"])

# print(f"Total registros tras quedarnos con último fichero: {len(df_total_last)}") # 289314

# print(df_total_last.head())

# Chequear algunos casos
filter =  df_total_last[(df_total_last["periodo"].str.contains("enero-marzo 2024")) & 
            (df_total_last["geo"] == "ANDALUCÍA") & 
            (df_total_last["tipo"] == "I. CRIMINALIDAD CONVENCIONAL")
              ]

# print(filter)

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
    '-Municipio de Egüés/Eguesibar' : '31086 Valle de Egüés/Eguesibar'
    }

df_total_last['geo'] = df_total_last['geo'].replace(replacement_dict)

# filter = (df_total_last["geo"].str.contains("Villanueva de la Cañada", na=False) |
#           df_total_last["geo"].str.contains("Almassora", na=False) |
#           df_total_last["geo"].str.contains("Alboraya", na=False) |
#           df_total_last["geo"].str.contains("Egüés", na=False)
# )

# print(df_total_last[filter]["geo"].unique())

df_total_last["geo"] = (
    df_total_last["geo"]
    .str.replace(r"\s+", " ", regex=True)  # colapsar espacios múltiples
    .str.replace(r"^\s*[-–—]\s*", "", regex=True)
)

# Chequear algunos casos
# print(df_total_last["geo"].str[:10].unique())



# Dividir el data set en municipio y no municipio
df_municipios = df_total_last[
                (df_total_last["geo"].str.match(r'^\d{5}', na=False)) |
                (df_total_last["geo"].str.contains(r'^\s*(?:[-–—]\s*)?muni[sc]ip[io]', case=False, na=False, regex=True))
                ].copy()

# ver los valores únicos de geo mirando los primeros 10 caracteres
#print(df_municipios["geo"].str[:10].unique())

# Crear una clave combinada (ej: geo + periodo + tipología)
df_total_last["clave"] = df_total_last[["geo", "periodo", "tipo"]].apply(lambda x: "_".join(x.astype(str)), axis=1)
df_municipios["clave"] = df_municipios[["geo", "periodo", "tipo"]].apply(lambda x: "_".join(x.astype(str)), axis=1)

# Filtrar
claves_municipios = df_municipios["clave"].dropna().unique()
df_no_municipios = df_total_last[~df_total_last["clave"].isin(claves_municipios)].copy()

# Opcional: quitar columna "clave" si no la necesitas
df_no_municipios = df_no_municipios.drop(columns=["clave"])
df_municipios = df_municipios.drop(columns=["clave"])
# df_no_municipios = df_total_last[~df_municipios].copy()

# print(df_no_municipios["geo"].str[:10].unique())

# # Conteo de registros en cada subset
# print(f"\nTotal registros no municipios:{len(df_no_municipios)}", # 50850
#       f"\nTotal reigistros municipios:{len(df_municipios)}", # 238464 
#       f"\nTotal registros finales: {len(df_no_municipios) + len(df_municipios)}") # 289314

# Reemplazar manualmente algunos municipios porque su nombre se modifica
replacement_dict = {
    'València': 'Valencia',
    #'Alboraya': 'Alboraia/Alboraya',
    'Palma de Mallorca': 'Palma',
    'O Porriño': 'Porriño, O',
   # 'Villanueva de la Cañada': 'Villanueva de la Cañada',
   # 'Egüés': 'Valle de Egüés/Eguesibar',
    'San Cristóbal de la Laguna': 'San Cristóbal de La Laguna',
    'Vila-Real': 'Vila-real'
    #'Almassora': 'Almazora/Almassora'
}

# Define a function to find and replace values
def flexible_replace(text):
    for old_value, new_value in replacement_dict.items():
        if old_value in text:
            return new_value
    return text

# Apply the function to the 'geo' column
df_municipios['geo'] = df_municipios['geo'].apply(flexible_replace)

# Reemplazar 'Municipio de ' por cadena vacía al inicio del texto
df_municipios["geo"] = df_municipios["geo"].str.replace(r"^Municipio de ", "", regex=True)
# print(df_municipios["geo"].str[:10].unique())

# # -----------------------
# # Mapeo de municipios a códigos postales
# # -----------------------

# Crear un diccionario para mapear municipio a código postal
municipio_a_codigo = {}

# Extraer y mapear todos los registros con formato de código postal
# Usar la columna limpia para crear el mapeo
for item in df_municipios["geo"].dropna().unique():
    match = re.match(r"^(\d{5})\s+(.*)", str(item))
    if match:
        codigo = match.group(1)
        municipio = match.group(2).strip()
        # Solo agrega al diccionario si el municipio no existe
        if municipio not in municipio_a_codigo:
            municipio_a_codigo[municipio] = codigo

# print(f"Se crearon {len(municipio_a_codigo)} mapeos municipio -> código postal")

# # Mostrar algunos ejemplos del mapeo
# print("\nEjemplos de mapeos creados:")
# for i, (municipio, codigo) in enumerate(list(municipio_a_codigo.items())[:5]):
#     print(f"  '{municipio}' -> {codigo}")

# print(df_municipios.nunique())
# geo           861
# tipo           40
# periodo        43
# valor        6957
# fichero        37
# clave      238464

# # -----------------------
# # Unir datos: Mapear municipios sin CP a su formato completo
# # -----------------------

def unir_municipio_a_cp(fila_original):
    # Manejar valores NaN
    if pd.isna(fila_original):
        return fila_original
    
    fila_str = str(fila_original)
    
    # Si ya tiene el formato completo (empieza con 5 dígitos), mantenerlo
    if re.match(r"^\d{5}", fila_str):
        return fila_original
    
    # Limpiar el formato para buscar en el diccionario
    fila_limpia = re.sub(r"^[\s\-]+", "", fila_str)
    fila_limpia = re.sub(r"^Municipio de ", "", fila_limpia)
    
    # Buscar en el diccionario
    if fila_limpia in municipio_a_codigo:
        codigo = municipio_a_codigo[fila_limpia]
        return f"{codigo} {fila_limpia}"
    
    # Si no se encuentra mapeo, devolver el valor original limpio
    # (esto mantiene los datos históricos pero con formato consistente)
    else:
        return fila_limpia

# Aplicar la función a la columna 'geo' original
df_municipios["geo"] = df_municipios["geo"].apply(unir_municipio_a_cp)

# # Eliminar la columna auxiliar
# df_municipios = df_municipios.drop('geo_limpia', axis=1)

# # -----------------------
# # Verificaciones
# # -----------------------

# print(f"\nRegistros finales: {len(df_municipios)}")

# Verificar Badalona específicamente
# filter_badalona = df_municipios["geo"].str.contains("Badalona", na=False)
# print(f"\nRegistros de Badalona: {filter_badalona.sum()}")

# print(df_municipios.iloc[300:310])
# print(f"\ndinstict geo: {df_municipios['geo'].str[:9].unique()}")

# aquellos registros que geo no empiecen por 5 dígitos
filter = ~df_municipios["geo"].str.match(r"^\d{5}", na=False)
print(df_municipios[filter]["geo"].unique())
# Municpios que no cruzan y deben arreglarse a mano:
# 'Alboraya' 'O Porriño' 'Municipo de Villanueva de la Cañada' 'Egüés'
#  'Santa Eulalia del Río' 'Palma de Mallorca' 'San Cristóbal de la Laguna'
#  'Vila-Real' 'Almassora' 'València' 'Egüés/Eguesibar' 'Calatayud'
#  'Barañain'





filter = df_municipios["geo"].str.contains("calatayud", na=False)
# filter = df_municipios["geo"] == "Palma"
# print(df_municipios[filter]["geo"].unique())