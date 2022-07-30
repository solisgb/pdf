# -*- coding: utf-8 -*-
"""
Created on Sat Jun 25 11:09:09 2022

@author: solis
"""
from collections import OrderedDict
import csv
import traceback

import littleLogging as logging

NMAX_ERROR_READING_FILE = 15


class Registro_sub():

    def __init__(self):
        self.d = OrderedDict([('tipo',''), ('ca',''), ('prov',''), ('tm',''),
                              ('folio',''), ('seccion',''), ('tomo',''),
                              ('clave',''), ('fechac',''), ('clase',''),
                              ('vol',''), ('area',''), ('acuifero',''),
                              ('paraje',''), ('titular','')])


    def property_set(self, name: str, value):
        if name == 'tipo inscripción':
            self.d['tipo']=value
        elif name == 'comunidad autónoma':
            self.d['ca']=value
        elif name == 'provincia':
            self.d['prov']=value
        elif name == 'municipio':
            self.d['tm']=value
        elif name == 'folio':
            self.d['folio']=value
        elif name == 'sección':
            self.d['seccion']=value
        elif name == 'tomo':
            self.d['tomo']=value
        elif name == 'clave':
            self.d['clave']=value
        elif name == 'fecha concesión':
            self.d['fechac']=value
        elif name == 'clase yafeccion':
            self.d['clase']=value
        elif name == 'vol. max.anual(m3)':
            value = value.replace(',','.')
            self.d['vol'] = Registro_sub.__test_is_number(name, value)
        elif name == 'superficie':
            value = value.replace(',','.')
            self.d['area'] = Registro_sub.__test_is_number(name, value)
        elif name == '(ha)':
            value = value.replace(',','.')
            self.d['area'] = Registro_sub.__test_is_number(name, value)
        elif name == 'corriente -acuifero':
            self.d['acuifero']=value
        elif name == 'paraje':
            self.d['paraje']=value
        elif name == 'titular':
            self.d['titular']=value


    def headers_get(self):
        return list(self.d.keys())


    def values_get(self):
        return list(self.d.values())


    @staticmethod
    def __test_is_number(name: str, value: str):
        try:
            value = float(value)
        except:
            logging.append(f'{name} "{value}" no es un número', False)
            value = ''
        return value


class Toma_sub():

    def __init__(self, clave, toma, x, y, huso):
        self.d = OrderedDict([('clave', clave), ('toma', toma),
                              ('x', x), ('y', y), ('huso', huso)])


    def headers_get(self):
        return list(self.d.keys())


    def values_get(self):
        return list(self.d.values())


    @staticmethod
    def toma_from_name_tomas(ws, ntoma_no_codificada,
                             prefix_toma_no_codificada, clave):
        # 'Tomas: TOMA:860/2004 -1UTMX:626639UTMY:4341844HUSO:30 '
        # Tomas: TOMA: -UTMX: 626480 UTM Y: 4341250 HUSO: 30
        lst = ws[2].strip().split(' ')
        if len(lst) == 1:
            ntoma_no_codificada += 1
            toma = f'{prefix_toma_no_codificada}' +\
                f'{ntoma_no_codificada:d}'
        else:
            toma = ws[2].strip().split(' ')[0].strip()
        x = ws[3].strip().split('u')[0].strip()
        y = ws[4].strip().split('h')[0].strip()
        huso = ws[5].strip()
        t = Toma_sub(clave, toma, x, y, huso)
        return ntoma_no_codificada, t


def read_chj_file(fi1, fo_registro, fo_captacion):
    """
    Lee un fichero de registro de subterráneas pasado de pdf a txt
        usando adobe reader save as txt

    Parameters
    ----------
    fi1 : str
         path 2 data text file
    fo_registro, fo_captacion : str
         path 2 output csv files

    Returns
    -------
    None.

    """

    bad_formatted_lines = ('clase yafeccion', 'corriente -acuifero',
                           'paraje')

    str_bad_formatted_lines = ','.join(bad_formatted_lines)
    reg = Registro_sub()
    tomas = []
    ntoma_no_codificada = 0
    prefix_toma_no_codificada = 'tmp'
    clave = ''
    nclave_no_codificada = 0
    prefix_clave_no_codificada = 'clv'
    nerrs = 0
    lineas_no_tratadas = []
    with open(fi1, 'r', encoding='utf-8') as fi, \
        open(fo_registro, 'w', newline='', encoding='utf-8') as freg, \
        open(fo_captacion, 'w', newline='', encoding='utf-8') as fcap:
        reg_writer = csv.writer(freg, delimiter=',', quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)
        tomas_writer = csv.writer(fcap, delimiter=',', quotechar='"',
                                  quoting=csv.QUOTE_MINIMAL)
        reg_writer.writerow(reg.headers_get())
        t1 = Toma_sub('', '', '', '', '')
        tomas_writer.writerow(t1.headers_get())
        for il, line in enumerate(fi):
            if il % 250 == 0:
                print(il)
            line = line.strip().lower()
            # if 'ene' in line:
            #     kk=1
            if len(line) == 0:
                continue
            try:
                ws = line.split(':')
                nw = len(ws)
                if nw == 1:
                    if 'página' in ws[0]:
                        __grabar(reg_writer, reg, tomas_writer, tomas)
                        reg, tomas, clave = __init()
                    else:
                        if line not in lineas_no_tratadas:
                            lineas_no_tratadas.append(f'{line}')
                    continue
                elif nw == 2 :
                    reg.property_set(ws[0].strip(),
                                     ws[1].strip())
                elif nw > 2:
                    if ws[0].strip() == 'tomas':
                        # 'Tomas: TOMA:860/2004 -1UTMX:626639UTMY:4341844HUSO:30 '
                        # Tomas: TOMA: -UTMX: 626480 UTM Y: 4341250 HUSO: 30
                        lst = ws[2].strip().split(' ')
                        if len(lst) == 1:
                            ntoma_no_codificada += 1
                            toma = f'{prefix_toma_no_codificada}' +\
                                f'{ntoma_no_codificada:d}'
                        else:
                            toma = ws[2].strip().split(' ')[0].strip()
                        x = ws[3].strip().split('u')[0].strip()
                        y = ws[4].strip().split('h')[0].strip()
                        huso = ws[5].strip()
                        t = Toma_sub(clave, toma, x, y, huso)
                        tomas.append(t)
                    elif ws[0].strip() == 'toma':
                        # TOMA:6572/2005 -2UTMX:607913UTMY:4326753HUSO:30
                        # TOMA:1887/2000-1UTMX:622918UTMY:4340827HUSO:30
                        # TOMA:739/1994UTMX:594091UTMY:4313676HUSO:30
                        # TOMA:3246/2005 -1UTMX:592153UTMY:4315359HUSO:30
                        if ' ' in ws[1].strip():
                            sep = ' '
                        elif '-' in ws[1].strip():
                            sep = '-'
                        else:
                            sep = 'u'
                        toma = ws[1].strip().split(sep)[0].strip()

                        x = ws[2].strip().split('u')[0].strip()
                        y = ws[3].strip().split('h')[0].strip()
                        huso = ws[4].strip()
                        t = Toma_sub(clave, toma, x, y, huso)
                        tomas.append(t)
                    elif ws[0] in str_bad_formatted_lines and len(ws) > 2:
                        # ejemplos casos considerados
                        # corriente -acuifero: 8.29 -manchaoriental. masadeaguasubterránea:080.129:
                        # paraje: tndiseminados1543(a)bi:0suelo
                        # clase yafeccion: industrial:alimentaria
                        name, value = __value_with_extra_sep(ws)
                        reg.property_set(name, value)
                    elif ws[0].strip() == 'fecha concesión' and len(ws) == 3:
                        # Fecha Concesión: Ene 17200312:0
                        name = ws[0].strip()
                        value = __str2date(ws[1].strip())
                        reg.property_set(name, value)
                    elif ws[0].strip() == 'folio' and len(ws) == 3:
                        # folio: 71tomo: 25
                        name = ws[0].strip()
                        digits = [a for a in (ws[1].strip()) if a.isdigit()]
                        value = ''.join(digits)
                        reg.property_set(name, value)

                        nodigits = [a for a in (ws[1].strip()) if a != ' ' and not a.isdigit()]
                        name = ''.join(nodigits)
                        value = ws[2].strip()
                        reg.property_set(name, value)
                    elif ws[0].strip() == 'folio' and len(ws) == 4:
                        # folio: 9sección: c tomo: 28
                        name = ws[0].strip()
                        digits = [a for a in (ws[1].strip()) if a.isdigit()]
                        value = ''.join(digits)
                        reg.property_set(name, value)

                        nodigits = [a for a in (ws[1].strip()) if a != ' ' and not a.isdigit()]
                        name = ''.join(nodigits)
                        value = ws[2].strip().split(' ')[0]
                        reg.property_set(name, ws[2].strip())

                        name = ws[2].strip().split(' ')[1]
                        value = ws[3].strip()
                        reg.property_set(name, value)
                    else:
                        # líneas bien formadas
                        for i in range(1, nw):
                            if i == 1:
                                name = ws[i-1].strip()
                                value = ws[i].strip().split(' ')[0].strip()
                            elif i == nw-1:
                                name = ws[i-1].strip().split(' ')[1].strip()
                                value = ws[i].strip()
                            else:
                                name = ws[i-1].strip().split(' ')[1].strip()
                                value = ws[i].strip().split(' ')[0].strip()

                            if name == 'clave':
                                if value == '':
                                    nclave_no_codificada += 1
                                    value = f'{prefix_clave_no_codificada}' +\
                                        f'{nclave_no_codificada:d}'
                                # para corregir estradas del tipo
                                # 1987ip0630 ughab060
                                clave = value.split(' ')[0]

                            reg.property_set(name, value)

            except Exception:
                msg = traceback.format_exc()
                print(f'Error fichero line {il+1:d}\n{line}')
                logging.append(f'\nError fichero line {il+1:d}\n{line}\n{msg}',
                               False)

                nerrs += 1
                if nerrs == NMAX_ERROR_READING_FILE:
                    logging.append('Se ha alcanzado en núm máx errors' + \
                                   ' permitido al leer el fichero')
                    return

                __grabar(reg_writer, reg, tomas_writer, tomas)
                reg, tomas, clave = __init()
                continue

    print(il)
    logging.append('Contenidos en una Línea no tratados', False)
    logging.append('\n'.join(lineas_no_tratadas), False)
    print(f'Se han producido {nerrs} errores, grabados en app.log')


def __str2date(chunck: str):
    months = {'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 'may': '05', 'jun': '06',
             'jul': '07', 'ago': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'}
    day = chunck[3:5]
    month = months[chunck[0:3]]
    year = chunck[5:9]
    return f'{day}/{month}/{year}'


def __value_with_extra_sep(ws):
    name = ws[0].strip()
    value = ' '.join(ws[1:-1]).strip()
    return name, value


def __grabar(reg_writer, reg, tomas_writer, tomas):
    reg_writer.writerow(reg.values_get())
    for toma1 in tomas:
        if len(toma1.d['clave']) == 0 :
            toma1.d['clave'] = reg.d['clave']
        tomas_writer.writerow(toma1.values_get())


def __init():
    reg = Registro_sub()
    tomas = []
    clave = ''
    return reg, tomas, clave