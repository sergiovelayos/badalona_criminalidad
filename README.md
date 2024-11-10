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


