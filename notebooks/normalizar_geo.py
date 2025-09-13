import pandas as pd
import re

pd.set_option("display.max_columns", None)

# -----------------------
# Rutas
# -----------------------
file_delitos = r"./data/esp_desagg_ytd_normalizado.csv"

# -----------------------
# Lectura y limpieza inicial
# -----------------------
delitos = pd.read_csv(file_delitos, sep=",")
# copia delitos para no modificar el original
delitos_original = delitos.copy()

# print(f"Registros originales: {len(delitos)}")
# print(f"Años únicos en datos originales: {sorted(delitos['año'].unique())}")

# LIMPIEZA INICIAL MÁS SELECTIVA
# Solo eliminar registros que claramente no son municipios (ej: "- Isla de...")
# Mantener los municipios que empiecen por "- " ya que son datos históricos válidos
delitos = delitos[~delitos["geo"].str.match(r"^\s*-\s*Isla de.*", na=False)]

# Limpiar el formato "- " del inicio SOLO para crear el diccionario de mapeo
# pero SIN eliminar los registros
delitos["geo_limpia"] = delitos["geo"].str.replace(r"^[\s\-]+", "", regex=True)

# Reemplazar 'Municipio de ' por cadena vacía al inicio del texto
delitos["geo_limpia"] = delitos["geo_limpia"].str.replace(r"^Municipio de ", "", regex=True)

# -----------------------
# Mapeo de municipios a códigos postales
# -----------------------

# Crear un diccionario para mapear municipio a código postal
municipio_a_codigo = {}

# Extraer y mapear todos los registros con formato de código postal
# Usar la columna limpia para crear el mapeo
for item in delitos["geo_limpia"].dropna().unique():
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

# -----------------------
# Unir datos: Mapear municipios sin CP a su formato completo
# -----------------------

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
delitos["geo"] = delitos["geo"].apply(unir_municipio_a_cp)

# Eliminar la columna auxiliar
delitos = delitos.drop('geo_limpia', axis=1)

# # -----------------------
# # Verificaciones
# # -----------------------

# print(f"\nRegistros finales: {len(delitos)}")
# print(f"¿Se mantuvieron todos los registros?: {len(delitos) == len(delitos_original)}")

# # Verificar Badalona específicamente
# filter_badalona = delitos["geo"].str.contains("Badalona", na=False)
# print(f"\nRegistros de Badalona: {filter_badalona.sum()}")
# print(f"Años con datos de Badalona: {sorted(delitos.loc[filter_badalona,'año'].unique())}")

# # Mostrar algunos ejemplos de valores de Badalona
# print("\nEjemplos de registros de Badalona:")
# badalona_examples = delitos.loc[filter_badalona, ['año', 'geo']].drop_duplicates().sort_values('año')
# for _, row in badalona_examples.head(10).iterrows():
#     print(f"  {row['año']}: '{row['geo']}'")

# # Estadísticas generales del mapeo
# valores_con_cp = delitos["geo"].str.match(r"^\d{5}", na=False).sum()
# valores_sin_cp = len(delitos) - valores_con_cp

# print(f"\nEstadísticas del mapeo:")
# print(f"Registros con código postal: {valores_con_cp}")
# print(f"Registros sin código postal: {valores_sin_cp}")

# # Verificar que no se perdieron años
# print(f"\nAños en datos finales: {sorted(delitos['año'].unique())}")

# Opcional: guardar para verificación
delitos.to_csv("./data/esp_geo_normalized.csv", index=False, encoding="utf-8")