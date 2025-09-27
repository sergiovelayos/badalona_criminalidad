import pandas as pd
import unicodedata
import re

pd.set_option("display.max_columns", None)

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

# -----------------------
# Lectura
# -----------------------
df = pd.read_csv("./data/esp_desagg_ytd_normalizado.csv", sep=",")
geo_maestro = pd.read_csv("./data/maestro_geo_provincia_ccaa.csv")
poblacion = pd.read_csv("./data/pobmunanual.csv", sep=";")

# print(f"\nTotal registros iniciales: \ndf {len(df)} \ngeo_maestro {len(geo_maestro)}")




print(poblacion.head())





# # -----------------------
# # Filtro: quitar municipios
# # -----------------------
# df_filtrado = df[
#     ~(df["geo"].str.match(r'^\d{5}', na=False)) &
#     ~(df["geo"].str.contains(r'^\s*(?:[-–—]\s*)?muni[sc]ip[io]', case=False, na=False, regex=True))
# ].copy()

# # -----------------------
# # Normalización
# # -----------------------
# df_filtrado["geo_norm"] = df_filtrado["geo"].map(normalizar)
# geo_maestro["valor_norm"] = geo_maestro["Valor Original"].map(normalizar)

# # -----------------------
# # Merge
# # -----------------------
# df_geo = pd.merge(
#     df_filtrado,
#     geo_maestro[["valor_norm", "Provincia", "Comunidad Autónoma"]],
#     left_on="geo_norm",
#     right_on="valor_norm",
#     how="left"
# ).drop(columns=["geo_norm", "valor_norm"])

# # -----------------------
# # Verificación de cruces
# # -----------------------
# no_cruzados = df_geo[df_geo["Provincia"].isna()]["geo"].unique()

# # print(f"\nTotal registros después del merge: {len(df_geo)}")
# # print(f"Valores de 'geo' sin cruce ({len(no_cruzados)}):")
# # for val in no_cruzados:
# #     print(f"  - {val}")

# # -----------------------
# # Guardar resultado
# # -----------------------
# # df_geo.to_csv("data/delitos_sin_mun_geo_maestro.csv", index=False)

# # print("=== Provincias únicas ===")
# # print(df_geo["Provincia"].dropna().unique())

# # print("\n=== Comunidades Autónomas únicas ===")
# # print(df_geo["Comunidad Autónoma"].dropna().unique())

# # print(poblacion["PROVINCIA"].dropna().unique())




# # Diccionario de correspondencia: {df_geo: (poblacion, comunidad_autonoma)}
# equivalencias = {
#     # Illes Balears
#     "Balears (Illes)": ("Balears, Illes", "Illes Balears"),
#     # Canarias
#     "Las Palmas": ("Palmas, Las", "Canarias"),
#     "Santa Cruz de Tenerife": ("Santa Cruz de Tenerife", "Canarias"),
#     # Galicia
#     "A Coruña": ("Coruña, A", "Galicia"),
#     "Lugo": ("Lugo", "Galicia"),
#     "Ourense": ("Ourense", "Galicia"),
#     "Pontevedra": ("Pontevedra", "Galicia"),
#     # Andalucía
#     "Almería": ("Almería", "Andalucía"),
#     "Cádiz": ("Cádiz", "Andalucía"),
#     "Córdoba": ("Córdoba", "Andalucía"),
#     "Granada": ("Granada", "Andalucía"),
#     "Huelva": ("Huelva", "Andalucía"),
#     "Jaén": ("Jaén", "Andalucía"),
#     "Málaga": ("Málaga", "Andalucía"),
#     "Sevilla": ("Sevilla", "Andalucía"),
#     # Aragón
#     "Huesca": ("Huesca", "Aragón"),
#     "Teruel": ("Teruel", "Aragón"),
#     "Zaragoza": ("Zaragoza", "Aragón"),
#     # Asturias
#     "Asturias": ("Asturias", "Principado de Asturias"),
#     # Cantabria
#     "Cantabria": ("Cantabria", "Cantabria"),
#     # Castilla-La Mancha
#     "Albacete": ("Albacete", "Castilla-La Mancha"),
#     "Ciudad Real": ("Ciudad Real", "Castilla-La Mancha"),
#     "Cuenca": ("Cuenca", "Castilla-La Mancha"),
#     "Guadalajara": ("Guadalajara", "Castilla-La Mancha"),
#     "Toledo": ("Toledo", "Castilla-La Mancha"),
#     # Castilla y León
#     "Ávila": ("Ávila", "Castilla y León"),
#     "Burgos": ("Burgos", "Castilla y León"),
#     "León": ("León", "Castilla y León"),
#     "Palencia": ("Palencia", "Castilla y León"),
#     "Salamanca": ("Salamanca", "Castilla y León"),
#     "Segovia": ("Segovia", "Castilla y León"),
#     "Soria": ("Soria", "Castilla y León"),
#     "Valladolid": ("Valladolid", "Castilla y León"),
#     "Zamora": ("Zamora", "Castilla y León"),
#     # Cataluña
#     "Barcelona": ("Barcelona", "Cataluña"),
#     "Girona": ("Girona", "Cataluña"),
#     "Lleida": ("Lleida", "Cataluña"),
#     "Tarragona": ("Tarragona", "Cataluña"),
#     # Ceuta y Melilla
#     "Ciudad Autónoma de Ceuta": ("Ceuta", "Ciudad Autónoma de Ceuta"),
#     "Ciudad Autónoma de Melilla": ("Melilla", "Ciudad Autónoma de Melilla"),
#     # Comunitat Valenciana
#     "Alicante/Alacant": ("Alicante/Alacant", "Comunitat Valenciana"),
#     "Castellón/Castelló": ("Castellón/Castelló", "Comunitat Valenciana"),
#     "Valencia/València": ("Valencia/València", "Comunitat Valenciana"),
#     # Extremadura
#     "Badajoz": ("Badajoz", "Extremadura"),
#     "Cáceres": ("Cáceres", "Extremadura"),
#     # Madrid
#     "Madrid": ("Madrid", "Comunidad de Madrid"),
#     # Murcia
#     "Murcia": ("Murcia", "Región de Murcia"),
#     # Navarra
#     "Navarra": ("Navarra", "Comunidad Foral de Navarra"),
#     # País Vasco
#     "Araba/Álava": ("Araba/Álava", "País Vasco"),
#     "Bizkaia": ("Bizkaia", "País Vasco"),
#     "Gipuzkoa": ("Gipuzkoa", "País Vasco"),
#     # La Rioja
#     "La Rioja": ("Rioja, La", "La Rioja"),
# }

# # Convertir a DataFrame para verlo claro
# df_equivalencias = pd.DataFrame([
#     {"Provincia_df_geo": k, "Provincia_poblacion": v[0], "Comunidad Autónoma": v[1]}
#     for k, v in equivalencias.items()
# ])

# # print(df_equivalencias)

# df_geo["pk"] = (
#     df_geo["geo"].astype(str) + "||" +
#     df_geo["año"].astype(str) + "||" +
#     df_geo["trimestre"].astype(str) + "||" +
#     df_geo["tipo_normalizado"].astype(str) + "||" +
#     df_geo["valor"].astype(str)
# )
# duplicados = df_geo[df_geo.duplicated(subset=["pk"], keep=False)].sort_values("pk")
# print(f"\nRegistros duplicados tras el merge: {len(duplicados)}")
# if len(duplicados) > 0:
#     print(duplicados)