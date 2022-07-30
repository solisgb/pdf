# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 18:15:52 2022

@author: solis
"""
from collections import OrderedDict
import copy
import csv
import traceback

import littleLogging as logging

NMAX_ERROR_READING_FILE = 15

NULL_VALUE = ''

keys_inscripcion = [('clave',NULL_VALUE),
                    ('seccion',NULL_VALUE), ('tomo',NULL_VALUE),
                    ('folio',NULL_VALUE), ('tipo',NULL_VALUE),
                    ('fecha',NULL_VALUE), ('clase_afeccion',NULL_VALUE),
                    ('vol_max_m3',NULL_VALUE), ('superficie_ha',NULL_VALUE),
                    ('corriente_acu',NULL_VALUE),
                    ('paraje',NULL_VALUE), ('municipio',NULL_VALUE),
                    ('provincia',NULL_VALUE), ('ca', NULL_VALUE),
                    ('titular',NULL_VALUE)]

keys_toma = [('clave', NULL_VALUE), ('toma', NULL_VALUE),
             ('xutm', NULL_VALUE), ('yutm', NULL_VALUE), ('huso', NULL_VALUE)]

class IT():
    """
    Características de la inscripción y sus tomas facilitados por la CHJ
    mediante un fichero pdf en su página web
    """

    def __init__(self, keys: [()]):
        self.d = OrderedDict(keys)


    def property_set(self, name: str, value: str):
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
        Boolean
        """
        if name in self.keys():
            self.d[name] = value
            return True
        else:
            return False

    def keys_get(self):
        return list(self.d.keys())


    def values_get(self):
        return list(self.d.values())


    def is_key(self, name:str):
        if name in self.d:
            return True
        else:
            return False


    def all_values_are_set(self):
        for v1 in self.keys_get():
            if v1 == '':
                return False
        return True


class File_convertio():

    # keys en fichero de la CHJ
    keys = ('TIPO INSCRIPCIÓN:',
             'COMUNIDAD AUTÓNOMA:',
             'PROVINCIA:',
             'Municipio:',
             'Sección:',
             'Tomo:',
             'Folio:',
             'Clave:',
             'Fecha Concesión:',
             'Clase y Afeccion:',
             'Vol. Max. Anual (m3):',
             'Superficie (ha):',
             'Corriente - Acuifero:',
             'Paraje:',
             'Municipio:',
             'Provincia:',
             'Titular:',
             'TOMA:',
             'UTMX:',
             'UTM Y:',
             'HUSO:')

    def __init__(self, fi1: str, fo_inscripcion: str, fo_toma: str):
        """
        Lee un fichero de inscripciones convertido de pdf a txt
            usando convertio

        Parameters
        ----------
        fi1 : str
             path 2 data text file
        fo_inscripcion: str
            csv file with data incription (output)
        fo_toma : str
            csv file with data tomas in incription (output)

        Returns
        -------
        None.

        """
        self.fi1 = fi1
        self.fo_inscripcion = fo_inscripcion
        self.fo_toma = fo_toma


    @staticmethod
    def __translate_to_true_keys(name: str):
        # translates the names in the file to the key names
        if name == 'TIPO INSCRIPCIÓN:':
            name = 'tipo'
        elif name == 'COMUNIDAD AUTÓNOMA:':
            name = 'ca'
        elif name == 'PROVINCIA:':
            name = 'provincia'
        elif name == 'Municipio:':
            name = 'municipio'
        elif name == 'Sección:':
            name = 'seccion'
        elif name == 'Tomo:':
            name = 'tomo'
        elif name == 'Folio:':
            name = 'folio'
        elif name == 'Clave:':
            name = 'clave'
        elif name == 'Fecha Concesión:':
            name = 'fecha'
        elif name == 'Clase y Afeccion:':
            name = 'clase_afeccion'
        elif name == 'Vol. Max. Anual (m3):':
            name = 'vol_max_m3'
        elif name == 'Superficie (ha):':
            name = 'superficie_ha'
        elif name == 'Corriente - Acuifero:':
            name = 'corriente_acu'
        elif name == 'Paraje:':
            name = 'paraje'
        elif name == 'Municipio:':
            name = 'municipio'
        elif name == 'Provincia:':
            name = 'provincia'
        elif name == 'Titular:':
            name = 'titular'
        elif name == 'TOMA:':
            name = 'toma'
        elif name == 'UTMX:':
            name = 'xutm'
        elif name == 'UTM Y:':
            name = 'yutm'
        elif name == 'HUSO:':
            name = 'huso'
        else:
            name = None
        return name


    def change_format(self):
        """
        Reads self.fi1 and writes self.fo_inscripcion and self.fo_toma

        Returns
        -------
        None.

        """

        # Las líneas con este contenido no se consideran
        skip_text = 'CONFEDERACIÓN HIDROGRÁFICA DEL JÚCAR'

        nclave_no_codificada = 0
        prefix_clave_no_codificada = 'cnc_'

        ntoma_no_codificada = 0
        prefix_toma_no_codificada = 'tnc_'

        keys_values = []
        ninscrip = 0
        inscrip = IT(keys_inscripcion)
        toma = IT(keys_toma)
        tomas = []

        with open(self.fi1, 'r', encoding='utf-8') as fi, \
            open(self.fo_inscripcion, 'w', newline='',
                 encoding='utf-8') as finscrip, \
            open(self.fo_toma, 'w', newline='', encoding='utf-8') as ftoma:

            inscrip_w = csv.writer(finscrip, delimiter=',')
            toma_w = csv.writer(ftoma, delimiter=',')
            inscrip_w.writerow(inscrip.keys_get())
            toma_w.writerow(tomas.keys_get())

            for ir, row in enumerate(fi):
                if ir % 250 == 0:
                    print(ir)

                row = row.strip()
                if len(row) == 0:
                    continue

                if skip_text in row:
                    continue

                if 'página' in row:
                    if 'página 1 ' not in row:
                        # grabo los datos de la inscripcion y sus tomas
                        for k1, v1, r1 in keys_values:
                            k1 = self.__translate_to_true_keys(k1)
                            if k1 is None:
                                logging.append(f'row {r1}, "{k1}" is not a valid key')
                                continue
                            if k1 == 'clave' and v1 == '':
                                nclave_no_codificada += 1
                                value = f'{prefix_clave_no_codificada}' +\
                                    f'{nclave_no_codificada:d}'
                            elif k1 == 'toma' and v1 == '':
                                ntoma_no_codificada +=1
                                value = f'{prefix_toma_no_codificada}' +\
                                    f'{ntoma_no_codificada:d}'

                            if inscrip.is_key(k1):
                                inscrip.property_set(k1, v1)
                            elif toma.is_key(k1):
                                toma.property_set(k1, v1)
                                if k1 == toma.keys_get()[-1]:
                                    # asignar clave
                                    name = 'clave'
                                    value = inscrip.d[name]
                                    toma.property_set(name, value)
                                    tomas.append(copy.copy(toma))
                                    toma = IT(keys_toma)
                            else:
                                raise ValueError(f'clave "{k1}" no reconocida')

                        ninscrip += 1
                        inscrip_w.writerow(inscrip.values_get())
                        inscrip = IT(keys_inscripcion)
                        for toma1 in tomas:
                            toma_w.writerow(toma1.values_get())
                        toma = IT(keys_toma)
                        tomas = []
                        keys_values = []
                    continue

                present_keys = [key1 for key1 in self.keys if key1 in row]
                pos0 = [row.find(key1) for key1 in present_keys]
                pos1 = [row.find(key1)+len(key1) for key1 in present_keys]

                ilength = len(present_keys) - 1
                for i, (k1, p0, p1) in enumerate(zip(present_keys, pos0, pos1)):
                    if i < ilength:
                        pe = pos0[i+1]
                        keys_values.append(k1[0:], row[p1:pe].strip(), ir+1)
                    else:
                        keys_values.append(k1[0:], row[p1:].strip(), ir+1)


    # def change_format_deprecated(self):
    #     """
    #     Reads self.fi1 and writes self.fo_inscripcion and self.fo_toma

    #     Returns
    #     -------
    #     None.

    #     """

    #     # Las líneas con este contenido no se consideran
    #     skip_text = ('confederación hidrográfica del júcar',)

    #     # En algunas líneas el carácter : aparece como separador key:value
    #     # y como carácter normal dentro de value, lo que requiere un
    #     # tratamiento singular
    #     # Ejemplos:
    #     # Clase y Afeccion: INDUSTRIAL: ALIMENTARIA
    #     # Corriente - Acuifero: MASA DE AGUA SUBTERRÁNEA: 080.129 - MANCHA ORIENTAL
    #     # Fecha Concesión: Ene 23 1997 12:0
    #     # Titular: S. COOP. HERMANOS MARTINEZ LOPEZ, CIF: F02370310

    #     singular_rows = ('fecha concesión', 'titular', 'corriente - acuifero',
    #                      'clase y afeccion')

    #     inscrip = Inscripcion()
    #     inscrip_prev_key = None

    #     tomas = []
    #     ntoma_no_codificada = 0
    #     prefix_toma_no_codificada = 'tmp'

    #     nclave_no_codificada = 0
    #     prefix_clave_no_codificada = 'clv'

    #     lineas_no_tratadas = []
    #     nlineas_no_tratadas = 0

    #     with open(self.fi1, 'r', encoding='utf-8') as fi, \
    #         open(self.fo_inscripcion, 'w', newline='',
    #              encoding='utf-8') as finscrip, \
    #         open(self.fo_toma, 'w', newline='', encoding='utf-8') as ftoma:

    #         inscrip_writer = csv.writer(finscrip, delimiter=',', quotechar='"',
    #                                 quoting=csv.QUOTE_MINIMAL)
    #         tomas_writer = csv.writer(ftoma, delimiter=',', quotechar='"',
    #                                   quoting=csv.QUOTE_MINIMAL)

    #         inscrip_writer.writerow(inscrip.headers_get())

    #         t1 = Toma('', '', '', '', '')
    #         tomas_writer.writerow(t1.headers_get())

    #         for ir, row in enumerate(fi):
    #             if ir % 250 == 0:
    #                 print(ir)

    #             row = row.strip().lower()
    #             if len(row) == 0:
    #                 continue

    #             for item in skip_text:
    #                 if item in row:
    #                     continue

    #             if 'página' in row:
    #                 if 'página 1 ' not in row:
    #                     inscrip_writer.writerow(inscrip.values_get())
    #                     inscrip = Inscripcion()
    #                     inscrip_prev_key = None
    #                     # igual tomas
    #                 continue

    #             if ':' not in row:
    #                 if inscrip_prev_key is not None:
    #                     pass
    #                 nlineas_no_tratadas += 1
    #                 if row not in lineas_no_tratadas:
    #                     lineas_no_tratadas.append(f'{row}')
    #                 continue

    #             if 'toma' in row:
    #                 # de momento
    #                 continue

    #             ws = row.split(':')
    #             nw = len(ws)

    #             if nw == 2 :
    #                 inscrip.property_set(ws[0].strip(), ws[1].strip(), ir+1)
    #             else:
    #                 act_type = 0
    #                 for iw in range(1, nw):
    #                     try:
    #                         for item in singular_rows:
    #                             if item in row:
    #                                 if row.count(':') > 1:
    #                                     act_type = 1
    #                                     break
    #                         if act_type == 1:
    #                             name = ws[0].strip()
    #                             value = ':'.join(ws[1:len(ws)]).strip()
    #                         else:
    #                             name, value = self.__name_value_set(nw, iw, ws)
    #                     except IndexError:
    #                         msg = traceback.format_exc()
    #                         logging.append(f'en línea {ir+1:d}\n{msg}')
    #                         return

    #                     if name == 'tomas':
    #                         continue

    #                     if name == 'clave' and value == '':
    #                         nclave_no_codificada += 1
    #                         value = f'{prefix_clave_no_codificada}' +\
    #                             f'{nclave_no_codificada:d}'

    #                     inscrip.property_set(name, value, ir+1)

    #         if nlineas_no_tratadas > 0:
    #             a = '\n'.join(lineas_no_tratadas)
    #             a = f'\nContenidos de filas no tratadas\n{a}'
    #             logging.append(a)
