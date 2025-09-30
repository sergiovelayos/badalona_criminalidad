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

# --- RUTAS A LOS ARCHIVOS ---
# Se recomienda usar rutas relativas para que el proyecto sea portable.
db_path = "data/delitos.db"
geojson_ccaa = "data/mapas/comunidades_simplificadas.geojson"
geojson_provincias = "data/mapas/provincias_simplificadas.geojson"
geojson_municipios = "data/mapas/municipios_simplificadas.geojson"
# Rutas a los diccionarios para un cruce más robusto
dic_ccaa_path = "data/pob_ccaa.csv"
dic_pro_path = "data/pob_provincias.csv"
dic_mun_path = "data/pob_municipios.csv"

# --- FUNCIONES DE CARGA DE DATOS ---

@st.cache_data
def load_real_crime_data():
    """Carga los datos reales de delitos y población desde la base de datos y los prepara."""
    try:
        conn = sqlite3.connect(db_path)
        # MODIFICACIÓN: Se añade la columna POB a la consulta
        df = pd.read_sql_query("SELECT geo, tipo, periodo, valor, POB FROM delitos", conn)
        conn.close()
    except Exception as e:
        st.error(f"Error al cargar la base de datos de delitos: {e}")
        st.warning("Asegúrate de que la ruta 'data/delitos.db' es correcta y contiene la columna 'POB'.")
        return pd.DataFrame(), {}

    mapeo_delitos = {
        'III. TOTAL INFRACCIONES PENALES': 'TOTAL DELITOS',
        'I. CRIMINALIDAD CONVENCIONAL': 'Subtotal Criminalidad Convencional',
        '1. Homicidios dolosos y asesinatos consumados': ' --- Homicidios y Asesinatos',
        '2. Homicidios dolosos y asesinatos en grado tentativa': ' --- Homicidios en Tentativa',
        '3. Delitos graves y menos graves de lesiones y riña tumultuaria': ' --- Lesiones y Riñas',
        '4. Secuestro': ' --- Secuestros',
        '5. Delitos contra la libertad sexual': ' --- Delitos Sexuales',
        '5.1.-Agresión sexual con penetración': ' --- Agresiones Sexuales con Penetración',
        '5.2.-Resto de delitos contra la libertad sexual': ' --- Otros Delitos Sexuales',
        '6. Robos con violencia e intimidación': ' --- Robos con Violencia',
        '7. Robos con fuerza en domicilios, establecimientos y otras instalaciones': ' --- Robos con Fuerza',
        '7.1.-Robos con fuerza en domicilios': ' --- Robos en Domicilios',
        '8. Hurtos': ' --- Hurtos',
        '9. Sustracciones de vehículos': ' --- Sustracción de Vehículos',
        '10. Tráfico de drogas': ' --- Tráfico de Drogas',
        '11. Resto de criminalidad convencional': ' --- Otros Delitos Convencionales',
        'II. CIBERCRIMINALIDAD (infracciones penales cometidas en/por medio ciber)': 'Subtotal Cibriminalidad',
        '12.-Estafas informáticas': ' --- Estafas Informáticas',
        '13.-Otros ciberdelitos': ' --- Otros Ciberdelitos'
    }

    df['tipo_display'] = df['tipo'].map(mapeo_delitos).fillna(df['tipo'])
    df['geo_clean'] = df['geo'].str.replace('CCAA:|PROVINCIA:|MUNICIPIO:', '', regex=True)
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    df['POB'] = pd.to_numeric(df['POB'], errors='coerce')
    
    # MODIFICACIÓN: Cálculo de la tasa por 1000 habitantes
    df['tasa_por_1000'] = df.apply(
        lambda row: (row['valor'] / row['POB']) * 1000 if row['POB'] > 0 else 0, axis=1
    )
    
    return df, mapeo_delitos

@st.cache_data
def load_geo_data(geojson_path, level):
    """Carga datos GeoJSON y prepara el JOIN_CODE."""
    gdf = gpd.read_file(geojson_path)
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")

    # Crear JOIN_CODE para la unión
    if level == "ccaa":
        gdf["JOIN_CODE"] = gdf["NATCODE"].astype(str).str[2:4]
    elif level == "provincia":
        gdf["JOIN_CODE"] = gdf["NATCODE"].astype(str).str[4:6]
    elif level == "municipio":
        gdf["JOIN_CODE"] = gdf["NATCODE"].astype(str).str[-5:]
    
    return gdf

def display_map(gdf_unido, level_name, legend_title):
    """Muestra un mapa coroplético a partir de un GeoDataFrame ya unido."""
    # MODIFICACIÓN: Creamos una columna para el tooltip que esté siempre formateada
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
                num_escalones = 6
                bins = pd.qcut(valores_positivos, q=num_escalones, retbins=True, duplicates='drop')[1]
                num_colors = len(bins) - 1
                
                colormap = cm.StepColormap(
                    colors=cm.linear.YlOrRd_09.colors[-num_colors:], index=bins,
                    vmin=valores_positivos.min(), vmax=valores_positivos.max(), caption=legend_title
                )
                colormap.add_to(m)

            except Exception:
                min_val = valores_positivos.min(); max_val = valores_positivos.max()
                if min_val == max_val: max_val = min_val + 1
                colormap = cm.linear.YlOrRd_09.scale(min_val, max_val).to_step(n=6)
                colormap.caption = legend_title
                colormap.add_to(m)

        def style_function(feature):
            valor = feature['properties']['Valor']
            fill_opacity = 0.8; line_opacity = 0.3; weight = 0.5
            
            if valor is None: fill_color = 'white'; fill_opacity = 0
            elif valor == 0: fill_color = '#d3d3d3'
            else: fill_color = colormap(valor) if colormap else '#d3d3d3'
            
            return {'fillColor': fill_color, 'color': 'black', 'weight': weight, 'fillOpacity': fill_opacity, 'lineOpacity': line_opacity}

        folium.GeoJson(
            gdf_unido.to_json(), style_function=style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=["NAMEUNIT", "Valor_tooltip"],
                aliases=[f"{level_name.capitalize()}:", "Valor:"],
                localize=True
            )
        ).add_to(m)

    else: # LÓGICA ORIGINAL PARA CCAA
        geojson_data = gdf_unido.to_json()
        max_val = gdf_unido["Valor"].max() if not gdf_unido.empty else 1
        bins = list(np.linspace(0, max_val, 7)) if max_val > 0 else [0, 1]

        folium.Choropleth(
            geo_data=geojson_data, data=gdf_unido,
            columns=["JOIN_CODE", "Valor"], key_on="feature.properties.JOIN_CODE",
            fill_color="YlOrRd", fill_opacity=0.8, line_opacity=0.3,
            legend_name=legend_title, bins=bins, nan_fill_color="white"
        ).add_to(m)

        folium.GeoJson(
            geojson_data, style_function=lambda x: {"fillOpacity": 0, "weight": 0},
            tooltip=folium.GeoJsonTooltip(
                fields=["NAMEUNIT", "Valor_tooltip"],
                aliases=[f"{level_name.capitalize()}:", "Valor:"],
                localize=True
            )
        ).add_to(m)

    st.subheader(f"🗺️ Mapa por {level_name.capitalize()}")
    st_folium(m, width=1000, height=600)

# --- CARGA INICIAL DE DATOS ---
df_crime, mapeo_delitos = load_real_crime_data()
gdf_ccaa = load_geo_data(geojson_ccaa, "ccaa")
gdf_pro = load_geo_data(geojson_provincias, "provincia")
gdf_mun = load_geo_data(geojson_municipios, "municipio")

try:
    dic_ccaa = pd.read_csv(dic_ccaa_path, sep=";", dtype={'CODCCAA': str})
    dic_pro = pd.read_csv(dic_pro_path, sep=";", dtype={'CPRO': str})
    dic_mun = pd.read_csv(dic_mun_path, sep=";", dtype={'CP': str})
except FileNotFoundError as e:
    st.error(f"No se encontró un archivo de diccionario: {e}.")
    dic_ccaa = pd.DataFrame(columns=['CODCCAA', 'CCAA']); dic_pro = pd.DataFrame(columns=['CPRO', 'PROVINCIA']); dic_mun = pd.DataFrame(columns=['CP', 'MUNICIPIO'])

# --- APP ---
st.title("🗺️ Mapas de España por CCAA, Provincias y Municipios")
st.markdown("---")

st.markdown("### Filtros para los mapas")
if not df_crime.empty:
    col1, col2, col3 = st.columns(3)
    with col1:
        crime_options = sorted(list(mapeo_delitos.values()))
        default_index = crime_options.index("TOTAL DELITOS") if "TOTAL DELITOS" in crime_options else 0
        selected_crime = st.selectbox("Tipología del Delito:", options=crime_options, index=default_index)
    with col2:
        period_options = sorted(df_crime['periodo'].unique(), key=lambda x: int(x.split(' ')[1]) * 10 + int(x.split(' ')[0][1]), reverse=True)
        selected_period = st.selectbox("Trimestre:", options=period_options)
    # MODIFICACIÓN: Nuevo selector de métrica
    with col3:
        metric_options = ['Ratio por 1.000 habitantes', 'Volumen total']
        selected_metric = st.selectbox("Métrica:", options=metric_options, index=0)
    
    df_filtered = df_crime[(df_crime['tipo_display'] == selected_crime) & (df_crime['periodo'] == selected_period)]

    # MODIFICACIÓN: Determinar qué columna usar en base a la métrica seleccionada
    source_column = 'tasa_por_1000' if selected_metric == 'Ratio por 1.000 habitantes' else 'valor'

    df_filtered_ccaa = df_filtered[df_filtered['geo'].str.startswith('CCAA:')].copy()
    df_filtered_pro = df_filtered[df_filtered['geo'].str.startswith('PROVINCIA:')].copy()
    df_filtered_mun = df_filtered[df_filtered['geo'].str.startswith('MUNICIPIO:')].copy()

    df_ccaa_con_codigo = pd.merge(df_filtered_ccaa, dic_ccaa, left_on='geo_clean', right_on='CCAA', how='inner')
    gdf_ccaa_final = pd.merge(gdf_ccaa, df_ccaa_con_codigo, left_on='JOIN_CODE', right_on='CODCCAA', how='left')
    
    df_pro_con_codigo = pd.merge(df_filtered_pro, dic_pro, left_on='geo_clean', right_on='PROVINCIA', how='inner')
    gdf_pro_final = pd.merge(gdf_pro, df_pro_con_codigo, left_on='JOIN_CODE', right_on='CPRO', how='left')

    dic_mun_unique = dic_mun[['CP', 'MUNICIPIO']].drop_duplicates()
    df_mun_con_codigo = pd.merge(df_filtered_mun, dic_mun_unique, left_on='geo_clean', right_on='MUNICIPIO', how='inner')
    gdf_mun_final = pd.merge(gdf_mun, df_mun_con_codigo, left_on='JOIN_CODE', right_on='CP', how='left')

    # MODIFICACIÓN: Renombrar la columna de origen (ratio o valor) a 'Valor' para el mapa
    gdf_ccaa_final.rename(columns={source_column: 'Valor'}, inplace=True)
    gdf_pro_final.rename(columns={source_column: 'Valor'}, inplace=True)
    gdf_mun_final.rename(columns={source_column: 'Valor'}, inplace=True)

else:
    st.warning("No se pudieron cargar los datos de delitos. No se pueden mostrar los mapas.")
    gdf_ccaa_final, gdf_pro_final, gdf_mun_final = gdf_ccaa.copy(), gdf_pro.copy(), gdf_mun.copy()
    gdf_ccaa_final["Valor"], gdf_pro_final["Valor"], gdf_mun_final["Valor"] = np.nan, np.nan, np.nan

# --- PESTAÑAS PARA CADA MAPA ---
st.markdown("---")
tab1, tab2, tab3 = st.tabs(["Comunidades Autónomas", "Provincias", "Municipios"])

legend_title = f"{selected_metric}: {selected_crime} ({selected_period})" if not df_crime.empty else "Sin datos"

with tab1:
    display_map(gdf_ccaa_final, "ccaa", legend_title)
with tab2:
    display_map(gdf_pro_final, "provincia", legend_title)
with tab3:
    display_map(gdf_mun_final, "municipio", legend_title)

