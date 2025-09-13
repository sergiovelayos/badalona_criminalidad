import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io

# --- CONFIGURACIÓN INICIAL DE LA PÁGINA ---
st.set_page_config(page_title="Criminalidad por Municipio", layout="wide")
st.title("📊 Evolución de Delitos por Municipio y Año")

# Diccionario para mapear los nombres de delitos a una versión más legible
mapeo_delitos = {
    '1. Homicidios dolosos y asesinatos consumados': 'Homicidios y Asesinatos',
    '2. Homicidios dolosos y asesinatos en grado tentativa': 'Homicidios en Tentativa',
    '3. Delitos graves y menos graves de lesiones y riña tumultuaria': 'Lesiones y Riñas',
    '4. Secuestro': 'Secuestros',
    '5. Delitos contra la libertad sexual': 'Delitos Sexuales',
    '5.1.-Agresión sexual con penetración': 'Agresiones Sexuales con Penetración',
    '5.2.-Resto de delitos contra la libertad sexual': 'Otros Delitos Sexuales',
    '6. Robos con violencia e intimidación': 'Robos con Violencia',
    '7. Robos con fuerza en domicilios, establecimientos y otras instalaciones': 'Robos con Fuerza',
    '7.1.-Robos con fuerza en domicilios': 'Robos en Domicilios',
    '8. Hurtos': 'Hurtos',
    '9. Sustracciones de vehículos': 'Sustracción de Vehículos',
    '10. Tráfico de drogas': 'Tráfico de Drogas',
    '11. Resto de criminalidad convencional': 'Otros Delitos Convencionales',
    '12.-Estafas informáticas': 'Estafas Informáticas',
    '13.-Otros ciberdelitos': 'Otros Ciberdelitos',
    'I. CRIMINALIDAD CONVENCIONAL': 'Total Criminalidad Convencional',
    'II. CIBERCRIMINALIDAD (infracciones penales cometidas en/por medio ciber)': 'Total Cibercriminalidad',
    'III. TOTAL INFRACCIONES PENALES': 'TOTAL de Delitos'
}

# --- CARGA DE DATOS ---
@st.cache_data
def cargar_datos():
    """
    Carga los datos directamente desde el archivo CSV y aplica el mapeo.
    """
    try:
        df = pd.read_csv('data/datos_criminalidad_webapp.csv')
    except FileNotFoundError:
        st.error("Error: Archivo 'data/datos_criminalidad_webapp.csv' no encontrado.")
        st.stop()
    
    # Asegurar tipos de datos correctos
    df['año'] = df['año'].astype(int)
    df['trimestre'] = df['trimestre'].astype(str)
    if 'municipio_nombre' in df.columns and 'municipio' not in df.columns:
        df.rename(columns={'municipio_nombre': 'municipio'}, inplace=True)
    
    # Aplicar el mapeo a la columna de tipologías
    df['tipo_normalizado'] = df['tipo_normalizado'].map(mapeo_delitos)
    
    # Calcular la tasa de criminalidad
    df['tasa_criminalidad_x1000'] = (df['valor'] / df['poblacion']) * 1000

    return df

# --- FUNCIÓN DE PREPROCESAMIENTO ---
def crear_periodo_ordenado(df):
    """Crea una columna 'periodo' y ordena el DataFrame cronológicamente."""
    df = df.copy()
    df['periodo'] = df['año'].astype(str) + '-' + df['trimestre']
    df['trimestre_num'] = df['trimestre'].str.replace('T', '', regex=False).astype(int)
    df = df.sort_values(['año', 'trimestre_num', 'municipio'])
    df = df.drop(columns=['trimestre_num'])
    return df

# --- LÓGICA PRINCIPAL DE LA APP ---
df_cargado = cargar_datos()
if df_cargado is None:
    st.stop()

df_base = crear_periodo_ordenado(df_cargado)

# --- FILTROS DE SELECCIÓN ---
col1, col2 = st.columns(2)

with col1:
    municipios_unicos = sorted(df_base["municipio"].unique().tolist())
    municipio_seleccionado = st.selectbox(
        "📍 Selecciona un municipio",
        options=municipios_unicos
    )

with col2:
    opciones_delito = list(mapeo_delitos.values())
    delito_seleccionado = st.selectbox(
        "⚖️ Selecciona un tipo de delito",
        options=opciones_delito
    )

# --- LÓGICA DE FILTRADO ---
# Se filtra el DataFrame principal basado en la selección del usuario.
df_principal = df_base[
    (df_base["municipio"] == municipio_seleccionado) &
    (df_base["tipo_normalizado"] == delito_seleccionado)
].copy()


if df_principal.empty:
    st.warning("⚠️ No hay datos disponibles para la selección actual.")
    st.stop()

# --- CAMBIO NUEVO: SELECCIÓN DEL SEGUNDO MUNICIPIO ---
st.subheader("Comparar con otro municipio")
municipios_comparables = [m for m in municipios_unicos if m != municipio_seleccionado]
municipio_comparado = st.selectbox(
    "Selecciona un segundo municipio para comparar (opcional)",
    options=["Ninguno"] + municipios_comparables
)

# --- CÁLCULO Y FILTRADO DE DATOS DEL SEGUNDO MUNICIPIO ---
df_comparado = pd.DataFrame()
if municipio_comparado != "Ninguno":
    df_comparado = df_base[
        (df_base["municipio"] == municipio_comparado) &
        (df_base["tipo_normalizado"] == delito_seleccionado)
    ].copy()

# --- GRÁFICO PRINCIPAL ---
st.subheader(f"Comparativa de Tasa de Criminalidad: {delito_seleccionado}")
fig, ax1 = plt.subplots(figsize=(14, 6))

# Trazar la línea principal
ax1.plot(
    df_principal["periodo"],
    df_principal["tasa_criminalidad_x1000"],
    marker="o",
    color="#d62728",
    linewidth=2.5,
    label=municipio_seleccionado
)

# Trazar la línea del segundo municipio si está seleccionado
if not df_comparado.empty:
    ax1.plot(
        df_comparado["periodo"],
        df_comparado["tasa_criminalidad_x1000"],
        marker="o",
        color="#1f77b4",
        linewidth=2.5,
        linestyle="--",  # Esto crea la línea discontinua
        label=municipio_comparado
    )
    
ax1.set_title(f"Tasa de Criminalidad de {delito_seleccionado} (por 1000 hab.)", fontsize=16, fontweight='bold', pad=20)
ax1.set_xlabel("Periodo")
ax1.set_ylabel("Tasa por 1000 habitantes")
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(title="Municipios")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
st.pyplot(fig)

# --- MÉTRICAS Y TABLAS (Modificadas para mostrar solo el municipio principal) ---
st.divider()
st.subheader("Detalles del municipio seleccionado")
col1, col2, col3 = st.columns(3)

total_casos_principal = df_principal["valor"].sum()
col1.metric("Total de casos", f"{total_casos_principal:,.0f}")

promedio_tasa_principal = df_principal["tasa_criminalidad_x1000"].mean()
col2.metric("Promedio de Tasa/1000 hab.", f"{promedio_tasa_principal:.2f}")

periodos_unicos = df_principal["periodo"].nunique()
col3.metric("Nº de periodos", periodos_unicos)

with st.expander("📋 Ver datos detallados del municipio seleccionado"):
    st.dataframe(df_principal[["municipio", "periodo", "valor", "poblacion", "tasa_criminalidad_x1000", "tipo_normalizado"]], use_container_width=True)

if not df_comparado.empty:
    st.divider()
    st.subheader(f"Detalles de {municipio_comparado}")
    total_casos_comparado = df_comparado["valor"].sum()
    promedio_tasa_comparado = df_comparado["tasa_criminalidad_x1000"].mean()
    
    col1c, col2c, col3c = st.columns(3)
    col1c.metric("Total de casos", f"{total_casos_comparado:,.0f}")
    col2c.metric("Promedio de Tasa/1000 hab.", f"{promedio_tasa_comparado:.2f}")
    col3c.metric("Nº de periodos", df_comparado["periodo"].nunique())

    with st.expander(f"📋 Ver datos detallados de {municipio_comparado}"):
        st.dataframe(df_comparado[["municipio", "periodo", "valor", "poblacion", "tasa_criminalidad_x1000", "tipo_normalizado"]], use_container_width=True)