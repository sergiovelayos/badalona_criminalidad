# import geopandas as gpd
# import pandas as pd
# from shapely import wkt

# # 1. Cargar el CSV como DataFrame
# df = pd.read_csv("/Users/macmini/Public/badalona_criminalidad/data/shp_atributos_revision.csv")

# # 2. Convertir la columna con geometría (suponiendo que se llama 'geometry') a shapely
# df["geometry"] = df["geometry"].apply(wkt.loads)

# # 3. Pasar a GeoDataFrame
# gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

# # 4. Simplificar geometrías (tolerance ajusta el nivel de simplificación)
# gdf_simplified = gdf.copy()
# gdf_simplified["geometry"] = gdf_simplified["geometry"].simplify(tolerance=0.05, preserve_topology=True)

# # 5. Guardar el resultado en un nuevo archivo
# gdf_simplified.to_file("comunidades_simplificadas.geojson", driver="GeoJSON")

# print("Archivo simplificado guardado en 'comunidades_simplificadas.geojson'")

import geopandas as gpd

# --- FUNCIÓN PARA SIMPLIFICAR Y GUARDAR ---
def simplificar_shapefile(input_path, output_geojson, tolerance=0.05):
    """
    Carga un shapefile, simplifica las geometrías y guarda el resultado en GeoJSON.
    
    Args:
        input_path (str): ruta al shapefile (.shp)
        output_geojson (str): ruta donde guardar el GeoJSON resultante
        tolerance (float): tolerancia de simplificación (mayor valor = menos detalle)
    """
    print(f"📂 Cargando: {input_path}")
    gdf = gpd.read_file(input_path)

    # Reproyectar a WGS84 si no está en EPSG:4326
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")

    # Simplificar geometrías
    gdf["geometry"] = gdf["geometry"].simplify(tolerance, preserve_topology=True)

    # Guardar a GeoJSON
    gdf.to_file(output_geojson, driver="GeoJSON")
    print(f"✅ Guardado GeoJSON simplificado en: {output_geojson}")


# --- EJEMPLOS DE USO ---

# Simplificar comunidades autónomas
# simplificar_shapefile(
#     input_path="/Users/macmini/Public/badalona_criminalidad/data/mapas/recintos_autonomicas_inspire_peninbal_etrs89/recintos_autonomicas_inspire_peninbal_etrs89.shp",
#     output_geojson="/Users/macmini/Public/badalona_criminalidad/data/mapas/comunidades_simplificadas.geojson",
#     tolerance=0.05
# )

# # Simplificar provincias
# simplificar_shapefile(
#     input_path="/Users/macmini/Public/badalona_criminalidad/data/mapas/recintos_provinciales_inspire_peninbal_etrs89/recintos_provinciales_inspire_peninbal_etrs89.shp",
#     output_geojson="/Users/macmini/Public/badalona_criminalidad/data/mapas/provincias_simplificadas.geojson",
#     tolerance=0.05
# )

# Simplificar municipios
simplificar_shapefile(
    input_path="/Users/macmini/Public/badalona_criminalidad/data/mapas/recintos_municipales_inspire_peninbal_etrs89/recintos_municipales_inspire_peninbal_etrs89.shp",
    output_geojson="/Users/macmini/Public/badalona_criminalidad/data/mapas/municipios_simplificadas.geojson",
    tolerance=0.01
)
