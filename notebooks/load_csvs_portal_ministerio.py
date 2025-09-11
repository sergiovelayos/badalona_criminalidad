import pandas as pd
import glob
import re

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
    df["año_fichero"] = año
    df["trimestre_fichero"] = trimestre
    df["orden"] = año * 10 + trimestre  # valor creciente para ordenar
    
    dfs.append(df)

# Unir todos los dataframes
df_total = pd.concat(dfs, ignore_index=True)

# Eliminar duplicados quedándonos con la versión más reciente
df_total = (
    df_total
    .sort_values("orden")  # ordenamos por año/trimestre
    .drop_duplicates(
        subset=["Geografía", "Tipología penal", "Periodos:"],
        keep="last"  # nos quedamos con el más reciente
    )
    .reset_index(drop=True)
)

# Convertir la columna 'Total' a numérico (puede tener comas como decimales)
df_total["Total"] = df_total["Total"].astype(str).str.replace(".", "", regex=False)

df_total["Total"] = pd.to_numeric(
    df_total["Total"].astype(str).str.replace(",", ".", regex=False),
    errors="coerce"
)

# df_total.to_csv("./data/delitos_csv_min_merged.csv", index=False, sep=";")

