# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 13:08:40 2020

@author: solis
"""
import glob
from os.path import basename, join, splitext
from time import time
import traceback

import littleLogging as logging
import Inscripcion_chj_convertio as inscrip_chj

# ===================================================
dir_data = r'H:\LSGB\data2db\chj_inscripciones'
pattern = '*ALBACETE_convertio.txt'

dir_out = r'H:\LSGB\data2db\chj_inscripciones\output_convertio'
# ===================================================

if __name__ == "__main__":

    startTime = time()

    try:
        files = [basename(f1) for f1 in glob.glob(join(dir_data,pattern))]
        for f1 in files:
            fname, fextension = splitext(f1)
            fo_inscrip = 'ins_' + fname + '.csv'
            fo_toma = 'toma_' + fname + '.csv'

            obj = inscrip_chj.File_convertio(join(dir_data, f1.lower()),
                                             join(dir_out, fo_inscrip.lower()),
                                             join(dir_out, fo_toma.lower()))

            obj.change_format()

    except ValueError:
        msg = traceback.format_exc()
        logging.append(msg)
    except Exception:
        msg = traceback.format_exc()
        logging.append(msg)
    finally:
        logging.dump()
        xtime = time() - startTime
        print(f'El script tardó {xtime:0.1f} s')

