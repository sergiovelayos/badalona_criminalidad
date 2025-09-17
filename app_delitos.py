import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

# --- CONFIGURACIÓN INICIAL Y CONSTANTES (Sin cambios) ---
st.set_page_config(page_title="Criminalidad por Municipio", layout="wide")
st.title("📊 Evolución de Delitos por Municipio y Trimestre")
st.markdown("""
Compara fácilmente los datos de [Balances trimestrales de criminalidad del Ministerio de Interior](https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/balances) entre municipios de más de 20.000 habitantes desde 2015 hasta junio de 2025. [Más info](https://github.com/sergiovelayos/badalona_criminalidad)
""")

DB_PATH = "data/delitos.db"
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
mapeo_inverso_delitos = {v: k for k, v in mapeo_delitos.items()}

# --- FUNCIONES OPTIMIZADAS ---

@st.cache_data
def get_municipios():
    """Obtiene solo la lista de municipios únicos. Es muy rápido."""
    conn = sqlite3.connect(DB_PATH)
    municipios = pd.read_sql_query("SELECT DISTINCT municipio FROM delitos ORDER BY municipio", conn)
    conn.close()
    return municipios["municipio"].tolist()

@st.cache_data
def get_crime_data(municipios: list, tipo_delito_normalizado: str):
    """
    Función optimizada que busca SOLO los datos para los municipios y delito seleccionados.
    Adaptada para la nueva estructura de base de datos optimizada.
    """
    if not municipios or not tipo_delito_normalizado:
        return pd.DataFrame()

    tipo_delito_original = mapeo_inverso_delitos.get(tipo_delito_normalizado)
    if not tipo_delito_original:
        return pd.DataFrame()

    # --- CONSULTA SQL OPTIMIZADA para la nueva estructura ---
    # Como ya no hay duplicados en la DB, la consulta es más simple y eficiente
    query = """
    SELECT
        d.año,
        d.trimestre,
        d.municipio,
        d.tipo_normalizado,
        d.valor,
        (
            SELECT p.POB
            FROM poblacion p
            WHERE p.cod_mun = d.codigo_postal
              AND p.AÑO <= d.año
            ORDER BY p.AÑO DESC
            LIMIT 1
        ) AS poblacion
    FROM delitos d
    WHERE
        d.municipio IN ({placeholders})
        AND d.tipo_normalizado = ?
    ORDER BY
        d.año, d.trimestre;
    """.format(placeholders=','.join('?' for _ in municipios))

    params = municipios + [tipo_delito_original]

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if df.empty:
        return pd.DataFrame()

    # --- PROCESAMIENTO SIMPLIFICADO (ya no hay duplicados que manejar) ---
    # Mapear nombres de delitos
    df["tipo_normalizado"] = df["tipo_normalizado"].map(mapeo_delitos).fillna(df["tipo_normalizado"])
    
    # Convertir tipos de datos
    df["año"] = df["año"].astype(int)
    df["trimestre"] = df["trimestre"].astype(str)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
    df["poblacion"] = pd.to_numeric(df["poblacion"], errors="coerce").fillna(0)

    # Calcular tasa de criminalidad
    df["tasa_criminalidad_x1000"] = df.apply(
        lambda row: (row["valor"] / row["poblacion"] * 1000) if row["poblacion"] > 0 else 0,
        axis=1
    )

    # Crear periodo ordenado para visualización
    df["periodo"] = df["año"].astype(str) + "-" + df["trimestre"]
    df["trimestre_num"] = df["trimestre"].str.replace("T", "", regex=False).astype(int)
    df = df.sort_values(["año", "trimestre_num", "municipio"])

    return df.drop(columns=["trimestre_num"])

# --- INTERFAZ DE STREAMLIT  ---

col1, col2 = st.columns(2)
with col1:
    municipios_unicos = get_municipios()
    municipio_seleccionado = st.selectbox("📍 Selecciona un municipio", options=municipios_unicos)
with col2:
    opciones_delito = list(mapeo_delitos.values())
    delito_seleccionado = st.selectbox("⚖️ Selecciona un tipo de delito", options=opciones_delito)

# Reemplaza la sección del gráfico de tasa de criminalidad (aproximadamente línea 120-140)

st.subheader(f"Comparativa de Tasa de Criminalidad: {delito_seleccionado}")
fig, ax1 = plt.subplots(figsize=(14, 6))

# Gráfico del municipio principal
ax1.plot(df_principal["periodo"], df_principal["tasa_criminalidad_x1000"],
         marker="o", color="#d62728", linewidth=2.5, label=municipio_seleccionado)

# Solo añadir el segundo municipio si existe y tiene datos
if not df_comparado.empty:
    ax1.plot(df_comparado["periodo"], df_comparado["tasa_criminalidad_x1000"],
             marker="o", color="#1f77b4", linewidth=2.5, linestyle="--", label=municipio_comparado)

# Configuración del gráfico
ax1.set_title(f"Tasa de Criminalidad de {delito_seleccionado} (por 1000 hab.)", fontsize=16, fontweight="bold", pad=20)
ax1.set_xlabel("Periodo")
ax1.set_ylabel("Tasa por 1000 habitantes")
ax1.grid(True, linestyle="--", alpha=0.6)
ax1.legend(title="Municipios")

# Rotar etiquetas X solo si hay muchos períodos
if len(df_principal["periodo"]) > 10:
    plt.xticks(rotation=45, ha="right")
else:
    plt.xticks(rotation=30, ha="right")

plt.tight_layout()
st.pyplot(fig)

# Reemplaza la sección del gráfico de volumen de delitos (aproximadamente línea 150-190)

# --- GRÁFICO DE VOLUMEN DE DELITOS (Corregido para diferentes períodos) ---
st.subheader(f"Comparativa de volumen de delitos: {delito_seleccionado}")
fig, ax1 = plt.subplots(figsize=(14, 6))

if not df_comparado.empty:
    # CREAR DATASET COMBINADO para alinear períodos
    # Obtener todos los períodos únicos de ambos municipios
    todos_los_periodos = sorted(list(set(df_principal["periodo"].tolist() + df_comparado["periodo"].tolist())))
    
    # Crear DataFrames completos con todos los períodos (rellenar con 0 si falta)
    df_principal_completo = pd.DataFrame({'periodo': todos_los_periodos})
    df_principal_completo = df_principal_completo.merge(
        df_principal[['periodo', 'valor']], 
        on='periodo', 
        how='left'
    ).fillna(0)
    
    df_comparado_completo = pd.DataFrame({'periodo': todos_los_periodos})
    df_comparado_completo = df_comparado_completo.merge(
        df_comparado[['periodo', 'valor']], 
        on='periodo', 
        how='left'
    ).fillna(0)
    
    # Configurar barras
    bar_width = 0.35
    x_indices = range(len(todos_los_periodos))
    
    # Barras para ambos municipios
    ax1.bar([i - bar_width/2 for i in x_indices], df_principal_completo["valor"],
            width=bar_width, color="#d62728", label=municipio_seleccionado, align='center')
    
    ax1.bar([i + bar_width/2 for i in x_indices], df_comparado_completo["valor"],
            width=bar_width, color="#1f77b4", label=municipio_comparado, align='center')
    
    # Configuración del gráfico
    ax1.set_xticks(x_indices)
    ax1.set_xticklabels(todos_los_periodos, rotation=45, ha="right")

else:
    # Solo un municipio - gráfico simple
    bar_width = 0.35
    x_indices = range(len(df_principal["periodo"]))
    
    ax1.bar(x_indices, df_principal["valor"],
            width=bar_width, color="#d62728", label=municipio_seleccionado)
    
    ax1.set_xticks(x_indices)
    ax1.set_xticklabels(df_principal["periodo"], rotation=45, ha="right")

# Configuración común del gráfico
ax1.set_title(f"Volumen de delitos de {delito_seleccionado}", fontsize=16, fontweight="bold", pad=20)
ax1.set_xlabel("Periodo")
ax1.set_ylabel("Volumen delitos")
ax1.grid(True, linestyle="--", alpha=0.6, axis='y')
ax1.legend(title="Municipios")
plt.tight_layout()
st.pyplot(fig)






st.divider()
st.subheader(f"Detalles de {municipio_seleccionado}")
col1, col2, col3 = st.columns(3)
col1.metric("Total de casos", f"{df_principal['valor'].sum():,.0f}")
col2.metric("Promedio de Tasa/1000 hab.", f"{df_principal['tasa_criminalidad_x1000'].mean():.2f}")
col3.metric("Nº de periodos", df_principal["periodo"].nunique())
with st.expander("📋 Ver datos detallados"):
    st.dataframe(df_principal[["municipio","periodo","valor","poblacion","tasa_criminalidad_x1000","tipo_normalizado"]], use_container_width=True)

if not df_comparado.empty:
    st.divider()
    st.subheader(f"Detalles de {municipio_comparado}")
    col1c, col2c, col3c = st.columns(3)
    col1c.metric("Total de casos", f"{df_comparado['valor'].sum():,.0f}")
    col2c.metric("Promedio de Tasa/1000 hab.", f"{df_comparado['tasa_criminalidad_x1000'].mean():.2f}")
    col3c.metric("Nº de periodos", df_comparado["periodo"].nunique())
    with st.expander(f"📋 Ver datos detallados de {municipio_comparado}"):
        st.dataframe(df_comparado[["municipio","periodo","valor","poblacion","tasa_criminalidad_x1000","tipo_normalizado"]], use_container_width=True)