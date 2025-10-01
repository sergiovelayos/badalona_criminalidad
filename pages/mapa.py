import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import sqlite3
import branca.colormap as cm

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="🗺️ Mapas España: CCAA, Provincias y Municipios", layout="wide")

# --- RUTAS A LOS ARCHIVOS OPTIMIZADOS ---
db_path = "data/delitos.db"
# --- MEJORA DE RENDIMIENTO: Leemos desde los archivos GeoParquet, mucho más rápidos ---
geojson_ccaa = "data/mapas/comunidades_simplificadas.geoparquet"
geojson_provincias = "data/mapas/provincias_simplificadas.geoparquet"
geojson_municipios = "data/mapas/municipios_simplificadas.geoparquet"

# --- FUNCIONES DE CARGA DE DATOS ---

@st.cache_data
def load_optimized_crime_data():
    """Carga los datos pre-procesados y optimizados desde la base de datos."""
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM datos_mapa_optimizados", conn)
        conn.close()
    except Exception as e:
        st.error(f"Error al cargar la tabla optimizada 'datos_mapa_optimizados': {e}")
        st.warning("Asegúrate de haber ejecutado primero el script 'preprocesar_datos.py' para generar la tabla optimizada.")
        return pd.DataFrame(), {}

    mapeo_delitos = {
        'III. TOTAL INFRACCIONES PENALES': 'TOTAL DELITOS', 'I. CRIMINALIDAD CONVENCIONAL': 'Subtotal Criminalidad Convencional',
        '1. Homicidios dolosos y asesinatos consumados': ' --- Homicidios y Asesinatos', '2. Homicidios dolosos y asesinatos en grado tentativa': ' --- Homicidios en Tentativa',
        '3. Delitos graves y menos graves de lesiones y riña tumultuaria': ' --- Lesiones y Riñas', '4. Secuestro': ' --- Secuestros',
        '5. Delitos contra la libertad sexual': ' --- Delitos Sexuales', '5.1.-Agresión sexual con penetración': ' --- Agresiones Sexuales con Penetración',
        '5.2.-Resto de delitos contra la libertad sexual': ' --- Otros Delitos Sexuales', '6. Robos con violencia e intimidación': ' --- Robos con Violencia',
        '7. Robos con fuerza en domicilios, establecimientos y otras instalaciones': ' --- Robos con Fuerza', '7.1.-Robos con fuerza en domicilios': ' --- Robos en Domicilios',
        '8. Hurtos': ' --- Hurtos', '9. Sustracciones de vehículos': ' --- Sustracción de Vehículos', '10. Tráfico de drogas': ' --- Tráfico de Drogas',
        '11. Resto de criminalidad convencional': ' --- Otros Delitos Convencionales', 'II. CIBERCRIMINALIDAD (infracciones penales cometidas en/por medio ciber)': 'Subtotal Cibriminalidad',
        '12.-Estafas informáticas': ' --- Estafas Informáticas', '13.-Otros ciberdelitos': ' --- Otros Ciberdelitos'
    }
    df['tipo_display'] = df['tipo'].map(mapeo_delitos).fillna(df['tipo'])
    return df, mapeo_delitos

@st.cache_data
def load_geo_data(geoparquet_path, level):
    """Carga datos GeoParquet y prepara el JOIN_CODE."""
    try:
        gdf = gpd.read_parquet(geoparquet_path)
    except Exception as e:
        st.error(f"Error al cargar el archivo de mapa optimizado '{os.path.basename(geoparquet_path)}': {e}")
        st.warning("Asegúrate de haber ejecutado el script 'preprocesar_datos.py' para generar los archivos .geoparquet.")
        return None

    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
    if level == "ccaa": gdf["JOIN_CODE"] = gdf["NATCODE"].astype(str).str[2:4]
    elif level == "provincia": gdf["JOIN_CODE"] = gdf["NATCODE"].astype(str).str[4:6]
    elif level == "municipio": gdf["JOIN_CODE"] = gdf["NATCODE"].astype(str).str[-5:]
    return gdf

def display_map(gdf_unido, level_name, legend_title):
    """Muestra un mapa coroplético a partir de un GeoDataFrame ya unido."""
    if gdf_unido is None or gdf_unido.empty:
        st.warning("No hay datos geográficos para mostrar en el mapa.")
        return

    gdf_unido['Valor_tooltip'] = gdf_unido['Valor'].apply(lambda x: f'{x:,.2f}' if pd.notnull(x) else 'Sin datos')
    gdf_unido["Valor"] = gdf_unido["Valor"].fillna(0)
    if level_name == "municipio":
        gdf_unido = gdf_unido[gdf_unido["Valor"] > 0]
    
    m = folium.Map(location=[40.4168, -3.7038], zoom_start=6, tiles="cartodbpositron")
    if level_name in ['provincia', 'municipio']:
        valores_positivos = gdf_unido[gdf_unido['Valor'] > 0]['Valor']
        colormap = None
        if not valores_positivos.empty:
            try:
                bins = pd.qcut(valores_positivos, q=6, retbins=True, duplicates='drop')[1]
                colormap = cm.StepColormap(colors=cm.linear.YlOrRd_09.colors[-(len(bins)-1):], index=bins, vmin=valores_positivos.min(), vmax=valores_positivos.max(), caption=legend_title).add_to(m)
            except Exception:
                min_val, max_val = valores_positivos.min(), valores_positivos.max()
                colormap = cm.linear.YlOrRd_09.scale(min_val, max_val if max_val > min_val else min_val + 1).to_step(n=6, caption=legend_title).add_to(m)
        def style_function(feature):
            valor = feature['properties']['Valor']
            fill_color = '#d3d3d3' if valor == 0 else (colormap(valor) if colormap and valor else '#d3d3d3')
            return {'fillColor': fill_color, 'color': 'black', 'weight': 0.5, 'fillOpacity': 0 if valor is None else 0.8}
        folium.GeoJson(gdf_unido.to_json(), style_function=style_function, tooltip=folium.GeoJsonTooltip(fields=["NAMEUNIT", "Valor_tooltip"], aliases=[f"{level_name.capitalize()}:", "Valor:"], localize=True)).add_to(m)
    else:
        max_val = gdf_unido["Valor"].max() if not gdf_unido.empty else 1
        bins = list(np.linspace(0, max_val, 7)) if max_val > 0 else [0, 1]
        folium.Choropleth(geo_data=gdf_unido.to_json(), data=gdf_unido, columns=["JOIN_CODE", "Valor"], key_on="feature.properties.JOIN_CODE", fill_color="YlOrRd", fill_opacity=0.8, line_opacity=0.3, legend_name=legend_title, bins=bins, nan_fill_color="white").add_to(m)
        folium.GeoJson(gdf_unido.to_json(), style_function=lambda x: {"fillOpacity": 0, "weight": 0}, tooltip=folium.GeoJsonTooltip(fields=["NAMEUNIT", "Valor_tooltip"], aliases=[f"{level_name.capitalize()}:", "Valor:"], localize=True)).add_to(m)
    st.subheader(f"🗺️ Mapa por {level_name.capitalize()}")
    st_folium(m, width=1000, height=600)

# --- CARGA INICIAL DE DATOS ---
df_crime, mapeo_delitos = load_optimized_crime_data()
gdf_ccaa = load_geo_data(geojson_ccaa, "ccaa")
gdf_pro = load_geo_data(geojson_provincias, "provincia")
gdf_mun = load_geo_data(geojson_municipios, "municipio")

# --- APP ---
st.title("🗺️ Mapas de España por CCAA, Provincias y Municipios")
st.markdown("---")
st.markdown("### Filtros para los mapas")
if not df_crime.empty:
    col1, col2, col3 = st.columns(3)
    with col1: selected_crime = st.selectbox("Tipología del Delito:", options=sorted(list(mapeo_delitos.values())), index=sorted(list(mapeo_delitos.values())).index("TOTAL DELITOS"))
    with col2: selected_period = st.selectbox("Trimestre:", options=sorted(df_crime['periodo'].unique(), key=lambda x: int(x.split(' ')[1]) * 10 + int(x.split(' ')[0][1]), reverse=True))
    with col3: selected_metric = st.selectbox("Métrica:", options=['Ratio por 1.000 habitantes', 'Volumen total'], index=0)
    
    df_filtered = df_crime[(df_crime['tipo_display'] == selected_crime) & (df_crime['periodo'] == selected_period)]
    source_column = 'tasa_por_1000' if selected_metric == 'Ratio por 1.000 habitantes' else 'valor'

    gdf_ccaa_final, gdf_pro_final, gdf_mun_final = None, None, None
    if gdf_ccaa is not None:
        gdf_ccaa_final = pd.merge(gdf_ccaa, df_filtered[df_filtered['tipo_geo'] == 'ccaa'], left_on='JOIN_CODE', right_on='codigo_geo', how='left')
        gdf_ccaa_final.rename(columns={source_column: 'Valor'}, inplace=True)
    if gdf_pro is not None:
        gdf_pro_final = pd.merge(gdf_pro, df_filtered[df_filtered['tipo_geo'] == 'provincia'], left_on='JOIN_CODE', right_on='codigo_geo', how='left')
        gdf_pro_final.rename(columns={source_column: 'Valor'}, inplace=True)
    if gdf_mun is not None:
        gdf_mun_final = pd.merge(gdf_mun, df_filtered[df_filtered['tipo_geo'] == 'municipio'], left_on='JOIN_CODE', right_on='codigo_geo', how='left')
        gdf_mun_final.rename(columns={source_column: 'Valor'}, inplace=True)
else:
    st.warning("No se pudieron cargar los datos optimizados. Ejecuta el script de pre-procesamiento.")
    gdf_ccaa_final, gdf_pro_final, gdf_mun_final = gdf_ccaa.copy() if gdf_ccaa is not None else None, gdf_pro.copy() if gdf_pro is not None else None, gdf_mun.copy() if gdf_mun is not None else None
    if gdf_ccaa_final is not None: gdf_ccaa_final["Valor"] = np.nan
    if gdf_pro_final is not None: gdf_pro_final["Valor"] = np.nan
    if gdf_mun_final is not None: gdf_mun_final["Valor"] = np.nan

# --- PESTAÑAS PARA CADA MAPA ---
st.markdown("---")
tab1, tab2, tab3 = st.tabs(["Comunidades Autónomas", "Provincias", "Municipios"])
legend_title = f"{selected_metric}: {selected_crime} ({selected_period})" if not df_crime.empty else "Sin datos"
with tab1: display_map(gdf_ccaa_final, "ccaa", legend_title)
with tab2: display_map(gdf_pro_final, "provincia", legend_title)
with tab3: display_map(gdf_mun_final, "municipio", legend_title)

