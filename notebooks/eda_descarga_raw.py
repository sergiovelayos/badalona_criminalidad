import pandas as pd
from io import StringIO
import openpyxl
import os
import seaborn as sns
import matplotlib.pyplot as plt

# Configurar pandas para mostrar todas las columnas al imprimir un DataFrame
pd.set_option('display.max_columns', None)

# Ruta al archivo CSV
filename = r"./data/españa_semestre_1_2_24_25.csv"
filepob = r"./data/poblacion_municipios_bcn_24_limpiado.csv"

with open(filename, encoding='latin-1') as f:
    data = f.read()

# crea un DataFrame desde el texto leído, usando ';' como separador y saltando la primera línea
data = pd.read_csv(StringIO(data), sep=';', skiprows=1)

# nombre de las columnas
data.columns = [
    "geografía",
    "tipología",
    "periodo",
    "valor"
]
# convierte la columna valor a numérica, cambiando las comas por puntos y forzando los errores a NaN
data['valor'] = pd.to_numeric(
    data['valor'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False),
    errors='coerce'
)

# crear columna que selecciona los valores de la columna geografía que contienen 5 números y que puede empezar por 0
data['cp'] = data['geografía'].str.extract(r'(\b\d{5}\b)')
# aquellas observaciones que tienen 5 números en geografía, crear otra columna con el resto del texto que se llame población
data['población'] = data['geografía'].str.replace(r'^\d{5}\s*', '', regex=True).str.strip()

# crea una columna que se llame provincia que contenga todos los registros de geografía que empiecen por Provincia
data['provincia'] = data['geografía'].where(data['geografía'].str.startswith('Provincia'))

# Filtrar por todos aquellos que el campo cp tiene los 2 primers dígitos 08 (provincia de Barcelona)
bcn = data[data['cp'].str.startswith('08', na=False)]
# print(bcn['periodo'].unique())

# Normalizar la columna 'periodo' para evitar problemas de espacios o mayúsculas/minúsculas
bcn.loc[:, 'periodo'] = bcn['periodo'].str.strip().str.lower()

# group by población y tipología en periodo enero-junio 2025 y sumar los valores
bcn_grouped = (
    bcn[bcn['periodo'] == 'enero-junio 2025']
    .groupby(['población', 'tipología','cp'])['valor']
    .sum()
    .reset_index()
    .sort_values(['población', 'tipología'], ascending=[True, False])
)
# print(bcn_grouped.info())


# Leer el archivo CSV de población
poblacion = pd.read_csv(filepob, dtype={'cod_mun': 'object'})
# print(poblacion.info())
# unir dataframe población usando cod_mun con data usando la columna cp
bcn_grouped = bcn_grouped.merge(poblacion, left_on='cp', right_on='cod_mun', how='left')
# eliminar la columna cod_mun
bcn_grouped = bcn_grouped.drop(columns=['cod_mun','Sexo','Periodo','Municipios'])

bcn_grouped = bcn_grouped.rename(columns={'población': 'municipio', 'Total': 'población'})

bcn_grouped['valor_ratio'] = ((bcn_grouped['valor'] / bcn_grouped['población']) * 100).round(2)

# print(bcn_grouped.head())

# # Filtrar por tipología 'Tráfico de drogas' y ordenar descendente por 'valor'
# trafico_drogas = bcn_grouped[bcn_grouped['tipología'] == '10. Tráfico de drogas']
# # print(trafico_drogas)

# # Eliminar posibles NaN en 'valor' y 'población'
# trafico_drogas = trafico_drogas.dropna(subset=['valor', 'población'])

# Ordenar y seleccionar top 10
top10 = bcn_grouped.sort_values('valor', ascending=False)[['municipio', 'tipología', 'valor', 'población', 'valor_ratio']]

top10.to_csv('./data/top_criminalidad_bcn_enero_junio_2025.csv', index=False, encoding='utf-8')

def plot_heatmap_by_tipologia(tipologia, df=bcn_grouped, top_n=20):
    # Filtrar por tipología
    filtered = df[df['tipología'] == tipologia].dropna(subset=['valor_ratio'])
    # Seleccionar top N por valor_ratio
    top = filtered.sort_values('valor_ratio', ascending=False).head(top_n)
    if top.empty:
        print(f"No hay datos para la tipología '{tipologia}'.")
        return
    # Crear directorio si no existe
    os.makedirs('./charts', exist_ok=True)
    # Crear mapa de calor
    plt.figure(figsize=(10, 8))
    heatmap_data = top.pivot_table(index='municipio', values='valor_ratio', aggfunc='first')
    sns.heatmap(heatmap_data, annot=True, cmap='YlOrRd', fmt='.2f', linewidths=.5, cbar_kws={'label': 'Ratio (%)'})
    plt.title(f"Top {top_n} municipios por '{tipologia}' (valor_ratio)")
    plt.xlabel('Tipología')
    plt.ylabel('Municipio')
    plt.tight_layout()
    filename = f'./charts/heatmap_{tipologia.replace(".", "").replace(" ", "_").lower()}.png'
    plt.savefig(filename)
    plt.close()
    print(f"Mapa de calor guardado en {filename}")

# Ejemplo de uso:
# plot_heatmap_by_tipologia('10. Tráfico de drogas')



# if not top10.empty:
#     # Crear directorio si no existe
#     os.makedirs('./charts', exist_ok=True)
#     # Crear gráfica de barras
#     plt.figure(figsize=(10, 6))
#     bars = plt.bar(top10['población'], top10['valor'], color='skyblue')
#     plt.xlabel('Población')
#     plt.ylabel('Valor')
#     plt.title('Top 10 poblaciones por Tráfico de drogas (enero-junio 2025)')
#     plt.xticks(rotation=45, ha='right')
#     plt.tight_layout()

#     # Añadir el valor encima de cada barra
#     for bar in bars:
#         height = bar.get_height()
#         plt.text(
#             bar.get_x() + bar.get_width() / 2,
#             height,
#             f'{int(height)}',
#             ha='center',
#             va='bottom'
#         )

#     # Guardar la figura en el directorio /charts
#     plt.savefig('./charts/top10_trafico_drogas.png')
#     plt.close()
#     print("Gráfica guardada en ./charts/top10_trafico_drogas.png")
# else:
#     print("No hay datos para 'Tráfico de drogas' en el periodo seleccionado.")