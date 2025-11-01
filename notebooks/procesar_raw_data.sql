DROP TABLE IF EXISTS delitos_aux;

create table delitos_aux as 
with names as (
SELECT
	Geografía as geo,
	"Tipología penal" as tipo,
	"Periodos:" as periodo,
	Total as valor,
	fichero
FROM
	delitos ) ,
cte1 as (
select
	geo,
	tipo,
	DATE( CASE WHEN LOWER(periodo) LIKE '%diciembre%' THEN SUBSTR(periodo, -4) || '-12-01' WHEN LOWER(periodo) LIKE '%septiembre%' THEN SUBSTR(periodo, -4) || '-09-01' WHEN LOWER(periodo) LIKE '%junio%' THEN SUBSTR(periodo, -4) || '-06-01' WHEN LOWER(periodo) LIKE '%marzo%' THEN SUBSTR(periodo, -4) || '-03-01' END ) AS periodo,
	CAST(REPLACE(valor, '.', '') AS INTEGER) AS valor,
	fichero
from
	names
where
	periodo not like "Varia%"
	and NOT (
  (tipo IN ("I. CRIMINALIDAD CONVENCIONAL", "11. Resto de criminalidad convencional") AND fichero = 20224)
  OR 
  (tipo IN ("II. CIBERCRIMINALIDAD (infracciones penales cometidas en/por medio ciber)", "12.-Estafas informáticas", "13.-Otros ciberdelitos") AND fichero = 20224)
  OR 
  (tipo = "Resto de infracciones penales" AND fichero = 20184)
  OR
  (tipo =  'III. TOTAL INFRACCIONES PENALES' AND periodo in ('Enero-diciembre 2019','Enero-diciembre 2021'))
)
order by
	fichero ,
	periodo,
	geo,
	tipo ) ,
fix_tipo as (
select
	distinct case
		when geo in ('Municipo de Villanueva de la Cañada', '-Municipo de Villanueva de la Cañada') then 'Municipio de Villanueva de la Cañada'
		when geo = '- Municipio de Palma de Mallorca' then '- Municipio de Palma'
		when geo = '- Municipio de San Cristóbal de la Laguna' then '- Municipio de San Cristóbal de La Laguna'
		when geo = '- Municipio de Vila-Real' then '- Municipio de Vila-real'
		when geo = '-Municipio de Alboraya' then '-Municipio de Alboraia/Alboraya'
		when geo = '-Municipio de Almassora' then '-Municipio de Almazora/Almassora'
		when geo in ('-Municipio de Egüés', '-Municipio de Egüés/Eguesibar') then '31086 Valle de Egüés/Eguesibar'
		when geo = '-Municipio de O Porriño' then '-Municipio de Porriño, O'
		when geo = '-Municipio de València' then '46250 Valencia'
		else geo
	end as geo,
	case
		when tipo in ('1. Homicidios dolosos y asesinatos consumados', '1.-Homicidios dolosos y asesinatos consumados', '2.-HOMICIDIOS DOLOSOS Y ASESINATOS CONSUMADOS (EU)') then 'Homicidios dolosos y asesinatos consumados'
		when tipo in ('2. Homicidios dolosos y asesinatos en grado tentativa', '2.-Homicidios dolosos y asesinatos en grado tentativa') then 'Homicidios dolosos y asesinatos en grado tentativa'
		when tipo in ('3.-Delitos graves y menos graves de lesiones y riña tumultuaria', '3. Delitos graves y menos graves de lesiones y riña tumultuaria') then 'Delitos graves y menos graves de lesiones y riña tumultuaria'
		when tipo in ('4. Secuestro', '4.-Secuestro') then 'Secuestro'
		when tipo in ('5. Delitos contra la libertad sexual', '5.-Delitos contra la libertad e indemnidad sexual') then 'Delitos contra la libertad e indemnidad sexual'
		when tipo in ('5.1.-Agresión sexual con penetración') then 'Agresión sexual con penetración'
		when tipo in ('5.2.-Resto de delitos contra la libertad e indemnidad sexual', '5.2.-Resto de delitos contra la libertad sexual') then 'Resto de delitos contra la libertad sexual'
		when tipo in ('3.-ROBO CON VIOLENCIA E INTIMIDACIÓN (EU)', '6. Robos con violencia e intimidación', '6.-Robos con violencia e intimidación') then 'Robos con violencia e intimidación'
		when tipo in ('4.-ROBOS CON FUERZA EN DOMICILIOS (EU)', '7. Robos con fuerza en domicilios, establecimientos y otras instalaciones', '7.- Robos con fuerza en domicilios, establecimientos y otras instalaciones') then 'Robos con fuerza en domicilios, establecimientos y otras instalaciones'
		when tipo in ('1.-DELITOS Y FALTAS (EU)', 'TOTAL INFRACCIONES PENALES', 'I. CRIMINALIDAD CONVENCIONAL') then 'Subtotal Criminalidad Convencional'
		when tipo in ('III. TOTAL INFRACCIONES PENALES') then 'Total Criminalidad'
		when tipo in ('11. Resto de criminalidad convencional', 'Resto de infracciones penales') then 'Resto de infracciones penales'
		when tipo in ('10. Tráfico de drogas', '10.-Tráfico de drogas', '6.-TRÁFICO DE DROGAS (EU)') then 'Tráfico de drogas'
		when tipo in ('8. Hurtos', '8.-HURTOS', '8.-Hurtos') then 'Hurtos'
		when tipo in ('7.-DAÑOS') then 'Daños'
		when tipo in ('II. CIBERCRIMINALIDAD (infracciones penales cometidas en/por medio ciber)') then 'Subtotal Cibercriminalidad'
		when tipo in ('9. Sustracciones de vehículos', '9.-Sustracciones de vehículos', '5.-SUSTRACCIÓN VEHÍCULOS A MOTOR (EU)') then 'Sustracciones de vehículos'
		when tipo in ('12.-Estafas informáticas') then 'Estafas informáticas'
		when tipo in ('13.-Otros ciberdelitos') then 'Otros ciberdelitos'
	end as tipo,
	periodo,
	valor,
	fichero
FROM
	cte1
where
	tipo <> '7.1.-Robos con fuerza en domicilios'
	and geo NOT IN ('- Municipio de Santa Eulalia del Río', '-Municipio de Calatayud', '-Municipio de Barañain') ) 
	-----  GEO  ------
,	geo_cp as (
select
	distinct geo AS geo_cp,
	SUBSTR(geo, 1, INSTR(geo, ' ') - 1) AS codigo,
	SUBSTR(geo, INSTR(geo, ' ') + 1) AS nombre
FROM
	fix_tipo
WHERE
	geo GLOB '[0-9][0-9][0-9][0-9][0-9]*' ) ,
geo_no_cp AS (
SELECT
	DISTINCT REPLACE(LTRIM(LTRIM(geo, '-'), ' '), 'Municipio de ', '') AS nombre,
	geo as geo_no_cp
FROM
	fix_tipo
WHERE
	geo like '%Municipio%'
order by
	1 ) ,
master_geo as (
SELEcT
	distinct geo_cp,
	codigo as cp,
	s.nombre as nombre_cp,
	n.nombre as nombre_no_cp,
	geo_no_cp
FROM
	geo_cp s
left JOIN geo_no_cp n ON
	trim(n.nombre) = trim(s.nombre) ) ,
merge_geo as (
select
	distinct periodo,
	coalesce(geo_cp, geo) as geo ,
	tipo,
	valor,
	fichero
from
	fix_tipo a
left join master_geo b on
	a.geo = b.geo_cp
	or a.geo = b.geo_no_cp ) ,
fix_geo as (
select
	periodo,
	tipo,
	valor,
	case
		when geo = 'MADRID (COMUNIDAD DE)' then 'CCAA 13 Madrid'
		when geo in ('MURCIA (REGION DE)', 'MURCIA (REGIÓN DE)') then 'CCAA 14 Murcia'
		when geo = 'NAVARRA (COMUNIDAD FORAL DE)' then 'CCAA 15 Navarra'
		when geo = 'PAÍS VASCO' then 'CCAA 16 País Vasco'
		when geo = 'RIOJA (LA)' then 'CCAA 17 La Rioja'
		when geo = 'ANDALUCÍA' then 'CCAA 01 Andalucía'
		when geo = 'ARAGÓN' then 'CCAA 02 Aragón'
		when geo = 'ASTURIAS (PRINCIPADO DE)' then 'CCAA 03 Asturias'
		when geo = 'BALEARS (ILLES)' then 'CCAA 04 Baleares'
		when geo = 'CANARIAS' then 'CCAA 05 Canarias'
		when geo = 'CANTABRIA' then 'CCAA 06 Cantabria'
		when geo = 'CASTILLA - LA MANCHA' then 'CCAA 08 Castilla la Mancha'
		when geo in ('CASTILLA Y LEON', 'CASTILLA Y LEÓN') then 'CCAA 07 Castilla y León'
		when geo = 'CATALUÑA' then 'CCAA 09 Cataluña'
		when geo = 'CIUDAD AUTÓNOMA DE CEUTA' then 'CCAA 18 Ceuta'
		when geo = 'CIUDAD AUTÓNOMA DE MELILLA' then 'CCAA 19 Melilla'
		when geo = 'COMUNITAT VALENCIANA' then 'CCAA 10 Valencia'
		when geo = 'GALICIA' then 'CCAA 12 Galicia'
		when geo = 'EXTREMADURA' then 'CCAA 11 Extremadura'
		WHEN geo = 'Provincia de ALBACETE' THEN 'Provincia 02 Albacete'
		WHEN geo = 'Provincia de ALICANTE/ALACANT' THEN 'Provincia 03 Alicante'
		WHEN geo = 'Provincia de ALMERÍA' THEN 'Provincia 04 Almería'
		WHEN geo = 'Provincia de ARABA/ÁLAVA' THEN 'Provincia 01 Álava'
		WHEN geo = 'Provincia de ÁVILA' THEN 'Provincia 05 Ávila'
		WHEN geo = 'Provincia de BADAJOZ' THEN 'Provincia 06 Badajoz'
		WHEN geo = 'Provincia de BARCELONA' THEN 'Provincia 08 Barcelona'
		WHEN geo = 'Provincia de BIZKAIA' THEN 'Provincia 48 Vizcaya'
		WHEN geo = 'Provincia de BURGOS' THEN 'Provincia 09 Burgos'
		WHEN geo = 'Provincia de CÁCERES' THEN 'Provincia 10 Cáceres'
		WHEN geo = 'Provincia de CÁDIZ' THEN 'Provincia 11 Cádiz'
		WHEN geo = 'Provincia de CASTELLÓN/CASTELLÓ' THEN 'Provincia 12 Castellón'
		WHEN geo = 'Provincia de CIUDAD REAL' THEN 'Provincia 13 Ciudad Real'
		WHEN geo = 'Provincia de CÓRDOBA' THEN 'Provincia 14 Córdoba'
		WHEN geo = 'Provincia de CORUÑA (A)' THEN 'Provincia 15 A Coruña'
		WHEN geo = 'Provincia de CUENCA' THEN 'Provincia 16 Cuenca'
		WHEN geo = 'Provincia de GIPUZKOA' THEN 'Provincia 20 Guipuzcoa'
		WHEN geo = 'Provincia de GIRONA' THEN 'Provincia 17 Girona'
		WHEN geo = 'Provincia de GRANADA' THEN 'Provincia 18 Granada'
		WHEN geo = 'Provincia de GUADALAJARA' THEN 'Provincia 19 Guadalajara'
		WHEN geo = 'Provincia de HUELVA' THEN 'Provincia 21 Huelva'
		WHEN geo = 'Provincia de HUESCA' THEN 'Provincia 22 Huesca'
		WHEN geo = 'Provincia de JAÉN' THEN 'Provincia 23 Jaén'
		WHEN geo = 'Provincia de LEÓN' THEN 'Provincia 24 León'
		WHEN geo = 'Provincia de LLEIDA' THEN 'Provincia 25 Lleida'
		WHEN geo = 'Provincia de LUGO' THEN 'Provincia 27 Lugo'
		WHEN geo = 'Provincia de MÁLAGA' THEN 'Provincia 29 Málaga'
		WHEN geo = 'Provincia de OURENSE' THEN 'Provincia 32 Ourense'
		WHEN geo = 'Provincia de PALENCIA' THEN 'Provincia 34 Palencia'
		WHEN geo = 'Provincia de PALMAS (LAS)' THEN 'Provincia 35 Las Palmas'
		WHEN geo = 'Provincia de PONTEVEDRA' THEN 'Provincia 36 Pontevedra'
		WHEN geo = 'Provincia de SALAMANCA' THEN 'Provincia 37 Salamanca'
		WHEN geo = 'Provincia de SANTA CRUZ DE TENERIFE' THEN 'Provincia 38 Santa Cruz de Tenerife'
		WHEN geo = 'Provincia de SEGOVIA' THEN 'Provincia 40 Segovia'
		WHEN geo = 'Provincia de SEVILLA' THEN 'Provincia 41 Sevilla'
		WHEN geo = 'Provincia de SORIA' THEN 'Provincia 42 Soria'
		WHEN geo = 'Provincia de TARRAGONA' THEN 'Provincia 43 Tarragona'
		WHEN geo = 'Provincia de TERUEL' THEN 'Provincia 44 Teruel'
		WHEN geo = 'Provincia de TOLEDO' THEN 'Provincia 45 Toledo'
		WHEN geo = 'Provincia de VALENCIA/VALÈNCIA' THEN 'Provincia 46 Valencia'
		WHEN geo = 'Provincia de VALLADOLID' THEN 'Provincia 47 Valladolid'
		WHEN geo = 'Provincia de ZAMORA' THEN 'Provincia 49 Zamora'
		WHEN geo = 'Provincia de ZARAGOZA' THEN 'Provincia 50 Zaragoza'
		else geo
	end as geo,
	fichero
from
	merge_geo
where
	geo not like '%Isla de%'
	and geo not in ('EN EL EXTRANJERO', 'EXTRANJERA', 'FUERA DE ESPAÑA')
		and geo <> 'Isla de Eivissa' ) 	
	,rank as ( --------- CHECK   --------
select
	geo,
	tipo,
	periodo,
	valor,
	fichero,
	ROW_NUMBER() OVER (PARTITION BY geo,
	tipo,
	periodo
ORDER BY
	fichero DESC) AS rn
from
	fix_geo ) ,
	rank_fix as (
select
	distinct 
	geo,
	periodo,
	tipo,
	valor
from
	rank
where
	rn = 1
order by
	periodo,
	geo,
	tipo ) 
------------------ 	POBLACIÓN	--------------->>	
,pob_mun AS (
SELECT
	a.periodo,
	a.geo,
	a.tipo,
	a.valor,
	b.POB AS pob
FROM
	rank_fix a
INNER JOIN pob_municipios b ON
	b.cod_mun = SUBSTR(a.geo, 1, 5)
		AND b."AÑO" = CASE
			WHEN STRFTIME('%Y', a.periodo) = '2025' THEN 2024
			ELSE STRFTIME('%Y', a.periodo)
		END
	WHERE
		geo NOT LIKE 'Provincia%'
		AND geo NOT LIKE 'CCAA%'
		AND geo <> 'NACIONAL' ) ,
pob_pro AS (
SELECT
	a.periodo,
	a.geo,
	a.tipo,
	a.valor,
	b.POB as pob
FROM
	rank_fix a
INNER JOIN pob_provincias b ON
	b.CPRO = SUBSTR(a.geo, 11, 2)
		AND b."AÑO" = CASE
			WHEN STRFTIME('%Y', a.periodo) = '2025' THEN 2024
			ELSE STRFTIME('%Y', a.periodo)
		END
	WHERE
		geo LIKE 'Provincia%' ) ,
pob_ccaas as (
SELECT
	a.periodo,
	a.geo,
	a.tipo,
	a.valor,
	b.POB as pob
FROM
	rank_fix a
INNER JOIN pob_ccaa b ON
	b.CODCCAA = SUBSTR(a.geo, 6, 2)
		AND b."AÑO" = CASE
			WHEN STRFTIME('%Y', a.periodo) = '2025' THEN 2024
			ELSE STRFTIME('%Y', a.periodo)
		END
	WHERE
		a.geo LIKE 'CCAA%' ) ,
pob_nacional_calc as (
select
	"AÑO",
	SUM(POB) as pob
from
	pob_ccaa
group by
	"AÑO" ) ,
pob_nacional as (
SELECT
	a.periodo,
	a.geo,
	a.tipo,
	a.valor,
	b.POB as pob
FROM
	rank_fix a
INNER JOIN pob_nacional_calc b ON
	b."AÑO" = CASE
		WHEN STRFTIME('%Y', a.periodo) = '2025' THEN 2024
		ELSE STRFTIME('%Y', a.periodo)
	END
WHERE
	a.geo = 'NACIONAL' ) ,
merge_pobs as (
select
	periodo,
	geo,
	tipo,
	valor,
	POB
from
	pob_nacional
UNION ALL
select
	periodo,
	geo,
	tipo,
	valor,
	pob
from
	pob_ccaas
union all
select
	periodo,
	geo,
	tipo,
	valor,
	pob
from
	pob_pro
union all
select
	periodo,
	geo,
	tipo,
	valor,
	pob
from
	pob_mun 
	) 
, desagg_calc AS (
    SELECT 
        periodo,
        geo,
        tipo,
        valor AS valor_acumulado,
        pob,
        LAG(valor) OVER (
            PARTITION BY geo, tipo, strftime('%Y', periodo) 
            ORDER BY periodo
        ) AS valor_anterior
    FROM merge_pobs
)
SELECT 
    periodo,
    geo,
    tipo,
    valor_acumulado,
    CASE 
        WHEN strftime('%m', periodo) = '03' THEN valor_acumulado
        ELSE valor_acumulado - COALESCE(valor_anterior, 0)
    END AS valor,
    pob,
    CASE 
        WHEN strftime('%m', periodo) = '03' THEN (valor_acumulado * 1000.0 / pob)
        ELSE ((valor_acumulado - COALESCE(valor_anterior, 0)) * 1000.0 / pob)
    END AS tasa
FROM desagg_calc
ORDER BY geo, tipo, periodo;