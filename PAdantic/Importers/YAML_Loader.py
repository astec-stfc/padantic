from copy import copy
from typing import get_origin, Any, Dict
from pydantic import BaseModel
import glob

from Importers.Magnet_Table import add_magnet_table_parameters
from models.PV import (MagnetPV, BPMPV, CameraPV, ScreenPV, ChargeDiagnosticPV, VacuumGuagePV, LaserEnergyMeterPV, LaserHWPPV, LaserMirrorPV,
                       LightingPV, PIDPV, LLRFPV, RFModulatorPV, ShutterPV, ValvePV, RFProtectionPV, RFHeartbeatPV,
                       PV, elementTypes, PVTypes,
                       )
from models.element import *

def interpret_YAML_Element(elem):
    # print(elem['class_name'] in globals())
    if 'class_name' in elem and elem['class_name'] in globals():
        try:
            felem = globals()[elem['class_name']]
            elemmodel = felem(**elem)
            return elemmodel
        except Exception as e:
            print('Error', e)

def read_YAML_File(filename):
    print('File:',filename)
    elemlist = {}
    with open(filename, 'r') as stream:
        data = yaml.load(stream, Loader=yaml.Loader)
    # print(data)
    return interpret_YAML_Element(data)

YAML_files = glob.glob(r'C:\Users\jkj62.CLRC\Documents\GitHub\PAdantic\PAdantic\YAML\**\*.yaml', recursive=True)
