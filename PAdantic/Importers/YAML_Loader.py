import yaml
from yaml import CLoader as Loader

from ..models.PV import (  # noqa
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
from ..models.element import *  # noqa


def interpret_YAML_Element(elem):
    if "hardware_type" in elem and elem["hardware_type"] in globals():
        try:
            felem = globals()[elem["hardware_type"]]
            elemmodel = felem(**elem)
            return elemmodel
        except Exception as e:
            print("interpret_YAML_Element - Error", e)


def read_YAML_Element_File(filename):
    with open(filename, "r") as stream:
        data = yaml.load(stream, Loader=Loader)
    return interpret_YAML_Element(data)


def read_YAML_Combined_File(filename):
    with open(filename, "r") as stream:
        elements = yaml.load(stream, Loader=Loader)
    return [interpret_YAML_Element(element) for element in elements.values()]
