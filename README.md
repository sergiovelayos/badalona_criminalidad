# ⚖️ Comparador de Criminalidad en España
Compara fácilmente los datos de los **Balances Trimestrales de Criminalidad** del [Ministerio del Interior](https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/balances) entre:
* Municipios de más de 20.000 habitantes
* Provincias
* Comunidades Autónomas
* Nivel Nacional

El análisis cubre el periodo desde **2015 hasta junio de 2025**.

### **Mejoras Clave de los Datos**

Los datos originales del Ministerio son acumulativos, lo que dificulta el análisis de la evolución real cada trimestre. Para solucionar esto, he aplicado dos mejoras fundamentales:

1.  **Desagregación por Trimestre:** He procesado los datos para calcular las cifras correspondientes a **cada trimestre de forma individual**, permitiendo un análisis preciso de la estacionalidad y las tendencias a corto plazo.
2.  **Tasa por 1,000 Habitantes:** He cruzado los datos de delitos con el censo de cada ubicación y año. Esto permite calcular una tasa que hace posible **comparar de forma justa** territorios con poblaciones muy diferentes.

---

*Creado por [Sergio Velayos Fernández](https://www.linkedin.com/in/sergiovelayos/).*

## Funcionalidades
- Elige un municipio de más de 20.000 habitantes y un tipo de delito.
- Visualiza la evolución de la selección desde el 2015 (no disponible para todos los delitos).
- Un gráfico de líneas que muestra la tasa de criminalidad por 1.000 habitantes (total de infracciones penales conocidas *(1.000) / total de la población).
- Elige una segunda localización para poder comparar con el mismo ratio.
- En la esquina superior derecha del gráfico de líneas puedes cambiar al modo tabla para ver el detalle de los datos que se visualizan y puedes descargarlos.


## **Descripción de los Datos** 📊

### **Origen de los Datos**

Los datos del del Ministerio del Interior provienen del **Sistema Estadístico de Criminalidad (SEC)** . Puedes encontrar todos los [datos por trimestres y sin modificar en mi repositorio de Github](https://github.com/sergiovelayos/badalona_criminalidad/tree/main/data/descargas_portal_ministerio). Incluyen los delitos registrados por los siguientes cuerpos policiales:

* Policía Nacional
* Guardia Civil
* Policías Autonómicas (Ertzaintza, Mossos d’Esquadra y Policía Foral de Navarra)
* Policías Locales que reportan datos al sistema.

[**Fuente:** Metodología oficial del Ministerio](https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/dam/jcr:b36b25ac-491b-49a6-be33-9cdcb168f0c9/01_Metodolog%C3%ADa_Balances_criminalidad.pdf)

---

### **Definición de Conceptos Clave**

**"Hechos conocidos"** se refiere al total de infracciones penales que las fuerzas de seguridad han registrado, ya sea a través de una denuncia o por actuación policial directa (investigación o prevención).

---

## **Tipologías Penales** 📋

A continuación, se describen las categorías de delitos utilizadas en los informes de acuerdo al Ministerio del Interior (*incluyo aclaraciones personales en cursiva.*).

### **I. Criminalidad Convencional**

Esta categoría agrupa los delitos que no son considerados cibercrimen. Se obtiene restando la **Cibercriminalidad** del total de infracciones penales.(*"📁 Criminalidad Convencional" en la App. Reportado en todo el periodo*)

---

* **1. Homicidios dolosos y asesinatos consumados:** Incluye homicidios intencionados y asesinatos que se han completado.(*"Homicidios y Asesinatos Consumados" en la App. Reportado en todo el periodo*)

* **2. Homicidios dolosos y asesinatos en grado de tentativa:** Intentos de homicidio o asesinato que no llegaron a consumarse.(*"Homicidios y Asesinatos en Tentativa" en la App. Reportado desde 2016*)

* **3. Delitos graves de lesiones y riña tumultuaria:** Lesiones serias y peleas multitudinarias.(*"Lesiones y Riña Tumultuaria" en la App. Reportado desde 2016*)

* **4. Secuestro:** Privación de libertad de una persona.(*"Secuestros" en la App. Reportado desde 2016*)

* **5. Delitos contra la libertad sexual:** Incluye todas las agresiones y abusos sexuales que no se cometen por medios cibernéticos.(*"Delitos Sexuales (Total)" en la App. Reportado desde 2016*)
    * **5.1. Agresión sexual con penetración.**(*"Agresión sexual con penetración" en la App. . Reportado desde 2016*)
    * **5.2. Resto de delitos contra la libertad sexual:** Todas las demás formas de agresión o abuso sexual.(*"Otros Delitos Sexuales" en la App. Reportado desde 2016*)

* **6. Robos con violencia o intimidación:** Robos en los que se usa la fuerza o amenazas directas contra una persona.(*"Robos con Violencia e Intimidación" en la App. Reportado en todo el periodo*)

* **7. Robos con fuerza en domicilios, establecimientos y otras instalaciones:** Robos que implican forzar cerraduras, romper ventanas, etc., para acceder a un lugar (viviendas, locales, fábricas, etc.).(*"Robos con Fuerza" en la App. Reportado en todo el periodo*)

* **7.1. Robos con fuerza en domicilios:** Robos que implican forzar cerraduras, ventanas, etc., específicamente en viviendas y sus anexos.(*No lo incluyo en la App porque es muy similar a "Robos con Fuerza" con el ánimo de simplificar.*)
* **8. Hurtos:** Apropiación de bienes ajenos sin emplear fuerza contra las cosas ni violencia o intimidación contra las personas. Incluye hurtos en el interior de vehículos.(*"Hurtos" en la App. Reportado en todo el periodo*)
* **9. Sustracciones de vehículos:** Incluye tanto el robo como el hurto de vehículos, así como la apropiación indebida.(*"Sustracción de Vehículos" en la App. Reportado en todo el periodo*)
* **10. Tráfico de drogas:** Delitos relacionados con la elaboración, cultivo, tráfico o posesión ilícita de drogas.(*"Tráfico de Drogas" en la App. Reportado en todo el periodo*)
* **11. Resto de criminalidad convencional:** Agrupa el resto de delitos que no encajan en las categorías anteriores y no son considerados cibercrimen.(*"📋 Resto de Infracciones Penales" en la App. Reportado desde 2018.*)

---

### **II. Cibercriminalidad (Delitos Informáticos) 💻**

Infracciones penales cometidas a través de medios digitales. Para más detalle, se puede consultar la [metodología oficial de cibercriminalidad](https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/dam/jcr:d96d4063-98d8-4647-8c76-d46a331a4ba3/03_Metodolog%C3%ADa_Cibercriminalidad.pdf).(*"💻 Cibercriminalidad" en la App. Reportado desde 2022.*)

* **12. Estafas informáticas:** Fraudes cometidos a través de internet, englobados bajo el concepto de "Fraude Informático".(*"Estafas Informáticas" en la App. Reportado desde 2022.*)
* **13. Otros ciberdelitos:** Incluye una amplia gama de delitos como el hacking, la suplantación de identidad, delitos sexuales online, contra la propiedad intelectual, el honor, amenazas y coacciones.(*"Otros Ciberdelitos" en la App. Reportado desde 2022.*)

---

### **Total de Infracciones Penales**

Es la **suma** de todos los delitos, tanto de la **Criminalidad Convencional** como de la **Cibercriminalidad**. (*📊 TOTAL CRIMINALIDAD en la App. Reportado desde 2022.*)


## **Evolución de la Estructura de los Datos** 📈

A lo largo del tiempo, los ficheros de datos del Ministerio han sufrido varias transformaciones estructurales, aumentando progresivamente su detalle y volumen.

---

### **1. Línea Base (2016) 🏗️**

Los ficheros del año **2016** presentan la estructura más simple y estable, sirviendo como punto de partida:

* **Geografías:** 221
* **Tipologías penales:** 8
* **Volumen:** ~5.300 registros por trimestre.

---

### **2. Primera Gran Expansión (2017) 🚀**

A partir del primer trimestre de **2017**, se produce un cambio significativo que duplica el volumen de los datos:

* **Geografías:** Aumentan a más de **320**.
* **Tipologías penales:** Crecen de **8 a 14**.
* **Volumen:** Se estabiliza en torno a los **13.500** registros por fichero.

---

### **3. Ampliación Geográfica (2021) 🗺️**

En **2021**, el foco del crecimiento se centra en un mayor detalle geográfico:

* **Geografías:** Se expanden notablemente, pasando de 328 a **489**.
* **Volumen:** Aumenta hasta los **22.000** registros por trimestre, manteniendo estables las tipologías.

---

### **4. Reestructuración Final (2022 - 2023) 📊**

El último periodo introduce la estructura más compleja y el mayor volumen de datos hasta la fecha.

* **Punto de Inflexión (4T 2022):** El cuarto trimestre de **2022** marca un antes y un después:
    * **Tipologías penales:** Alcanzan su máximo histórico con **19** categorías.
    * **Pico de Registros:** Se detecta un pico anómalo de más de **46.000** registros, reflejando la transición.

* **Nueva Estructura Consolidada (desde 2023):** A partir de **2023**, la estructura se estabiliza en una nueva base mucho más detallada:
    * **Geografías:** Se consolidan en casi **500** ubicaciones distintas.
    * **Tipologías penales:** Se mantienen en **19**.
    * **Volumen:** La nueva línea base se sitúa en torno a los **28.000** registros por trimestre.


## Tratamiento de los datos
- La tipología 'I. CRIMINALIDAD CONVENCIONAL' que entra a partir del T4 2022, incluyendo los años completos del 2019, 2021 y 2022 pero solo tenemos evolución trimestral desde T1 2022. 
- La tipología '1.-DELITOS Y FALTAS (EU)' solo aparece en los ficheros de 2016. 

## **Tratamiento y Procesamiento de los Datos de Criminalidad**

Para asegurar la calidad y consistencia de los datos en nuestra aplicación, hemos realizado un proceso de transformación y enriquecimiento sobre las cifras brutas publicadas por el Ministerio del Interior. A continuación, se detallan los pasos clave de este proceso.

---

## **Limpieza y Estandarización Inicial 🧹**

El primer paso consiste en limpiar y dar un formato coherente a los datos originales.
* **Formato de Datos:** Convertimos los datos a los formatos correctos. Las cifras de delitos se transforman en **números enteros** y los periodos de texto (ej. "Enero-Junio 2023") se convierten a un **formato de fecha estándar** (ej. `2023-06-01`).
* **Unificación de Categorías:** Los informes originales utilizan nombres diferentes para el mismo delito o lugar a lo largo del tiempo. Hemos **unificado y estandarizado** tanto las tipologías penales como los nombres geográficos (municipios, provincias y CCAA) para que sean consistentes en toda la serie histórica. Por ejemplo, `8.-HURTOS` y `Hurtos` se agrupan bajo la misma categoría.

* **Eliminación de Duplicados e Inconsistencias:** Se eliminan registros duplicados, priorizando la información de los ficheros más recientes. También se excluyen datos geográficos ambiguos (como "En el extranjero") y se corrigen errores puntuales detectados en informes específicos para evitar inconsistencias.

---

## **Enriquecimiento con Datos de Población 👨‍👩‍👧‍👦**

Para poder contextualizar las cifras de criminalidad, cruzamos los datos de delitos con los **datos de población del INE** [Instituto Nacional de Estadística](https://www.ine.es/dynt3/inebase/index.htm?padre=525).
* Se asigna a cada municipio, provincia, comunidad autónoma y al total nacional su población correspondiente para el año en curso.
* Esto nos permite realizar comparaciones justas entre territorios con tamaños de población muy diferentes.

---

## **Cálculo de Cifras por Trimestre (Desagregación) 🗓️**

Un paso crucial de nuestro proceso es transformar los datos para su análisis trimestral.
* Los datos originales del Ministerio son **acumulativos**. Por ejemplo, el informe del segundo trimestre (junio) incluye los delitos cometidos desde enero hasta junio.
* Para obtener las cifras de **cada trimestre de forma individual**, aplicamos un cálculo que resta el valor acumulado del trimestre anterior al del actual.

> **Ejemplo:** Para obtener los delitos del 2º trimestre (abril-junio), tomamos el total de enero a junio y le restamos el total de enero a marzo.

---

## **Cálculo de la Tasa de Criminalidad 📊**

Finalmente, con los datos ya limpios y calculados por trimestre, obtenemos el indicador principal: la **tasa de criminalidad**.
* Esta tasa representa el **número de infracciones penales por cada 1.000 habitantes**.
* La fórmula utilizada es: `(Número de delitos del trimestre / Población) * 1.000`.

Este proceso garantiza que los datos presentados en la aplicación sean fiables, consistentes y permitan un análisis comparativo riguroso de la criminalidad en España.

## **Transformación Detallada de las Tipologías Penales**

Para garantizar la coherencia y fiabilidad del análisis, aplicamos un meticuloso proceso de estandarización y limpieza a las categorías de delitos. Este proceso se divide en dos fases principales: la **exclusión de datos problemáticos** y la **unificación de tipologías**.

---

### **1. Exclusión de Datos Problemáticos**

Antes de estandarizar, filtramos y eliminamos ciertos registros que podrían generar errores o duplicidades en los cálculos.

* **Eliminación de Filas de Variación:** Descartamos todas las filas que no representaban cifras de delitos, sino cálculos de **variación porcentual**. Estos datos no son relevantes para analizar los totales de criminalidad.

* **Exclusión de Totales y Subtotales Inconsistentes:** Quitamos ciertos totales precalculados en informes específicos que eran redundantes o presentaban inconsistencias.
    * Por ejemplo, en el informe del **cuarto trimestre de 2022**, eliminamos los grandes agregados de "Criminalidad Convencional" y "Cibercriminalidad" para evitar contar los delitos dos veces (una vez por el total y otra por sus componentes individuales).
    * De forma similar, se corrigieron inconsistencias en los totales de los informes anuales de **2019** y **2021** para asegurar la precisión del cómputo global.

---

### **2. Unificación y Estandarización de Categorías**

El principal desafío de los datos originales es que **un mismo delito aparece con nombres diferentes** a lo largo del tiempo, debido a cambios en la numeración, abreviaturas o descripciones. Para solucionarlo, agrupamos todas estas variantes bajo una única etiqueta estandarizada.

* **Agrupación por Delito:**
    * **Ejemplo (Homicidios):** Variantes como "1. Homicidios dolosos...", "1.-Homicidios dolosos..." y "2.-HOMICIDIOS DOLOSOS... (EU)" se consolidaron todas en la categoría final: **'Homicidios dolosos y asesinatos consumados'**.
    * **Ejemplo (Robos):** Múltiples descripciones como "6. Robos con violencia e intimidación" y "3.-ROBO CON VIOLENCIA E INTIMIDACIÓN (EU)" se unificaron en **'Robos con violencia e intimidación'**.

* **Creación de Subtotales Coherentes:** También se renombraron los grandes agregados para que su propósito fuera más claro.
    * **Ejemplo:** Términos como "TOTAL INFRACCIONES PENALES" o "I. CRIMINALIDAD CONVENCIONAL" se mapearon a nombres más descriptivos como **'Subtotal Criminalidad Convencional'** o **'Total Criminalidad'**, lo que permite organizar los datos en una jerarquía lógica y controlada.

Este doble proceso de **filtrado selectivo** y **estandarización exhaustiva** es fundamental para construir una serie de datos homogénea y fiable, eliminando el "ruido" y las inconsistencias de los ficheros originales.


## Mejoras desde el lanzamiento de la App
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
- Visualizar las Islas en el mapa

## Refactorización
Rehago el código para optimizar el proceso de tratamiento de datos para que los próximos trimestres se cargue automáticamente.
El principal problema es el campo geografía y su cruce con la población.
La población la tenemos por municipio y los nombres de los municipios no coinciden en algunos casos. 