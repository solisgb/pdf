# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 13:08:40 2020

@author: solis
"""
from os.path import join
from time import time
import traceback

import littleLogging as logging
import Inscripcion_chj_convertio as inscrip_chj

# ===================================================
fi1 = r'H:\LSGB\data2db\chj_inscripciones\SUBTERRANEO_ALBACETE_convertio.txt'
dir_out = r'H:\LSGB\data2db\chj_inscripciones\output_convertio'
fo_inscripcion = join(dir_out, 'inscripciones_sub_albacete.csv')
fo_toma = join(dir_out, 'tomas_sub_albacete')
# ===================================================

if __name__ == "__main__":

    try:
        startTime = time()

        obj = inscrip_chj.File_convertio(fi1, fo_inscripcion, fo_toma)

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

