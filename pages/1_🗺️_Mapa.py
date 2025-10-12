import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import sqlite3
import branca.colormap as cm
import os

# --- CONFIGURACIÓN ---
st.set_page_config(
    page_title="Mapas Criminalidad España",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- RUTAS A LOS ARCHIVOS ---
# 1. RUTA DE LA BASE DE DATOS ACTUALIZADA
db_path = "data/delitos_raw.db" 
geojson_ccaa = "data/mapas/comunidades_simplificadas.geoparquet"
geojson_provincias = "data/mapas/provincias_simplificadas.geoparquet"
geojson_municipios = "data/mapas/municipios_simplificadas.geoparquet"

# --- FUNCIONES DE CARGA Y PROCESAMIENTO DE DATOS ---

@st.cache_data
def load_optimized_crime_data():
    """Carga los datos desde la nueva DB, los procesa y prepara para la app."""
    try:
        # Conectar a la nueva base de datos y leer la tabla
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM delitos_aux"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Asignar nombres a las columnas según la estructura de delitos_aux
        df.columns = ['periodo', 'geo', 'tipo', 'valor_acumulado', 'valor', 'pob', 'tasa_por_1000']

    except Exception as e:
        st.error(f"Error al cargar datos desde '{db_path}': {e}")
        return pd.DataFrame(), {}

    # --- Procesamiento de la columna 'geo' ---
    df['tipo_geo'] = np.nan
    df['codigo_geo'] = np.nan
    df['nombre_geo'] = np.nan

    # Municipios (empiezan con 5 dígitos)
    mun_mask = df['geo'].str.match(r'^\d{5}')
    df.loc[mun_mask, 'tipo_geo'] = 'municipio'
    df.loc[mun_mask, 'codigo_geo'] = df.loc[mun_mask, 'geo'].str.slice(0, 5)
    df.loc[mun_mask, 'nombre_geo'] = df.loc[mun_mask, 'geo'].str.slice(6)

    # Provincias (empiezan con 'Provincia')
    pro_mask = df['geo'].str.startswith('Provincia')
    df.loc[pro_mask, 'tipo_geo'] = 'provincia'
    df.loc[pro_mask, 'codigo_geo'] = df.loc[pro_mask, 'geo'].str.split().str[1]
    df.loc[pro_mask, 'nombre_geo'] = df.loc[pro_mask, 'geo'].str.split(n=2).str[2]

    # CCAA (empiezan con 'CCAA')
    ccaa_mask = df['geo'].str.startswith('CCAA')
    df.loc[ccaa_mask, 'tipo_geo'] = 'ccaa'
    df.loc[ccaa_mask, 'codigo_geo'] = df.loc[ccaa_mask, 'geo'].str.split().str[1]
    df.loc[ccaa_mask, 'nombre_geo'] = df.loc[ccaa_mask, 'geo'].str.split(n=2).str[2]
    
    # --- Formatear el periodo a trimestres ---
    df['periodo_dt'] = pd.to_datetime(df['periodo'])
    df['quarter'] = df['periodo_dt'].dt.quarter
    df['year'] = df['periodo_dt'].dt.year
    df['periodo'] = "T" + df['quarter'].astype(str) + " " + df['year'].astype(str)
    
    # --- Mapear nombres de delitos para una mejor visualización ---
    # Se usan los nombres limpios de la DB como claves
    # Diccionario para mapear los nombres de los delitos
    mapeo_delitos = {
        # Totales principales
        'Total Criminalidad': '📊 TOTAL CRIMINALIDAD',
        'Subtotal Criminalidad Convencional': '📁 Criminalidad Convencional',
        'Subtotal Cibercriminalidad': '💻 Cibercriminalidad',
        
        # Delitos convencionales (subcategorías)
        'Homicidios dolosos y asesinatos consumados': '\u00A0\u00A0• Homicidios y Asesinatos Consumados',
        'Homicidios dolosos y asesinatos en grado tentativa': '\u00A0\u00A0• Homicidios y Asesinatos en Tentativa',
        'Delitos graves y menos graves de lesiones y riña tumultuaria': '\u00A0\u00A0• Lesiones y Riña Tumultuaria',
        'Secuestro': '\u00A0\u00A0• Secuestros',
        'Delitos contra la libertad e indemnidad sexual': '\u00A0\u00A0• Delitos Sexuales (Total)',
        'Agresión sexual con penetración': '\u00A0\u00A0\u00A0\u00A0└─ Agresión Sexual con Penetración',
        'Resto de delitos contra la libertad sexual': '\u00A0\u00A0\u00A0\u00A0└─ Otros Delitos Sexuales',
        'Robos con violencia e intimidación': '\u00A0\u00A0• Robos con Violencia e Intimidación',
        'Robos con fuerza en domicilios, establecimientos y otras instalaciones': '\u00A0\u00A0• Robos con Fuerza',
        'Hurtos': '\u00A0\u00A0• Hurtos',
        'Sustracciones de vehículos': '\u00A0\u00A0• Sustracción de Vehículos',
        'Tráfico de drogas': '\u00A0\u00A0• Tráfico de Drogas',
        #'Daños': '\u00A0\u00A0• Daños',
        
        # Ciberdelitos (subcategorías)
        'Estafas informáticas': '\u00A0\u00A0• Estafas Informáticas',
        'Otros ciberdelitos': '\u00A0\u00A0• Otros Ciberdelitos',
        
        # Resto
        'Resto de infracciones penales': '📋 Resto de Infracciones Penales'
    }
    df['tipo_display'] = df['tipo'].map(mapeo_delitos).fillna(df['tipo'])

    # Limpiar y asegurar tipos de datos correctos
    df.drop(columns=['geo', 'valor_acumulado', 'pob', 'periodo_dt', 'quarter', 'year'], inplace=True)
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    df['tasa_por_1000'] = pd.to_numeric(df['tasa_por_1000'], errors='coerce')
    
    return df, mapeo_delitos

@st.cache_data
def load_geo_data(geoparquet_path, level):
    """Carga datos GeoParquet y prepara el JOIN_CODE."""
    try:
        gdf = gpd.read_parquet(geoparquet_path)
    except Exception as e:
        st.error(f"Error al cargar mapa '{os.path.basename(geoparquet_path)}': {e}")
        return None

    if gdf.crs != "EPSG:4258":
        gdf = gdf.to_crs("EPSG:4258")

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

    if level_name == "municipio":
        gdf_unido = gdf_unido[gdf_unido["Valor"] > 0]

    zoom_start = 5 if is_mobile else 6
    location = [40.0, -3.5] if is_mobile else [40.4168, -3.7038]

    m = folium.Map(location=location, zoom_start=zoom_start, tiles="cartodbpositron")

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
            fill_color = '#d3d3d3' if valor == 0 else (colormap(valor) if colormap and valor > 0 else '#d3d3d3')
            return {'fillColor': fill_color, 'color': 'black', 'weight': 0.5, 'fillOpacity': 0 if valor is None else 0.7}

        folium.GeoJson(gdf_unido.to_json(), style_function=style_function, tooltip=folium.GeoJsonTooltip(fields=["NAMEUNIT", "Valor_tooltip"], aliases=["Nombre:", "Valor:"], localize=True, sticky=False)).add_to(m)
    else:
        max_val = gdf_unido["Valor"].max() if not gdf_unido.empty else 1
        bins = list(np.linspace(0, max_val, 7)) if max_val > 0 else [0, 1]
        folium.Choropleth(geo_data=gdf_unido.to_json(), data=gdf_unido, columns=["JOIN_CODE", "Valor"], key_on="feature.properties.JOIN_CODE", fill_color="YlOrRd", fill_opacity=0.7, line_opacity=0.3, legend_name=legend_title, bins=bins, nan_fill_color="white").add_to(m)
        folium.GeoJson(gdf_unido.to_json(), style_function=lambda x: {"fillOpacity": 0, "weight": 0}, tooltip=folium.GeoJsonTooltip(fields=["NAMEUNIT", "Valor_tooltip"], aliases=["Nombre:", "Valor:"], localize=True, sticky=False)).add_to(m)

    return m

def format_spanish(value, is_volume=False):
    """Formatea un número al estilo español ('.' para miles, ',' para decimales)."""
    if pd.isna(value):
        return "N/A"
    if is_volume:
        return f"{value:,.0f}".replace(",", ".")
    else:
        return f"{value:,.2f}".replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")

# --- CSS PERSONALIZADO (Omitido por brevedad) ---
st.markdown("""<style> ... </style>""", unsafe_allow_html=True)

# --- CARGA INICIAL DE DATOS ---
df_crime, mapeo_delitos = load_optimized_crime_data()
gdf_ccaa = load_geo_data(geojson_ccaa, "ccaa")
gdf_pro = load_geo_data(geojson_provincias, "provincia")
gdf_mun = load_geo_data(geojson_municipios, "municipio")

# --- APP ---
st.title("🗺️ Mapa de la criminalidad en España")
st.markdown("""
Explora la criminalidad en España con este mapa interactivo. Usa los filtros del menú lateral para analizar los datos por tipo de delito, periodo y métrica.

<strong>¿Cómo interpretar el mapa?</strong>
<ul>
    <li><strong>Escala de color:</strong> Las zonas con colores más intensos (naranja a rojo) tienen una mayor incidencia del delito seleccionado, mientras que las más claras (amarillo) tienen menor incidencia.</li>
    <li><strong>Zonas en gris:</strong> Indican que no hay datos registrados para esa selección. Esto es común en provincias de comunidades uniproviales (como Madrid o Asturias), donde los datos se reportan a nivel autonómico.</li>
    <li><strong>Municipios:</strong> El mapa solo muestra municipios con más de 20.000 habitantes que hayan reportado datos.</li>
</ul>

<strong>Fuente de los datos:</strong>
<br>Los datos provienen de los <strong><a href="https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/balances" target="_blank">Balances Trimestrales de Criminalidad</a></strong> publicados por el Ministerio del Interior.
<br><em>Última actualización: Junio de 2025.</em>
<br>
Creado por <strong><a href="https://www.linkedin.com/in/sergiovelayos/" target="_blank">Sergio Velayos Fernández</a></strong>.
<hr>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("Opciones de Vista")
    is_mobile = st.checkbox("Modo móvil optimizado", value=False, help="Activa para mejor experiencia en móvil")
    st.markdown("---")
    st.info("💡 **Tip**: Usa zoom y arrastra el mapa para explorar.")

if not df_crime.empty:
    # --- FILTROS Y MÉTRICAS PRINCIPALES ---
    st.markdown("### Filtros del mapa")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        # Se eliminó sorted() para mantener el orden del diccionario
        opciones_delito = list(mapeo_delitos.values())
        selected_crime = st.selectbox("Tipo de Delito:", options=opciones_delito, index=opciones_delito.index("📊 TOTAL CRIMINALIDAD"), help="Selecciona el tipo de delito a visualizar")
    with col2:
        selected_period = st.selectbox("Periodo:", options=sorted(df_crime['periodo'].unique(), key=lambda x: int(x.split(' ')[1]) * 10 + int(x.split(' ')[0][1]), reverse=True), help="Selecciona el trimestre")
    with col3:
        nivel_geo_display = st.selectbox("Nivel geográfico", options=["Comunidades Autónomas", "Provincias", "Municipios"], index=0, help="Selecciona si quieres ver datos por CCAA, provincias o municipios")
        nivel_geo_map = {"Comunidades Autónomas": "ccaa", "Provincias": "provincia", "Municipios": "municipio"}
        nivel_geo = nivel_geo_map[nivel_geo_display]
    with col4:
        selected_metric = st.selectbox("Métrica:", options=['Ratio por 1.000 hab.', 'Volumen total'], index=0, help="Ratio: normalizado por población\nVolumen: números absolutos")

    source_column = 'tasa_por_1000' if 'Ratio' in selected_metric else 'valor'
    metric_label = "Ratio por 1.000 hab." if 'Ratio' in selected_metric else "Volumen total"
    df_filtered = df_crime[(df_crime['tipo_display'] == selected_crime) & (df_crime['periodo'] == selected_period)]
    
    # --- CÁLCULO Y VISUALIZACIÓN DE MÉTRICAS ---
    df_nivel = df_filtered[df_filtered['tipo_geo'] == nivel_geo]
    promedio = df_nivel[source_column].mean()
    is_volume = 'Volumen' in selected_metric
    
    with col5:
        st.metric(f"📊 Promedio {nivel_geo.title()}", format_spanish(promedio, is_volume), help=f"{metric_label} promedio entre {nivel_geo}s")
    
    with col6:
        if not df_nivel.empty:
            # Lógica de "Máximo" simplificada gracias a la columna 'nombre_geo'
            max_row = df_nivel.nlargest(1, source_column)
            valor_max = max_row.iloc[0][source_column]
            nombre_max = max_row.iloc[0]['nombre_geo']
            st.metric(f"🔴 Máximo {nivel_geo.title()}", format_spanish(valor_max, is_volume), help=f"Mayor {metric_label.lower()} en {nivel_geo}: {nombre_max}")
        else:
            st.metric(f"🔴 Máximo {nivel_geo.title()}", "N/A")

    st.markdown("---")
    
    # --- VISUALIZACIÓN DINÁMICA DE MAPA Y TABLA ---
    st.header(f"Mapa Interactivo: {nivel_geo.replace('_', ' ').title()}")
    
    gdf_final, gdf_mapa, level_name_singular, top_n = None, None, None, None
    if nivel_geo == 'ccaa':
        gdf_mapa, level_name_singular = gdf_ccaa, 'Comunidad Autónoma'
    elif nivel_geo == 'provincia':
        gdf_mapa, level_name_singular = gdf_pro, 'Provincia'
    elif nivel_geo == 'municipio':
        gdf_mapa, level_name_singular, top_n = gdf_mun, 'Municipio', 20
        st.info("ℹ️ Solo se muestran municipios con datos registrados")

    gdf_final = prepare_map_data(gdf_mapa, df_filtered, nivel_geo, source_column)
    
    if gdf_final is not None:
        mapa = create_map(gdf_final, nivel_geo, f"{selected_crime} ({selected_period})", is_mobile)
        if mapa:
            map_height = 400 if is_mobile else 550
            st_folium(mapa, width=None, height=map_height, key=f"mapa_{nivel_geo}", returned_objects=[])

        expander_title = f"📋 Ver tabla de datos por {level_name_singular}"
        if top_n: expander_title = f"📋 Ver Top {top_n} {level_name_singular}es"
        
        with st.expander(expander_title):
            tabla_df = gdf_final[gdf_final['Valor'] > 0][['NAMEUNIT', 'Valor']].copy().drop_duplicates(subset=['NAMEUNIT'])
            tabla_df.columns = [level_name_singular, metric_label]
            tabla_df = tabla_df.sort_values(metric_label, ascending=False).reset_index(drop=True)
            if top_n: tabla_df = tabla_df.head(top_n)
            
            is_volume_table = 'Volumen' in metric_label
            tabla_df[metric_label] = tabla_df[metric_label].apply(lambda x: format_spanish(x, is_volume_table))
            
            st.dataframe(tabla_df, use_container_width=True, hide_index=True)
else:
    st.error("❌ No se pudieron cargar los datos. Verifica que la base de datos esté disponible.")

# --- FOOTER ---
st.markdown("---"); st.caption("📊 Datos de criminalidad en España | Visualización interactiva")