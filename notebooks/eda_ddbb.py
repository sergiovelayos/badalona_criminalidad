# import streamlit as st
# import pandas as pd
# import sqlite3

# DB_PATH = "data/delitos.db"

# # --- funciones auxiliares ---
# def run_query(query, params=()):
#     conn = sqlite3.connect(DB_PATH)
#     df = pd.read_sql_query(query, conn, params=params)
#     conn.close()
#     return df

# # --- app ---
# st.title("🔎 Explorador de Delitos y Población")

# # ver qué tablas existen
# if st.checkbox("Mostrar tablas disponibles en la base de datos"):
#     df_tablas = run_query("SELECT name FROM sqlite_master WHERE type='table';")
#     st.write(df_tablas)

# # lista de municipios
# municipios = run_query("SELECT DISTINCT municipio FROM delitos ORDER BY municipio;")["municipio"].tolist()
# municipio_sel = st.selectbox("Selecciona un municipio", municipios)

# # consulta de delitos + población
# query = """
# SELECT 
#     c.año,
#     c.trimestre,
#     c.municipio,
#     c.tipo_normalizado,
#     c.valor AS delitos,
#     (
#         SELECT p.POB
#         FROM poblacion p
#         WHERE p.cod_mun = c.codigo_postal
#           AND p.AÑO <= c.año
#         ORDER BY p.AÑO DESC
#         LIMIT 1
#     ) AS poblacion,
#     ROUND(
#         CAST(c.valor AS FLOAT) / (
#             SELECT p.POB
#             FROM poblacion p
#             WHERE p.cod_mun = c.codigo_postal
#               AND p.AÑO <= c.año
#             ORDER BY p.AÑO DESC
#             LIMIT 1
#         ) * 100000, 2
#     ) AS ratio_100k
# FROM delitos c
# WHERE c.municipio = ?
# ORDER BY c.año, c.trimestre;
# """

# df = run_query(query, (municipio_sel,))

# st.subheader(f"📊 Datos de {municipio_sel}")
# st.dataframe(df)

# # gráfico delitos totales por año
# if not df.empty:
#     # asegurarse de que 'delitos' es numérico
#     df['delitos'] = pd.to_numeric(df['delitos'], errors='coerce').fillna(0)

#     # agrupar y pivotear
#     delitos_anuales = df.groupby(["año", "tipo_normalizado"])["delitos"].sum().reset_index()
#     pivot = delitos_anuales.pivot(index="año", columns="tipo_normalizado", values="delitos")

#     # ordenar por año y graficar
#     pivot = pivot.sort_index()
#     st.line_chart(pivot)

#     ratio_anual = df.groupby("año")["ratio_100k"].mean().reset_index()
#     st.line_chart(ratio_anual.set_index("año"))
# else:
#     st.warning("No hay datos disponibles para este municipio.")


import sqlite3

# Verificar que la DB existe y tiene ambas tablas
conn = sqlite3.connect("data/delitos.db")
cursor = conn.cursor()

# Listar tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tablas = cursor.fetchall()
print("Tablas en la DB:", tablas)

# Verificar registros en cada tabla
cursor.execute("SELECT COUNT(*) FROM delitos")
print("Registros delitos:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM poblacion") 
print("Registros poblacion:", cursor.fetchone()[0])

# Verificar distribución de población por nivel
cursor.execute("SELECT NIVEL, COUNT(*) FROM poblacion GROUP BY NIVEL")
print("Población por nivel:", cursor.fetchall())

conn.close()