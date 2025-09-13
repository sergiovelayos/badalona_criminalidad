import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Configuración inicial
st.set_page_config(page_title="Criminalidad por Municipio", layout="wide")
st.title("📊 Evolución de Delitos por Municipio y Año")

# Cargar datos
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv('data/datos_criminalidad_webapp.csv')
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
        return None

df = cargar_datos()
if df is None:
    st.stop()

# st.success("✅ Datos cargados correctamente")

# Función para ordenar periodos cronológicamente
def crear_periodo_ordenado(df):
    """Crea una columna de periodo y la ordena cronológicamente"""
    df = df.copy()
    
    # Crear período como string
    df["periodo"] = df["año"].astype(str) + "-" + df["trimestre"]
    
    # Crear columna auxiliar para ordenamiento correcto
    df["trimestre_num"] = df["trimestre"].str.replace("T", "").astype(int)
    
    # Ordenar por año y trimestre
    df = df.sort_values(["año", "trimestre_num"])
    
    # Eliminar columna auxiliar
    df = df.drop("trimestre_num", axis=1)
    
    return df

# Selección de municipio y delito
col1, col2 = st.columns(2)

with col1:
    municipio = st.selectbox(
        "📍 Selecciona un municipio",
        options=["Todos"] + sorted(df["municipio"].unique().tolist())
    )

with col2:
    delito = st.selectbox(
        "⚖️ Selecciona un tipo de delito",
        options=["Todos"] + sorted(df["tipo_normalizado"].unique().tolist())
    )

# Filtrar datos
df_filtrado = df.copy()
if municipio != "Todos":
    df_filtrado = df_filtrado[df_filtrado["municipio"] == municipio]
if delito != "Todos":
    df_filtrado = df_filtrado[df_filtrado["tipo_normalizado"] == delito]

# Aplicar ordenamiento cronológico
df_filtrado = crear_periodo_ordenado(df_filtrado)

# Verificar que hay datos
if len(df_filtrado) == 0:
    st.warning("⚠️ No hay datos para la selección actual")
    st.stop()

# Crear gráfico mejorado
# st.subheader(f"Evolución de casos: {delito if delito != 'Todos' else 'Todos los delitos'}")

fig, ax1 = plt.subplots(figsize=(14, 6))

# Si hay múltiples municipios, graficar cada uno con diferente color
if municipio == "Todos" and len(df_filtrado["municipio"].unique()) > 1:
    # Limitar a máximo 10 municipios para legibilidad
    municipios_unicos = df_filtrado["municipio"].unique()[:10]
    if len(df_filtrado["municipio"].unique()) > 10:
        st.warning(f"⚠️ Mostrando solo los primeros 10 municipios de {len(df_filtrado['municipio'].unique())} disponibles")
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(municipios_unicos)))
    
    for i, municipio_grupo in enumerate(municipios_unicos):
        datos_grupo = df_filtrado[df_filtrado["municipio"] == municipio_grupo]
        datos_grupo = datos_grupo.sort_values(["año", "trimestre"])
        
        ax1.plot(
            range(len(datos_grupo)),  # Usar índices numéricos para el eje X
            datos_grupo["valor"], 
            marker="o", 
            label=municipio_grupo,
            color=colors[i],
            linewidth=2,
            markersize=4
        )
    
    # Configurar etiquetas del eje X
    if len(datos_grupo) > 0:
        ax1.set_xticks(range(len(datos_grupo)))
        ax1.set_xticklabels(datos_grupo["periodo"].tolist(), rotation=45)
    
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
else:
    # Un solo municipio o municipio específico
    # Agrupar por periodo si hay múltiples registros por periodo
    if municipio != "Todos":
        datos_agrupados = df_filtrado.groupby(["año", "trimestre", "periodo"])["valor"].sum().reset_index()
        datos_agrupados = datos_agrupados.sort_values(["año", "trimestre"])
    else:
        datos_agrupados = df_filtrado.groupby(["año", "trimestre", "periodo"])["valor"].sum().reset_index()
        datos_agrupados = datos_agrupados.sort_values(["año", "trimestre"])
    
    ax1.plot(
        range(len(datos_agrupados)),  # Usar índices numéricos
        datos_agrupados["valor"], 
        marker="o", 
        color="red", 
        linewidth=3,
        markersize=6,
        markerfacecolor="white",
        markeredgecolor="red",
        markeredgewidth=2
    )
    
    # Configurar etiquetas del eje X
    ax1.set_xticks(range(len(datos_agrupados)))
    ax1.set_xticklabels(datos_agrupados["periodo"].tolist(), rotation=45)

# Configuración del gráfico
ax1.set_title(f"{delito} por trimestre - {municipio}", fontsize=16, fontweight='bold')
ax1.set_xlabel("Periodo", fontsize=12)
ax1.set_ylabel("Número de casos", fontsize=12)
ax1.grid(True, alpha=0.3)

# Ajustar layout
plt.tight_layout()
st.pyplot(fig)

# Estadísticas adicionales
col1, col2, col3 = st.columns(3)

with col1:
    total_casos = df_filtrado["valor"].sum()
    st.metric("Total de casos", f"{total_casos:,}")

with col2:
    promedio_casos = df_filtrado["valor"].mean()
    st.metric("Promedio por periodo", f"{promedio_casos:.1f}")

with col3:
    periodos_unicos = df_filtrado["periodo"].nunique()
    st.metric("Periodos analizados", periodos_unicos)

# Mostrar datos en tabla (mejorada)
with st.expander("📋 Ver datos detallados"):
    # Mostrar datos ordenados correctamente
    tabla_display = df_filtrado[["municipio", "año", "trimestre", "periodo", "tipo_normalizado", "valor", "tasa_criminalidad_x1000"]].reset_index(drop=True,).copy()
    
    # Ordenar la tabla
    tabla_display = tabla_display.sort_values(["municipio", "año", "trimestre"])
    
    st.dataframe(
        tabla_display,
        use_container_width=True,
        column_config={
            "valor": st.column_config.NumberColumn("Casos", format="%d"),
            "tasa_criminalidad_x1000": st.column_config.NumberColumn("Tasa x1000", format="%.3f"),
        }
    )

# Análisis adicional si es un municipio específico
if municipio != "Todos" and delito != "Todos":
    st.subheader("📊 Análisis adicional")
    
    # Mostrar tasa de criminalidad si está disponible
    if "tasa_criminalidad_x1000" in df_filtrado.columns:
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        
        datos_tasa = df_filtrado.groupby(["año", "trimestre", "periodo"])["tasa_criminalidad_x1000"].mean().reset_index()
        datos_tasa = datos_tasa.sort_values(["año", "trimestre"])
        
        ax2.plot(
            range(len(datos_tasa)),
            datos_tasa["tasa_criminalidad_x1000"],
            marker="s",
            color="blue",
            linewidth=2,
            markersize=5,
            label="Tasa por 1000 habitantes"
        )
        
        ax2.set_xticks(range(len(datos_tasa)))
        ax2.set_xticklabels(datos_tasa["periodo"].tolist(), rotation=45)
        ax2.set_title(f"Tasa de criminalidad por 1000 habitantes - {municipio}", fontsize=14)
        ax2.set_xlabel("Periodo")
        ax2.set_ylabel("Tasa por 1000 habitantes")
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        st.pyplot(fig2)

# Información sobre los datos
with st.expander("ℹ️ Información sobre los datos"):
    st.write(f"""
    **Resumen del dataset:**
    - Total de registros: {len(df):,}
    - Municipios únicos: {df['municipio'].nunique():,}
    - Tipos de delito únicos: {df['tipo_normalizado'].nunique()}
    - Rango de años: {df['año'].min()} - {df['año'].max()}
    - Registros filtrados: {len(df_filtrado):,}
    """)