# Datos de criminalidad por tipología penal en Badalona
Los medios de comunicación, políticos e instituciones hacen un uso poco riguroso de los datos de criminalidad con frecuencia. No se contextualiza o no se compara con la misma base y casi nunca se enlaza a la fuente para poder comprobar la veracidad. Por todos estos motivos he creado este dataset con datos del [Ministerio del Interior](https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/balances.html).

![image](https://github.com/user-attachments/assets/03700369-ca91-4e3c-bae0-d953987700f0)


Estos datos se publican con periodicidad trimestral en un formato poco amigable para realizar cualquier análisis. Estas son algunas de las advertencias que tendría en cuenta a la hora de analizar estos datos:
- El origen de datos se inicia en el primer trimestre de 2016.
- El 10 de noviembre de 2024 había datos hasta el sedungo trimestre de 2024
- Los conceptos cambian por lo que no podemos comparar un mismo concepto durante todo el periodo comprendido
- Hay categorías que agregan sub categorías pero la suma de las subcategorías no coincide con las categorías. Por ejemplo: en el tercer trimestre
- Los datos para un mismo periodo pueden cambiar.

¿Cómo obtener los datos desde el portal del ministerio?

He descargado cada trimestre por separado después de filtrar el municipio de Badalona.

![image](https://github.com/user-attachments/assets/0c5ac74a-07b6-474a-9ebe-85ed368ec5ff)


Luego he creado un script en Python para unir todos los excels en un solo excel separados en pestañas.

El formato de la tabla de origen contiene una columna con las tipologías penales, otra columna con los valores de un periodo, otra columna con los valores del anterior periodo al primero y la última columna con la variación entre los 2 periodos anteriores.

He hecho las siguientes transformación en cada una de las tablas:
- Transformar el texto fecha a un campo fecha con varios atributos: pasar de "enero-septiembre 2022" a un campo con fecha inicio y fin del periodo, año, trimestre y año+trimestre
- Unpivot de estas cabeceras usando Power Query
- Concatenación de todas la tablas
- Normalización de los conceptos de tipología penal. Por ejemplo: "8. Hurtos" a "08. Hurtos" o "8. HURTOS" a "08. Hurtos"

He añadido la métrica del valor absoluto por trimestre. Los valores son siempre acumulados por lo que no se puede ver la evolución por trimestre.
También he añadido una nuevo columna para simplificar las tipologías penales con la ayuda de Chat GPT.

Idealmente el ministerior debería ofrecer la opción descargar los datos crudos para poder analizarlos sin tanto procesamiento. A lo mejor existe una API para descargarlos de forma cruda pero no la he encontrado.

Añado nuevas tablas con errores de cálculo corregido y otros formatos.

## Actualización septiembre 2025
Estoy rehaciendo el proceso de los datos. Estos son los principales pasos:
- En primer lugar descargo los datos completos sin tratar (/data/descargas_portal_ministerio) desde 2016
    - He creado un script que puede automatizar esta descarga en *descargar_ficheros_ministerio.py*
- Luego uno estos datos, quedándome en caso de duplicados, con el último dato en *load_csv_portal_ministerio.py*
    - El resultado es /data/delitos_raw_merged.csv
- El dato se reporta acumulado anual y lo quiero desagregar por trimestre en */notebooks/desagg_ytd.py*. Fichero resultado: */data/esp_desagg_ytd.csv*
- En */notebooks/normalizar_tipologias.py* estoy intentando normalizar tipologías para poder comparar durante todo el periodo. Fichero resultado: */data/esp_desagg_ytd_normalizado.csv*
    - Ejemplo de las distintas tipologías de **Homicidios**
        - "2.-HOMICIDIOS DOLOSOS Y ASESINATOS CONSUMADOS (EU)": "Homicidios dolosos y asesinatos consumados",
        - "1.-Homicidios dolosos y asesinatos consumados": "Homicidios dolosos y asesinatos consumados",
        - "1. Homicidios dolosos y asesinatos consumados": "Homicidios dolosos y asesinatos consumados",
    - Estas 3 tipologías de homicidios las unifico en "Homicidios dolosos y asesinatos consumados". Y así con todas las tipologías

- Para poder comparar entre distintias ciudades o regiones quiero usar una tasa por 1000 habitantes de los distintos delitos (Tasa de criminalidad = total de infracciones penales conocidas *(1.000) / total de la población). Para ello necesito datos de población.
    - Descargo datos del padrón municipal agregado por provincia en el INE 
        - Ejemplo de [fichero descargado](https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/2854.csv?nocab=1)
        - Los ficheros están en */data/pobmun*
        - Uno los ficheros en */data/pobmun24.csv*
        - Limpio el fichero en */notebooks/pob_naciona24.py* y el resultado es el fichero */data/pobmun24_limpio.csv*
    - Desde 2024, el campo geografía de los delitos incluye el código postal. Ejemplo:
        - 04003 Adra;I. CRIMINALIDAD CONVENCIONAL;enero-marzo 2024;225
        - Como en los datos del 24, están los datos actualizados del 23, hay que modificar los nombres del campo geografía antes del 23.
        - Borro todos los registros del año 23 cuyo campo de geografía no incluye el código postal
        - Normalizo los valores de geografía en */notebooks/normalizar_geo.py*
            - El resultado lo guardo en */data/esp_geo_normalized.csv*
    - Uno las tablas de población y delitos con los campos geografía y tipología normalizados:
        - En */notebooks/join_delitos_pob.py* y como resultados el */data/delitos_con_poblacion.csv*
    - Ahora calculo la Tasa de criminalidad en *notebooks/tasa_criminalidad.py* y el resultado está en *datos_criminalidad_webapp.csv*
- Creo una webapp con streamlit en *app_delitos.py*
- Ahora que puedo visualizar los datos y cambiar la población y la tipología pueda hacer comprobaciones de calidad del dato:
    - Hay un pico de delitos para todos los municipios en el cuarto trimestre de 2022(T422):
        - Se debe a que en los datos del cuarto trimestre de 2022, se incluyeron 3 periodos en lugar de 2 y esto no lo he tenido en cuenta en el tratamiento de datos.
            - Normalmente un registro es así:
                08015 Badalona;8. Hurtos;enero-junio 2024;1.899
                08015 Badalona;8. Hurtos;enero-junio 2025;2.093
                08015 Badalona;8. Hurtos;Variación % 2025/2024;10,2
            - Pero en T422:
                -Municipio de Badalona;8. Hurtos;Enero-diciembre 2019;3.684
                -Municipio de Badalona;8. Hurtos;Enero-diciembre 2021;3.347
                -Municipio de Badalona;8. Hurtos;Enero-diciembre 2022;3.825
                -Municipio de Badalona;8. Hurtos;Variación % 2022/2019;3,8
                -Municipio de Badalona;8. Hurtos;Variación % 2022/2021;14,3
        - Corrijo el error y ahora no se ven los picos de T422
        



        
