# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# import sqlite3

# # --- CONFIGURACIÓN INICIAL Y CONSTANTES (Sin cambios) ---
# st.set_page_config(page_title="Criminalidad por Municipio", layout="wide")
# st.title("📊 Evolución de Delitos por Municipio y Trimestre")
# st.markdown("""
# Compara fácilmente los datos de [Balances trimestrales de criminalidad del Ministerio de Interior](https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/balances) entre municipios de más de 20.000 habitantes desde 2015 hasta junio de 2025. [Más info](https://github.com/sergiovelayos/badalona_criminalidad)
# """)

# DB_PATH = "data/delitos.db"
# mapeo_delitos = {
#     'III. TOTAL INFRACCIONES PENALES': 'TOTAL DELITOS',
#     'I. CRIMINALIDAD CONVENCIONAL': 'Subtotal Criminalidad Convencional',
#     '1. Homicidios dolosos y asesinatos consumados': ' --- Homicidios y Asesinatos',
#     '2. Homicidios dolosos y asesinatos en grado tentativa': ' --- Homicidios en Tentativa',
#     '3. Delitos graves y menos graves de lesiones y riña tumultuaria': ' --- Lesiones y Riñas',
#     '4. Secuestro': ' --- Secuestros',
#     '5. Delitos contra la libertad sexual': ' --- Delitos Sexuales',
#     '5.1.-Agresión sexual con penetración': ' --- Agresiones Sexuales con Penetración',
#     '5.2.-Resto de delitos contra la libertad sexual': ' --- Otros Delitos Sexuales',
#     '6. Robos con violencia e intimidación': ' --- Robos con Violencia',
#     '7. Robos con fuerza en domicilios, establecimientos y otras instalaciones': ' --- Robos con Fuerza',
#     '7.1.-Robos con fuerza en domicilios': ' --- Robos en Domicilios',
#     '8. Hurtos': ' --- Hurtos',
#     '9. Sustracciones de vehículos': ' --- Sustracción de Vehículos',
#     '10. Tráfico de drogas': ' --- Tráfico de Drogas',
#     '11. Resto de criminalidad convencional': ' --- Otros Delitos Convencionales',
#     'II. CIBERCRIMINALIDAD (infracciones penales cometidas en/por medio ciber)': 'Subtotal Cibercriminalidad',
#     '12.-Estafas informáticas': ' --- Estafas Informáticas',
#     '13.-Otros ciberdelitos': ' --- Otros Ciberdelitos'
# }
# mapeo_inverso_delitos = {v: k for k, v in mapeo_delitos.items()}

# # --- FUNCIONES OPTIMIZADAS ---

# @st.cache_data
# def get_municipios():
#     """Obtiene solo la lista de municipios únicos. Es muy rápido."""
#     conn = sqlite3.connect(DB_PATH)
#     municipios = pd.read_sql_query("SELECT DISTINCT municipio FROM delitos ORDER BY municipio", conn)
#     conn.close()
#     return municipios["municipio"].tolist()

# @st.cache_data
# def get_crime_data(municipios: list, tipo_delito_normalizado: str):
#     """
#     Función optimizada que busca SOLO los datos para los municipios y delito seleccionados.
#     Adaptada para la nueva estructura de base de datos optimizada.
#     """
#     if not municipios or not tipo_delito_normalizado:
#         return pd.DataFrame()

#     tipo_delito_original = mapeo_inverso_delitos.get(tipo_delito_normalizado)
#     if not tipo_delito_original:
#         return pd.DataFrame()

#     # --- CONSULTA SQL OPTIMIZADA para la nueva estructura ---
#     # Como ya no hay duplicados en la DB, la consulta es más simple y eficiente
#     query = """
#     SELECT
#         d.año,
#         d.trimestre,
#         d.municipio,
#         d.tipo_normalizado,
#         d.valor,
#         (
#             SELECT p.POB
#             FROM poblacion p
#             WHERE p.cod_mun = d.codigo_postal
#               AND p.AÑO <= d.año
#             ORDER BY p.AÑO DESC
#             LIMIT 1
#         ) AS poblacion
#     FROM delitos d
#     WHERE
#         d.municipio IN ({placeholders})
#         AND d.tipo_normalizado = ?
#     ORDER BY
#         d.año, d.trimestre;
#     """.format(placeholders=','.join('?' for _ in municipios))

#     params = municipios + [tipo_delito_original]

#     conn = sqlite3.connect(DB_PATH)
#     df = pd.read_sql_query(query, conn, params=params)
#     conn.close()

#     if df.empty:
#         return pd.DataFrame()

#     # --- PROCESAMIENTO SIMPLIFICADO (ya no hay duplicados que manejar) ---
#     # Mapear nombres de delitos
#     df["tipo_normalizado"] = df["tipo_normalizado"].map(mapeo_delitos).fillna(df["tipo_normalizado"])
    
#     # Convertir tipos de datos
#     df["año"] = df["año"].astype(int)
#     df["trimestre"] = df["trimestre"].astype(str)
#     df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
#     df["poblacion"] = pd.to_numeric(df["poblacion"], errors="coerce").fillna(0)

#     # Calcular tasa de criminalidad
#     df["tasa_criminalidad_x1000"] = df.apply(
#         lambda row: (row["valor"] / row["poblacion"] * 1000) if row["poblacion"] > 0 else 0,
#         axis=1
#     )

#     # Crear periodo ordenado para visualización
#     df["periodo"] = df["año"].astype(str) + "-" + df["trimestre"]
#     df["trimestre_num"] = df["trimestre"].str.replace("T", "", regex=False).astype(int)
#     df = df.sort_values(["año", "trimestre_num", "municipio"])

#     return df.drop(columns=["trimestre_num"])

# # --- INTERFAZ DE STREAMLIT  ---

# col1, col2 = st.columns(2)
# with col1:
#     municipios_unicos = get_municipios()
#     municipio_seleccionado = st.selectbox("📍 Selecciona un municipio", options=municipios_unicos)
# with col2:
#     opciones_delito = list(mapeo_delitos.values())
#     delito_seleccionado = st.selectbox("⚖️ Selecciona un tipo de delito", options=opciones_delito)

# st.subheader("Comparar con otro municipio")
# municipios_comparables = [m for m in municipios_unicos if m != municipio_seleccionado]
# municipio_comparado = st.selectbox("Selecciona un segundo municipio (opcional)", options=["Ninguno"] + municipios_comparables)

# # AQUÍ SE DEFINEN LAS VARIABLES - ESTA PARTE FALTABA EN TU CÓDIGO
# municipios_a_buscar = [municipio_seleccionado]
# if municipio_comparado != "Ninguno":
#     municipios_a_buscar.append(municipio_comparado)

# df_total = get_crime_data(municipios_a_buscar, delito_seleccionado)

# if df_total.empty:
#     st.warning("⚠️ No hay datos disponibles para la selección actual.")
#     st.stop()

# df_principal = df_total[df_total["municipio"] == municipio_seleccionado]
# df_comparado = pd.DataFrame()
# if municipio_comparado != "Ninguno":
#     df_comparado = df_total[df_total["municipio"] == municipio_comparado]

# # AHORA SÍ PODEMOS USAR df_principal Y df_comparado EN LOS GRÁFICOS

# # --- GRÁFICO DE TASA DE CRIMINALIDAD (LÍNEAS) ---
# st.subheader(f"Comparativa de Tasa de Criminalidad: {delito_seleccionado}")
# fig, ax1 = plt.subplots(figsize=(14, 6))

# # Gráfico del municipio principal
# ax1.plot(df_principal["periodo"], df_principal["tasa_criminalidad_x1000"],
#          marker="o", color="#d62728", linewidth=2.5, label=municipio_seleccionado)

# # Solo añadir el segundo municipio si existe y tiene datos
# if not df_comparado.empty:
#     ax1.plot(df_comparado["periodo"], df_comparado["tasa_criminalidad_x1000"],
#              marker="o", color="#1f77b4", linewidth=2.5, linestyle="--", label=municipio_comparado)

# # Configuración del gráfico
# ax1.set_title(f"Tasa de Criminalidad de {delito_seleccionado} (por 1000 hab.)", fontsize=16, fontweight="bold", pad=20)
# ax1.set_xlabel("Periodo")
# ax1.set_ylabel("Tasa por 1000 habitantes")
# ax1.grid(True, linestyle="--", alpha=0.6)
# ax1.legend(title="Municipios")

# # Rotar etiquetas X solo si hay muchos períodos
# if len(df_principal["periodo"]) > 10:
#     plt.xticks(rotation=45, ha="right")
# else:
#     plt.xticks(rotation=30, ha="right")

# plt.tight_layout()
# st.pyplot(fig)

# # --- GRÁFICO DE VOLUMEN DE DELITOS (BARRAS) ---
# st.subheader(f"Comparativa de volumen de delitos: {delito_seleccionado}")
# fig, ax1 = plt.subplots(figsize=(14, 6))

# if not df_comparado.empty:
#     # CREAR DATASET COMBINADO para alinear períodos
#     # Obtener todos los períodos únicos de ambos municipios
#     todos_los_periodos = sorted(list(set(df_principal["periodo"].tolist() + df_comparado["periodo"].tolist())))
    
#     # Crear DataFrames completos con todos los períodos (rellenar con 0 si falta)
#     df_principal_completo = pd.DataFrame({'periodo': todos_los_periodos})
#     df_principal_completo = df_principal_completo.merge(
#         df_principal[['periodo', 'valor']], 
#         on='periodo', 
#         how='left'
#     ).fillna(0)
    
#     df_comparado_completo = pd.DataFrame({'periodo': todos_los_periodos})
#     df_comparado_completo = df_comparado_completo.merge(
#         df_comparado[['periodo', 'valor']], 
#         on='periodo', 
#         how='left'
#     ).fillna(0)
    
#     # Configurar barras
#     bar_width = 0.35
#     x_indices = range(len(todos_los_periodos))
    
#     # Barras para ambos municipios
#     ax1.bar([i - bar_width/2 for i in x_indices], df_principal_completo["valor"],
#             width=bar_width, color="#d62728", label=municipio_seleccionado, align='center')
    
#     ax1.bar([i + bar_width/2 for i in x_indices], df_comparado_completo["valor"],
#             width=bar_width, color="#1f77b4", label=municipio_comparado, align='center')
    
#     # Configuración del gráfico
#     ax1.set_xticks(x_indices)
#     ax1.set_xticklabels(todos_los_periodos, rotation=45, ha="right")

# else:
#     # Solo un municipio - gráfico simple
#     bar_width = 0.35
#     x_indices = range(len(df_principal["periodo"]))
    
#     ax1.bar(x_indices, df_principal["valor"],
#             width=bar_width, color="#d62728", label=municipio_seleccionado)
    
#     ax1.set_xticks(x_indices)
#     ax1.set_xticklabels(df_principal["periodo"], rotation=45, ha="right")

# # Configuración común del gráfico
# ax1.set_title(f"Volumen de delitos de {delito_seleccionado}", fontsize=16, fontweight="bold", pad=20)
# ax1.set_xlabel("Periodo")
# ax1.set_ylabel("Volumen delitos")
# ax1.grid(True, linestyle="--", alpha=0.6, axis='y')
# ax1.legend(title="Municipios")
# plt.tight_layout()
# st.pyplot(fig)

# # --- SECCIÓN DE DETALLES ---
# st.divider()
# st.subheader(f"Detalles de {municipio_seleccionado}")
# col1, col2, col3 = st.columns(3)
# col1.metric("Total de casos", f"{df_principal['valor'].sum():,.0f}")
# col2.metric("Promedio de Tasa/1000 hab.", f"{df_principal['tasa_criminalidad_x1000'].mean():.2f}")
# col3.metric("Nº de periodos", df_principal["periodo"].nunique())
# with st.expander("📋 Ver datos detallados"):
#     st.dataframe(df_principal[["municipio","periodo","valor","poblacion","tasa_criminalidad_x1000","tipo_normalizado"]], use_container_width=True)

# if not df_comparado.empty:
#     st.divider()
#     st.subheader(f"Detalles de {municipio_comparado}")
#     col1c, col2c, col3c = st.columns(3)
#     col1c.metric("Total de casos", f"{df_comparado['valor'].sum():,.0f}")
#     col2c.metric("Promedio de Tasa/1000 hab.", f"{df_comparado['tasa_criminalidad_x1000'].mean():.2f}")
#     col3c.metric("Nº de periodos", df_comparado["periodo"].nunique())
#     with st.expander(f"📋 Ver datos detallados de {municipio_comparado}"):
#         st.dataframe(df_comparado[["municipio","periodo","valor","poblacion","tasa_criminalidad_x1000","tipo_normalizado"]], use_container_width=True)


# # --- ANÁLISIS ADICIONAL DE T4 2022 (PARA DESARROLLADORES) ---
# # Esta sección es para desarrolladores que quieran entender cómo se ha limpiado el dato de T4 2022
# # Se puede eliminar o comentar en producción
# st.divider()
# st.subheader("🔍 Análisis adicional")








# ============== CLAUDE ==============
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

# --- CONFIGURACIÓN INICIAL Y CONSTANTES ---
st.set_page_config(page_title="Criminalidad por Municipio", layout="wide")
st.title("📊 Evolución de Delitos por Municipio y Trimestre")
st.markdown("""
Compara fácilmente los datos de [Balances trimestrales de criminalidad del Ministerio de Interior](https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/balances) entre municipios de más de 20.000 habitantes desde 2015 hasta junio de 2025. [Más info](https://github.com/sergiovelayos/badalona_criminalidad)
""")

DB_PATH = "data/delitos.db"

# Mapeo actualizado para los nuevos nombres de delitos
mapeo_delitos = {
    'III. TOTAL INFRACCIONES PENALES': 'TOTAL DELITOS',
    'I. CRIMINALIDAD CONVENCIONAL': 'Subtotal Criminalidad Convencional',
    '1.-Homicidios dolosos y asesinatos consumados': ' --- Homicidios y Asesinatos',
    '2.-Homicidios dolosos y asesinatos en grado te...': ' --- Homicidios en Tentativa', 
    '3.-Delitos graves y menos graves de lesiones y...': ' --- Lesiones y Riñas',
    '4.-Secuestro': ' --- Secuestros',
    '5.-Delitos contra la libertad e indemnidad sexual': ' --- Delitos Sexuales',
    '5.1.-Agresión sexual con penetración': ' --- Agresiones Sexuales con Penetración',
    '5.2.-Resto de delitos contra la libertad e ind...': ' --- Otros Delitos Sexuales',
    '6.-Robos con violencia e intimidación': ' --- Robos con Violencia',
    '7.- Robos con fuerza en domicilios, establecim...': ' --- Robos con Fuerza',
    '7.1.-Robos con fuerza en domicilios': ' --- Robos en Domicilios',
    '8.-Hurtos': ' --- Hurtos',
    '9.-Sustracciones de vehículos': ' --- Sustracción de Vehículos',
    '10.-Tráfico de drogas': ' --- Tráfico de Drogas',
    '11.-Resto de criminalidad convencional': ' --- Otros Delitos Convencionales',
    'II. CIBERCRIMINALIDAD (infracciones penales co...': 'Subtotal Cibercriminalidad',
    '12.-Estafas informáticas': ' --- Estafas Informáticas',
    '13.-Otros ciberdelitos': ' --- Otros Ciberdelitos'
}

mapeo_inverso_delitos = {v: k for k, v in mapeo_delitos.items()}

# --- FUNCIONES OPTIMIZADAS ---

@st.cache_data
def get_municipios():
    """Obtiene la lista de municipios únicos disponibles en la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    try:
        # Verificar si existe la columna municipio
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(delitos)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        if 'municipio' in columnas:
            municipios = pd.read_sql_query(
                "SELECT DISTINCT municipio FROM delitos WHERE nivel = 'Municipal' AND municipio IS NOT NULL ORDER BY municipio", 
                conn
            )
            return municipios["municipio"].tolist()
        else:
            st.error("No se encontró la columna 'municipio' en la base de datos")
            return []
    except Exception as e:
        st.error(f"Error al obtener municipios: {e}")
        return []
    finally:
        conn.close()

@st.cache_data
def get_tipos_delito():
    """Obtiene los tipos de delito disponibles en la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    try:
        tipos = pd.read_sql_query(
            "SELECT DISTINCT tipo_normalizado FROM delitos WHERE tipo_normalizado IS NOT NULL ORDER BY tipo_normalizado", 
            conn
        )
        # Mapear a nombres amigables
        tipos_mapeados = []
        for tipo in tipos["tipo_normalizado"].tolist():
            nombre_amigable = mapeo_delitos.get(tipo, tipo)
            tipos_mapeados.append(nombre_amigable)
        
        return sorted(list(set(tipos_mapeados)))
    except Exception as e:
        st.error(f"Error al obtener tipos de delito: {e}")
        return []
    finally:
        conn.close()

@st.cache_data
def get_crime_data(municipios: list, tipo_delito_normalizado: str):
    """
    Función optimizada para obtener datos de criminalidad con población.
    Adaptada para la nueva estructura de base de datos.
    """
    if not municipios or not tipo_delito_normalizado:
        return pd.DataFrame()

    # Obtener el nombre original del delito
    tipo_delito_original = mapeo_inverso_delitos.get(tipo_delito_normalizado)
    if not tipo_delito_original:
        tipo_delito_original = tipo_delito_normalizado

    # Consulta SQL optimizada usando la vista creada
    query = """
    SELECT 
        d.año,
        d.trimestre,
        d.municipio,
        d.tipo_normalizado,
        d.valor,
        d.periodo,
        p.POB as poblacion
    FROM delitos d
    LEFT JOIN poblacion p ON d.codigo_postal = p.CODIGO_POSTAL AND d.año = p.AÑO
    WHERE d.municipio IN ({placeholders})
      AND d.tipo_normalizado = ?
      AND d.nivel = 'Municipal'
    ORDER BY d.año, d.trimestre
    """.format(placeholders=','.join('?' for _ in municipios))

    params = municipios + [tipo_delito_original]

    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        st.error(f"Error en la consulta SQL: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

    if df.empty:
        return pd.DataFrame()

    # Procesamiento de datos
    df["tipo_normalizado"] = df["tipo_normalizado"].map(mapeo_delitos).fillna(df["tipo_normalizado"])
    
    # Convertir tipos de datos
    df["año"] = pd.to_numeric(df["año"], errors="coerce").fillna(0).astype(int)
    df["trimestre"] = pd.to_numeric(df["trimestre"], errors="coerce").fillna(1).astype(int)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
    df["poblacion"] = pd.to_numeric(df["poblacion"], errors="coerce").fillna(0)

    # Calcular tasa de criminalidad por 1000 habitantes
    df["tasa_criminalidad_x1000"] = df.apply(
        lambda row: (row["valor"] / row["poblacion"] * 1000) if row["poblacion"] > 0 else 0,
        axis=1
    )

    # Crear periodo para visualización
    df["periodo_display"] = df["año"].astype(str) + "-T" + df["trimestre"].astype(str)
    df = df.sort_values(["año", "trimestre", "municipio"])

    return df

# --- VERIFICACIÓN DE BASE DE DATOS ---
def verificar_base_datos():
    """Verifica que la base de datos existe y tiene las tablas necesarias."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = [row[0] for row in cursor.fetchall()]
        
        if 'delitos' not in tablas:
            st.error("❌ No se encontró la tabla 'delitos' en la base de datos")
            return False
            
        if 'poblacion' not in tablas:
            st.warning("⚠️ No se encontró la tabla 'poblacion' en la base de datos")
        
        # Verificar datos
        cursor.execute("SELECT COUNT(*) FROM delitos")
        total_delitos = cursor.fetchone()[0]
        
        if total_delitos == 0:
            st.error("❌ No hay datos en la tabla delitos")
            return False
            
        st.success(f"✅ Base de datos cargada correctamente: {total_delitos:,} registros de delitos")
        return True
        
    except Exception as e:
        st.error(f"❌ Error conectando a la base de datos: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

# --- INTERFAZ PRINCIPAL ---

# Verificar base de datos al inicio
if not verificar_base_datos():
    st.stop()

# Selectores principales
col1, col2 = st.columns(2)

with col1:
    municipios_disponibles = get_municipios()
    if not municipios_disponibles:
        st.error("No se encontraron municipios en la base de datos")
        st.stop()
    
    municipio_seleccionado = st.selectbox(
        "📍 Selecciona un municipio", 
        options=municipios_disponibles,
        help="Municipios con más de 20,000 habitantes según datos del Ministerio"
    )

with col2:
    tipos_delito_disponibles = get_tipos_delito()
    if not tipos_delito_disponibles:
        st.error("No se encontraron tipos de delito en la base de datos")
        st.stop()
        
    delito_seleccionado = st.selectbox(
        "⚖️ Selecciona un tipo de delito", 
        options=tipos_delito_disponibles,
        help="Clasificación según el Ministerio del Interior"
    )

# Selector de comparación
st.subheader("Comparar con otro municipio")
municipios_comparables = [m for m in municipios_disponibles if m != municipio_seleccionado]
municipio_comparado = st.selectbox(
    "Selecciona un segundo municipio (opcional)", 
    options=["Ninguno"] + municipios_comparables
)

# Obtener datos
municipios_a_buscar = [municipio_seleccionado]
if municipio_comparado != "Ninguno":
    municipios_a_buscar.append(municipio_comparado)

df_total = get_crime_data(municipios_a_buscar, delito_seleccionado)

if df_total.empty:
    st.warning("⚠️ No hay datos disponibles para la selección actual.")
    st.info("Esto puede deberse a que el tipo de delito seleccionado no tiene registros para este municipio.")
    st.stop()

# Separar datos por municipio
df_principal = df_total[df_total["municipio"] == municipio_seleccionado]
df_comparado = pd.DataFrame()
if municipio_comparado != "Ninguno":
    df_comparado = df_total[df_total["municipio"] == municipio_comparado]

# --- GRÁFICOS ---

# Gráfico de tasa de criminalidad (líneas)
st.subheader(f"Evolución de la tasa de criminalidad: {delito_seleccionado}")

fig, ax = plt.subplots(figsize=(14, 8))

# Municipio principal
if not df_principal.empty:
    ax.plot(
        df_principal["periodo_display"], 
        df_principal["tasa_criminalidad_x1000"],
        marker="o", 
        color="#d62728", 
        linewidth=2.5, 
        label=municipio_seleccionado,
        markersize=6
    )

# Municipio comparado
if not df_comparado.empty:
    ax.plot(
        df_comparado["periodo_display"], 
        df_comparado["tasa_criminalidad_x1000"],
        marker="s", 
        color="#1f77b4", 
        linewidth=2.5, 
        linestyle="--", 
        label=municipio_comparado,
        markersize=6
    )

ax.set_title(f"Tasa de Criminalidad: {delito_seleccionado} (por 1,000 hab.)", fontsize=16, fontweight="bold", pad=20)
ax.set_xlabel("Periodo", fontsize=12)
ax.set_ylabel("Tasa por 1,000 habitantes", fontsize=12)
ax.grid(True, linestyle="--", alpha=0.3)
ax.legend(title="Municipios", loc='best')

# Mejorar legibilidad del eje X
n_periodos = len(df_principal["periodo_display"]) if not df_principal.empty else 0
if n_periodos > 15:
    plt.xticks(rotation=45, ha="right")
    # Mostrar solo cada 2º o 3º período si hay muchos
    step = max(1, n_periodos // 10)
    ax.set_xticks(ax.get_xticks()[::step])
else:
    plt.xticks(rotation=30, ha="right")

plt.tight_layout()
st.pyplot(fig)

# Gráfico de volumen de delitos (barras)
st.subheader(f"Volumen de delitos: {delito_seleccionado}")

fig, ax = plt.subplots(figsize=(14, 8))

if not df_comparado.empty:
    # Comparación entre dos municipios
    todos_los_periodos = sorted(list(set(df_principal["periodo_display"].tolist() + df_comparado["periodo_display"].tolist())))
    
    # Completar datos faltantes
    df_principal_completo = pd.DataFrame({'periodo_display': todos_los_periodos})
    df_principal_completo = df_principal_completo.merge(
        df_principal[['periodo_display', 'valor']], 
        on='periodo_display', 
        how='left'
    ).fillna(0)
    
    df_comparado_completo = pd.DataFrame({'periodo_display': todos_los_periodos})
    df_comparado_completo = df_comparado_completo.merge(
        df_comparado[['periodo_display', 'valor']], 
        on='periodo_display', 
        how='left'
    ).fillna(0)
    
    # Crear barras agrupadas
    bar_width = 0.35
    x_indices = range(len(todos_los_periodos))
    
    ax.bar([i - bar_width/2 for i in x_indices], df_principal_completo["valor"],
           width=bar_width, color="#d62728", label=municipio_seleccionado, alpha=0.8)
    
    ax.bar([i + bar_width/2 for i in x_indices], df_comparado_completo["valor"],
           width=bar_width, color="#1f77b4", label=municipio_comparado, alpha=0.8)
    
    ax.set_xticks(x_indices)
    ax.set_xticklabels(todos_los_periodos)
    
else:
    # Solo un municipio
    x_indices = range(len(df_principal["periodo_display"]))
    ax.bar(x_indices, df_principal["valor"],
           color="#d62728", label=municipio_seleccionado, alpha=0.8)
    
    ax.set_xticks(x_indices)
    ax.set_xticklabels(df_principal["periodo_display"])

ax.set_title(f"Número de casos: {delito_seleccionado}", fontsize=16, fontweight="bold", pad=20)
ax.set_xlabel("Periodo", fontsize=12)
ax.set_ylabel("Número de casos", fontsize=12)
ax.grid(True, linestyle="--", alpha=0.3, axis='y')
ax.legend(title="Municipios", loc='best')

# Mejorar legibilidad
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
st.pyplot(fig)

# --- ESTADÍSTICAS DETALLADAS ---

st.divider()

# Estadísticas del municipio principal
if not df_principal.empty:
    st.subheader(f"📊 Estadísticas de {municipio_seleccionado}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_casos = df_principal['valor'].sum()
    promedio_tasa = df_principal['tasa_criminalidad_x1000'].mean()
    max_tasa = df_principal['tasa_criminalidad_x1000'].max()
    num_periodos = df_principal["periodo_display"].nunique()
    
    col1.metric("Total de casos", f"{total_casos:,.0f}")
    col2.metric("Tasa promedio /1000 hab.", f"{promedio_tasa:.2f}")
    col3.metric("Tasa máxima /1000 hab.", f"{max_tasa:.2f}")
    col4.metric("Períodos con datos", num_periodos)
    
    with st.expander("📋 Ver datos detallados"):
        df_mostrar = df_principal[["periodo_display", "valor", "poblacion", "tasa_criminalidad_x1000"]].copy()
        df_mostrar.columns = ["Periodo", "Casos", "Población", "Tasa x1000 hab."]
        st.dataframe(df_mostrar, use_container_width=True)

# Estadísticas del municipio comparado
if not df_comparado.empty:
    st.subheader(f"📊 Estadísticas de {municipio_comparado}")
    
    col1c, col2c, col3c, col4c = st.columns(4)
    
    total_casos_comp = df_comparado['valor'].sum()
    promedio_tasa_comp = df_comparado['tasa_criminalidad_x1000'].mean()
    max_tasa_comp = df_comparado['tasa_criminalidad_x1000'].max()
    num_periodos_comp = df_comparado["periodo_display"].nunique()
    
    col1c.metric("Total de casos", f"{total_casos_comp:,.0f}")
    col2c.metric("Tasa promedio /1000 hab.", f"{promedio_tasa_comp:.2f}")
    col3c.metric("Tasa máxima /1000 hab.", f"{max_tasa_comp:.2f}")
    col4c.metric("Períodos con datos", num_periodos_comp)
    
    with st.expander(f"📋 Ver datos detallados de {municipio_comparado}"):
        df_mostrar_comp = df_comparado[["periodo_display", "valor", "poblacion", "tasa_criminalidad_x1000"]].copy()
        df_mostrar_comp.columns = ["Periodo", "Casos", "Población", "Tasa x1000 hab."]
        st.dataframe(df_mostrar_comp, use_container_width=True)

# --- INFORMACIÓN ADICIONAL ---
st.divider()
st.subheader("ℹ️ Información sobre los datos")

col1, col2 = st.columns(2)

with col1:
    st.write("**Fuente de datos:**")
    st.write("- Ministerio del Interior de España")
    st.write("- Balances trimestrales de criminalidad")
    st.write("- Municipios con más de 20,000 habitantes")

with col2:
    st.write("**Metodología:**")
    st.write("- Tasa calculada por cada 1,000 habitantes")
    st.write("- Datos de población del INE")
    st.write("- Períodos trimestrales acumulados")