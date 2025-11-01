import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
import sqlite3
import os

st.title("🔍 Diagnóstico del Mapa de Criminalidad")
st.markdown("---")

# --- RUTAS ---
db_path = "data/delitos_raw.db" 
geojson_ccaa = "data/mapas/comunidades_simplificadas.geoparquet"
geojson_provincias = "data/mapas/provincias_simplificadas.geoparquet"
geojson_municipios = "data/mapas/municipios_simplificadas.geoparquet"

# TEST 1: Verificar archivos
st.header("📁 TEST 1: Verificación de Archivos")
archivos = {
    "Base de datos": db_path,
    "GeoJSON CCAA": geojson_ccaa,
    "GeoJSON Provincias": geojson_provincias,
    "GeoJSON Municipios": geojson_municipios
}

for nombre, ruta in archivos.items():
    existe = os.path.exists(ruta)
    if existe:
        st.success(f"✅ {nombre}: **ENCONTRADO** ({ruta})")
    else:
        st.error(f"❌ {nombre}: **NO ENCONTRADO** ({ruta})")

st.markdown("---")

# TEST 2: Cargar y verificar datos de la base de datos
st.header("🗄️ TEST 2: Verificación de Base de Datos")
try:
    conn = sqlite3.connect(db_path)
    
    # Verificar tablas
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()
    st.info(f"📋 Tablas encontradas: {[t[0] for t in tablas]}")
    
    # Leer datos
    query = "SELECT * FROM delitos_aux LIMIT 5"
    df_sample = pd.read_sql_query(query, conn)
    
    st.success(f"✅ Datos cargados: {len(df_sample)} filas de muestra")
    st.write("**Primeras 5 filas:**")
    st.dataframe(df_sample)
    
    # Mostrar nombres de columnas
    st.write("**Nombres de columnas:**", list(df_sample.columns))
    
    # Contar registros totales
    cursor.execute("SELECT COUNT(*) FROM delitos_aux")
    total = cursor.fetchone()[0]
    st.info(f"📊 Total de registros en delitos_aux: **{total:,}**")
    
    conn.close()
    
except Exception as e:
    st.error(f"❌ Error al cargar base de datos: {e}")
    st.stop()

st.markdown("---")

# TEST 3: Procesamiento de datos
st.header("🔄 TEST 3: Procesamiento de Datos")
try:
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM delitos_aux"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Asignar nombres (versión corregida)
    df.columns = ['periodo', 'geo', 'tipo', 'valor_acumulado', 'valor', 'pob', 'tasa']
    st.success(f"✅ Columnas renombradas correctamente")
    
    # Procesamiento de geo
    df['tipo_geo'] = np.nan
    df['codigo_geo'] = np.nan
    df['nombre_geo'] = np.nan
    
    # Municipios
    mun_mask = df['geo'].str.match(r'^\d{5}')
    df.loc[mun_mask, 'tipo_geo'] = 'municipio'
    df.loc[mun_mask, 'codigo_geo'] = df.loc[mun_mask, 'geo'].str.slice(0, 5)
    df.loc[mun_mask, 'nombre_geo'] = df.loc[mun_mask, 'geo'].str.slice(6)
    
    # Provincias
    pro_mask = df['geo'].str.startswith('Provincia')
    df.loc[pro_mask, 'tipo_geo'] = 'provincia'
    df.loc[pro_mask, 'codigo_geo'] = df.loc[pro_mask, 'geo'].str.split().str[1]
    df.loc[pro_mask, 'nombre_geo'] = df.loc[pro_mask, 'geo'].str.split(n=2).str[2]
    
    # CCAA
    ccaa_mask = df['geo'].str.startswith('CCAA')
    df.loc[ccaa_mask, 'tipo_geo'] = 'ccaa'
    df.loc[ccaa_mask, 'codigo_geo'] = df.loc[ccaa_mask, 'geo'].str.split().str[1]
    df.loc[ccaa_mask, 'nombre_geo'] = df.loc[ccaa_mask, 'geo'].str.split(n=2).str[2]
    
    # Verificar distribución de tipo_geo
    st.write("**Distribución de tipo_geo:**")
    tipo_geo_counts = df['tipo_geo'].value_counts()
    st.dataframe(tipo_geo_counts)
    
    # Mostrar ejemplos de cada tipo
    st.write("**Ejemplos de municipios:**")
    st.dataframe(df[df['tipo_geo'] == 'municipio'][['geo', 'codigo_geo', 'nombre_geo']].head(3))
    
    st.write("**Ejemplos de provincias:**")
    st.dataframe(df[df['tipo_geo'] == 'provincia'][['geo', 'codigo_geo', 'nombre_geo']].head(3))
    
    st.write("**Ejemplos de CCAA:**")
    st.dataframe(df[df['tipo_geo'] == 'ccaa'][['geo', 'codigo_geo', 'nombre_geo']].head(3))
    
    # Procesar periodo
    df['periodo_dt'] = pd.to_datetime(df['periodo'])
    df['quarter'] = df['periodo_dt'].dt.quarter
    df['year'] = df['periodo_dt'].dt.year
    df['periodo'] = "T" + df['quarter'].astype(str) + " " + df['year'].astype(str)
    
    st.write("**Periodos únicos (primeros 10):**", sorted(df['periodo'].unique())[:10])
    
    # Renombrar tasa
    df.rename(columns={'tasa': 'tasa_por_1000'}, inplace=True)
    
    st.success("✅ Procesamiento de datos completado")
    
    # Guardar para siguientes tests
    st.session_state['df_processed'] = df
    
except Exception as e:
    st.error(f"❌ Error en procesamiento: {e}")
    import traceback
    st.code(traceback.format_exc())
    st.stop()

st.markdown("---")

# TEST 4: Cargar geodatos
st.header("🗺️ TEST 4: Verificación de Geodatos")
try:
    # CCAA
    st.subheader("Comunidades Autónomas")
    gdf_ccaa = gpd.read_parquet(geojson_ccaa)
    st.success(f"✅ CCAA cargadas: {len(gdf_ccaa)} registros")
    st.write("**CRS:**", gdf_ccaa.crs)
    st.write("**Columnas:**", list(gdf_ccaa.columns))
    
    # Crear JOIN_CODE
    if gdf_ccaa.crs != "EPSG:4258":
        gdf_ccaa = gdf_ccaa.to_crs("EPSG:4258")
    gdf_ccaa["JOIN_CODE"] = gdf_ccaa["NATCODE"].astype(str).str[2:4]
    st.write("**JOIN_CODE ejemplos:**", gdf_ccaa[["NATCODE", "JOIN_CODE", "NAMEUNIT"]].head(3))
    
    # Provincias
    st.subheader("Provincias")
    gdf_pro = gpd.read_parquet(geojson_provincias)
    st.success(f"✅ Provincias cargadas: {len(gdf_pro)} registros")
    if gdf_pro.crs != "EPSG:4258":
        gdf_pro = gdf_pro.to_crs("EPSG:4258")
    gdf_pro["JOIN_CODE"] = gdf_pro["NATCODE"].astype(str).str[4:6]
    st.write("**JOIN_CODE ejemplos:**", gdf_pro[["NATCODE", "JOIN_CODE", "NAMEUNIT"]].head(3))
    
    # Municipios
    st.subheader("Municipios")
    gdf_mun = gpd.read_parquet(geojson_municipios)
    st.success(f"✅ Municipios cargados: {len(gdf_mun)} registros")
    if gdf_mun.crs != "EPSG:4258":
        gdf_mun = gdf_mun.to_crs("EPSG:4258")
    gdf_mun["JOIN_CODE"] = gdf_mun["NATCODE"].astype(str).str[-5:]
    st.write("**JOIN_CODE ejemplos:**", gdf_mun[["NATCODE", "JOIN_CODE", "NAMEUNIT"]].head(3))
    
    st.session_state['gdf_ccaa'] = gdf_ccaa
    st.session_state['gdf_pro'] = gdf_pro
    st.session_state['gdf_mun'] = gdf_mun
    
except Exception as e:
    st.error(f"❌ Error al cargar geodatos: {e}")
    import traceback
    st.code(traceback.format_exc())
    st.stop()

st.markdown("---")

# TEST 5: Merge de datos
st.header("🔗 TEST 5: Prueba de Merge")

if 'df_processed' in st.session_state and 'gdf_ccaa' in st.session_state:
    df = st.session_state['df_processed']
    gdf_ccaa = st.session_state['gdf_ccaa']
    
    # Filtrar para un caso específico
    st.subheader("Prueba con CCAA")
    
    # Seleccionar un periodo y tipo
    periodos = sorted(df['periodo'].unique(), reverse=True)
    periodo_test = st.selectbox("Selecciona un periodo para probar:", periodos)
    
    tipos = df['tipo'].unique()
    tipo_test = st.selectbox("Selecciona un tipo de delito:", sorted(tipos)[:10])
    
    # Filtrar datos
    df_filtered = df[(df['periodo'] == periodo_test) & (df['tipo'] == tipo_test)]
    st.write(f"**Registros filtrados:** {len(df_filtered)}")
    
    if len(df_filtered) > 0:
        st.write("**Muestra de datos filtrados:**")
        st.dataframe(df_filtered[['periodo', 'geo', 'tipo', 'tipo_geo', 'codigo_geo', 'valor', 'tasa_por_1000']].head())
        
        # Filtrar solo CCAA
        df_ccaa = df_filtered[df_filtered['tipo_geo'] == 'ccaa']
        st.write(f"**Registros de CCAA:** {len(df_ccaa)}")
        
        if len(df_ccaa) > 0:
            st.write("**Códigos en datos de criminalidad:**")
            st.write(sorted(df_ccaa['codigo_geo'].unique()))
            
            st.write("**Códigos en geodatos:**")
            st.write(sorted(gdf_ccaa['JOIN_CODE'].unique()))
            
            # Intentar merge
            try:
                gdf_merged = pd.merge(
                    gdf_ccaa,
                    df_ccaa,
                    left_on='JOIN_CODE',
                    right_on='codigo_geo',
                    how='left'
                )
                
                st.success(f"✅ Merge exitoso: {len(gdf_merged)} registros")
                st.write("**Registros con datos:**", gdf_merged['valor'].notna().sum())
                st.write("**Registros sin datos:**", gdf_merged['valor'].isna().sum())
                
                # Mostrar datos fusionados
                st.write("**Muestra del merge:**")
                st.dataframe(gdf_merged[['NAMEUNIT', 'JOIN_CODE', 'codigo_geo', 'valor', 'tasa_por_1000']].head(10))
                
                # Verificar si hay valores para mostrar
                valores_positivos = gdf_merged[gdf_merged['valor'].notna() & (gdf_merged['valor'] > 0)]
                st.write(f"**Registros con valores > 0:** {len(valores_positivos)}")
                
                if len(valores_positivos) > 0:
                    st.write("**Rango de valores:**")
                    st.write(f"- Mínimo: {valores_positivos['valor'].min()}")
                    st.write(f"- Máximo: {valores_positivos['valor'].max()}")
                    st.write(f"- Promedio: {valores_positivos['valor'].mean():.2f}")
                else:
                    st.warning("⚠️ No hay valores mayores a 0 en el merge")
                
            except Exception as e:
                st.error(f"❌ Error en merge: {e}")
                import traceback
                st.code(traceback.format_exc())
        else:
            st.warning("⚠️ No hay datos de CCAA para el periodo y tipo seleccionados")
    else:
        st.warning("⚠️ No hay datos para el periodo y tipo seleccionados")

st.markdown("---")

# TEST 6: Verificar tipos de delitos
st.header("📊 TEST 6: Tipos de Delitos Disponibles")
if 'df_processed' in st.session_state:
    df = st.session_state['df_processed']
    
    st.write(f"**Total de tipos únicos:** {df['tipo'].nunique()}")
    st.write("**Lista de tipos:**")
    for tipo in sorted(df['tipo'].unique()):
        count = len(df[df['tipo'] == tipo])
        st.text(f"  • {tipo} ({count:,} registros)")

st.markdown("---")
st.success("🎉 Diagnóstico completado. Revisa los resultados arriba para identificar el problema.")