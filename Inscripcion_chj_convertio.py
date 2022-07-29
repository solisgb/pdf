# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 18:15:52 2022

@author: solis
"""
from collections import OrderedDict
import csv
import re
import sys
import traceback

import littleLogging as logging

NMAX_ERROR_READING_FILE = 15


class Inscripcion():
    """
    Lee el fichero txt generado por convertio
    """

    def __init__(self):
        self.d = OrderedDict([('tipo',''),
                              ('seccion',''), ('tomo',''), ('folio',''),
                              ('clave',''),
                              ('fechac',''), ('clase',''),
                              ('vol',''), ('superficie',''),
                              ('corriente_acu',''),
                              ('paraje',''), ('municipio',''),
                              ('provincia',''), ('ca', ''), ('titular','')])


    def property_set(self, name: str, value: str, ir: int):
        """
        Set the values in self.d with values readed from file generated
        with convertio

        Parameters
        ----------
        name : str
            key in file.
        value : str
            key value.

        Returns
        -------
        None.
        """

        # translates some names to the key name in self.d
        if name == 'tipo inscripción':
            name = 'tipo'
        elif name == 'comunidad autónoma':
            name = 'ca'
        elif name == 'sección':
            name = 'seccion'
        elif name == 'fecha concesión':
            name = 'fechac'
        elif name == 'clase y afeccion':
            name = 'clase'
        elif name == 'vol. max. anual (m3)':
            name = 'vol'
        elif name == 'superficie (ha)':
            name == 'superficie'
        elif re.search('^corriente', name) or re.search('acuifero', name):
            name = 'corriente_acu'

        if name not in self.d:
            logging.append(f'"Row {ir}: {name}" is not a valid key in Inscripcion')
            return

        self.d[name] = value


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


class Toma():

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
        t = Toma(clave, toma, x, y, huso)
        return ntoma_no_codificada, t


class File_convertio():

    def __init__(self, fi1: str, fo_inscripcion: str, fo_toma: str):
        """
        Lee un fichero de inscripciones convertido de pdf a txt
            usando convertio

        Parameters
        ----------
        fi1 : str
             path 2 data text file
        fo_inscripcion, fo_toma : str
             path 2 output csv files

        Returns
        -------
        None.

        """
        self.fi1 = fi1
        self.fo_inscripcion = fo_inscripcion
        self.fo_toma = fo_toma


    @staticmethod
    def __name_value_set(nw, iw, ws):
        if iw == 1:
            name = ws[iw-1].strip()
            value = ws[iw].split()[0].strip()
        elif iw == nw-1:
            name = ws[iw-1].split()[1].strip()
            value = ws[iw].strip()
        else:
            name = ws[iw-1].split()[1].strip()
            value = ws[iw].split()[0].strip()
        return name, value


    def change_format(self):
        """
        Reads self.fi1 and writes self.fo_inscripcion and self.fo_toma

        Returns
        -------
        None.

        """

        skip_text = ('confederación hidrográfica del júcar',)
        # en algunas líneas el carácter : aparece como separador key: value
        # y como carácter normal dentro de value, lo que requiere un
        # tratamiento singular
        # Cases:
        # Corriente - Acuifero: MASA DE AGUA SUBTERRÁNEA: 080.129 - MANCHA ORIENTAL
        # Clase y Afeccion: INDUSTRIAL: ALIMENTARIA
        singular_rows = ('corriente - acuifero', 'clase y afeccion')

        inscrip = Inscripcion()

        tomas = []
        ntoma_no_codificada = 0
        prefix_toma_no_codificada = 'tmp'

        nclave_no_codificada = 0
        prefix_clave_no_codificada = 'clv'

        lineas_no_tratadas = []
        nlineas_no_tratadas = 0

        with open(self.fi1, 'r', encoding='utf-8') as fi, \
            open(self.fo_inscripcion, 'w', newline='',
                 encoding='utf-8') as finscrip, \
            open(self.fo_toma, 'w', newline='', encoding='utf-8') as ftoma:

            inscrip_writer = csv.writer(finscrip, delimiter=',', quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
            tomas_writer = csv.writer(ftoma, delimiter=',', quotechar='"',
                                      quoting=csv.QUOTE_MINIMAL)

            inscrip_writer.writerow(inscrip.headers_get())

            t1 = Toma('', '', '', '', '')
            tomas_writer.writerow(t1.headers_get())

            for ir, row in enumerate(fi):
                if ir % 250 == 0:
                    print(ir)

                row = row.strip().lower()
                if len(row) == 0:
                    continue

                if 'página 1 ' in row:
                    continue

                for item in skip_text:
                    if item in row:
                        continue

                if 'página' in row:
                    inscrip_writer.writerow(inscrip.values_get())
                    inscrip = Inscripcion()
                    # igual tomas
                    pass

                if ':' not in row:
                    nlineas_no_tratadas += 1
                    if row not in lineas_no_tratadas:
                        lineas_no_tratadas.append(f'{row}')
                    continue

                if 'toma' in row:
                    # de momento
                    continue

                ws = row.split(':')
                nw = len(ws)

                if nw == 2 :
                    inscrip.property_set(ws[0].strip(), ws[1].strip(), ir)
                else:
                    act_type = 0
                    for iw in range(1, nw):
                        try:
                            for item in singular_rows:
                                if item in row:
                                    if row.count(':') > 1:
                                        act_type = 1
                                        break
                            if act_type == 1:
                                name = ws[0].strip()
                                value = ':'.join(ws[1:len(ws)]).strip()
                            else:
                                name, value = self.__name_value_set(nw, iw, ws)
                        except IndexError:
                            msg = traceback.format_exc()
                            logging.append(f'en línea {ir+1:d}\n{msg}')
                            return

                        if name == 'tomas':
                            continue

                        if name == 'clave' and value == '':
                            nclave_no_codificada += 1
                            value = f'{prefix_clave_no_codificada}' +\
                                f'{nclave_no_codificada:d}'

                        inscrip.property_set(name, value, ir)

            if nlineas_no_tratadas > 0:
                a = '\n'.join(lineas_no_tratadas)
                a = f'líneas no tratadas\n{a}'
                logging.append(a)
