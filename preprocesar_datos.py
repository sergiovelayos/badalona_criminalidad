import pandas as pd
import sqlite3
import geopandas as gpd
import os

# --- CONFIGURACIÓN DE RUTAS ---
db_path = "data/delitos.db"
dic_ccaa_path = "data/pob_ccaa.csv"
dic_pro_path = "data/pob_provincias.csv"
dic_mun_path = "data/pob_municipios.csv"
mapas_dir = "data/mapas"

def procesar_datos_delitos(conn):
    """Procesa y une los datos de delitos con sus códigos geográficos."""
    print("Iniciando pre-procesamiento de datos de delitos...")
    df_delitos = pd.read_sql_query("SELECT geo, tipo, periodo, valor, POB FROM delitos", conn)
    
    dic_ccaa = pd.read_csv(dic_ccaa_path, sep=";", dtype={'CODCCAA': str}, usecols=['CODCCAA', 'CCAA'])
    dic_pro = pd.read_csv(dic_pro_path, sep=";", dtype={'CPRO': str}, usecols=['CPRO', 'PROVINCIA'])
    dic_mun = pd.read_csv(dic_mun_path, sep=";", dtype={'CP': str}, usecols=['CP', 'MUNICIPIO'])

    df_delitos['geo_clean'] = df_delitos['geo'].str.replace('CCAA:|PROVINCIA:|MUNICIPIO:', '', regex=True)
    df_delitos['valor'] = pd.to_numeric(df_delitos['valor'], errors='coerce')
    df_delitos['POB'] = pd.to_numeric(df_delitos['POB'], errors='coerce')
    df_delitos['tasa_por_1000'] = df_delitos.apply(lambda row: (row['valor'] / row['POB']) * 1000 if row['POB'] > 0 else 0, axis=1)
    
    def get_geo_type(geo_str):
        if geo_str.startswith('CCAA:'): return 'ccaa'
        if geo_str.startswith('PROVINCIA:'): return 'provincia'
        if geo_str.startswith('MUNICIPIO:'): return 'municipio'
        return 'desconocido'
    df_delitos['tipo_geo'] = df_delitos['geo'].apply(get_geo_type)

    df_ccaa = pd.merge(df_delitos[df_delitos['tipo_geo'] == 'ccaa'], dic_ccaa, left_on='geo_clean', right_on='CCAA', how='left')
    df_pro = pd.merge(df_delitos[df_delitos['tipo_geo'] == 'provincia'], dic_pro, left_on='geo_clean', right_on='PROVINCIA', how='left')
    dic_mun_unique = dic_mun[['CP', 'MUNICIPIO']].drop_duplicates()
    df_mun = pd.merge(df_delitos[df_delitos['tipo_geo'] == 'municipio'], dic_mun_unique, left_on='geo_clean', right_on='MUNICIPIO', how='left')

    df_ccaa['codigo_geo'] = df_ccaa['CODCCAA']
    df_pro['codigo_geo'] = df_pro['CPRO']
    df_mun['codigo_geo'] = df_mun['CP']

    columnas_finales = ['tipo', 'periodo', 'valor', 'POB', 'tasa_por_1000', 'codigo_geo', 'tipo_geo']
    df_final = pd.concat([df_ccaa[columnas_finales], df_pro[columnas_finales], df_mun[columnas_finales]]).dropna(subset=['codigo_geo'])
    
    table_name = 'datos_mapa_optimizados'
    print(f"Guardando datos de delitos en la tabla '{table_name}'...")
    df_final.to_sql(table_name, conn, if_exists='replace', index=False)
    
    cursor = conn.cursor()
    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_codigo_geo ON {table_name} (codigo_geo);")
    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_tipo_geo ON {table_name} (tipo_geo);")
    conn.commit()
    print("Datos de delitos procesados y guardados.")


def convertir_geojson_a_geoparquet():
    """Convierte los archivos GeoJSON a formato GeoParquet para una carga más rápida."""
    print("\nIniciando conversión de GeoJSON a GeoParquet...")
    geojson_files = ["comunidades_simplificadas.geojson", "provincias_simplificadas.geojson", "municipios_simplificadas.geojson"]
    
    for file_name in geojson_files:
        geojson_path = os.path.join(mapas_dir, file_name)
        geoparquet_path = geojson_path.replace('.geojson', '.geoparquet')
        
        if os.path.exists(geojson_path):
            print(f"Convirtiendo '{file_name}'...")
            gdf = gpd.read_file(geojson_path)
            gdf.to_parquet(geoparquet_path)
            print(f" -> Guardado como '{os.path.basename(geoparquet_path)}'")
        else:
            print(f"AVISO: No se encontró el archivo '{geojson_path}'. Se omitió la conversión.")
    print("Conversión de mapas completada.")

if __name__ == '__main__':
    # Ejecutar ambos procesos
    connection = sqlite3.connect(db_path)
    procesar_datos_delitos(connection)
    connection.close() # Cerrar la conexión antes de la siguiente función
    
    convertir_geojson_a_geoparquet()
    
    print("\n¡Pre-procesamiento completo!")

