import pandas as pd
import sqlite3

DB_PATH = "data/delitos.db"
TABLE_NAME = "delitos"

print(f"--- Inspeccionando el contenido de '{DB_PATH}' ---")

try:
    conn = sqlite3.connect(DB_PATH)
    # Leemos solo las 10 primeras filas para una revisión rápida
    df_inspector = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME} WHERE GEO LIKE '%Madrid%' AND tipo = 'III. TOTAL INFRACCIONES PENALES' and periodo = 'T1 2025' limit 10", conn)
    conn.close()

    print(f"✅ Se han leído las primeras filas de la tabla '{TABLE_NAME}':")
    print(df_inspector[['periodo', 'geo', 'tipo', 'valor']])

except Exception as e:
    print(f"❌ Error al intentar leer la base de datos: {e}")
    print("Asegúrate de que la ruta al fichero y el nombre de la tabla son correctos.")