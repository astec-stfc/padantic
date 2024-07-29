from copy import copy
from typing import get_origin, Any, Dict, Optional
from pydantic import BaseModel, field_validator, ValidationInfo
import glob

from .Magnet_Table import add_magnet_table_parameters
from ..models.PV import (MagnetPV, BPMPV, CameraPV, ScreenPV, ChargeDiagnosticPV, VacuumGuagePV, LaserEnergyMeterPV, LaserHWPPV, LaserMirrorPV,
                       LightingPV, PIDPV, LLRFPV, RFModulatorPV, ShutterPV, ValvePV, RFProtectionPV, RFHeartbeatPV,
                       PV, elementTypes, PVTypes,
                       )
from ..models.element import *

class SimFrame_Conversion(BaseModel):
    typeclass: Any
    hardware_class: str
    hardware_type: str|None = Field(validate_default=True, default=None)

    @field_validator('hardware_type', mode='before')
    def check_type(cls, value: Any, info: ValidationInfo) -> str:
        if value is None:
            value = info.data['typeclass'].model_fields['hardware_type'].default
        return value or None

SimFrame_Elements = {
    'quadrupole': SimFrame_Conversion(typeclass=Quadrupole, hardware_class='Magnet'),
    'dipole': SimFrame_Conversion(typeclass=Dipole, hardware_class='Magnet'),
    'sextupole': SimFrame_Conversion(typeclass=Sextupole, hardware_class='Magnet'),
    'solenoid': SimFrame_Conversion(typeclass=Solenoid, hardware_class='Magnet'),
    'marker': SimFrame_Conversion(typeclass=Marker, hardware_class='Simulation'),
    'aperture': SimFrame_Conversion(typeclass=Aperture, hardware_class='Simulation'),
    'collimator': SimFrame_Conversion(typeclass=Collimator, hardware_class='Simulation'),
    'beam_position_monitor': SimFrame_Conversion(typeclass=BPM, hardware_class='BPM'),
    'beam_arrival_monitor': SimFrame_Conversion(typeclass=BAM, hardware_class='BAM'),
    'bunch_length_monitor': SimFrame_Conversion(typeclass=BLM, hardware_class='BLM'),
    'wall_current_monitor': SimFrame_Conversion(typeclass=ChargeDiagnostic, hardware_class='Charge'),
    'faraday_cup': SimFrame_Conversion(typeclass=ChargeDiagnostic, hardware_class='Charge'),
    'integrated_current_transformer': SimFrame_Conversion(typeclass=ChargeDiagnostic, hardware_class='Charge'),
    'screen': SimFrame_Conversion(typeclass=Screen, hardware_class='Screen'),
    # 'rf_deflecting_cavity': SimFrame_Conversion(typeclass=Sextupole, hardware_class='Magnet'),
    'kicker': SimFrame_Conversion(typeclass=Corrector, hardware_class='Magnet'),
    'hkicker': SimFrame_Conversion(typeclass=Horizontal_Corrector, hardware_class='Magnet'),
    'vkicker': SimFrame_Conversion(typeclass=Vertical_Corrector, hardware_class='Magnet'),
    # 'monitor': SimFrame_Conversion(typeclass=Sextupole, hardware_class='Magnet'),
    'longitudinal_wakefield': SimFrame_Conversion(typeclass=Wakefield, hardware_class='Simulation'),
    'cavity': SimFrame_Conversion(typeclass=RFCavity, hardware_class='RFCavity'),
    'rf_deflecting_cavity': SimFrame_Conversion(typeclass=RFDeflectingCavity, hardware_class='RFCavity'),
    'shutter': SimFrame_Conversion(typeclass=Shutter, hardware_class='Shutter'),
}

def get_SimFrame_YAML_filename(original, replacement):
    splitstr = original.replace('\\','/').split('/')
    idx = splitstr.index('YAML')
    return '/'.join(splitstr[:idx]) + '/' + replacement

def get_SimFrame_MachineArea(name):
    return PV(pv_string=name+':').area

def get_SimFrame_PV(name):
    return PV(pv_string=name+':')

def interpret_SimFrame_Element(name, elem):
    if 'type' in elem and elem['type'] in SimFrame_Elements:
        # try:
            # print('type',elem['type'],'found')
            felem = SimFrame_Elements[elem['type']].typeclass
            hasPV = SimFrame_Elements[elem['type']].hardware_class in PVTypes

            elem.update(dict(SimFrame_Elements[elem['type']]))
            elem.update({'name': name, 'machine_area': get_SimFrame_MachineArea(name), 'hardware_type': elem['type']})
            fields = elem
            if hasPV:
                try:
                    fpv = globals()[PVTypes[SimFrame_Elements[elem['type']].hardware_class]]
                    elemPV = fpv.with_defaults(name)
                    fields['controls'] = elemPV
                except Exception as e:
                    print('interpret_SimFrame_Element', name, elem, fpv)
                    raise e
            fields.update(**{k:v.annotation.from_CATAP(elem) for k,v in felem.model_fields.items() if hasattr(v.annotation, 'from_CATAP')})
            elemmodel = felem(**fields)
            if SimFrame_Elements[elem['type']].hardware_class == 'Magnet':
                elemmodel = add_magnet_table_parameters(name, elemmodel, get_SimFrame_PV(name))
            return elemmodel
      # except Exception as e:
        #     print('Error', name, e)

def read_SimFrame_YAML(filename):
    # print('File:',filename)
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
                elemlist.update({hname: elemmodel})
                elemmodel = interpret_SimFrame_Element(vname, velem)
                elemlist.update({vname: elemmodel})
            else:
                elemmodel = interpret_SimFrame_Element(name, elem)
                elemlist.update({name: elemmodel})
        else:
            # pass
            print('read_SimFrame_YAML', name, elem['type'])
        if 'sub_elements' in elem:
            for subname, subelem in elem['sub_elements'].items():
                if 'type' in subelem and subelem['type'] in SimFrame_Elements:
                    # print('Subelement:', subelem)
                    subelem['subelement'] = True
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
