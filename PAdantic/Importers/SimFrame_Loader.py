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

class SimFrame_Conversion(BaseModel):
    typeclass: Any
    hardware_type: str

SimFrame_Elements = {
    'quadrupole': SimFrame_Conversion(typeclass=Quadrupole, hardware_type='Magnet'),
    'dipole': SimFrame_Conversion(typeclass=Dipole, hardware_type='Magnet'),
    'sextupole': SimFrame_Conversion(typeclass=Sextupole, hardware_type='Magnet'),
    'solenoid': SimFrame_Conversion(typeclass=Solenoid, hardware_type='Magnet'),
    # 'marker': SimFrame_Conversion(typeclass=Sextupole, hardware_type='Magnet'),
    # 'aperture': SimFrame_Conversion(typeclass=Sextupole, hardware_type='Magnet'),
    'beam_position_monitor': SimFrame_Conversion(typeclass=BPM, hardware_type='BPM'),
    'screen': SimFrame_Conversion(typeclass=Screen, hardware_type='Screen'),
    # 'rf_deflecting_cavity': SimFrame_Conversion(typeclass=Sextupole, hardware_type='Magnet'),
    'kicker': SimFrame_Conversion(typeclass=Corrector, hardware_type='Magnet'),
    'hkicker': SimFrame_Conversion(typeclass=Horizontal_Corrector, hardware_type='Magnet'),
    'vkicker': SimFrame_Conversion(typeclass=Vertical_Corrector, hardware_type='Magnet'),
    # 'monitor': SimFrame_Conversion(typeclass=Sextupole, hardware_type='Magnet'),
    # 'longitudinal_wakefield': SimFrame_Conversion(typeclass=Sextupole, hardware_type='Magnet'),
    # 'cavity': SimFrame_Conversion(typeclass=Sextupole, hardware_type='Magnet'),
}

def get_SimFrame_YAML_filename(original, replacement):
    splitstr = original.replace('\\','/').split('/')
    idx = splitstr.index('YAML')
    return '/'.join(splitstr[:idx]) + '/' + replacement

def get_SimFrame_MachineArea(name):
    return PV.fromString(name+':').area

def get_SimFrame_PV(name):
    return PV.fromString(name+':')

def interpret_SimFrame_Element(name, elem):
    if 'type' in elem and elem['type'] in SimFrame_Elements:
        try:
            # print('type',elem['type'],'found')
            felem = SimFrame_Elements[elem['type']].typeclass
            fpv = globals()[PVTypes[SimFrame_Elements[elem['type']].hardware_type]]
            elemPV = fpv.with_defaults(name)

            fields = elem
            elem.update(dict(SimFrame_Elements[elem['type']]))
            elem.update({'name': name, 'machine_area': get_SimFrame_MachineArea(name)})
            fields['controls'] = elemPV
            fields.update(**{k:v.annotation.from_CATAP(elem) for k,v in felem.model_fields.items() if hasattr(v.annotation, 'from_CATAP')})
            elemmodel = felem(**fields)
            if SimFrame_Elements[elem['type']].hardware_type == 'Magnet':
                elemmodel = add_magnet_table_parameters(name, elemmodel, get_SimFrame_PV(name))
            return elemmodel
        except Exception as e:
            print('Error', name, e)

def read_SimFrame_YAML(filename):
    print('File:',filename)
    elemlist = {}
    with open(filename, 'r') as stream:
        data = yaml.load(stream, Loader=yaml.Loader)
    for name, elem in data['elements'].items():
        if name == 'filename':#and isinstance(elem, str):
            if isinstance(elem, str):
                newfilename = get_SimFrame_YAML_filename(filename, elem)
                elemlist.update(read_SimFrame_YAML(newfilename))
            elif isinstance(elem, list):
                for e in elem:
                    newfilename = get_SimFrame_YAML_filename(filename, e)
                    elemlist.update(read_SimFrame_YAML(newfilename))
        elif 'type' in elem and elem['type'] in SimFrame_Elements:
            if elem['type'] == 'kicker':
                helem = copy(elem)
                helem['type'] = 'hkicker'
                helem['mag_type'] = 'HORIZONTAL_CORRECTOR'
                hname = name.replace('HVCOR', 'HCOR')
                velem = copy(elem)
                velem['type'] = 'vkicker'
                velem['mag_type'] = 'VERTICAL_CORRECTOR'
                vname = name.replace('HVCOR', 'VCOR')
                elemmodel = interpret_SimFrame_Element(hname, helem)
                elemlist.update({name: elemmodel})
                elemmodel = interpret_SimFrame_Element(vname, velem)
                elemlist.update({name: elemmodel})
            else:
                elemmodel = interpret_SimFrame_Element(name, elem)
                elemlist.update({name: elemmodel})
        else:
            pass
            # print(name)
        if 'sub_elements' in elem:
            for subname, subelem in elem['sub_elements'].items():
                if 'type' in subelem and subelem['type'] in SimFrame_Elements:
                    # print('Subelement:', subelem)
                    elemmodel = interpret_SimFrame_Element(subname, subelem)
                    # print(subname, elemmodel)
                    elemlist.update({subname: elemmodel})
    # print('simframe',elemlist)
    return elemlist

# SF_files = glob.glob(r'C:\Users\jkj62.CLRC\Documents\GitHub\masterlattice\MasterLattice\YAML\*.yaml', recursive=True)
SF_files = [
    r'C:\Users\jkj62.CLRC\Documents\GitHub\masterlattice\MasterLattice\YAML\CLA_Gun400.yaml',
    r'C:\Users\jkj62.CLRC\Documents\GitHub\masterlattice\MasterLattice\YAML\CLA_SP2.yaml',
    r'C:\Users\jkj62.CLRC\Documents\GitHub\masterlattice\MasterLattice\YAML\CLA_SP3.yaml',
    r'C:\Users\jkj62.CLRC\Documents\GitHub\masterlattice\MasterLattice\YAML\CLA_FEBE.yaml',
]
