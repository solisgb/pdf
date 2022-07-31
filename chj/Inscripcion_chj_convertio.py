# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 18:15:52 2022

@author: solis
"""
from collections import OrderedDict
import copy
import csv

import littleLogging as logging

NMAX_ERROR_READING_FILE = 15

NULL_VALUE = ''

keys_inscripcion = [('clave',NULL_VALUE),
                    ('seccion',NULL_VALUE), ('tomo',NULL_VALUE),
                    ('folio',NULL_VALUE), ('ugh',NULL_VALUE),
                    ('tipo',NULL_VALUE),
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
    Characteristics of the inscriptions and its intakes provided by the CHJ
    through a pdf file downloaded from its web site
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
        if name in self.d.keys():
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


class Counter():
    """
    Counter to be passed by ref to a function
    """
    def __init__(self, i: int):
        self.__i = i

    @property
    def i(self):
        return self.__i

    def __iadd__(self, i:int):
        self.__i += i
        return self


class File_convertio():
    """
    To read a chj registration file downloaded from chj web page and
    exported from pdf to txt using convertio on line

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

    # keys in the chj pdf file
    keys = ('TIPO INSCRIPCIÓN:',
             'COMUNIDAD AUTÓNOMA:',
             'PROVINCIA:',
             'Municipio:',
             'Sección:',
             'Tomo:',
             'Folio:',
             'Clave:',
             'UGH:',
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
        Names of the files used to read a chj registration file as txt and two
        output files: inscriptions and intakes of inscripcions. One
        inscription can have 1 or more intakes

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
        """
        Translates the names of the keys in the file to key names in IT obj

        Parameters
        ----------
        name : str
            Name of the keys in the file

        Returns
        -------
        name : str
            Name of the key in object IT

        """

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
        elif name == 'UGH:':
            name = 'ugh'
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


    def __ins_from_list(self, keys_values: [[str, str]],
                        nclave_no_codificada: Counter,
                        prefix_clave_no_codificada:str,
                        ntoma_no_codificada: Counter,
                        prefix_toma_no_codificada: str,
                        inscrip: IT, toma: IT, tomas:[]):
        """
        Assigns the properties of the "inscrip" and "toma" objects based on
        the contents of the "keys_values" object.

        Parameters
        ----------
        keys_values : [[str, str, int]]
            For each element key, value, number of row in the input file
        nclave_no_codificada : Counter
            Counter of objects inscrip with no clave id in the file.
        prefix_clave_no_codificada : str
            Prefix to set a clave id when none is provided
        ntoma_no_codificada : Counter
            Counter of objects toma with no toma id in the file.
        prefix_toma_no_codificada : str
            Prefix to set a toma id when none is provided.
        inscrip : IT
            Object IT for registration (inscripción) data
        toma : IT
            Object IT for intake (toma) data.
        tomas : []
            list of objects toma for a registration

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        for k1, v1, r1 in keys_values:
            k1 = self.__translate_to_true_keys(k1)
            if k1 is None:
                logging.append(f'row {r1}, "{k1}" is not a valid key')
                continue
            if k1 == 'clave' and (v1 == '' or v1 == '-'):
                nclave_no_codificada += 1
                v1 = f'{prefix_clave_no_codificada}' +\
                    f'{nclave_no_codificada.i:d}'
            elif k1 == 'toma' and (v1 == '' or v1 == '-'):
                ntoma_no_codificada += 1
                v1 = f'{prefix_toma_no_codificada}' +\
                    f'{ntoma_no_codificada.i:d}'

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


    def change_format(self):
        """
        Reads self.fi1 and writes self.fo_inscripcion and self.fo_toma

        Returns
        -------
        None.

        """

        # Las líneas con este contenido no se consideran
        skip_text = 'CONFEDERACIÓN HIDROGRÁFICA DEL JÚCAR'

        nclave_no_codificada = Counter(0)
        prefix_clave_no_codificada = 'cnc_'

        ntoma_no_codificada = Counter(0)
        prefix_toma_no_codificada = 'tnc_'

        keys_values = []
        ninscrip = Counter(0)
        inscrip = IT(keys_inscripcion)
        toma = IT(keys_toma)
        tomas = []

        inscription_end = 'Página'
        inscription_end_cover = 'Página 1 '

        with open(self.fi1, 'r', encoding='utf-8') as fi, \
            open(self.fo_inscripcion, 'w', newline='',
                 encoding='utf-8') as finscrip, \
            open(self.fo_toma, 'w', newline='', encoding='utf-8') as ftoma:

            inscrip_w = csv.writer(finscrip, delimiter=',')
            toma_w = csv.writer(ftoma, delimiter=',')
            inscrip_w.writerow(inscrip.keys_get())
            toma_w.writerow(toma.keys_get())

            for ir, row in enumerate(fi):
                if ir % 250 == 0:
                    print(ir)

                row = row.strip()
                if len(row) == 0:
                    continue

                if skip_text in row:
                    continue

                if inscription_end in row:
                    if inscription_end_cover in row:
                        keys_values = []
                    else:
                        # grabo los datos de la inscripcion y sus tomas
                        self.__ins_from_list(keys_values,
                                             nclave_no_codificada,
                                             prefix_clave_no_codificada,
                                             ntoma_no_codificada,
                                             prefix_toma_no_codificada,
                                             inscrip, toma, tomas)
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
                if len(present_keys) == 0:
                    # linea suelta, cot. de la previa
                    if len(keys_values) > 0:
                        keys_values[-1][1] = keys_values[-1][1] + ' ' + \
                            row.strip()
                    else:
                        logging.append(f'row {ir+1} "{row}" está suelta')
                    continue
                pos0 = [row.find(key1) for key1 in present_keys]
                pos1 = [row.find(key1)+len(key1) for key1 in present_keys]

                ilength = len(present_keys) - 1
                for i, (k1, p0, p1) in enumerate(zip(present_keys, pos0, pos1)):
                    if i < ilength:
                        pe = pos0[i+1]
                        keys_values.append([k1[0:], row[p1:pe].strip(), ir+1])
                    else:
                        keys_values.append([k1[0:], row[p1:].strip(), ir+1])

