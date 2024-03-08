import yaml
from models.PV import MagnetPV, BPMPV, CameraPV, PV, elementTypes, PVTypes
from models.element import Element, Dipole, Quadrupole, Sextupole, BPM, Camera

def readYAML(filename):
    ''' read a CATAP YAML file and convert to a pydantic model. '''
    with open(filename, 'r') as stream:
        data = yaml.load(stream, Loader=yaml.Loader)
    # for k in data['controls_information']['pv_record_map'].keys():
    #     print('    - '+k)
    # exit()
    fpv = globals()[PVTypes[data['properties']['hardware_type']]]

    if 'mag_type' in data['properties']:
        felem = globals()[elementTypes[data['properties']['mag_type']]]
    elif 'bpm_type' in data['properties']:
        felem = globals()[elementTypes[data['properties']['bpm_type']]]
    elif data['properties']['hardware_type'] == 'Camera':
        felem = globals()[elementTypes['Camera']]

    elemPV = fpv(**{k: PV.fromString(v) for k, v in data['controls_information']['pv_record_map'].items()})

    fields = {k:v.annotation(**data['properties']) for k,v in felem.model_fields.items() if k != 'PV'}
    fields['controls'] = elemPV
    return felem(**fields)

if __name__ == "__main__":
    # elem = readYAML(r'YAML\CLA-S02-MAG-QUAD-01.yml')
    # elem = readYAML(r'YAML\\CLA-C2V-DIA-BPM-01.yaml')
    elem = readYAML(r'YAML\CLA-S01-DIA-CAM-01.yaml')
    # elem.physical.error.position_error.x = 1
    print(elem.model_dump())
