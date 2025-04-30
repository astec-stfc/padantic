import os
import glob
from yaml import load
from Importers.MySafeLoader import MySafeLoader
from PAdantic.models.PV import (  # noqa: F401
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
from PAdantic.models.element import *  # noqa


class ReplacePc:
    def __init__(self, filename):
        self.fn = filename
        self.buffer = ""

    def __enter__(self):
        self.fh = open(self.fn, "r")
        return self

    def __exit__(self, _type, _value, _tb):
        self.fh.close()

    def read(self, size):
        eof = False
        while self.fn is not None and not eof and len(self.buffer) < size:
            line = self.fh.readline()
            if line == "":
                eof = True
            self.buffer += line.replace("\t", " ")
        if len(self.buffer) > size:
            chunk = self.buffer[:size]
            self.buffer = self.buffer[size:]
        else:
            chunk = self.buffer
            self.buffer = ""
        return chunk


def get_possible_pv_names(pvdict):
    names = []
    for pv in pvdict.values():
        prefix, postfix = pv.split(":", 1)
        names.append(prefix)
    sortednames = [(i, names.count(i)) for i in set(names)]
    sortednames.sort(reverse=True, key=lambda x: x[1])
    return [n[0] for n in sortednames]


def get_camera_pv_names(name):
    prefix = name
    substr = prefix.split("-")
    iocsubstr = ["CLA", "C10", "IOC", "CS", "03"]
    ledsubstr = substr + []
    ledsubstr[1] = "LAS"
    ledsubstr[3] = "LED"
    return ["-".join(a) for a in [substr, iocsubstr, ledsubstr]]


def read_CATAP_YAML(filename):
    """read a CATAP YAML file and convert to a pydantic model."""
    print("File:", filename)
    with ReplacePc(filename) as stream:
        data = load(stream, Loader=MySafeLoader)
    # for k in data['controls_information']['pv_record_map'].keys():
    #     print('    - '+k)
    # exit()
    fpv = globals()[PVTypes[data["properties"]["hardware_type"]]]

    if "mag_type" in data["properties"]:
        felem = globals()[elementTypes[data["properties"]["mag_type"]]]
    else:
        felem = globals()[elementTypes[data["properties"]["hardware_type"]]]

    # print(data['controls_information']['pv_record_map'].items())
    if data["properties"]["hardware_type"] == "Camera":
        names = get_camera_pv_names(data["properties"]["name"])
        # print(names)
        # exit()
        elemPV = fpv.with_defaults(*names)
    else:
        elemPV = fpv.with_defaults(data["properties"]["name"])

    elemPV.update(
        **{
            k: PV.fromString(v)
            for k, v in data["controls_information"]["pv_record_map"].items()
        }
    )

    fields = data["properties"]
    fields.update(
        **{
            k: v.annotation.from_CATAP(data["properties"])
            for k, v in felem.model_fields.items()
            if k != "controls" and hasattr(v.annotation, "from_CATAP")
        }
    )
    fields["controls"] = elemPV
    # print(felem)
    elem = felem(**fields)
    return {elem.name: elem}


catap_files = [
    r"YAML\CLA-S02-MAG-QUAD-01.yml",
    # r'YAML\\CLA-C2V-DIA-BPM-01.yaml',
    # r'YAML\CLA-S01-DIA-CAM-01.yaml',
    # r'YAML\CLA-S01-DIA-SCR-01.yaml',
    # r'YAML\CLA-S01-DIA-WCM-01.yaml',
    # r'YAML\CLA-S02-DIA-FCUP-01.yaml',
    # r'YAML\EBT-INJ-VAC-IMG-02.yaml',
    # r'YAML\CLA-LAS-DIA-EM-06.yaml',
    # r'YAML\EBT-LAS-OPT-HWP-2.yaml',
    # r'YAML\EBT-LAS-OPT-PM-11.yml',
    # r'YAML\ALL-LIGHTS.yaml',
    # r'YAML\CLA-L01-LRF-CTRL-01.yaml',
    # r'YAML\gun.yaml',
    # r'YAML\L01Modulator.yaml',
    # r'YAML\EBT-INJ-LSR-SHUT-02.yaml',
    # r'YAML\CLA-S01-VAC-VALV-01.yaml',
    # r'YAML\CLA-L01-RF-PROTE-01.yaml',
]

catap_path = os.path.join(
    "\\\\claraserv3.dl.ac.uk",
    "claranet",
    "packages",
    "CATAP",
    "Nightly",
    "CATAP_Nightly_17_01_2024",
    "python310",
    "MasterLattice",
)

catap_files = glob.glob(os.path.join(catap_path, "*", "CLA*.yaml"), recursive=True)
catap_files += glob.glob(os.path.join(catap_path, "*", "CLA*.yml"), recursive=True)
