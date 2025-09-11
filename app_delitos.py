import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuración inicial
st.set_page_config(page_title="Criminalidad por Municipio", layout="wide")
st.title("📊 Evolución de Delitos por Municipio y Año")

# Cargar datos (¡AJUSTA ESTA RUTA SI ES NECESARIO!)
try:
    df = pd.read_csv('data/datos_criminalidad_webapp.csv')
    st.success("✅ Datos cargados correctamente")
except Exception as e:
    st.error(f"❌ Error al cargar datos: {str(e)}")
    st.stop()

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

# Crear período para el eje X (ej: "2016-T1")
df_filtrado["periodo"] = df_filtrado["año"].astype(str) + "-" + df_filtrado["trimestre"]

# Mostrar gráfico
st.subheader(f"Evolución de casos: {delito if delito != 'Todos' else 'Todos los delitos'}")
plt.figure(figsize=(12, 6))

# Si hay múltiples municipios, graficar cada uno con diferente color
if municipio == "Todos" and len(df_filtrado["municipio"].unique()) > 1:
    for municipio_grupo in df_filtrado["municipio"].unique():
        datos_grupo = df_filtrado[df_filtrado["municipio"] == municipio_grupo]
        plt.plot(
            datos_grupo["periodo"], 
            datos_grupo["valor"], 
            marker="o", 
            label=municipio_grupo
        )
    plt.legend()
else:
    plt.plot(
        df_filtrado["periodo"], 
        df_filtrado["valor"], 
        marker="o", 
        color="red", 
        linewidth=2
    )

plt.title(f"Casos registrados por trimestre", fontsize=14)
plt.xlabel("Periodo", fontsize=12)
plt.ylabel("Número de casos", fontsize=12)
plt.xticks(rotation=45)
plt.grid(alpha=0.3)
st.pyplot(plt)

# Mostrar datos en tabla (opcional)
with st.expander("Ver datos crudos"):
    st.dataframe(df_filtrado[["municipio", "periodo", "tipo_normalizado", "valor"]])