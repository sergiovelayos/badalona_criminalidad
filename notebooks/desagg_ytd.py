import pandas as pd

pd.set_option("display.max_columns", None)

# La ruta a tu archivo CSV
csv_file = r"./data/delitos_raw_merged.csv"

# Leemos el archivo directamente desde su ruta.Seleccionar columnas en el read_csv
df = pd.read_csv(csv_file, sep=';', usecols=[0,1,2,3])

df.columns = ["geo", "tipo", "periodo", "valor"]

# # Filtramos solo Badalona
# df = df[df["geo"].str.contains("Badalona")]

# # Limpiar geo. Eliminar '-Municipio de ' o '- Municipio de'
# df["geo"] = df["geo"].str.replace(r"-\s*Municipio de\s*", "", regex=True).str.strip()

# df["geo"] = df["geo"].replace("Badalona", "08015 Badalona").str.strip()


# print(df["geo"].value_counts())

# print("Info:\n",data_grouped.info(), "Head:\n", data_grouped.head(10))

# Excluir periodos que contengan 'Variación' o 'tasa' (no son datos de conteo)
df = df[~df["periodo"].str.contains("Variación", case=False, na=False)]

# Normalizar 'periodo'
df["periodo"] = df["periodo"].str.strip().str.lower()

# print(df["periodo"].value_counts())


# Mapear periodos
map_periodos = {
    "enero-marzo": "T1",
    "enero-junio": "T2",
    "enero-septiembre": "T3",
    "enero-diciembre": "T4",
    "enero--diciembre": "T4"
}

def parse_periodo(p):
    for k, v in map_periodos.items():
        if p.startswith(k):
            año = p.split()[-1]
            return int(año), v
    return None, None

df = df.copy()
df[["año", "trimestre"]] = df["periodo"].apply(lambda x: pd.Series(parse_periodo(x)))

# --- 2. Pivotear acumulados por municipio, tipología y año
tabla = (
    df.pivot_table(
        index=["geo", "tipo", "año"],
        columns="trimestre",
        values="valor",
        aggfunc="sum"   # por si hay duplicados
    )
)

# Filtrar T3 y T4 en 2025 nulos
# tabla = tabla[~(tabla["T3"].isna() & tabla["T4"].isna() & tabla["año"] == 2025)]

# tabla = tabla[~(
#     (tabla["T3"].isna()) & 
#     (tabla["T4"].isna()) & 
#     (tabla["año"] == 2025)
# )]

# --- 3. Calcular trimestres reales (desacumulados)
tabla_desacum = pd.DataFrame(index=tabla.index)
tabla_desacum["T1"] = tabla["T1"]
tabla_desacum["T2"] = tabla["T2"] - tabla["T1"]
tabla_desacum["T3"] = tabla["T3"] - tabla["T2"]
tabla_desacum["T4"] = tabla["T4"] - tabla["T3"]

# --- 4. Pasar de tabla pivotada a formato largo (plano)
result = tabla_desacum.reset_index().melt(
    id_vars=["geo", "tipo", "año"],
    value_vars=["T1", "T2", "T3", "T4"],
    var_name="trimestre",
    value_name="valor"
).dropna(subset=["valor"])  # quitar trimestres vacíos

result.to_csv("./data/esp_desagg_ytd.csv", index=False, encoding="utf-8")

# print("Info:\n",result.info(), "Head:\n", result.head(10))

# print(result[result["tipo"].str.contains("robo", case=False)])

# print(result["tipo"].value_counts().sort_values(ascending=False))
