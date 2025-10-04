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
- Los datos para un mismo periodo pueden cambiar al año siguiente por lo que es necesario elegir el dato más actualizado.
- Solo el T4 2022 contiene 2 periodos anterioes (2021 y 2019) por lo que requiere un tratamiento especial.

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

## Mejoras desde el lanzamiento
- Añadir población para cada año. En la primera versión usaba la población de 2024 para todo el periodo pero no es correcto, si el dato de criminalidad de un municipio es de 2020, hay que calcular la ratio con la población de ese año. Como la población sale con el año vencido, en el año actual, 2025, usaré la última población de 2024.
- Reemplazar los CSVs por base de datos con SQLite
- Cambiar el orden de las tipologías colocando primero el TOTAL DELITOS y formateando los delitos dentro de Subtotales para que sea más legible
- Nuevo gráfico con volumen de delitos
- Añadir datos provinciales y autónomicos en *notebooks/eda_esp_desagg_ytd_normalizado.py*:
    - Quitar municipios de *data/esp_desagg_ytd_normalizado.csv*
    - Normalizar valores de geografía con el uso de una tabla maestra *data/maestro_geo_provincia_ccaa.csv*

## Próximas funcionalidades
- ~~Elegir entre datos absolutos y ratio por 1000 habitantes.~~
- ~~Añadir datos provinciales, autonómicos y nacionales para poder comparar el dato del municipio.~~
- Añadir otras dimensiones que puedan dar más contexto a los delitos: nacionalidad, renta per cápita...
- Añadir visualización mapa de calor
- Calcular la variación de criminalidad y poder variar los periodos con un slicer

## Refactorización
Rehago el código para optimizar el proceso de tratamiento de datos para que los próximos trimestres se cargue automáticamente.
El principal problema es el campo geografía y su cruce con la población.
La población la tenemos por municipio y los nombres de los municipios no coinciden en algunos casos. 

## Descripción de los datos
### Origen de los datos
Los datos han sido obtenidos del Sistema Estadístico de Criminalidad (SEC). Para su cómputo se
tienen en cuenta los hechos de los que han tenido conocimiento los siguientes cuerpos policiales:
Policía Nacional, Guardia Civil, Policías dependientes de las diferentes comunidades autonómicas
(Ertzaintza, Mossos d’Esquadra y Policía Foral de Navarra) y las Policías Locales que facilitan datos
al SEC. [Fuente Ministerio](https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/dam/jcr:b36b25ac-491b-49a6-be33-9cdcb168f0c9/01_Metodolog%C3%ADa_Balances_criminalidad.pdf)
### Definición de conceptos
Por hechos conocidos se entienden el conjunto de infracciones penales que han sido conocidas
por las distintas Fuerzas y Cuerpos de Seguridad, bien por medio de denuncia interpuesta o por
actuación policial realizada motu propio (labor preventiva o de investigación).
### TIPOLOGÍAS PENALES (infracciones penales)
I. CRIMINALIDAD CONVENCIONAL. Se obtiene excluyendo del cómputo del TOTAL
CRIMINALIDAD la CIBERCRIMINALIDAD.
1. Homicidios dolosos y asesinatos consumados: art. 138, 139, 140 CP. Homicidio doloso y
asesinato (grado consumado).
2. Homicidios dolosos y asesinatos en grado tentativa: art. 138, 139, 140 CP. Homicidio doloso
y asesinato (grado tentativa).
3. Delitos graves y menos graves de lesiones y riña tumultuaria: art. 147 a 152 y 154 CP.
Delitos graves y menos graves. Lesiones y riña tumultuaria.
4. Secuestro: art. 164 a 167 CP. Secuestros.
5. Delitos contra la libertad sexual: Título VIII del Libro II CP. Delitos contra la libertad sexual,
excluyendo los delitos asociados a la cibercriminalidad, que se computarían junto al resto de delitos
de esta modalidad en el apartado 13 (Otros ciberdelitos).
5.1. Agresión sexual con penetración: art. 179. Agresión sexual con penetración, excluyendo los
delitos asociados a la cibercriminalidad, que se computarían junto al resto de delitos de esta
modalidad en el apartado 13 (Otros ciberdelitos)
5.2. Resto de delitos contra la libertad sexual: Título VIII del Libro II CP excepto delitos al art.
179, excluyendo los delitos asociados a la cibercriminalidad, que se computarían junto al resto de
delitos de esta modalidad en el apartado 13 (Otros ciberdelitos)
6. Robos con violencia o intimidación: art. 242 CP. Robo con violencia o intimidación.
7. Robos con fuerza en domicilios, establecimientos y otras instalaciones: art. 238 a 241 CP.
Robo con fuerza en las cosas (lugar específico: viviendas, otras dependencias comunes/anexos de
viviendas, establecimientos, oficina de correos, domicilio jurídico/oficina, fábrica e instalación
militar).
7.1. Robos con fuerza en domicilios: art. 238 a 241 CP. Robo con fuerza en las cosas (lugar
específico: viviendas y otras dependencias comunes/anexos de viviendas).
8. Hurtos: art. 234 a 236 CP. Hurto y hurto en el interior de vehículo.
9. Sustracciones de vehículos: art. 244, 253 y 254 CP. Robo de vehículos, hurto de vehículos y
apropiación indebida de vehículos.
10. Tráfico de drogas: art. 368 a 371 CP. Tráfico de drogas.
11. Resto de criminalidad CONVENCIONAL: Resto de delitos no contemplados en el global de
los apartados 1, 2, 3, 4, 5, 6, 7, 8, 9 y 10, excepto los definidos en el Bloque II
(CIBERCRIMINALIDAD).
II. CIBERCRIMINALIDAD (infracciones penales cometidas en/por medio ciber): Tipología de
hechos según el módulo de cómputo de la cibercriminalidad que puede ser consultado en el
siguiente enlace:
https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/dam/jcr:d96d4063-98d8-
4647-8c76-d46a331a4ba3/03_Metodolog%C3%ADa_Cibercriminalidad.pdf
12. Estafas informáticas: Corresponde a las diferentes tipologías penales de ESTAFAS que
figuran en el módulo de cómputo de la cibercriminalidad bajo el epígrafe: “FRAUDE INFORMÁTICO”
(Ver enlace del Bloque II CIBERCRIMINALIDAD).
13. Otros ciberdelitos: Corresponde a las diferentes tipologías penales que figuran en el módulo
de cómputo de la cibercriminalidad bajo los epígrafes de “ACCESO E INTERCEPTACIÓN ILÍCITA,
INTERFERENCIA EN LOS DATOS Y EN EL SISTEMA, FALSIFICACIÓN INFORMÁTICA,
DELITOS SEXUALES, CONTRA LA PROPIEDAD INDUSTRIAL/INTELECTUAL, CONTRA EL
HONOR y AMENAZAS Y COACCIONES” (Ver enlace del Bloque II CIBERCRIMINALIDAD).
TOTAL DE INFRACCIÓNES PENALES: La suma de infracciones penales contempladas en la
CRIMINALIDAD CONVENCIONAL Y CIBERCRIMINALIDAD.
### Resumen datos por periodos
1. Estructura Inicial (2016)
Los ficheros correspondientes al año 2016 (20161 a 20164) presentan la estructura más reducida y estable, sirviendo como línea base:
- Geografías distintas: 221
- Tipologías penales distintas: 8
- Volumen de registros: 5.304 por trimestre

2. Primera Gran Expansión (2017)
A partir del primer trimestre de 2017 (20171), se produce el primer cambio estructural significativo:
- Aumento de Geografías: De 221 a 321-323.
- Aumento de Tipologías: De 8 a 14.
- Volumen de registros: El volumen se duplica, estabilizándose en torno a los 13.482 - 13.566 registros por fichero.

3. Segunda Expansión Geográfica (2021)
El año 2021 marca una nueva fase de crecimiento en el detalle geográfico:
- Aumento de Geografías: De 328 a 489.
- Volumen de registros: Se incrementa de forma notable, pasando de ~14.700 a 22.005 registros por trimestre, con las tipologías penales manteniéndose estables en 15.

4. Última Reestructuración y Mayor Volumen de Datos (2022 Q4 - 2023)
El periodo final incluye el cambio más complejo y un aumento drástico en el volumen de datos:
- Incremento de Tipologías (2022 Q4): En el cuarto trimestre de 2022 (20224), las Tipologías penales alcanzan su máximo histórico, pasando de 15 a 19.
- Pico de Registros (2022 Q4): El fichero 20224 presenta un pico anómalo de 46.265 registros.
- Nueva Base de Datos (2023 en adelante): A partir del primer trimestre de 2023, la estructura se consolida en una nueva base más alta:
    - Tipologías penales: 19
    - Geografías distintas: Estabilización en 490-497.
    - Volumen de registros: Nueva línea base cercana a los 28.000 registros por fichero (27.930 - 28.329).

