import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import sqlite3
import branca.colormap as cm

# --- CONFIGURACIÓN ---
st.set_page_config(
    page_title="🗺️ Mapas Criminalidad España", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- RUTAS A LOS ARCHIVOS OPTIMIZADOS ---
db_path = "data/delitos.db"
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
        st.error(f"Error al cargar datos: {e}")
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
    return df, mapeo_delitos

@st.cache_data
def load_geo_data(geoparquet_path, level):
    """Carga datos GeoParquet y prepara el JOIN_CODE."""
    try:
        gdf = gpd.read_parquet(geoparquet_path)
    except Exception as e:
        st.error(f"Error al cargar mapa: {e}")
        return None

    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
    
    if level == "ccaa": 
        gdf["JOIN_CODE"] = gdf["NATCODE"].astype(str).str[2:4]
    elif level == "provincia": 
        gdf["JOIN_CODE"] = gdf["NATCODE"].astype(str).str[4:6]
    elif level == "municipio": 
        gdf["JOIN_CODE"] = gdf["NATCODE"].astype(str).str[-5:]
    
    return gdf

@st.cache_data
def prepare_map_data(_gdf, df_filtered, tipo_geo, source_column):
    """Prepara los datos para el mapa combinando geodatos con datos de crimen."""
    if _gdf is None or df_filtered.empty:
        return None
    
    gdf_merged = pd.merge(
        _gdf, 
        df_filtered[df_filtered['tipo_geo'] == tipo_geo], 
        left_on='JOIN_CODE', 
        right_on='codigo_geo', 
        how='left'
    )
    gdf_merged.rename(columns={source_column: 'Valor'}, inplace=True)
    gdf_merged['Valor_tooltip'] = gdf_merged['Valor'].apply(
        lambda x: f'{x:,.2f}' if pd.notnull(x) else 'Sin datos'
    )
    gdf_merged["Valor"] = gdf_merged["Valor"].fillna(0)
    
    return gdf_merged

def create_map(gdf_unido, level_name, legend_title, is_mobile=False):
    """Crea un mapa coroplético adaptado para móvil o escritorio."""
    if gdf_unido is None or gdf_unido.empty:
        st.warning("No hay datos geográficos para mostrar.")
        return None

    # Para municipios, filtrar solo valores > 0
    if level_name == "municipio":
        gdf_unido = gdf_unido[gdf_unido["Valor"] > 0]
    
    # Configuración adaptativa según dispositivo
    if is_mobile:
        zoom_start = 5
        location = [40.0, -3.5]
    else:
        zoom_start = 6
        location = [40.4168, -3.7038]
    
    m = folium.Map(
        location=location,
        zoom_start=zoom_start,
        tiles="cartodbpositron",
        scrollWheelZoom=True,
        dragging=True,
        zoom_control=True,
        attributionControl=True
    )
    
    if level_name in ['provincia', 'municipio']:
        valores_positivos = gdf_unido[gdf_unido['Valor'] > 0]['Valor']
        colormap = None
        
        if not valores_positivos.empty:
            try:
                bins = pd.qcut(valores_positivos, q=6, retbins=True, duplicates='drop')[1]
                colormap = cm.StepColormap(
                    colors=cm.linear.YlOrRd_09.colors[-(len(bins)-1):], 
                    index=bins, 
                    vmin=valores_positivos.min(), 
                    vmax=valores_positivos.max(), 
                    caption=legend_title
                ).add_to(m)
            except Exception:
                min_val, max_val = valores_positivos.min(), valores_positivos.max()
                colormap = cm.linear.YlOrRd_09.scale(
                    min_val, 
                    max_val if max_val > min_val else min_val + 1
                ).to_step(n=6, caption=legend_title).add_to(m)
        
        def style_function(feature):
            valor = feature['properties']['Valor']
            fill_color = '#d3d3d3' if valor == 0 else (
                colormap(valor) if colormap and valor else '#d3d3d3'
            )
            return {
                'fillColor': fill_color, 
                'color': 'black', 
                'weight': 0.5, 
                'fillOpacity': 0 if valor is None else 0.7
            }
        
        folium.GeoJson(
            gdf_unido.to_json(), 
            style_function=style_function, 
            tooltip=folium.GeoJsonTooltip(
                fields=["NAMEUNIT", "Valor_tooltip"], 
                aliases=["Nombre:", "Valor:"], 
                localize=True,
                sticky=False
            )
        ).add_to(m)
    else:
        max_val = gdf_unido["Valor"].max() if not gdf_unido.empty else 1
        bins = list(np.linspace(0, max_val, 7)) if max_val > 0 else [0, 1]
        
        folium.Choropleth(
            geo_data=gdf_unido.to_json(), 
            data=gdf_unido, 
            columns=["JOIN_CODE", "Valor"], 
            key_on="feature.properties.JOIN_CODE", 
            fill_color="YlOrRd", 
            fill_opacity=0.7, 
            line_opacity=0.3, 
            legend_name=legend_title, 
            bins=bins, 
            nan_fill_color="white"
        ).add_to(m)
        
        folium.GeoJson(
            gdf_unido.to_json(), 
            style_function=lambda x: {"fillOpacity": 0, "weight": 0}, 
            tooltip=folium.GeoJsonTooltip(
                fields=["NAMEUNIT", "Valor_tooltip"], 
                aliases=["Nombre:", "Valor:"], 
                localize=True,
                sticky=False
            )
        ).add_to(m)
    
    return m

# --- CSS PERSONALIZADO PARA MEJOR UX MÓVIL ---
st.markdown("""
<style>
    /* Mejor espaciado en móvil */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Títulos más compactos */
    h1 {
        font-size: 1.8rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        font-size: 1.3rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h3 {
        font-size: 1.1rem !important;
        margin-top: 0.5rem !important;
    }
    
    /* Mejorar visualización de pestañas en móvil */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 8px 12px;
        font-size: 0.9rem;
    }
    
    /* Evitar que el mapa se salga de los márgenes */
    iframe {
        max-width: 100% !important;
        border-radius: 8px;
    }
    
    /* Mejor visualización de selectbox en móvil */
    .stSelectbox label {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }
    
    /* Reducir padding en columnas en móvil */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        
        h1 {
            font-size: 1.5rem !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 6px 8px;
            font-size: 0.85rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- CARGA INICIAL DE DATOS ---
df_crime, mapeo_delitos = load_optimized_crime_data()
gdf_ccaa = load_geo_data(geojson_ccaa, "ccaa")
gdf_pro = load_geo_data(geojson_provincias, "provincia")
gdf_mun = load_geo_data(geojson_municipios, "municipio")

# --- APP ---
st.title("🗺️ Criminalidad en España")

# --- FILTROS EN SIDEBAR PARA MEJOR UX MÓVIL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    
    if not df_crime.empty:
        selected_crime = st.selectbox(
            "Tipo de Delito:", 
            options=sorted(list(mapeo_delitos.values())), 
            index=sorted(list(mapeo_delitos.values())).index("TOTAL DELITOS"),
            help="Selecciona el tipo de delito a visualizar"
        )
        
        selected_period = st.selectbox(
            "Periodo:", 
            options=sorted(
                df_crime['periodo'].unique(), 
                key=lambda x: int(x.split(' ')[1]) * 10 + int(x.split(' ')[0][1]), 
                reverse=True
            ),
            help="Selecciona el trimestre"
        )
        
        selected_metric = st.radio(
            "Métrica:", 
            options=['Ratio por 1.000 hab.', 'Volumen total'], 
            index=0,
            help="Ratio: normalizado por población\nVolumen: números absolutos"
        )
        
        # Detectar si es móvil (heurística basada en ancho de ventana)
        is_mobile = st.checkbox("Modo móvil optimizado", value=False, help="Activa para mejor experiencia en móvil")
        
        st.markdown("---")
        st.info("💡 **Tip**: Usa zoom y arrastra el mapa para explorar. Pasa el cursor sobre las regiones para ver los datos.")

if not df_crime.empty:
    # Ajustar nombre de columna según métrica
    source_column = 'tasa_por_1000' if 'Ratio' in selected_metric else 'valor'
    metric_label = "Ratio por 1.000 habitantes" if 'Ratio' in selected_metric else "Volumen total"
    
    df_filtered = df_crime[
        (df_crime['tipo_display'] == selected_crime) & 
        (df_crime['periodo'] == selected_period)
    ]
    
    # Mostrar resumen de datos
    col1, col2, col3 = st.columns(3)
    
    total_nacional = df_filtered[df_filtered['tipo_geo'] == 'ccaa'][source_column].sum()
    
    with col1:
        st.metric(
            "📊 Total Nacional", 
            f"{total_nacional:,.0f}" if 'Volumen' in selected_metric else f"{total_nacional:.2f}",
            help=f"{metric_label} a nivel nacional"
        )
    
    with col2:
        max_ccaa = df_filtered[df_filtered['tipo_geo'] == 'ccaa'].nlargest(1, source_column)
        if not max_ccaa.empty:
            valor_max = max_ccaa.iloc[0][source_column]
            st.metric(
                "🔴 Valor máximo CCAA", 
                f"{valor_max:,.2f}" if 'Ratio' in selected_metric else f"{valor_max:,.0f}",
                help=f"Mayor {metric_label.lower()} en una CCAA"
            )
    
    with col3:
        st.metric("📅 Periodo", selected_period)
    
    st.markdown("---")
    
    # --- PESTAÑAS PARA CADA NIVEL ---
    tab1, tab2, tab3 = st.tabs(["🏛️ CCAA", "🗺️ Provincias", "🏘️ Municipios"])
    
    legend_title = f"{selected_crime} ({selected_period})"
    
    with tab1:
        gdf_ccaa_final = prepare_map_data(gdf_ccaa, df_filtered, 'ccaa', source_column)
        if gdf_ccaa_final is not None:
            mapa_ccaa = create_map(gdf_ccaa_final, "ccaa", legend_title, is_mobile)
            if mapa_ccaa:
                # Altura adaptativa
                map_height = 400 if is_mobile else 550
                st_folium(mapa_ccaa, width=None, height=map_height, key="mapa_ccaa", returned_objects=[])
                
                # Tabla resumen debajo del mapa
                with st.expander("📋 Ver tabla de datos por CCAA"):
                    tabla = gdf_ccaa_final[['NAMEUNIT', 'Valor']].copy()
                    tabla.columns = ['Comunidad Autónoma', metric_label]
                    tabla = tabla.sort_values(metric_label, ascending=False).reset_index(drop=True)
                    st.dataframe(tabla, use_container_width=True, hide_index=True)
    
    with tab2:
        gdf_pro_final = prepare_map_data(gdf_pro, df_filtered, 'provincia', source_column)
        if gdf_pro_final is not None:
            mapa_pro = create_map(gdf_pro_final, "provincia", legend_title, is_mobile)
            if mapa_pro:
                map_height = 400 if is_mobile else 550
                st_folium(mapa_pro, width=None, height=map_height, key="mapa_provincia", returned_objects=[])
                
                with st.expander("📋 Ver tabla de datos por Provincia"):
                    tabla = gdf_pro_final[['NAMEUNIT', 'Valor']].copy()
                    tabla.columns = ['Provincia', metric_label]
                    tabla = tabla.sort_values(metric_label, ascending=False).reset_index(drop=True)
                    st.dataframe(tabla, use_container_width=True, hide_index=True)
    
    with tab3:
        gdf_mun_final = prepare_map_data(gdf_mun, df_filtered, 'municipio', source_column)
        if gdf_mun_final is not None:
            st.info("ℹ️ Solo se muestran municipios con datos registrados")
            mapa_mun = create_map(gdf_mun_final, "municipio", legend_title, is_mobile)
            if mapa_mun:
                map_height = 400 if is_mobile else 550
                st_folium(mapa_mun, width=None, height=map_height, key="mapa_municipio", returned_objects=[])
                
                with st.expander("📋 Ver Top 20 municipios"):
                    tabla = gdf_mun_final[gdf_mun_final['Valor'] > 0][['NAMEUNIT', 'Valor']].copy()
                    tabla.columns = ['Municipio', metric_label]
                    tabla = tabla.sort_values(metric_label, ascending=False).head(20).reset_index(drop=True)
                    st.dataframe(tabla, use_container_width=True, hide_index=True)
else:
    st.error("❌ No se pudieron cargar los datos. Verifica que la base de datos esté disponible.")

# --- FOOTER ---
st.markdown("---")
st.caption("📊 Datos de criminalidad en España | Visualización interactiva")