-- importacion de datos de inscripciones y tomas de la chj
drop table ins.chj_ins;
drop table ins.chj_toma;

-- primero creo las talas sin primary keys
create table ins.chj_ins(
	fid serial primary key,
	seccion varchar not null,
	tomo varchar not null,
	folio varchar not null,
	clave varchar,
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
	titular varchar,
	unique (seccion, tomo, folio)
);

comment on table ins.chj_ins is 'Inscripciones en la CHJ descargadas de su página web';

create table ins.chj_toma(
	gid serial primary key,
	seccion varchar not null,
	tomo varchar not null,
	folio varchar not null,
	toma varchar not null,
	xutm real not null,
	yutm real not null,
	huso varchar not null,
);

comment on table ins.chj_toma is 'Tomas relacionadas con chj_ins mediante el campo clave';

comment on column ins.chj_toma.xutm is 'xutm original de la inscripción; en el campo geometría puede ser distinto';
comment on column ins.chj_toma.yutm is 'yutm original de la inscripción; en el campo geometría puede ser distinto';

select AddGeometryColumn ('ins','chj_toma','geom',25830,'POINT',2);
create index on ins.chj_toma using gist (geom);

-- ====================insert data==============================
/* chj_insert: la columna clave no es la primary key
 * chj_toma: las columnas clave, toma no son la pk  
 * hago la importación a tablas temporales sin pk
 */

-- 1 ================inscripciones===============================
create table tmp.chj_ins(
	seccion varchar,
	tomo varchar,
	folio varchar,
	clave varchar,
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

copy tmp.chj_ins 
	from 'H:\LSGB\data2db\chj_inscripciones\output_convertio\ins_superficial_albacete_convertio.csv'
	with CSV header delimiter ',' encoding 'UTF-8'
;

-- exploro columnas para primary key: seccion , tomo, folio
select seccion , tomo, folio, count(*)
from tmp.chj_ins t
group by seccion , tomo, folio
having count(*) > 1
order by count(*) desc
;

-- Compruebo seccion, tomo, folio no tiene valores nulos 
select *
from tmp.chj_ins t
where seccion is null or tomo is null or folio is null
;
-- concluyo: seccion, tomo, folio son una pk válida

-- clave
select clave, count(*)
from tmp.chj_ins t
group by clave
having count(*) > 1
order by count(*) desc
;
-- no es pk

select count(*)
from tmp.chj_ins t;

select t.tipo, count(*) 
from tmp.chj_ins t
group by t.tipo
;

select * 
from tmp.chj_ins t
where t.seccion = 'A' and tomo = '5573/2003 - 1|77'


-- 2. ===================toma=================================

create table tmp.chj_toma(
	seccion varchar,
	tomo varchar,
	folio varchar,
	toma varchar,
	xutm real,
	yutm real,
	huso varchar
);


copy tmp.chj_toma 
	from 'H:\LSGB\data2db\chj_inscripciones\output_convertio\toma_superficial_albacete_convertio.csv'
	with CSV header delimiter ',' encoding 'UTF-8'
;

-- Compruebo seccion, toma, folio, toma para pk 
select seccion, tomo, folio, toma , count(*)
from tmp.chj_toma t
group by seccion, tomo, folio, toma
having count(*) > 1
order by count(*) desc
;
/*
seccion|tomo|folio|toma         |count|
-------+----+-----+-------------+-----+
A      |60  |77   |5573/2003 - 1|    2|
 */

select *
from tmp.chj_ins t
where seccion = 'A' and tomo = '60' and folio = '77'
;
/*
La misma inscripción tiene 2 tomas con el mismo código en diferente lugar 
lo interpreto como 2 tomas distintas y a una de ellas le voy a añadir 1 b
 */

select toma , count(*)
from tmp.chj_toma t
group by toma
having count(*) > 1
order by count(*) desc
;




-- Compruebo toma para pk 
select toma , count(*)
from tmp.chj_toma t
group by toma
having count(*) > 1
order by count(*) desc
;
-- no es una pk válida



 
-- conclusion: tengo que ligar la pk de ins a la columna toma

