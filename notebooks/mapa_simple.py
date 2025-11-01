import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("🧪 Test Incremental de Renderización")

# TEST 1: Mapa más simple posible
st.header("TEST 1: Mapa Vacío Básico")
st.write("El mapa más simple posible - solo mapa base, sin datos")

try:
    m1 = folium.Map(location=[40.4168, -3.7038], zoom_start=6)
    result1 = st_folium(m1, width=700, height=400, key="test1")
    st.success("✅ TEST 1 completado")
except Exception as e:
    st.error(f"❌ TEST 1 falló: {e}")

st.markdown("---")

# TEST 2: Mapa con tiles específicos
st.header("TEST 2: Mapa con tiles='cartodbpositron'")
st.write("Mismo tiles que usa tu app")

try:
    m2 = folium.Map(location=[40.4168, -3.7038], zoom_start=6, tiles="cartodbpositron")
    result2 = st_folium(m2, width=700, height=400, key="test2")
    st.success("✅ TEST 2 completado")
except Exception as e:
    st.error(f"❌ TEST 2 falló: {e}")

st.markdown("---")

# TEST 3: Con width=None (como tu app)
st.header("TEST 3: Con width=None")
st.write("Exactamente como lo llamas en tu app")

try:
    m3 = folium.Map(location=[40.4168, -3.7038], zoom_start=6, tiles="cartodbpositron")
    result3 = st_folium(m3, width=None, height=550, key="test3")
    st.success("✅ TEST 3 completado")
except Exception as e:
    st.error(f"❌ TEST 3 falló: {e}")

st.markdown("---")

# TEST 4: Sin asignar a variable
st.header("TEST 4: Sin asignar a variable (versión antigua)")
st.write("Para ver si el problema es la asignación")

try:
    m4 = folium.Map(location=[40.4168, -3.7038], zoom_start=6, tiles="cartodbpositron")
    st_folium(m4, width=None, height=550, key="test4")
    st.success("✅ TEST 4 completado")
except Exception as e:
    st.error(f"❌ TEST 4 falló: {e}")

st.markdown("---")

# TEST 5: Con returned_objects=[]
st.header("TEST 5: Con returned_objects=[] (versión problemática)")
st.write("Para confirmar si este es el problema")

try:
    m5 = folium.Map(location=[40.4168, -3.7038], zoom_start=6, tiles="cartodbpositron")
    st_folium(m5, width=None, height=550, key="test5", returned_objects=[])
    st.success("✅ TEST 5 completado")
except Exception as e:
    st.error(f"❌ TEST 5 falló: {e}")

st.markdown("---")

# TEST 6: En columnas (como algunos layouts de Streamlit)
st.header("TEST 6: Mapa en columnas")
st.write("Para ver si el layout afecta")

col1, col2 = st.columns([2, 1])
with col1:
    try:
        m6 = folium.Map(location=[40.4168, -3.7038], zoom_start=6, tiles="cartodbpositron")
        result6 = st_folium(m6, width=None, height=400, key="test6")
        st.success("✅ TEST 6 completado")
    except Exception as e:
        st.error(f"❌ TEST 6 falló: {e}")
with col2:
    st.info("Mapa a la izquierda")

st.markdown("---")

# Información del navegador
st.header("📋 Información de Debug")
st.write("**User Agent:**")
st.code(st.query_params)

st.markdown("""
### 🔍 Instrucciones de Debug

1. **¿Cuántos tests ves mapas?** Anota cuáles funcionan y cuáles no

2. **Abre la consola del navegador (F12)**
   - Ve a la pestaña "Console"
   - Busca errores en rojo
   - Busca advertencias sobre iframe, CORS, o CSP
   - Copia cualquier error relacionado con "folium", "leaflet" o "iframe"

3. **Revisa la pestaña Network (F12)**
   - Filtra por "iframe"
   - Verifica si los iframes se cargan correctamente
   - Estado 200 = OK, 404 = No encontrado, 403 = Bloqueado

4. **Prueba en modo incógnito**
   - Cierra este navegador
   - Abre en modo incógnito
   - Ejecuta de nuevo

5. **Prueba en otro navegador**
   - Chrome, Firefox, Safari, Edge
   - A veces hay incompatibilidades específicas

### 🎯 Interpretación:

- **Si NINGÚN test muestra mapa**: Problema con streamlit-folium o el navegador
- **Si TEST 1-4 funcionan pero TEST 5 no**: `returned_objects=[]` es el problema
- **Si TEST 1-3 funcionan pero TEST 4-5 no**: Problema con parámetros específicos
- **Si todos funcionan aquí pero no en tu app**: Problema con el contexto/layout de tu app
""")