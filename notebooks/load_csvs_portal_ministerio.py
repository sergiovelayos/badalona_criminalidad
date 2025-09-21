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

# print(f"Registros antes de limpiar: {len(df_total):,}")

# NUEVA LÓGICA: Filtrar registros problemáticos del T4 2022
def es_registro_problematico_t422(row):
    """
    Identifica registros problemáticos del T4 2022 que contienen datos anuales
    en lugar de trimestrales
    """
    if row["año_fichero"] == 2022 and row["trimestre_fichero"] == 4:
        periodo = str(row["Periodos:"]).lower()
        
        # Patrones que indican datos anuales problemáticos en T4 2022
        patrones_problematicos = [
            "enero-diciembre",
            "variación %",
            "variacion %",
            r"\d{4}/\d{4}",  # formato año/año como 2022/2019
            r"\d{4}/\d{2}",  # formato año/año corto como 2022/21
        ]
        
        for patron in patrones_problematicos:
            if re.search(patron, periodo, re.IGNORECASE):
                return True
    
    return False


# print(df_total.head())

# Obtener conteos, pero ordenar por el ÍNDICE (el valor del período), no por el conteo
print(df_total["Periodos:"].nunique())
conteos = df_total["Periodos:"].value_counts()
conteos_ordenados = conteos.sort_index()  # ← Ordena por el valor de "Periodos:"



# # Aplicar filtro para identificar registros problemáticos
# df_total["es_problematico_t422"] = df_total.apply(es_registro_problematico_t422, axis=1)

# # Mostrar estadísticas de registros problemáticos
# registros_problematicos = df_total["es_problematico_t422"].sum()
# print(f"Registros problemáticos identificados en T4 2022: {registros_problematicos:,}")

# if registros_problematicos > 0:
#     print("\nEjemplos de registros problemáticos:")
#     ejemplos = df_total[df_total["es_problematico_t422"]]["Periodos:"].unique()[:5]
#     for ejemplo in ejemplos:
#         print(f"  - {ejemplo}")

# # ELIMINAR los registros problemáticos ANTES de eliminar duplicados
# df_limpio = df_total[~df_total["es_problematico_t422"]].copy()
# print(f"Registros después de filtrar T4 2022 problemáticos: {len(df_limpio):,}")

# # Ahora eliminar duplicados normalmente (manteniendo el más reciente)
# df_final = (
#     df_limpio
#     .sort_values("orden")  # ordenamos por año/trimestre
#     .drop_duplicates(
#         subset=["Geografía", "Tipología penal", "Periodos:"],
#         keep="last"  # nos quedamos con el más reciente
#     )
#     .reset_index(drop=True)
# )

# print(f"Registros finales después de eliminar duplicados: {len(df_final):,}")

# # Convertir la columna 'Total' a numérico (puede tener comas como decimales)
# df_final["Total"] = df_final["Total"].astype(str).str.replace(".", "", regex=False)

# df_final["Total"] = pd.to_numeric(
#     df_final["Total"].astype(str).str.replace(",", ".", regex=False),
#     errors="coerce"
# )

# # Verificación adicional: Comprobar que no hay picos anómalos en T4 2022
# print("\n=== VERIFICACIÓN DE T4 2022 ===")
# t4_2022 = df_final[
#     (df_final["año_fichero"] == 2022) & 
#     (df_final["trimestre_fichero"] == 4)
# ]

# if len(t4_2022) > 0:
#     print(f"Registros conservados en T4 2022: {len(t4_2022):,}")
#     print("Ejemplos de periodos en T4 2022:")
#     periodos_t4_2022 = t4_2022["Periodos:"].unique()[:10]
#     for periodo in periodos_t4_2022:
#         print(f"  - {periodo}")
    
#     # Estadística de valores para detectar anomalías
#     total_mean_t4_2022 = t4_2022["Total"].mean()
#     print(f"Promedio de valores en T4 2022: {total_mean_t4_2022:.2f}")
    
#     # Comparar con trimestres adyacentes para detectar anomalías
#     t3_2022 = df_final[
#         (df_final["año_fichero"] == 2022) & 
#         (df_final["trimestre_fichero"] == 3)
#     ]
#     t1_2023 = df_final[
#         (df_final["año_fichero"] == 2023) & 
#         (df_final["trimestre_fichero"] == 1)
#     ]
    
#     if len(t3_2022) > 0:
#         total_mean_t3_2022 = t3_2022["Total"].mean()
#         ratio_t4_vs_t3 = total_mean_t4_2022 / total_mean_t3_2022 if total_mean_t3_2022 > 0 else float('inf')
#         print(f"Ratio T4 2022 vs T3 2022: {ratio_t4_vs_t3:.2f}")
        
#         if ratio_t4_vs_t3 > 2:  # Si T4 es más del doble que T3, puede ser problemático
#             print("⚠️  ADVERTENCIA: T4 2022 sigue mostrando valores anómalamente altos")
    
#     if len(t1_2023) > 0:
#         total_mean_t1_2023 = t1_2023["Total"].mean()
#         ratio_t4_vs_t1 = total_mean_t4_2022 / total_mean_t1_2023 if total_mean_t1_2023 > 0 else float('inf')
#         print(f"Ratio T4 2022 vs T1 2023: {ratio_t4_vs_t1:.2f}")

# else:
#     print("No se encontraron registros en T4 2022 (pueden haber sido filtrados completamente)")

# # Eliminar columnas auxiliares
# df_final = df_final.drop(["es_problematico_t422"], axis=1)

# # Guardar resultado
# print(f"\n=== RESULTADO FINAL ===")
# print(f"Total de registros: {len(df_final):,}")
# print(f"Rango de años: {df_final['año_fichero'].min()} - {df_final['año_fichero'].max()}")
# print(f"Trimestres únicos: {sorted(df_final['trimestre_fichero'].unique())}")

# # Opcional: Guardar
# df_final.to_csv("./data/delitos_raw_merged_t422.csv", index=False, sep=";")

# # Verificación final por municipio específico (ej: Badalona)
# print(f"\n=== VERIFICACIÓN ESPECÍFICA ===")
# badalona_test = df_final[df_final["Geografía"].str.contains("Badalona", na=False)]
# if len(badalona_test) > 0:
#     print("Evolución de registros de Badalona por trimestre:")
#     evolucion_badalona = badalona_test.groupby(["año_fichero", "trimestre_fichero"])["Total"].sum().reset_index()
#     evolucion_badalona = evolucion_badalona.sort_values(["año_fichero", "trimestre_fichero"])
#     for _, row in evolucion_badalona.tail(8).iterrows():  # Últimos 8 trimestres
#         print(f"  {row['año_fichero']} T{row['trimestre_fichero']}: {row['Total']:,.0f}")

