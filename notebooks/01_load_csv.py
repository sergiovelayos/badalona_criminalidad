# import pandas as pd
# import glob
# import re
# import unicodedata

# pd.set_option("display.max_columns", None)
# pd.set_option('display.max_rows', None)

# # Ruta a los ficheros
# ruta = "data/descargas_portal_ministerio/*.csv"
# # geo_maestro = pd.read_csv("./data/maestro_geo_provincia_ccaa.csv")

# # Lista de todos los ficheros
# ficheros = glob.glob(ruta)

# dfs = []

# for fichero in ficheros:
#     # Extraer año y trimestre del nombre de fichero con regex
#     match = re.search(r"(\d{4})_(\d)_municipios\.csv", fichero)
#     if match:
#         año, trimestre = int(match.group(1)), int(match.group(2))
#     else:
#         continue
    
#     # Leer CSV (ajusta encoding/sep si hace falta)
#     df = pd.read_csv(fichero, sep=";", encoding="utf-8")
    
#     # Añadir columnas auxiliares
#     df["fichero"] = año * 10 + trimestre  # valor creciente para ordenar
    
#     dfs.append(df)

# # Unir todos los dataframes
# df_total = pd.concat(dfs, ignore_index=True)

# # print("\nValores únicos por columna\n", df_total.nunique(),"\n registros totales antes de cualquier proceso:", len(df_total))
# # Renombrar columnas
# df_total.columns = ["geo", "tipo", "periodo", "valor","fichero"]

# # Número de periodos distintos
# # print(df_total["periodo"].nunique()) # 60

# # Quitar los periodos de variación
# df_total = df_total[~df_total["periodo"].str.contains("Varia", case=False, na=False)]
# # print(df_total["periodo"].nunique()) # Bajamos a 49

# # print("\n registros totales después de quitar 'Variaciones':", len(df_total)) # 484405

# # Normalizar 'periodo'
# df_total["periodo"] = df_total["periodo"].str.strip().str.lower()
# # print(df_total["periodo"].nunique()) # 43

# # Agrupación de periodos por fichero
# resultado = df_total.groupby(['fichero', 'periodo']).size().sort_index()
# # print(resultado)

# df_total_last = df_total.loc[
#     df_total.groupby("periodo")["fichero"].idxmax()
# ].copy()
# # print(df_total_last)
# # print(f"Total registros tras quedarnos con último fichero: {len(df_total_last)}")
# # print(df_geo_last[["fichero", "periodo"]].sort_values("periodo").head(20))

# # Encontrar el fichero más reciente para cada periodo
# fichero_max_por_periodo = df_total.groupby("periodo")["fichero"].max().reset_index()

# # Hacer merge para obtener todos los registros del fichero más reciente
# df_total_last = df_total.merge(fichero_max_por_periodo, on=["periodo", "fichero"])

# # print(f"Total registros tras quedarnos con último fichero: {len(df_total_last)}") # 289314

# # print(df_total_last.head())

# # Chequear algunos casos
# filter =  df_total_last[(df_total_last["periodo"].str.contains("enero-marzo 2024")) & 
#             (df_total_last["geo"] == "ANDALUCÍA") & 
#             (df_total_last["tipo"] == "I. CRIMINALIDAD CONVENCIONAL")
#               ]

# # print(filter)

# ############
# #   HARMONIZACIÓN DE GEO
# ##########

# # Municipios que pierden los 20.000 habitantes y que desaparecen de la lista oficial. Los eliminamos.
# values_to_remove = ["- Municipio de Santa Eulalia del Río", "-Municipio de Calatayud", "-Municipio de Barañain"]
# df_total_last = df_total_last[~df_total_last["geo"].isin(values_to_remove)]

# # Arreglar algunos nombres manualmente
# replacement_dict = {
#     '-Municipo de Villanueva de la Cañada':'28176 Villanueva de la Cañada',
#     'Municipo de Villanueva de la Cañada':'28176 Villanueva de la Cañada',
#     '-Municipio de Almassora' : '12009 Almazora/Almassora',
#     '-Municipio de Almazora/Almassora' : '12009 Almazora/Almassora',
#     '-Municipio de Alboraya' : '46013 Alboraia/Alboraya',
#     '-Municipio de Alboraia/Alboraya': '46013 Alboraia/Alboraya',
#     '-Municipio de Egüés' : '31086 Valle de Egüés/Eguesibar',
#     '-Municipio de Valle de Egüés/Eguesibar' : '31086 Valle de Egüés/Eguesibar',
#     '-Municipio de Egüés/Eguesibar' : '31086 Valle de Egüés/Eguesibar',
#     'Palma de Mallorca': '07040 Palma',
#     'València': '46250 Valencia',
#     'O Porriño': '36039 Porriño, O',
#     'Vila-Real': '12135 Vila-real',
#     'San Cristóbal de la Laguna': '38023 San Cristóbal de La Laguna',
#     '-Municipio de València' : '46250 Valencia',
#     '-Municipio de O Porriño': '36039 Porriño, O',
#     '- Municipio de Palma de Mallorca': '07040 Palma',
#     '- Municipio de San Cristóbal de la Laguna': '38023 San Cristóbal de La Laguna',
#     '- Municipio de Vila-Real' : '12135 Vila-real'
#     }

# df_total_last['geo'] = df_total_last['geo'].replace(replacement_dict)

# # filter = (df_total_last["geo"].str.contains("O Porriño", na=False) |
# #           df_total_last["geo"].str.contains("Palma de Mallorca", na=False) |
# #           df_total_last["geo"].str.contains("San Cristóbal de la Laguna", na=False) |
# #           df_total_last["geo"].str.contains("Vila-Real", na=False) | 
# #           df_total_last["geo"].str.contains("València", na=False) 
# # )

# # print(df_total_last[filter]["geo"].unique())

# df_total_last["geo"] = (
#     df_total_last["geo"]
#     .str.replace(r"\s+", " ", regex=True)  # colapsar espacios múltiples
#     .str.replace(r"^\s*[-–—]\s*", "", regex=True)
# )

# # Chequear algunos casos
# # print(df_total_last["geo"].str[:10].unique())



# # Dividir el data set en municipio y no municipio
# df_municipios = df_total_last[
#                 (df_total_last["geo"].str.match(r'^\d{5}', na=False)) |
#                 (df_total_last["geo"].str.contains(r'^\s*(?:[-–—]\s*)?muni[sc]ip[io]', case=False, na=False, regex=True))
#                 ].copy()

# # ver los valores únicos de geo mirando los primeros 10 caracteres
# #print(df_municipios["geo"].str[:10].unique())

# # Crear una clave combinada (ej: geo + periodo + tipología)
# df_total_last["clave"] = df_total_last[["geo", "periodo", "tipo"]].apply(lambda x: "_".join(x.astype(str)), axis=1)
# df_municipios["clave"] = df_municipios[["geo", "periodo", "tipo"]].apply(lambda x: "_".join(x.astype(str)), axis=1)

# # Filtrar
# claves_municipios = df_municipios["clave"].dropna().unique()
# df_no_municipios = df_total_last[~df_total_last["clave"].isin(claves_municipios)].copy()

# # Opcional: quitar columna "clave" si no la necesitas
# df_no_municipios = df_no_municipios.drop(columns=["clave"])
# df_municipios = df_municipios.drop(columns=["clave"])
# # df_no_municipios = df_total_last[~df_municipios].copy()

# # print(df_no_municipios["geo"].str[:10].unique())

# # # # Conteo de registros en cada subset
# # print(f"\nTotal registros no municipios:{len(df_no_municipios)}", # 50850
# #       f"\nTotal reigistros municipios:{len(df_municipios)}", # 238126 
# #       f"\nTotal registros finales: {len(df_no_municipios) + len(df_municipios)}") # 288976


# # Reemplazar 'Municipio de ' por cadena vacía al inicio del texto
# df_municipios["geo"] = df_municipios["geo"].str.replace(r"^Municipio de ", "", regex=True)
# # print(df_municipios["geo"].str[:10].unique())

# # # -----------------------
# # # Mapeo de municipios a códigos postales
# # # -----------------------

# # Crear un diccionario para mapear municipio a código postal
# municipio_a_codigo = {}

# # Extraer y mapear todos los registros con formato de código postal
# # Usar la columna limpia para crear el mapeo
# for item in df_municipios["geo"].dropna().unique():
#     match = re.match(r"^(\d{5})\s+(.*)", str(item))
#     if match:
#         codigo = match.group(1)
#         municipio = match.group(2).strip()
#         # Solo agrega al diccionario si el municipio no existe
#         if municipio not in municipio_a_codigo:
#             municipio_a_codigo[municipio] = codigo

# # print(f"Se crearon {len(municipio_a_codigo)} mapeos municipio -> código postal")

# # # Mostrar algunos ejemplos del mapeo
# # print("\nEjemplos de mapeos creados:")
# # for i, (municipio, codigo) in enumerate(list(municipio_a_codigo.items())[:5]):
# #     print(f"  '{municipio}' -> {codigo}")

# # print(df_municipios.nunique())
# # geo           861
# # tipo           40
# # periodo        43
# # valor        6957
# # fichero        37
# # clave      238464

# # # -----------------------
# # # Unir datos: Mapear municipios sin CP a su formato completo
# # # -----------------------

# def unir_municipio_a_cp(fila_original):
#     # Manejar valores NaN
#     if pd.isna(fila_original):
#         return fila_original
    
#     fila_str = str(fila_original)
    
#     # Si ya tiene el formato completo (empieza con 5 dígitos), mantenerlo
#     if re.match(r"^\d{5}", fila_str):
#         return fila_original
    
#     # Limpiar el formato para buscar en el diccionario
#     fila_limpia = re.sub(r"^[\s\-]+", "", fila_str)
#     fila_limpia = re.sub(r"^Municipio de ", "", fila_limpia)
    
#     # Buscar en el diccionario
#     if fila_limpia in municipio_a_codigo:
#         codigo = municipio_a_codigo[fila_limpia]
#         return f"{codigo} {fila_limpia}"
    
#     # Si no se encuentra mapeo, devolver el valor original limpio
#     # (esto mantiene los datos históricos pero con formato consistente)
#     else:
#         return fila_limpia

# # Aplicar la función a la columna 'geo' original
# df_municipios["geo"] = df_municipios["geo"].apply(unir_municipio_a_cp)

# # # Eliminar la columna auxiliar
# # df_municipios = df_municipios.drop('geo_limpia', axis=1)

# # # -----------------------
# # # Verificaciones
# # # -----------------------

# # print(f"\nRegistros finales: {len(df_municipios)}")

# # Verificar Badalona específicamente
# # filter_badalona = df_municipios["geo"].str.contains("Badalona", na=False)
# # print(f"\nRegistros de Badalona: {filter_badalona.sum()}")

# # print(df_municipios.iloc[300:310])
# # print(f"\ndinstict geo: {df_municipios['geo'].str[:9].unique()}")

# # aquellos registros que geo no empiecen por 5 dígitos
# # filter = ~df_municipios["geo"].str.match(r"^\d{5}", na=False)
# # print(df_municipios[filter]["geo"].unique())


# filter = df_municipios["geo"].str.contains("calatayud", na=False)
# # filter = df_municipios["geo"] == "Palma"
# # print(df_municipios[filter]["geo"].unique())

# # # -----------------------
# # # Armonizar df_no_municipios
# # # -----------------------

# # print(df_no_municipios.iloc[300:310])
# # print(f"\ndinstict geo: {df_no_municipios['geo'].str[:9].unique()}")

# def normalizar(texto):
#     if pd.isna(texto):
#         return None
#     texto = str(texto)
#     texto = texto.replace("'", "").replace("´", "").replace("`", "")
#     # normalizar tildes
#     texto = "".join(
#         c for c in unicodedata.normalize("NFD", texto)
#         if unicodedata.category(c) != "Mn"
#     )
#     # bajar a minúsculas y limpiar espacios
#     texto = texto.lower().strip()
#     texto = re.sub(r"\s+", " ", texto)  # colapsar espacios múltiples
#     return texto


# # -----------------------
# # Normalización
# # -----------------------
# df_no_municipios["geo_norm"] = df_no_municipios["geo"].map(normalizar)
# #geo_maestro["valor_norm"] = geo_maestro["Valor Original"].map(normalizar)
# print("\nMuestra df_municipios:")
# print(df_municipios.iloc[300:310])
# print("\nMuestra df_no_municipios:")
# print(df_no_municipios.iloc[300:310])


# # print("\nValores únicos (10 primeros caracteres): ",df_no_municipios["geo_norm"].unique(), "\n# de valores únicos: ", len(df_no_municipios["geo_norm"].str[:10].unique()))
# # Valores únicos (10 primeros caracteres):  ['andalucia' 'provincia de almeria' 'provincia de cadiz'
# #  'provincia de cordoba' 'provincia de granada' 'provincia de huelva'
# #  'provincia de jaen' 'provincia de malaga' 'provincia de sevilla' 'aragon'
# #  'provincia de huesca' 'provincia de teruel' 'provincia de zaragoza'
# #  'asturias (principado de)' 'balears (illes)' 'isla de formentera'
# #  'isla de eivissa' 'isla de mallorca' 'isla de menorca' 'canarias'
# #  'provincia de palmas (las)' 'isla de fuerteventura'
# #  'isla de gran canaria' 'isla de lanzarote'
# #  'provincia de santa cruz de tenerife' 'isla de gomera (la)'
# #  'isla de hierro (el)' 'isla de palma (la)' 'isla de tenerife' 'cantabria'
# #  'castilla y leon' 'provincia de avila' 'provincia de burgos'
# #  'provincia de leon' 'provincia de palencia' 'provincia de salamanca'
# #  'provincia de segovia' 'provincia de soria' 'provincia de valladolid'
# #  'provincia de zamora' 'castilla - la mancha' 'provincia de albacete'
# #  'provincia de ciudad real' 'provincia de cuenca'
# #  'provincia de guadalajara' 'provincia de toledo' 'cataluna'
# #  'provincia de barcelona' 'provincia de girona' 'provincia de lleida'
# #  'provincia de tarragona' 'comunitat valenciana'
# #  'provincia de alicante/alacant' 'provincia de castellon/castello'
# #  'provincia de valencia/valencia' 'extremadura' 'provincia de badajoz'
# #  'provincia de caceres' 'galicia' 'provincia de coruna (a)'
# #  'provincia de lugo' 'provincia de ourense' 'provincia de pontevedra'
# #  'madrid (comunidad de)' 'murcia (region de)'
# #  'navarra (comunidad foral de)' 'pais vasco' 'provincia de araba/alava'
# #  'provincia de gipuzkoa' 'provincia de bizkaia' 'rioja (la)'
# #  'ciudad autonoma de ceuta' 'ciudad autonoma de melilla'
# #  'en el extranjero' 'nacional' 'fuera de espana' 'extranjera'] 

# provincias_mapping = {
#     'provincia de almeria': 'Almería',
#     'provincia de cadiz': 'Cádiz',
#     'provincia de cordoba': 'Córdoba',
#     'provincia de granada': 'Granada',
#     'provincia de huelva': 'Huelva',
#     'provincia de jaen': 'Jaén',
#     'provincia de malaga': 'Málaga',
#     'provincia de sevilla': 'Sevilla',
#     'provincia de huesca': 'Huesca',
#     'provincia de teruel': 'Teruel',
#     'provincia de zaragoza': 'Zaragoza',
#     'provincia de palmas (las)': 'Palmas, Las',
#     'provincia de santa cruz de tenerife': 'Santa Cruz de Tenerife',
#     'provincia de avila': 'Ávila',
#     'provincia de burgos': 'Burgos',
#     'provincia de leon': 'León',
#     'provincia de palencia': 'Palencia',
#     'provincia de salamanca': 'Salamanca',
#     'provincia de segovia': 'Segovia',
#     'provincia de soria': 'Soria',
#     'provincia de valladolid': 'Valladolid',
#     'provincia de zamora': 'Zamora',
#     'provincia de albacete': 'Albacete',
#     'provincia de ciudad real': 'Ciudad Real',
#     'provincia de cuenca': 'Cuenca',
#     'provincia de guadalajara': 'Guadalajara',
#     'provincia de toledo': 'Toledo',
#     'provincia de barcelona': 'Barcelona',
#     'provincia de girona': 'Girona',
#     'provincia de lleida': 'Lleida',
#     'provincia de tarragona': 'Tarragona',
#     'provincia de alicante/alacant': 'Alicante/Alacant',
#     'provincia de castellon/castello': 'Castellón/Castelló',
#     'provincia de valencia/valencia': 'Valencia/València',
#     'provincia de badajoz': 'Badajoz',
#     'provincia de caceres': 'Cáceres',
#     'provincia de coruna (a)': 'Coruña, A',
#     'provincia de lugo': 'Lugo',
#     'provincia de ourense': 'Ourense',
#     'provincia de pontevedra': 'Pontevedra',
#     'provincia de araba/alava': 'Araba/Álava',
#     'provincia de gipuzkoa': 'Gipuzkoa',
#     'provincia de bizkaia': 'Bizkia'
# }

# comunidades_mapping = {
#     'andalucia': 'Andalucía',
#     'aragon': 'Aragón',
#     'asturias (principado de)': 'Asturias, Principado de',
#     'balears (illes)': 'Balears, Illes',
#     'canarias': 'Canarias',
#     'cantabria': 'Cantabria',
#     'castilla y leon': 'Castilla y León',
#     'castilla - la mancha': 'Castilla-La Mancha',
#     'cataluna': 'Cataluña',
#     'comunitat valenciana': 'Comunitat Valenciana',
#     'extremadura': 'Extremadura',
#     'galicia': 'Galicia',
#     'madrid (comunidad de)': 'Madrid, Comunidad de',
#     'murcia (region de)': 'Murcia, Región de',
#     'navarra (comunidad foral de)': 'Navarra, Comunidad Foral de',
#     'pais vasco': 'País Vasco',
#     'rioja (la)': 'Rioja, La',
#     'ciudad autonoma de ceuta': 'Ceuta',
#     'ciudad autonoma de melilla': 'Melilla'
# }


# islas_mapping = {
#     'isla de formentera': 'Balears, Illes',
#     'isla de eivissa': 'Balears, Illes',
#     'isla de mallorca': 'Balears, Illes',
#     'isla de menorca': 'Balears, Illes',
#     'isla de fuerteventura': 'Palmas, Las',
#     'isla de gran canaria': 'Palmas, Las',
#     'isla de lanzarote': 'Palmas, Las',
#     'isla de gomera (la)': 'Santa Cruz de Tenerife',
#     'isla de hierro (el)': 'Santa Cruz de Tenerife',
#     'isla de palma (la)': 'Santa Cruz de Tenerife',
#     'isla de tenerife': 'Santa Cruz de Tenerife'
# }







# # # -----------------------
# # # Merge
# # # -----------------------
# # df_geo = pd.merge(
# #     df_no_municipios,
# #     geo_maestro[["valor_norm", "Provincia", "Comunidad Autónoma"]],
# #     left_on="geo_norm",
# #     right_on="valor_norm",
# #     how="left"
# # ).drop(columns=["geo_norm", "valor_norm"])

# # # -----------------------
# # # Verificación de cruces
# # # -----------------------
# # no_cruzados = df_geo[df_geo["Provincia"].isna()]["geo"].unique()

# # print(f"\nTotal registros después del merge: {len(df_geo)}")
# # print(f"Valores de 'geo' sin cruce ({len(no_cruzados)}):")
# # for val in no_cruzados:
# #     print(f"  - {val}")

# # # -----------------------
# # # Guardar resultado
# # # -----------------------
# # # df_geo.to_csv("data/delitos_sin_mun_geo_maestro.csv", index=False)

# # # print("=== Provincias únicas ===")
# # # print(df_geo["Provincia"].dropna().unique())

# # # print("\n=== Comunidades Autónomas únicas ===")
# # # print(df_geo["Comunidad Autónoma"].dropna().unique())

# # # print(poblacion["PROVINCIA"].dropna().unique())




# # # Diccionario de correspondencia: {df_geo: (poblacion, comunidad_autonoma)}
# # equivalencias = {
# #     # Illes Balears
# #     "Balears (Illes)": ("Balears, Illes", "Illes Balears"),
# #     # Canarias
# #     "Las Palmas": ("Palmas, Las", "Canarias"),
# #     "Santa Cruz de Tenerife": ("Santa Cruz de Tenerife", "Canarias"),
# #     # Galicia
# #     "A Coruña": ("Coruña, A", "Galicia"),
# #     "Lugo": ("Lugo", "Galicia"),
# #     "Ourense": ("Ourense", "Galicia"),
# #     "Pontevedra": ("Pontevedra", "Galicia"),
# #     # Andalucía
# #     "Almería": ("Almería", "Andalucía"),
# #     "Cádiz": ("Cádiz", "Andalucía"),
# #     "Córdoba": ("Córdoba", "Andalucía"),
# #     "Granada": ("Granada", "Andalucía"),
# #     "Huelva": ("Huelva", "Andalucía"),
# #     "Jaén": ("Jaén", "Andalucía"),
# #     "Málaga": ("Málaga", "Andalucía"),
# #     "Sevilla": ("Sevilla", "Andalucía"),
# #     # Aragón
# #     "Huesca": ("Huesca", "Aragón"),
# #     "Teruel": ("Teruel", "Aragón"),
# #     "Zaragoza": ("Zaragoza", "Aragón"),
# #     # Asturias
# #     "Asturias": ("Asturias", "Principado de Asturias"),
# #     # Cantabria
# #     "Cantabria": ("Cantabria", "Cantabria"),
# #     # Castilla-La Mancha
# #     "Albacete": ("Albacete", "Castilla-La Mancha"),
# #     "Ciudad Real": ("Ciudad Real", "Castilla-La Mancha"),
# #     "Cuenca": ("Cuenca", "Castilla-La Mancha"),
# #     "Guadalajara": ("Guadalajara", "Castilla-La Mancha"),
# #     "Toledo": ("Toledo", "Castilla-La Mancha"),
# #     # Castilla y León
# #     "Ávila": ("Ávila", "Castilla y León"),
# #     "Burgos": ("Burgos", "Castilla y León"),
# #     "León": ("León", "Castilla y León"),
# #     "Palencia": ("Palencia", "Castilla y León"),
# #     "Salamanca": ("Salamanca", "Castilla y León"),
# #     "Segovia": ("Segovia", "Castilla y León"),
# #     "Soria": ("Soria", "Castilla y León"),
# #     "Valladolid": ("Valladolid", "Castilla y León"),
# #     "Zamora": ("Zamora", "Castilla y León"),
# #     # Cataluña
# #     "Barcelona": ("Barcelona", "Cataluña"),
# #     "Girona": ("Girona", "Cataluña"),
# #     "Lleida": ("Lleida", "Cataluña"),
# #     "Tarragona": ("Tarragona", "Cataluña"),
# #     # Ceuta y Melilla
# #     "Ciudad Autónoma de Ceuta": ("Ceuta", "Ciudad Autónoma de Ceuta"),
# #     "Ciudad Autónoma de Melilla": ("Melilla", "Ciudad Autónoma de Melilla"),
# #     # Comunitat Valenciana
# #     "Alicante/Alacant": ("Alicante/Alacant", "Comunitat Valenciana"),
# #     "Castellón/Castelló": ("Castellón/Castelló", "Comunitat Valenciana"),
# #     "Valencia/València": ("Valencia/València", "Comunitat Valenciana"),
# #     # Extremadura
# #     "Badajoz": ("Badajoz", "Extremadura"),
# #     "Cáceres": ("Cáceres", "Extremadura"),
# #     # Madrid
# #     "Madrid": ("Madrid", "Comunidad de Madrid"),
# #     # Murcia
# #     "Murcia": ("Murcia", "Región de Murcia"),
# #     # Navarra
# #     "Navarra": ("Navarra", "Comunidad Foral de Navarra"),
# #     # País Vasco
# #     "Araba/Álava": ("Araba/Álava", "País Vasco"),
# #     "Bizkaia": ("Bizkaia", "País Vasco"),
# #     "Gipuzkoa": ("Gipuzkoa", "País Vasco"),
# #     # La Rioja
# #     "La Rioja": ("Rioja, La", "La Rioja"),
# # }

# # # # Convertir a DataFrame para verlo claro
# # # df_equivalencias = pd.DataFrame([
# # #     {"Provincia_df_geo": k, "Provincia_poblacion": v[0], "Comunidad Autónoma": v[1]}
# # #     for k, v in equivalencias.items()
# # # ])

# # # # print(df_equivalencias)

# # # df_geo["pk"] = (
# # #     df_geo["geo"].astype(str) + "||" +
# # #     df_geo["año"].astype(str) + "||" +
# # #     df_geo["trimestre"].astype(str) + "||" +
# # #     df_geo["tipo_normalizado"].astype(str) + "||" +
# # #     df_geo["valor"].astype(str)
# # # )
# # # duplicados = df_geo[df_geo.duplicated(subset=["pk"], keep=False)].sort_values("pk")
# # # print(f"\nRegistros duplicados tras el merge: {len(duplicados)}")
# # # if len(duplicados) > 0:
# # #     print(duplicados)







# ============= CLAUDE ==============
import pandas as pd
import glob
import re
import unicodedata

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

# Encontrar el fichero más reciente para cada periodo
fichero_max_por_periodo = df_total.groupby("periodo")["fichero"].max().reset_index()

# Hacer merge para obtener todos los registros del fichero más reciente
df_total_last = df_total.merge(fichero_max_por_periodo, on=["periodo", "fichero"])

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

# Dividir el data set en municipio y no municipio
df_municipios = df_total_last[
                (df_total_last["geo"].str.match(r'^\d{5}', na=False)) |
                (df_total_last["geo"].str.contains(r'^\s*(?:[-–—]\s*)?muni[sc]ip[io]', case=False, na=False, regex=True))
                ].copy()

# Crear una clave combinada (ej: geo + periodo + tipología)
df_total_last["clave"] = df_total_last[["geo", "periodo", "tipo"]].apply(lambda x: "_".join(x.astype(str)), axis=1)
df_municipios["clave"] = df_municipios[["geo", "periodo", "tipo"]].apply(lambda x: "_".join(x.astype(str)), axis=1)

# Filtrar
claves_municipios = df_municipios["clave"].dropna().unique()
df_no_municipios = df_total_last[~df_total_last["clave"].isin(claves_municipios)].copy()

# Quitar columna "clave"
df_no_municipios = df_no_municipios.drop(columns=["clave"])
df_municipios = df_municipios.drop(columns=["clave"])

# Reemplazar 'Municipio de ' por cadena vacía al inicio del texto
df_municipios["geo"] = df_municipios["geo"].str.replace(r"^Municipio de ", "", regex=True)

# -----------------------
# Mapeo de municipios a códigos postales
# -----------------------

# Crear un diccionario para mapear municipio a código postal
municipio_a_codigo = {}

# Extraer y mapear todos los registros con formato de código postal
for item in df_municipios["geo"].dropna().unique():
    match = re.match(r"^(\d{5})\s+(.*)", str(item))
    if match:
        codigo = match.group(1)
        municipio = match.group(2).strip()
        # Solo agrega al diccionario si el municipio no existe
        if municipio not in municipio_a_codigo:
            municipio_a_codigo[municipio] = codigo

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
    else:
        return fila_limpia

# Aplicar la función a la columna 'geo' original
df_municipios["geo"] = df_municipios["geo"].apply(unir_municipio_a_cp)

# -----------------------
# Armonizar df_no_municipios
# -----------------------

def normalizar(texto):
    if pd.isna(texto):
        return None
    texto = str(texto)
    texto = texto.replace("'", "").replace("´", "").replace("`", "")
    # normalizar tildes
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    # bajar a minúsculas y limpiar espacios
    texto = texto.lower().strip()
    texto = re.sub(r"\s+", " ", texto)  # colapsar espacios múltiples
    return texto

# Normalización para matching
df_no_municipios["geo_norm"] = df_no_municipios["geo"].map(normalizar)

# Mappings para armonizar nombres
provincias_mapping = {
    'provincia de almeria': 'Almería',
    'provincia de cadiz': 'Cádiz',
    'provincia de cordoba': 'Córdoba',
    'provincia de granada': 'Granada',
    'provincia de huelva': 'Huelva',
    'provincia de jaen': 'Jaén',
    'provincia de malaga': 'Málaga',
    'provincia de sevilla': 'Sevilla',
    'provincia de huesca': 'Huesca',
    'provincia de teruel': 'Teruel',
    'provincia de zaragoza': 'Zaragoza',
    'provincia de palmas (las)': 'Palmas, Las',
    'provincia de santa cruz de tenerife': 'Santa Cruz de Tenerife',
    'provincia de avila': 'Ávila',
    'provincia de burgos': 'Burgos',
    'provincia de leon': 'León',
    'provincia de palencia': 'Palencia',
    'provincia de salamanca': 'Salamanca',
    'provincia de segovia': 'Segovia',
    'provincia de soria': 'Soria',
    'provincia de valladolid': 'Valladolid',
    'provincia de zamora': 'Zamora',
    'provincia de albacete': 'Albacete',
    'provincia de ciudad real': 'Ciudad Real',
    'provincia de cuenca': 'Cuenca',
    'provincia de guadalajara': 'Guadalajara',
    'provincia de toledo': 'Toledo',
    'provincia de barcelona': 'Barcelona',
    'provincia de girona': 'Girona',
    'provincia de lleida': 'Lleida',
    'provincia de tarragona': 'Tarragona',
    'provincia de alicante/alacant': 'Alicante/Alacant',
    'provincia de castellon/castello': 'Castellón/Castelló',
    'provincia de valencia/valencia': 'Valencia/València',
    'provincia de badajoz': 'Badajoz',
    'provincia de caceres': 'Cáceres',
    'provincia de coruna (a)': 'Coruña, A',
    'provincia de lugo': 'Lugo',
    'provincia de ourense': 'Ourense',
    'provincia de pontevedra': 'Pontevedra',
    'provincia de araba/alava': 'Araba/Álava',
    'provincia de gipuzkoa': 'Gipuzkoa',
    'provincia de bizkaia': 'Bizkaia'
}

comunidades_mapping = {
    'andalucia': 'Andalucía',
    'aragon': 'Aragón',
    'asturias (principado de)': 'Asturias, Principado de',
    'balears (illes)': 'Balears, Illes',
    'canarias': 'Canarias',
    'cantabria': 'Cantabria',
    'castilla y leon': 'Castilla y León',
    'castilla - la mancha': 'Castilla-La Mancha',
    'cataluna': 'Cataluña',
    'comunitat valenciana': 'Comunitat Valenciana',
    'extremadura': 'Extremadura',
    'galicia': 'Galicia',
    'madrid (comunidad de)': 'Madrid, Comunidad de',
    'murcia (region de)': 'Murcia, Región de',
    'navarra (comunidad foral de)': 'Navarra, Comunidad Foral de',
    'pais vasco': 'País Vasco',
    'rioja (la)': 'Rioja, La',
    'ciudad autonoma de ceuta': 'Ceuta',
    'ciudad autonoma de melilla': 'Melilla'
}

islas_mapping = {
    'isla de formentera': 'Balears, Illes',
    'isla de eivissa': 'Balears, Illes',
    'isla de mallorca': 'Balears, Illes',
    'isla de menorca': 'Balears, Illes',
    'isla de fuerteventura': 'Palmas, Las',
    'isla de gran canaria': 'Palmas, Las',
    'isla de lanzarote': 'Palmas, Las',
    'isla de gomera (la)': 'Santa Cruz de Tenerife',
    'isla de hierro (el)': 'Santa Cruz de Tenerife',
    'isla de palma (la)': 'Santa Cruz de Tenerife',
    'isla de tenerife': 'Santa Cruz de Tenerife'
}

# Aplicar mappings para crear columnas normalizadas
def aplicar_mapping(geo_norm):
    if pd.isna(geo_norm):
        return None, None, None
    
    # Primero comprobar si es una provincia
    if geo_norm in provincias_mapping:
        provincia = provincias_mapping[geo_norm]
        return provincia, None, 'Provincial'
    
    # Comprobar si es una comunidad autónoma
    elif geo_norm in comunidades_mapping:
        ccaa = comunidades_mapping[geo_norm]
        return None, ccaa, 'Autonómico'
    
    # Comprobar si es una isla (mapear a su provincia)
    elif geo_norm in islas_mapping:
        provincia = islas_mapping[geo_norm]
        return provincia, None, 'Provincial'
    
    # Casos especiales
    elif geo_norm == 'nacional':
        return None, None, 'Nacional'
    elif geo_norm in ['en el extranjero', 'fuera de espana', 'extranjera']:
        return None, None, 'Extranjero'
    
    # Si no encuentra match, devolver el valor original
    else:
        return None, None, 'Sin clasificar'

# Aplicar la función y crear nuevas columnas
df_no_municipios[['provincia_normalizada', 'ccaa_normalizada', 'nivel']] = df_no_municipios['geo_norm'].apply(
    lambda x: pd.Series(aplicar_mapping(x))
)

# -----------------------
# PREPARAR MUNICIPIOS PARA MERGE CON POBLACIÓN
# -----------------------

def extraer_codigo_municipio(geo):
    """Extrae el código de municipio (CPRO + CMUN) del campo geo"""
    if pd.isna(geo):
        return None, None, None
    
    match = re.match(r"^(\d{2})(\d{3})\s+(.*)", str(geo))
    if match:
        cpro = match.group(1)
        cmun = match.group(2)
        municipio = match.group(3).strip()
        return cpro, cmun, municipio
    else:
        return None, None, str(geo)

# Aplicar extracción a municipios
df_municipios[['cpro', 'cmun', 'municipio_nombre']] = df_municipios['geo'].apply(
    lambda x: pd.Series(extraer_codigo_municipio(x))
)

# Agregar información de nivel para municipios
df_municipios['nivel'] = 'Municipal'

# -----------------------
# EXTRAER AÑO Y TRIMESTRE DEL PERIODO
# -----------------------

def extraer_año_trimestre(periodo):
    """Extrae año y trimestre del campo periodo"""
    if pd.isna(periodo):
        return None, None
    
    # Buscar año (4 dígitos)
    year_match = re.search(r'(\d{4})', str(periodo))
    año = int(year_match.group(1)) if year_match else None
    
    # Determinar trimestre basado en los meses mencionados
    periodo_lower = str(periodo).lower()
    if 'enero-marzo' in periodo_lower:
        trimestre = 1
    elif 'enero-junio' in periodo_lower:
        trimestre = 2
    elif 'enero-septiembre' in periodo_lower:
        trimestre = 3
    elif 'enero-diciembre' in periodo_lower:
        trimestre = 4
    else:
        trimestre = None
    
    return año, trimestre

# Aplicar a ambos dataframes
df_municipios[['año', 'trimestre']] = df_municipios['periodo'].apply(
    lambda x: pd.Series(extraer_año_trimestre(x))
)

df_no_municipios[['año', 'trimestre']] = df_no_municipios['periodo'].apply(
    lambda x: pd.Series(extraer_año_trimestre(x))
)

# -----------------------
# UNIR DATAFRAMES
# -----------------------

# Agregar columnas faltantes para poder unir
df_municipios['provincia_normalizada'] = None
df_municipios['ccaa_normalizada'] = None
df_municipios['geo_norm'] = None

df_no_municipios['cpro'] = None
df_no_municipios['cmun'] = None
df_no_municipios['municipio_nombre'] = None

# Seleccionar columnas comunes para la unión
columnas_comunes = [
    'geo', 'tipo', 'periodo', 'valor', 'fichero', 'año', 'trimestre', 'nivel',
    'cpro', 'cmun', 'municipio_nombre', 'provincia_normalizada', 'ccaa_normalizada', 'geo_norm'
]

df_delitos_completo = pd.concat([
    df_municipios[columnas_comunes],
    df_no_municipios[columnas_comunes]
], ignore_index=True)

# print("=== RESUMEN DEL DATASET FINAL ===")
# print(f"Total de registros: {len(df_delitos_completo):,}")
# print(f"Registros municipales: {len(df_municipios):,}")
# print(f"Registros no municipales: {len(df_no_municipios):,}")
# print(f"\nNiveles únicos: {df_delitos_completo['nivel'].value_counts()}")
# print(f"\nAños disponibles: {sorted(df_delitos_completo['año'].dropna().unique())}")
# print(f"Trimestres disponibles: {sorted(df_delitos_completo['trimestre'].dropna().unique())}")

# -----------------------
# PREPARAR PARA MERGE CON POBLACIÓN
# -----------------------

def preparar_para_poblacion(df_poblacion_path):
    """
    Función para hacer merge con los datos de población
    df_poblacion_path: ruta al archivo de población con formato CSV
    """
    
    # Leer datos de población
    df_poblacion = pd.read_csv(df_poblacion_path, sep=';', encoding='utf-8')
    
    # print("=== PREPARANDO MERGE CON POBLACIÓN ===")
    # print(f"Registros en población: {len(df_poblacion):,}")
    
    # Crear claves de merge para cada nivel
    
    # 1. Nivel Municipal: AÑO + CPRO + CMUN
    delitos_municipales = df_delitos_completo[
        (df_delitos_completo['nivel'] == 'Municipal') & 
        df_delitos_completo['cpro'].notna() & 
        df_delitos_completo['cmun'].notna()
    ].copy()
    
    poblacion_municipal = df_poblacion[df_poblacion['NIVEL'] == 'Municipal'].copy()
    
    # Merge municipal
    if len(delitos_municipales) > 0 and len(poblacion_municipal) > 0:
        merge_municipal = delitos_municipales.merge(
            poblacion_municipal,
            left_on=['año', 'cpro', 'cmun'],
            right_on=['AÑO', 'CPRO', 'CMUN'],
            how='left'
        )
        # print(f"Merge municipal: {len(merge_municipal):,} registros")
    
    # 2. Nivel Provincial: AÑO + PROVINCIA
    delitos_provinciales = df_delitos_completo[
        df_delitos_completo['nivel'] == 'Provincial'
    ].copy()
    
    poblacion_provincial = df_poblacion[df_poblacion['NIVEL'] == 'Provincial'].copy()
    
    # 3. Nivel Autonómico: AÑO + CCAA  
    delitos_autonomicos = df_delitos_completo[
        df_delitos_completo['nivel'] == 'Autonómico'
    ].copy()
    
    poblacion_autonomica = df_poblacion[df_poblacion['NIVEL'] == 'Autonómico'].copy()
    
    # 4. Nivel Nacional
    delitos_nacionales = df_delitos_completo[
        df_delitos_completo['nivel'] == 'Nacional'
    ].copy()
    
    poblacion_nacional = df_poblacion[df_poblacion['NIVEL'] == 'Nacional'].copy()
    
    return df_delitos_completo, df_poblacion


# print("\n=== Archivo guardado: data/delitos_armonizado_completo.csv ===")

# # Mostrar muestra del resultado final
# print("\n=== MUESTRA DEL DATASET FINAL ===")
# print("Municipales:")
# print(df_delitos_completo[df_delitos_completo['nivel'] == 'Municipal'].head())
# print("\nProvinciales:")
# print(df_delitos_completo[df_delitos_completo['nivel'] == 'Provincial'].head())
# print("\nAutonómicos:")
# print(df_delitos_completo[df_delitos_completo['nivel'] == 'Autonómico'].head())

df_delitos_completo['cp'] = df_delitos_completo['cpro'].astype(str).str.zfill(2) + df_delitos_completo['cmun'].astype(str).str.zfill(3)

# Eliminar columnas auxiliares
df_delitos_completo = df_delitos_completo.drop(columns=['geo', 'cpro','cmun','geo_norm','fichero'])
# Renombrar columnas
df_delitos_completo = df_delitos_completo.rename(columns={
    'municipio_nombre': 'municipio',
    'provincia_normalizada': 'provincia',
    'ccaa_normalizada': 'ccaa'      
})




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


df_delitos_completo["tipo_normalizado"] = df_delitos_completo["tipo"].apply(normalizar_tipologia)

# drop columna tipo original
df_delitos_completo = df_delitos_completo.drop(columns=["tipo"])
# filtro = df["geo"].str.contains("Badalona") & df["año"].isin([2022]) & df["trimestre"].isin(["T4"]) & df["tipo_normalizado"].str.contains("Hurtos")
# # imprimir el dataframe filtrado
# print(df[filtro])


# print("\n=== MUESTRA DEL DATASET FINAL LIMPIO ===")
# print(df_delitos_completo.head())

# print(df_delitos_completo['cp'].unique())

# Guardar resultado intermedio
df_delitos_completo.to_csv("data/delitos_armonizado_completo.csv", index=False, encoding='utf-8')