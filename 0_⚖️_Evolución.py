import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

# --- Configuración de la página ---
st.set_page_config(page_title="Comparador Criminalidad España", layout="wide")

# --- Título ---
st.title("⚖️ Comparador de Criminalidad en España")
st.markdown("""
Compara fácilmente los datos de [Balances trimestrales de criminalidad del Ministerio de Interior](https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/balances) entre municipios de más de 20.000 habitantes, provincias, comunidades autónomas y a nivel nacional desde 2015 hasta junio de 2025. 
Los datos reportados por el ministerio son acumulados trimestralmente evitando que pueda analizarse la evolución trimestral. Para mejorar esta circunstancia, he tratado los datos desagregando por trimestre. Además, he cruzado con el censo de cada ubicación y año para calcular la tasa por cada 1,000 habitantes con lo que es posible comparar ubicaciones con disintos censos.
<br>Creado por [Sergio Velayos Fernández](https://www.linkedin.com/in/sergiovelayos/).
<hr>
""", unsafe_allow_html=True) 



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
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        delito_seleccionado = st.selectbox("1. Elige el tipo de delito", tipos_delito_disponibles)
    with col2:
        ubicacion_1 = st.selectbox("2. Elige la ubicación principal", ubicaciones_disponibles)
    with col3:
        # Creamos una lista para la segunda ubicación que excluye la ya seleccionada
        opciones_comparacion = ["(Ninguna)"] + [u for u in ubicaciones_disponibles if u != ubicacion_1]
        ubicacion_2 = st.selectbox("3. Compara con (opcional)", opciones_comparacion)
    with col4:
        metrica_seleccionada = st.selectbox("4. Elige la métrica", ["Tasa por 1,000 hab.", "Volumen de casos"], index=0)

    
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

        # --- CÁLCULO DE VARIACIÓN ---
        variaciones = []
        for ubicacion in ubicaciones_a_mostrar:
            df_ubicacion = df_filtrado[df_filtrado['geo'] == ubicacion].sort_values('periodo_sort')
            if len(df_ubicacion) >= 2:
                tasa_inicial = df_ubicacion.iloc[0]['tasa_por_1000']
                tasa_final = df_ubicacion.iloc[-1]['tasa_por_1000']
                periodo_inicial = df_ubicacion.iloc[0]['periodo']
                periodo_final = df_ubicacion.iloc[-1]['periodo']
                
                variacion_absoluta = tasa_final - tasa_inicial
                variacion_porcentual = ((tasa_final - tasa_inicial) / tasa_inicial * 100) if tasa_inicial > 0 else 0
                
                variaciones.append({
                    'Ubicación': ubicacion,
                    'Periodo Inicial': periodo_inicial,
                    'Tasa Inicial': f"{tasa_inicial:.2f}",
                    'Periodo Final': periodo_final,
                    'Tasa Final': f"{tasa_final:.2f}",
                    'Variación Absoluta': f"{variacion_absoluta:+.2f}",
                    'Variación %': f"{variacion_porcentual:+.1f}%"
                })
        
        # Mostrar tabla de variaciones
        if variaciones:
            st.subheader("📊 Variación de la Tasa de Criminalidad (Inicio vs Final)")
            df_variaciones = pd.DataFrame(variaciones)
            
            # Aplicar formato condicional con colores
            def color_variacion(val):
                if isinstance(val, str) and ('+' in val or '-' in val):
                    if '+' in val:
                        return 'background-color: rgba(255, 100, 100, 0.3)'
                    else:
                        return 'background-color: rgba(100, 255, 100, 0.3)'
                return ''
            
            styled_df = df_variaciones.style.applymap(
                color_variacion, 
                subset=['Variación Absoluta', 'Variación %']
            )
            
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            st.markdown("---")

        # --- GRÁFICO: TASA O VOLUMEN (LÍNEAS SUAVIZADAS) ---
        if metrica_seleccionada == "Tasa por 1,000 hab.":
            titulo_grafico = f"Evolución de la Tasa de Criminalidad - {delito_seleccionado}"
            titulo_y = "Tasa por 1,000 Habitantes"
            campo_y = "tasa_por_1000"
            formato_tooltip = ".2f"
        else:
            titulo_grafico = f"Evolución del Volumen de Delitos - {delito_seleccionado}"
            titulo_y = "Número de Casos"
            campo_y = "valor"
            formato_tooltip = ","
        
        st.subheader(titulo_grafico)
        
        # Preparar datos para etiquetas finales
        df_ultimos = df_filtrado.loc[df_filtrado.groupby('geo')['periodo_sort'].idxmax()].copy()
        
        # Ordenar por la métrica seleccionada para calcular desplazamiento vertical y evitar superposición
        df_ultimos = df_ultimos.sort_values(campo_y).reset_index(drop=True)
        
        # Calcular desplazamiento si las etiquetas están muy cerca
        if len(df_ultimos) > 1:
            # Ajustar el umbral según la métrica
            umbral = 2 if metrica_seleccionada == "Tasa por 1,000 hab." else 50
            for i in range(1, len(df_ultimos)):
                diff = df_ultimos.loc[i, campo_y] - df_ultimos.loc[i-1, campo_y]
                # Si la diferencia es menor al umbral, ajustar la posición
                if diff < umbral:
                    df_ultimos.loc[i, campo_y] = df_ultimos.loc[i-1, campo_y] + umbral
        
        # Líneas suavizadas
        lineas = alt.Chart(df_filtrado).mark_line(
            strokeWidth=3,
            interpolate='monotone'  # Suavizado de líneas
        ).encode(
            x=alt.X('periodo:N', title='Periodo Trimestral', sort=alt.SortField(field="periodo_sort"), axis=alt.Axis(labelAngle=-45)),
            y=alt.Y(f'{campo_y}:Q', title=titulo_y),
            color=alt.Color('geo:N', title='Ubicación', legend=None),
            tooltip=['geo', 'periodo', alt.Tooltip(campo_y, title=titulo_y, format=formato_tooltip), 'POB']
        )
        
        # Etiquetas al final de las líneas con ubicación y valor (con saltos de línea)
        if metrica_seleccionada == "Tasa por 1,000 hab.":
            formula_label = 'datum.geo + "\\n" + "' + delito_seleccionado + '" + "\\n" + format(datum.' + campo_y + ', ".1f")'
        else:
            formula_label = 'datum.geo + "\\n" + "' + delito_seleccionado + '" + "\\n" + format(datum.' + campo_y + ', ",")'
        
        etiquetas = alt.Chart(df_ultimos).mark_text(
            align='left',
            dx=7,
            fontSize=11,
            fontWeight='bold',
            lineBreak='\n'
        ).encode(
            x=alt.X('periodo:N', sort=alt.SortField(field="periodo_sort")),
            y=alt.Y(f'{campo_y}:Q'),
            text=alt.Text('label:N'),
            color=alt.Color('geo:N', legend=None)
        ).transform_calculate(
            label=formula_label
        )
        
        # Combinar líneas y etiquetas
        chart = (lineas + etiquetas).properties(
            height=400
        )
        st.altair_chart(chart, use_container_width=True)
        
        # --- TABLA TOP 5 TASAS MÁS ALTAS Y MÁS BAJAS ---
        st.subheader(f"📊 Ranking de Ubicaciones - {delito_seleccionado}")
        
        # Obtener el último periodo disponible para cada ubicación
        df_ranking = df[df['tipo_display'] == delito_seleccionado].copy()
        df_ranking['tasa_por_1000'] = df_ranking.apply(
            lambda row: (row['valor'] / row['POB']) * 1000 if row['POB'] > 0 else 0, axis=1
        )
        
        # Obtener último periodo de cada ubicación
        df_ranking_ultimo = df_ranking.loc[df_ranking.groupby('geo')['periodo_sort'].idxmax()]
        
        # Ordenar y seleccionar top 5 más altas y más bajas
        df_ranking_sorted = df_ranking_ultimo.sort_values('tasa_por_1000', ascending=False)
        top_5_altas = df_ranking_sorted.head(5).copy()
        top_5_bajas = df_ranking_sorted.tail(5).copy()
        
        # Crear dos columnas para mostrar las tablas lado a lado
        col_alta, col_baja = st.columns(2)
        
        with col_alta:
            st.markdown("**🔴 Top 5 Tasas Más Altas**")
            top_5_altas_display = top_5_altas[['geo', 'tasa_por_1000', 'periodo', 'valor']].copy()
            top_5_altas_display.columns = ['Ubicación', 'Tasa por 1,000 hab.', 'Periodo', 'Casos']
            top_5_altas_display['Tasa por 1,000 hab.'] = top_5_altas_display['Tasa por 1,000 hab.'].apply(lambda x: f"{x:.2f}".replace('.', ','))
            top_5_altas_display = top_5_altas_display.reset_index(drop=True)
            
            st.dataframe(
                top_5_altas_display,
                use_container_width=True,
                hide_index=True
            )
        
        with col_baja:
            st.markdown("**🟢 Top 5 Tasas Más Bajas**")
            top_5_bajas_display = top_5_bajas[['geo', 'tasa_por_1000', 'periodo', 'valor']].copy()
            top_5_bajas_display.columns = ['Ubicación', 'Tasa por 1,000 hab.', 'Periodo', 'Casos']
            top_5_bajas_display['Tasa por 1,000 hab.'] = top_5_bajas_display['Tasa por 1,000 hab.'].apply(lambda x: f"{x:.2f}".replace('.', ','))
            top_5_bajas_display = top_5_bajas_display.reset_index(drop=True)
            
            st.dataframe(
                top_5_bajas_display,
                use_container_width=True,
                hide_index=True
            )
        
        st.markdown("---")

    else:
        st.warning("No se encontraron datos para la selección actual.")
else:
    st.error("No se pudieron cargar los datos. Asegúrate de que el archivo 'data/delitos.db' existe y contiene la tabla 'delitos'.")


# Botón para vaciar la caché y forzar el refresco
if st.button("🔄 Vaciar Caché y Refrescar Datos"):
    # 1. Vacía la caché de datos (si usas @st.cache_data)
    st.cache_data.clear()

    # 2. Opcional: Vacía la caché de recursos (si usas @st.cache_resource)
    # st.cache_resource.clear()

    # 3. Muestra un mensaje temporal de éxito
    st.success("Caché vaciada. Recargando aplicación...")

    # 4. Fuerza una nueva ejecución de la aplicación (rerun)
    st.rerun()

# --- LICENCIA Y PIE DE PÁGINA ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; font-size: 0.9em; color: grey;">
    <p>Esta aplicación y los datos visualizados se distribuyen bajo la licencia <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank">Creative Commons Atribución 4.0 Internacional (CC BY 4.0)</a>.</p>
    <p>Eres libre de compartir y adaptar esta obra para cualquier propósito, incluso comercialmente, siempre que reconozcas la autoría original.</p>
</div>
""", unsafe_allow_html=True)