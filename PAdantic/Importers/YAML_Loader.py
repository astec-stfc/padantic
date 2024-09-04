from yaml import CLoader as Loader
from copy import copy
from typing import get_origin, Any, Dict
from pydantic import BaseModel
import glob

from ..models.PV import (
    MagnetPV,
    BPMPV,
    CameraPV,
    ScreenPV,
    ChargeDiagnosticPV,
    VacuumGuagePV,
    LaserEnergyMeterPV,
    LaserHWPPV,
    LaserMirrorPV,
    LightingPV,
    PIDPV,
    LLRFPV,
    RFModulatorPV,
    ShutterPV,
    ValvePV,
    RFProtectionPV,
    RFHeartbeatPV,
    PV,
    elementTypes,
    PVTypes,
)
from ..models.element import *


def interpret_YAML_Element(elem):
    if "class_name" in elem and elem["class_name"] in globals():
        try:
            felem = globals()[elem["class_name"]]
            elemmodel = felem(**elem)
            return elemmodel
        except Exception as e:
            print("Error", e)


def read_YAML_Element_File(filename):
    with open(filename, "r") as stream:
        data = yaml.load(stream, Loader=Loader)
    return interpret_YAML_Element(data)


def read_YAML_Combined_File(filename):
    with open(filename, "r") as stream:
        elements = yaml.load(stream, Loader=Loader)
    return [interpret_YAML_Element(element) for element in elements.values()]
