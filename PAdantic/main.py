import yaml
from models.PV import MagnetPV, BPMPV, CameraPV, PV, elementTypes, PVTypes
from models.element import Element, Dipole, Quadrupole, Sextupole, BPM, Camera

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
    elif 'bpm_type' in data['properties']:
        felem = globals()[elementTypes[data['properties']['bpm_type']]]
    elif data['properties']['hardware_type'] == 'Camera':
        felem = globals()[elementTypes['Camera']]

    elemPV = fpv(**{k: PV.fromString(v) for k, v in data['controls_information']['pv_record_map'].items()})

    fields = {k:v.annotation.from_CATAP(data['properties']) for k,v in felem.model_fields.items() if k != 'controls'}
    fields['controls'] = elemPV
    return felem.from_CATAP(fields)

if __name__ == "__main__":
    # elem = read_CATAP_YAML(r'YAML\CLA-S02-MAG-QUAD-01.yml')
    # elem = read_CATAP_YAML(r'YAML\\CLA-C2V-DIA-BPM-01.yaml')
    elem = read_CATAP_YAML(r'YAML\CLA-S01-DIA-CAM-01.yaml')
    # elem.physical.error.position_error.x = 1
    print(elem)
