# Datos de criminalidad por tipología penal en Badalona
Los medios de comunicación, políticos e instituciones hacen un uso poco riguroso de los datos españoles de criminalidad. No se contextualiza o no se compara con la misma base y casi nunca se enlaza a la fuente para poder comprobar la veracidad de los datos. Por todos estos motivos he creado [delitos-app](https://delitos.streamlit.app/) basado en los datos del [Ministerio del Interior](https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/balances.html) que he tratado para que sean comparables facilmente.

## Funcionalidades
- Elige un municipio de más de 20.000 habitantes y un tipo de delito.
- Visualiza la evolución de la selección desde el 2015 (no disponible para todos los delitos).
- Un gráfico de líneas que muestra la tasa de criminalidad por 1000 habitantes (total de infracciones penales conocidas *(1.000) / total de la población).
- Elige una segunda ciudad para poder comparar con el mismo ratio.
- Debajo del gráfico de líneas puedes ver el detalle de los datos que se visualizan y puedes descargarlos.

## Sobre los datos del criminalidad
Estos datos se publican con periodicidad trimestral en un formato poco amigable para realizar cualquier análisis. Estas son algunas de las advertencias que tendría en cuenta a la hora de analizar estos datos:
- El origen de datos se inicia en el primer trimestre de 2016.
- Las tipologías de delitos cambian por lo que no podemos comparar un mismo concepto durante todo el periodo.
- Los datos para un mismo periodo pueden cambiar al año siguiente por lo que es necesario elegir el dato más actualizado

## ¿Cómo obtener los datos desde el portal del ministerio?

He descargado cada trimestre por municipio desde 2016 [aquí](https://github.com/sergiovelayos/badalona_criminalidad/tree/main/data/descargas_portal_ministerio).

Cada fichero contiene el periodo anterior y la variación.

El dato se reporta trimestre acumulado anual, lo desagrego por ver la evolución trimestre a trimestre.

## Explicación de la creación de la App

En primer lugar descargo los datos completos sin tratar (/data/descargas_portal_ministerio) desde 2016
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

## Próximas funcionalidades
- Elegir entre datos absolutos y ratio por 1000 habitantes.
- Añadir datos provinciales, autonómicos y nacionales para poder comparar el dato del municipio.



        
