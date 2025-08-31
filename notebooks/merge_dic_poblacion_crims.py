import pandas as pd

# Abrir un archivo Excel y crear un DataFrame
excel_filename = "./data/diccionario25_grografia_ine.xlsx"
df_excel = pd.read_excel(excel_filename, header=1)

df_excel.to_csv('./data/diccionario25_grografia_ine.csv', index=False)

# Mostrar las primeras filas del DataFrame
# print(df_excel[df_excel['NOMBRE'].str.contains('Badalona', case=False)])
#print(df_excel.count()) # 8132

#print(data['población'].nunique()) # 502

# Combina ambos dataframes por las columnas de población y NOMBRE y muestra cuantos de los registros de población no cruzan con NOMBRE siempre y cuando en la columna cp haya 5 números
# data = data[data['cp'].notnull()]
# realiza un merge left y añade una columna _merge para indicar el tipo de cruce      
# merged = pd.merge(data, df_excel, left_on='población', right_on='NOMBRE', how='left', indicator=True)
#print(merged[merged['_merge'] == 'left_only'].shape[0]) # 340
# muestra los registros que no cruzan
#print(merged[merged['_merge'] == 'left_only'][['población', 'geografía']].drop_duplicates().sort_values(by='población'))    

