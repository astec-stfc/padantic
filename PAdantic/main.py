import yaml
from models.PV import MagnetPV, PV, magnetTypes
from models.element import Element, Dipole, Quadrupole, Sextupole

def readYAML(filename):
    ''' read a CATAP YAML file and convert to a pydantic model. '''
    with open(filename, 'r') as stream:
        data = yaml.load(stream, Loader=yaml.Loader)
    magPV = MagnetPV(**{k: PV.fromString(v) for k, v in data['controls_information']['pv_record_map'].items()})
    f = globals()[magnetTypes[data['properties']['mag_type']]]
    fields = {k:v.annotation(**data['properties']) for k,v in f.model_fields.items() if k != 'PV'}
    fields['controls'] = magPV
    return f(**fields)

if __name__ == "__main__":
    # pos = Dipole_Magnet(middle=Position(z=1.2), kl=np.pi/6, length=0.3, global_rotation=Rotation(theta=0*np.pi/6))
    # print(pos.multipoles)
    # print(pos.angle)
    # print(pos.middle)
    # print(pos.start)
    # print(pos.end)
    # print(PV.fromString('CLA-S02-MAG-QUAD-01:GETSETI').basename)
    # print(pos.KnL(1))
    # pos.kl = 5
    # pos.multipoles.K2L.skew = 2.
    # print(pos.multipoles)
    # print([a.annotation.__name__ for a in Element.model_fields.values()])
    elem = readYAML(r'\\claraserv3.dl.ac.uk\claranet\packages\CATAP\Nightly\CATAP_Nightly_17_01_2024\python310\MasterLattice\Magnet\CLA-C2V-MAG-DIP-01.yml')
    elem.physical.error.position_error.x = 1
    print(elem.model_dump())
