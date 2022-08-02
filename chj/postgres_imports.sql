-- importacion de datos de inscripciones y tomas de la chj

create table ins.chj_ins(
	clave varchar primary key,
	seccion varchar,
	tomo varchar,
	folio varchar,
	ugh varchar,
	tipo varchar,
	fecha date,
	clase_afeccion varchar,
	vol_max_m3 real,
	superficie_ha real,
	corriente_acu varchar,
	paraje varchar,
	municipio varchar,
	provincia varchar,
	ca varchar,
	titular varchar
);

comment on table ins.chj_ins is 'Inscripciones en la CHJ descargadas de su página web';

create table ins.chj_toma(
	clave varchar,
	toma varchar,
	xutm real,
	yutm real,
	huso varchar,
	primary key (clave, toma)
);

comment on table ins.chj_toma is 'Tomas relacionadas con chj_ins mediante el campo clave';

comment on column ins.chj_toma.xutm is 'xutm original de la inscripción; en el campo geometría puede ser distinto';
comment on column ins.chj_toma.yutm is 'yutm original de la inscripción; en el campo geometría puede ser distinto';

select AddGeometryColumn ('ins','chj_toma','geom',25830,'POINT',2);
create index on ins.chj_toma using gist (geom);

-- insert data
/* hay claves duplicadas con volúmenes y superficies iguales
 * hago la importación a tablas temporales sin primary key
 */

-- 1 inscripciones
create table tmp.chj_ins as select * from ins.chj_ins;

copy tmp.chj_ins from 'H:\LSGB\data2db\chj_inscripciones\output_convertio\inscripciones_reutiliza_albacete.csv'
	with CSV header delimiter ',' encoding 'UTF-8'
;

select clave , tipo, count(*)
from tmp.chj_ins t
group by clave, tipo
having count(*) > 1
order by count(*) desc
;

select *
from tmp.chj_ins t
where clave = '91-RI-0002'
;

-- Compruebo clave, seccion, tomo, folio 
select *
from tmp.chj_ins t
where seccion is null or tomo is null or folio is null
;

-- La primary key debe estar formada por clave, seccion, tomo, folio

-- 2. toma
create table tmp.chj_toma as select * from ins.chj_toma;


