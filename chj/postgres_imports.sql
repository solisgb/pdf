-- importacion de datos de inscripciones y tomas de la chj
drop table ins.chj_ins;
drop table ins.chj_toma;
-- ====================insert data==============================
/* Los datos son insettados en 2 tablas temporales donde se analiza
las columnas que pueden actuar como primary key  
chj_insert: la columna clave no es la primary key
chj_toma: las columnas clave, toma no son la pk  
hago la importación a tablas temporales sin pk
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
-- drop table tmp.chj_toma;

create table tmp.chj_toma(
	toma_ins varchar,
	seccion varchar,
	tomo varchar,
	folio varchar,
	toma varchar,
	xutm real,
	yutm real,
	huso varchar
);


copy tmp.chj_toma 
	from 'H:\LSGB\data2db\chj_inscripciones\output_convertio\toma_manantial_albacete_convertio.csv'
	with CSV header delimiter ',' encoding 'UTF-8'
;

-- Compruebo seccion, toma, folio, toma para pk 
select toma_ins, seccion, tomo, folio , count(*)
from tmp.chj_toma t
group by toma_ins, seccion, tomo, folio 
having count(*) > 1
order by seccion, tomo, folio
;

select *
from tmp.chj_ins t
where seccion = 'A' and tomo = '60' and folio = '77'
;
select *
from tmp.chj_toma t
where seccion = 'A' and tomo = '60' and folio = '77'
;
/*
La misma inscripción tiene 2 tomas con el mismo código en diferente lugar 
lo interpreto como 2 tomas distintas y a una de ellas le voy a añadir 1 b
 */

-- ===============INSERTAR DATOS EN LAS TABLAS DEFINITIVAS=============================

drop table ins.chj_ins;
drop table ins.chj_toma;

create table ins.chj_ins(
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
	titular varchar,
	primary key (seccion, tomo, folio)
);

comment on table ins.chj_ins is 'Inscripciones en la CHJ descargadas de su página web';

create table ins.chj_toma(
	ntoma_ins varchar,
	seccion varchar not null,
	tomo varchar not null,
	folio varchar not null,
	toma varchar not null,
	xutm real not null,
	yutm real not null,
	huso varchar not null,
	primary key (ntoma_ins, seccion, tomo, folio)
);

comment on table ins.chj_toma is 'Tomas relacionadas con chj_ins mediante las columnas seccion, tomo, folio';

comment on column ins.chj_toma.ntoma_ins is 'número de toma en la inscripcion -no vale toma-';
comment on column ins.chj_toma.xutm is 'xutm original de la inscripción; en el campo geometría puede ser distinto';
comment on column ins.chj_toma.yutm is 'yutm original de la inscripción; en el campo geometría puede ser distinto';

select AddGeometryColumn ('ins','chj_toma','geom',25830,'POINT',2);
create index on ins.chj_toma using gist (geom);

comment on column ins.chj_toma.geom is 'Los cambios de posición se hacen en geom y se mantienen xutm, yutm con sus valores originales';

update ins.chj_toma set geom = st_setsrid(st_makepoint(xutm, yutm), 25830);

copy ins.chj_ins
	from 'H:\LSGB\data2db\chj_inscripciones\output_convertio\ins_manantial_albacete_convertio.csv'
	with CSV header delimiter ',' encoding 'UTF-8'
;

copy ins.chj_toma(ntoma_ins,seccion,tomo,folio,toma,xutm,yutm,huso)
	from 'H:\LSGB\data2db\chj_inscripciones\output_convertio\toma_superficial_albacete_convertio.csv'
	with CSV header delimiter ',' encoding 'UTF-8'
;

select  t.provincia , count(*)
from ins.chj_ins  t
group by t.provincia
;

select concat(t1.seccion , t1.tomo , t1.folio , t2.ntoma_ins) toma , t1.tipo , t1.vol_max_m3 , t1.superficie_ha ,
	t1.titular, t1.municipio , t1.provincia , t2.geom 
from ins.chj_ins t1
	join ins.chj_toma t2 using (seccion , tomo , folio)
order by seccion, tomo, folio
;


