import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

# --- Configuración de la página ---
st.set_page_config(page_title="Análisis de Criminalidad", layout="wide")

# --- Título ---
st.title("⚖️ Comparador de Criminalidad en España")
st.markdown("""
Compara fácilmente los datos de [Balances trimestrales de criminalidad del Ministerio de Interior](https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/balances) entre municipios de más de 20.000 habitantes, provincias, comunidades autónomas y a nivel nacional desde 2015 hasta junio de 2025. 
Los datos reportados por el ministerio son acumulados trimestralmente evitando que pueda analizarse la evolución trimestral. Para mejorar esta circunstancia, he tratado los datos desagregando por trimestre. Además, he cruzado con el censo de cada ubicación y año para calcular la tasa por cada 1,000 habitantes con lo que es posible comparar ubicaciones con disintos censos.
Creado por [Sergio Velayos Fernández](https://www.linkedin.com/in/sergiovelayos/)
""")

# --- Carga de datos desde SQLite (con caché para mayor velocidad) ---
@st.cache_data
def load_data():
    """Carga los datos y los prepara para el análisis."""
    conn = sqlite3.connect("data/delitos.db")
    df = pd.read_sql_query("SELECT geo, tipo, periodo, valor, POB FROM delitos", conn)
    conn.close()

    # Diccionario para mapear los nombres de los delitos
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
        'II. CIBERCRIMINALIDAD (infracciones penales cometidas en/por medio ciber)': 'Subtotal Cibercriminalidad',
        '12.-Estafas informáticas': ' --- Estafas Informáticas',
        '13.-Otros ciberdelitos': ' --- Otros Ciberdelitos'
    }
    
    # Aplicar el mapeo a una nueva columna
    df['tipo_display'] = df['tipo'].map(mapeo_delitos).fillna(df['tipo'])
    
    # Preparamos el campo 'periodo' para que se ordene cronológicamente en el gráfico
    df[['trimestre', 'año']] = df['periodo'].str.split(' ', expand=True)
    df['periodo_sort'] = df['año'].astype(int) * 10 + df['trimestre'].str.replace('T', '').astype(int)
    
    # Aseguramos que las columnas sean numéricas
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    df['POB'] = pd.to_numeric(df['POB'], errors='coerce')
    
    # Devolvemos también el diccionario para usarlo fuera de la función
    return df, mapeo_delitos

df, mapeo_delitos = load_data()

# --- Filtros de Comparación (en la parte superior) ---
st.subheader("Filtros de Comparación")

# Comprobamos que el DataFrame no esté vacío antes de crear los filtros
if not df.empty:

    # Creamos listas únicas y ordenadas para los selectores
    ubicaciones_disponibles = sorted(df['geo'].unique())
    
    # Usamos el orden del diccionario para el selector de delitos
    tipos_en_orden = list(mapeo_delitos.values())
    tipos_reales_en_datos = df['tipo_display'].unique()
    tipos_delito_disponibles = [t for t in tipos_en_orden if t in tipos_reales_en_datos]

    # Usamos columnas para organizar los filtros
    col1, col2, col3 = st.columns(3)

    with col1:
        delito_seleccionado = st.selectbox("1. Elige el tipo de delito", tipos_delito_disponibles)
    with col2:
        ubicacion_1 = st.selectbox("2. Elige la ubicación principal", ubicaciones_disponibles)
    with col3:
        # Creamos una lista para la segunda ubicación que excluye la ya seleccionada
        opciones_comparacion = ["(Ninguna)"] + [u for u in ubicaciones_disponibles if u != ubicacion_1]
        ubicacion_2 = st.selectbox("3. Compara con (opcional)", opciones_comparacion)

    
    st.markdown("---") # Separador visual

    # --- Filtrado de datos según la selección ---
    ubicaciones_a_mostrar = [ubicacion_1]
    if ubicacion_2 != "(Ninguna)":
        ubicaciones_a_mostrar.append(ubicacion_2)

    df_filtrado = df[
        # Filtramos usando la nueva columna 'tipo_display'
        (df['tipo_display'] == delito_seleccionado) &
        (df['geo'].isin(ubicaciones_a_mostrar))
    ].copy() # Usamos .copy() para evitar warnings

    # --- Visualización de los gráficos ---
    if not df_filtrado.empty:

        # --- CÁLCULO DEL RATIO ---
        df_filtrado['tasa_por_1000'] = df_filtrado.apply(
            lambda row: (row['valor'] / row['POB']) * 1000 if row['POB'] > 0 else 0, axis=1
        )

        # --- GRÁFICO 1: TASA DE CRIMINALIDAD (LÍNEAS) ---
        st.subheader("Evolución de la Tasa de Criminalidad")
        chart_tasa = alt.Chart(df_filtrado).mark_line().encode(
            x=alt.X('periodo:N', title='Periodo Trimestral', sort=alt.SortField(field="periodo_sort")),
            y=alt.Y('tasa_por_1000:Q', title='Tasa por 1,000 Habitantes'),
            color=alt.Color('geo:N', title='Ubicación', legend=alt.Legend(orient='bottom')),
            tooltip=['geo', 'periodo', alt.Tooltip('tasa_por_1000', title='Tasa/1000 hab.', format='.2f'), 'POB']
        ).properties(
            height=400
        ).interactive()
        st.altair_chart(chart_tasa, use_container_width=True)
        
        # --- GRÁFICO 2: VOLUMEN DE DELITOS (BARRAS) ---
        st.subheader("Evolución del Volumen de Delitos")
        chart_volumen = alt.Chart(df_filtrado).mark_bar().encode(
            x=alt.X('periodo:N', title='Periodo Trimestral', sort=alt.SortField(field="periodo_sort")),
            y=alt.Y('valor:Q', title='Número de Casos'),
            color=alt.Color('geo:N', title='Ubicación', legend=alt.Legend(orient='bottom')),
            xOffset='geo:N',
            tooltip=['geo', 'periodo', 'valor']
        ).properties(
            height=400
        ).interactive()
        st.altair_chart(chart_volumen, use_container_width=True)

    else:
        st.warning("No se encontraron datos para la selección actual.")
else:
    st.error("No se pudieron cargar los datos. Asegúrate de que el archivo 'data/delitos.db' existe y contiene la tabla 'delitos'.")

# --- LICENCIA Y PIE DE PÁGINA ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; font-size: 0.9em; color: grey;">
    <p>Esta aplicación y los datos visualizados se distribuyen bajo la licencia <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank">Creative Commons Atribución 4.0 Internacional (CC BY 4.0)</a>.</p>
    <p>Eres libre de compartir y adaptar esta obra para cualquier propósito, incluso comercialmente, siempre que reconozcas la autoría original.</p>
</div>
""", unsafe_allow_html=True)
