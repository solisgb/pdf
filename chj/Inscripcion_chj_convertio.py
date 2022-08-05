# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 18:15:52 2022

@author: solis
"""
from collections import OrderedDict
import copy
import csv
from datetime import date
from locale import atof, setlocale, LC_NUMERIC
from os.path import basename

import littleLogging as logging

setlocale(LC_NUMERIC, 'es_ES')

NULL = ''

keys_inscripcion = [('seccion', [NULL, str]), ('tomo', [NULL, str]),
                    ('folio', [NULL, str]),
                    ('clave', [NULL, str]), ('ugh', [NULL, str]),
                    ('tipo', [NULL, str]),
                    ('fecha', [NULL, date]),
                    ('clase_afeccion', [NULL, str]),
                    ('vol_max_m3', [NULL, float]),
                    ('superficie_ha', [NULL, float]),
                    ('corriente_acu', [NULL, str]),
                    ('paraje', [NULL, str]), ('municipio', [NULL, str]),
                    ('provincia', [NULL, str]), ('ca', [NULL, str]),
                    ('titular', [NULL, str])]

# WARNING: Last item in keys_toma must be last item to be read in chj file;
# ID_TOMA is a key not present in the chj file
ID_TOMA = 'toma_ins'
keys_toma = [(ID_TOMA, [NULL, str]),
             ('seccion', [NULL, str]), ('tomo', [NULL, str]),
             ('folio', [NULL, str]), ('toma', [NULL, str]),
             ('xutm', [NULL, float]), ('yutm', [NULL, float]),
             ('huso', [NULL, str])]

INSCRIPCION_PRIMARY_KEY = ('seccion', 'tomo', 'folio')


class IT():
    """
    Characteristics of the inscriptions and its intakes (tomas) provided
    by the CHJ through a pdf file downloaded from its web site
    """

    def __init__(self, keys: [()]):
        self.d = OrderedDict(copy.deepcopy(keys))


    def __getitem__(self, key: str):
        if key not in self.d.keys():
            raise KeyError
        return self.d[key][0]


    def __setitem__(self, key: str, value: str):
        """
        Set the values in self.d with values readed from txt file generated
        with convertio

        Parameters
        ----------
        key : str
            key in file.
        value : str
            key value.

        Returns
        -------
            Exceptions: KeyError
        """

        if key not in self.d.keys():
            raise KeyError(f'{key} is not a valid key')

        if self.d[key][1] is float:
            self.d[key][0] = self.str_to_float(value)
        elif self.d[key][1] is date:
            self.d[key][0] = self.str_to_date(value)
        else:
            if '  ' in value:
                lvalue = value.split()
                value = ' '.join(lvalue)
            self.d[key][0] = value


    def __str__(self):
        l = [str(item) for item in self.values_get()]
        return ','.join(l)


    def __rep__(self):
        return str(self)


    def keys_get(self):
        return list(self.d.keys())


    def values_get(self):
        return [v2[0] for v2 in list(self.d.values())]


    def has_key(self, name:str):
        if name in self.d.keys():
            return True
        else:
            return False


    def str_to_date(self, str_date: str):
        """
        formats str_date (date as str) as '%Y-%m-%d'
        ; if not returns str_date

        Parameters
        ----------
        str_date : str
            date as str

        Returns
        -------
            str '%Y-%m-%d' or ''
        """
        MONTHS = dict([('ene', 1),('jan',1),('feb',2),('mar',3),
                  ('abr',4),('may',5),('jun',6),
                  ('jul',7),('ago',8),('aug',8),('sep',9),
                  ('oct',10),('nov',11),('dic',12)])

        DATE_SEPARATORS = ('/', '-')

        try:
            for sep in DATE_SEPARATORS:
                ws = str_date.split(sep)
                if len(ws) == 3:
                    dt = date(int(ws[2]), int(ws[1]), int(ws[0]))
                    return dt.strftime('%Y-%m-%d')

            ws = str_date.split()
            if len(ws) >= 3:
                ws[0] = ws[0].lower()
                if ws[0] in MONTHS.keys():
                    ws[0] = MONTHS[ws[0]]
                    dt = date(int(ws[2]), int(ws[0]), int(ws[1]))
                    return dt.strftime('%Y-%m-%d')

            if len(str_date.strip()) == 0:
                return ''

            logging.append(f'{str_date} unkown str representation of a date')
            return ''
        except:
            logging.append(f'{str_date} can not be formated as date')
            return ''


    def str_to_float(self, str_float: str):
        """
        str to float using atof

        Parameters
        ----------
        str_float : str
            float as str

        Returns
        -------
            float or ''
        """
        if len(str_float.strip()) == 0:
            return ''

        try:
            return atof(str_float)
        except:
            logging.append(f'{str_float} can not be converted to float')
            return ''


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

    # alls keys in the chj pdf file
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

    PRINT_COUNTER_EACH = 500  # rows

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
    def __get_key(name: str):
        """
        Correspondence between the names of the keys in the file
        to key names in IT instance

        Parameters
        ----------
        name : str
            Name of the keys in the file

        Returns
        -------
        name : str
            Name of the key in object IT

        """
        dict_translate = \
            dict([('TIPO INSCRIPCIÓN:', 'tipo'),
                  ('COMUNIDAD AUTÓNOMA:', 'ca'),
                  ('PROVINCIA:', 'provincia'),
                  ('Municipio:', 'municipio'),
                  ('Sección:', 'seccion'),
                  ('Tomo:', 'tomo'),
                  ('Folio:', 'folio'),
                  ('Clave:', 'clave'),
                  ('UGH:', 'ugh'),
                  ('Fecha Concesión:', 'fecha'),
                  ('Clase y Afeccion:', 'clase_afeccion'),
                  ('Vol. Max. Anual (m3):', 'vol_max_m3'),
                  ('Superficie (ha):', 'superficie_ha'),
                  ('Corriente - Acuifero:', 'corriente_acu'),
                  ('Paraje:', 'paraje'),
                  ('Municipio:', 'municipio'),
                  ('Provincia:', 'provincia'),
                  ('Titular:', 'titular'),
                  ('TOMA:', 'toma'),
                  ('UTMX:', 'xutm'),
                  ('UTM Y:', 'yutm'),
                  ('HUSO:', 'huso')])

        if name not in dict_translate.keys():
            return None
        else:
            return dict_translate[name]


    def __ins_from_list(self, keys_values: [[str, str]],
                        inscrip: IT, toma: IT, tomas:[]):
        """
        Assigns the properties of the "inscrip" and "toma" objects based on
        the contents of the "keys_values" object.

        Parameters
        ----------
        keys_values : [[str, str, int]]
            For each element key, value, number of row in the input file
        inscrip : IT
            Object IT type inscription (inscripción)
        toma : IT
            Object IT type intake (toma).
        tomas : []
            list of objects toma for a inscription

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        ntoma = 0
        for k1, v1, r1 in keys_values:
            k1 = self.__get_key(k1)
            if k1 is None:
                logging.append(f'row {r1}, "{k1}" is not a valid key')
                continue

            if inscrip.has_key(k1):
                inscrip[k1] = v1
            elif toma.has_key(k1):
                toma[k1] = v1
                # si k1 es la última columna de toma
                if k1 == toma.keys_get()[-1]:
                    ntoma += 1
                    toma[ID_TOMA] = str(ntoma)
                    for ins_pk1 in INSCRIPCION_PRIMARY_KEY:
                        name = ins_pk1
                        value = inscrip[name]
                        toma[name] = value
                    tomas.append(copy.deepcopy(toma))
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

        keys_values = []
        inscrip = IT(keys_inscripcion)
        toma = IT(keys_toma)
        tomas = []

        inscription_end = 'Página'
        inscription_end_cover = 'Página 1 '

        with open(self.fi1, 'r', encoding='utf-8') as fi, \
            open(self.fo_inscripcion, 'w', newline='',
                 encoding='utf-8') as finscrip, \
            open(self.fo_toma, 'w', newline='', encoding='utf-8') as ftoma:

            print('\n', basename(self.fi1))
            inscrip_w = csv.writer(finscrip, delimiter=',')
            toma_w = csv.writer(ftoma, delimiter=',')
            inscrip_w.writerow(inscrip.keys_get())
            toma_w.writerow(toma.keys_get())

            for ir, row in enumerate(fi):
                if ir % self.PRINT_COUNTER_EACH == 0:
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
                        self.__ins_from_list(keys_values, inscrip, toma, tomas)
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
            print(ir)
