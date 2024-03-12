import yaml
from typing import get_origin
from pydantic import BaseModel
from models.PV import (MagnetPV, BPMPV, CameraPV, ScreenPV, ChargeDiagnosticPV, VacuumGuagePV, LaserEnergyMeterPV, LaserHWPPV, LaserMirrorPV,LightingPV,
                       PV, elementTypes, PVTypes,
                       )
from models.element import (Element, Dipole, Quadrupole, Sextupole, BPM, Camera, Screen,
                           ChargeDiagnostic, VacuumGuage, LaserEnergyMeter, LaserHalfWavePlate,
                           LaserMirror, Lighting
                           )

def read_CATAP_YAML(filename):
    ''' read a CATAP YAML file and convert to a pydantic model. '''
    with open(filename, 'r') as stream:
        data = yaml.load(stream, Loader=yaml.Loader)
    # for k in data['controls_information']['pv_record_map'].keys():
    #     print('    - '+k)
    # exit()
    fpv = globals()[PVTypes[data['properties']['hardware_type']]]

    if 'mag_type' in data['properties']:
        felem = globals()[elementTypes[data['properties']['mag_type']]]
    else:
        felem = globals()[elementTypes[data['properties']['hardware_type']]]

    # print({k: PV.fromString(v) for k, v in data['controls_information']['pv_record_map'].items()})
    elemPV = fpv(**{k: PV.fromString(v) for k, v in data['controls_information']['pv_record_map'].items()})

    fields = data['properties']
    fields.update(**{k:v.annotation.from_CATAP(data['properties']) for k,v in felem.model_fields.items() if k != 'controls' and hasattr(v.annotation, 'from_CATAP')})
    fields['controls'] = elemPV
    return felem(**fields)

files = [
    r'YAML\CLA-S02-MAG-QUAD-01.yml',
    r'YAML\\CLA-C2V-DIA-BPM-01.yaml',
    r'YAML\CLA-S01-DIA-CAM-01.yaml',
    r'YAML\CLA-S01-DIA-SCR-01.yaml',
    r'YAML\CLA-S01-DIA-WCM-01.yaml',
    r'YAML\CLA-S02-DIA-FCUP-01.yaml',
    r'YAML\EBT-INJ-VAC-IMG-02.yaml',
    r'YAML\CLA-LAS-DIA-EM-06.yaml',
    r'YAML\EBT-LAS-OPT-HWP-2.yaml',
    r'YAML\EBT-LAS-OPT-PM-11.yml',
    r'YAML\ALL-LIGHTS.yaml',
]

if __name__ == "__main__":
    for f in files:
        elem = read_CATAP_YAML(f)
        # elem.physical.error.position.x = 1
        print(elem.no_controls)
        print('\n')
