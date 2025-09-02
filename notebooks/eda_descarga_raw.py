import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
from io import StringIO

pd.set_option("display.max_columns", None)

# -----------------------
# Lector de CSV mixto (filas UTF-8 y Latin-1 mezcladas)
# -----------------------
def leer_csv_mixto(ruta, sep=";", skiprows=0, **kwargs):
    """
    Lee un CSV donde algunas filas están en UTF-8 y otras en Latin-1.
    Devuelve un DataFrame de pandas.
    """
    filas = []
    with open(ruta, "rb") as f:
        for raw_line in f:
            try:
                line = raw_line.decode("utf-8")
            except UnicodeDecodeError:
                line = raw_line.decode("latin-1")
            filas.append(line)
    contenido = "".join(filas)
    return pd.read_csv(StringIO(contenido), sep=sep, skiprows=skiprows, **kwargs)

# -----------------------
# Rutas
# -----------------------
filename = r"./data/crim_merged.csv"               # separador ';', salta 1 fila
filepob  = r"./data/pobmun24_limpio.csv"     # separador desconocido (auto)

# -----------------------
# Lectura y limpieza del fichero principal
# -----------------------
data = leer_csv_mixto(filename, sep=";", skiprows=1)

# Renombrar columnas
data.columns = ["geografía", "tipología", "periodo", "valor"]

# valor → numérico (quita miles '.' y usa ',' como decimal)
data["valor"] = pd.to_numeric(
    data["valor"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
    errors="coerce"
)

# Extraer código de 5 dígitos que encabeza el municipio (código INE municipal)
data["cp"] = data["geografía"].str.extract(r"(\b\d{5}\b)")

# Nombre de municipio sin el código delante
data["población"] = data["geografía"].str.replace(r"^\d{5}\s*", "", regex=True).str.strip()

# Provincia (si el texto empieza por 'Provincia')
data["provincia"] = data["geografía"].where(data["geografía"].str.startswith("Provincia"))

# # Filtrar provincia de Barcelona (códigos que empiezan por 08) -- ADAPTAR
# bcn = data[data["cp"].str.startswith("08", na=False)].copy()

# Normalizar 'periodo'
data["periodo"] = data["periodo"].str.strip().str.lower()

# Agrupar
data_grouped = (
    data.groupby(["periodo", "población", "tipología", "cp"])["valor"]
    .sum()
    .reset_index()
    .sort_values(["población", "tipología"], ascending=[True, False])
)

# -----------------------
# Lectura del fichero de población
#   - autodetectar separador (sep=None + engine="python")
#   - arreglar 'cod_mun' para que sea string de 5 dígitos con ceros
#   - si no hay 'cod_mun', lo extrae de 'Municipios' (p.ej. '08001 Abrera')
# -----------------------
poblacion = leer_csv_mixto(filepob, sep=None, engine="python")  # sniff del separador

# Normaliza nombres de columna a minúsculas sin espacios exteriores
poblacion.columns = [c.strip().lower() for c in poblacion.columns]

# Armoniza nombres esperados
# (permitimos 'municipios' o 'municipio', y 'total' para población total)
if "municipios" not in poblacion.columns and "municipio" in poblacion.columns:
    poblacion = poblacion.rename(columns={"municipio": "municipios"})

# Si existe 'cod_mun', lo normalizamos; si no, lo generamos desde 'municipios'
if "cod_mun" in poblacion.columns:
    # Paso 1: forzar a string
    poblacion["cod_mun"] = poblacion["cod_mun"].astype(str)

    # Paso 2: eliminar '.0' heredado de float y extraer dígitos
    poblacion["cod_mun"] = (
        poblacion["cod_mun"]
        .str.replace(r"\.0$", "", regex=True)     # '8001.0' -> '8001'
        .str.extract(r"(\d+)", expand=False)      # deja solo dígitos
        .fillna("")                               # por seguridad
        .str.zfill(5)                             # '8001' -> '08001'
    )
else:
    # Intento crear 'cod_mun' desde 'municipios' (si viene '08001 Abrera')
    if "municipios" in poblacion.columns:
        poblacion["cod_mun"] = (
            poblacion["municipios"].astype(str).str.extract(r"^\s*(\d{5})", expand=False)
        )
    else:
        raise ValueError(
            "No se encontró 'cod_mun' ni 'Municipios' en el fichero de población. "
            "No se puede construir la clave de cruce."
        )

# Asegura 'total' como numérico (población total)
if "pob24" in poblacion.columns:
    poblacion["pob24"] = pd.to_numeric(poblacion["pob24"], errors="coerce")
else:
    raise ValueError("La columna 'pob24' no existe en el fichero de población.")

# -----------------------
# Normalizar claves de cruce a 5 dígitos
# -----------------------
data_grouped["cp"] = (
    data_grouped["cp"]
    .astype(str)
    .str.extract(r"(\d+)", expand=False)
    .fillna("")
    .str.zfill(5)
)

poblacion["cod_mun"] = (
    poblacion["cod_mun"]
    .astype(str)
    .str.extract(r"(\d+)", expand=False)
    .fillna("")
    .str.zfill(5)
)

# -----------------------
# Merge
# -----------------------
data_grouped = data_grouped.merge(
    poblacion[["cod_mun", "pob24"]],  # solo lo necesario
    left_on="cp",
    right_on="cod_mun",
    how="left"
)

# Limpiar columnas y renombrar
if "cod_mun" in data_grouped.columns:
    data_grouped = data_grouped.drop(columns=["cod_mun"])
data_grouped = data_grouped.rename(columns={"población": "municipio", "pob24": "población"})

# # -----------------------
# # Diagnóstico de cruce
# # -----------------------
# en_poblacion = set(poblacion["cod_mun"].dropna())
# en_bcn = set(data_grouped["cp"].dropna())

# matched = len(en_bcn.intersection(en_poblacion))
# missing = sorted(list(en_bcn.difference(en_poblacion)))[:20]

# print(f"CP únicos en data_grouped: {len(en_bcn)}")
# print(f"Códigos únicos en población: {len(en_poblacion)}")
# print(f"Coincidencias (intersección): {matched}")
# if missing:
#     print(f"Códigos sin cruce (muestra): {missing}")

# -----------------------
# Métrica: ratio por cada 100 habitantes
# -----------------------
data_grouped["valor_ratio"] = ((data_grouped["valor"] / data_grouped["población"]) * 100).round(2)

# Eliminar filas que empiecen con 'variación'
data_grouped = data_grouped[~data_grouped['periodo'].str.contains('^variación', regex=True)]



# # -----------------------
# # Exportar resultados (UTF-8 limpio)
# # -----------------------
# os.makedirs("./data", exist_ok=True)
# data_grouped.to_csv("./data/criminalidad_join_1.csv", index=False, encoding="utf-8")
# print(data_grouped[(data_grouped["municipio"].str.lower() == "badalona") & 
# (data_grouped["tipología"] == "III. TOTAL INFRACCIONES PENALES") 
# # (data_grouped["periodo"].str.endswith("2024")) 
# ].sort_values("periodo"))

# -----------------------
# Gráfica opcional
# -----------------------
def plot_heatmap_by_tipologia(tipologia, df=data_grouped, top_n=20):
    filtered = df[df["tipología"] == tipologia].dropna(subset=["valor_ratio"])
    top = filtered.sort_values("valor_ratio", ascending=False).head(top_n)
    if top.empty:
        print(f"No hay datos para la tipología '{tipologia}'.")
        return
    os.makedirs("./charts", exist_ok=True)
    plt.figure(figsize=(10, 8))
    heatmap_data = top.pivot_table(index="municipio", values="valor_ratio", aggfunc="first")
    sns.heatmap(
        heatmap_data,
        annot=True,
        cmap="YlOrRd",
        fmt=".2f",
        linewidths=.5,
        cbar_kws={"label": "Ratio (%)"},
    )
    plt.title(f"Top {top_n} municipios por '{tipologia}' (valor_ratio)")
    plt.xlabel("Tipología")
    plt.ylabel("Municipio")
    plt.tight_layout()
    filename = f'./charts/heatmap_{tipologia.replace(".", "").replace(" ", "_").lower()}.png'
    plt.savefig(filename)
    plt.close()
    print(f"Mapa de calor guardado en {filename}")
# Ejemplo de uso
# plot_heatmap_by_tipologia("Hurtos")

# -----------------------
# Calcular delitos por trimestre
# -----------------------

# # Filtrar con copia para evitar warnings
# badalona_df = data_grouped[
#     (data_grouped["municipio"].str.lower() == "badalona")
#     & (data_grouped["tipología"] == "III. TOTAL INFRACCIONES PENALES")
# ].copy()

# Mapear periodos
map_periodos = {
    "enero-marzo": "Q1",
    "enero-junio": "Q2",
    "enero-septiembre": "Q3",
    "enero-diciembre": "Q4",
    "enero--diciembre": "Q4"
}

def parse_periodo(p):
    for k, v in map_periodos.items():
        if p.startswith(k):
            año = p.split()[-1]
            return int(año), v
    return None, None

df = data_grouped.copy()
df[["año", "trimestre"]] = df["periodo"].apply(lambda x: pd.Series(parse_periodo(x)))

# --- 2. Pivotear acumulados por municipio, tipología y año
tabla = (
    df.pivot_table(
        index=["cp","municipio", "tipología", "población", "año"],
        columns="trimestre",
        values="valor",
        aggfunc="sum"   # por si hay duplicados
    )
)

# --- 3. Calcular trimestres reales (desacumulados)
tabla_desacum = pd.DataFrame(index=tabla.index)
tabla_desacum["Q1"] = tabla["Q1"]
tabla_desacum["Q2"] = (tabla["Q2"] - tabla["Q1"]).round(0)
tabla_desacum["Q3"] = ( tabla["Q3"] - tabla["Q2"] ).round(0)
tabla_desacum["Q4"] = ( tabla["Q4"] - tabla["Q3"] ).round(0)

# --- 4. Pasar de tabla pivotada a formato largo (plano)
result = tabla_desacum.reset_index().melt(
    id_vars=["cp","municipio", "tipología", "población", "año"],
    value_vars=["Q1", "Q2", "Q3", "Q4"],
    var_name="trimestre",
    value_name="valor"
).dropna(subset=["valor"])  # quitar trimestres vacíos

# result.to_csv("./data/crims_desagg_review.csv", index=False, encoding="utf-8")

# print(result[(result["municipio"].str.lower() == "badalona")&(result["tipología"]=="III. TOTAL INFRACCIONES PENALES")].sort_values(["año","trimestre"]))

# suma de los delitos en badalona en 2024
print("Total delitos en Badalona en 2024:", result[(result["municipio"].str.lower() == "badalona") & (result["año"] == 2024)
& (result["trimestre"] == "Q4")])

# mañan seguir con 6. Robos con violencia e intimidación	8100 Badalona Q1 2024 en result cuando el valor original es 405
# qué falla en el cálculo porque otros sí están bien