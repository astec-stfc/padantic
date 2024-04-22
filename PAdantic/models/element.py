from typing import Type, List, Dict, Any
from pydantic import field_validator, Field, BaseModel, RootModel

from models.baseModels import T, Aliases, IgnoreExtra
from models.PV import (PV, MagnetPV, BPMPV, CameraPV, ScreenPV, ChargeDiagnosticPV, VacuumGuagePV, LaserEnergyMeterPV, LaserHWPPV,
                       LaserMirrorPV, LightingPV,  PIDPV, LLRFPV, RFModulatorPV, ShutterPV, ValvePV, RFProtectionPV, RFHeartbeatPV)
from models.manufacturer import ManufacturerElement
from models.electrical import ElectricalElement
from models.degauss import DegaussablElement
from models.physical import PhysicalElement
from models.magnetic import Dipole_Magnet, Quadrupole_Magnet, Sextupole_Magnet, Solenoid_Magnet
from models.diagnostic import BPM_Diagnostic, Camera_Diagnostic, Screen_Diagnostic, Charge_Diagnostic
from models.laser import LaserElement, LaserEnergyMeterElement, LaserMirrorElement
from models.lighting import LightingElement
from models.RF import PIDElement, LLRFElement, RFModulatorElement, RFProtectionElement, RFHeartbeatElement
from models.shutter import ShutterElement, ValveElement
import yaml


class string_with_quotes(str):
    pass

class flow_list(list):
    pass

def flow_list_rep(dumper, data):
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)

def quoted_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

yaml.add_representer(string_with_quotes, quoted_presenter)
yaml.add_representer(flow_list, flow_list_rep)

class _baseElement(IgnoreExtra):
    name: str
    hardware_type: str
    machine_area: str
    virtual_name: str = ''
    alias: str|list|Aliases = Field(alias='name_alias', default=None)

    @field_validator('name', mode='before')
    @classmethod
    def validate_name(cls, v: str) -> str:
        # print(list(map(str.strip, v.split(','))))
        assert isinstance(v, str)
        try:
            PV.fromString(str(v)+':')
        except:
            raise ValueError('name is not a valid element name')
        return v

    @field_validator('alias', mode='before')
    @classmethod
    def validate_alias(cls, v: str|List) -> Aliases:
        # print(list(map(str.strip, v.split(','))))
        if isinstance(v, str):
            return Aliases(aliases=list(map(str.strip, v.split(','))))
        elif isinstance(v, (list, tuple)):
            return Aliases(aliases=list(v))
        else:
            raise ValueError('alias should be a string or a list of strings')

    def escape_string_list(self, l):
        if len(list(l)) > 0:
            return  string_with_quotes(",".join(map(str,list(l))))
        return string_with_quotes("")

    @classmethod
    def from_CATAP(cls: Type[T], fields: dict) -> T:
        return cls(**fields)

    def generate_aliases(self):
        magnetPV = PV.fromString(str(self.name)+':')#('CLA', 'S07', 'QUAD', 1)
        return [magnetPV.area+'-'+magnetPV.typename+str(magnetPV.index).zfill(2),
                magnetPV.area+'-'+magnetPV.typename+str(magnetPV._indexString),
                magnetPV.area+'-'+magnetPV.typename+str(magnetPV.index)]

    def to_CATAP(self):
        aliases = ','.join(self.alias.aliases) if self.alias is not None else self.generate_aliases()
        return {
            'machine_area': self.machine_area,
            'hardware_type': self.hardware_type,
            'name': self.name,
            # 'virtual_name': self.virtual_name,
            'name_alias': ",".join(map(str,list(aliases)))
        }

    @property
    def no_controls(self):
        return self.__class__.__name__+'('+' '.join([k+'='+getattr(self, k).__repr__() for k in self.model_fields.keys() if k != 'controls'])+')'

class PhysicalElement(_baseElement):
    ''' Element with physical, degaussable, electrical, manufacturer, and controls items. '''
    physical: PhysicalElement

    def to_CATAP(self):
        catap_dict = super().to_CATAP()
        catap_dict.update({
            'position': list(self.physical.middle)[2],
        })
        return catap_dict

class Element(PhysicalElement):
    ''' Element with physical, degaussable, electrical, manufacturer, and controls items. '''
    electrical: ElectricalElement
    manufacturer: ManufacturerElement

    def to_CATAP(self):
        catap_dict = super().to_CATAP()
        catap_dict.update({
            'manufacturer': self.manufacturer.manufacturer,
            'serial_number': self.manufacturer.serial_number,
        })
        return catap_dict

class Magnet(Element):
    type: str = Field(alias='mag_type', default='')
    controls: MagnetPV
    degauss : DegaussablElement

    @field_validator('type', mode='before')
    @classmethod
    def validate_type(cls, v: str) -> str:
        # print(list(map(str.strip, v.split(','))))
        if isinstance(v, str):
            return v.upper()
        else:
            raise ValueError('alias should be a string or a list of strings')

    def to_CATAP(self):
        catap_dict = super().to_CATAP()
        catap_dict.update({
            'mag_type': self.type,
            'degauss_tolerance': self.degauss.tolerance,
            'degauss_values': self.escape_string_list(self.degauss.values),
            'num_degauss_steps': self.degauss.steps,
            'field_integral_coefficients': self.escape_string_list(self.magnetic.field_integral_coefficients),
            'linear_saturation_coefficients': self.escape_string_list(self.magnetic.linear_saturation_coefficients),
            'mag_set_max_wait_time': self.magnetic.settle_time,
            'magnetic_length': 1000*self.magnetic.length,
            'ri_tolerance': self.electrical.read_tolerance,
            'min_i': self.electrical.minI,
            'max_i': self.electrical.maxI,
        })
        return catap_dict

class Dipole(Magnet):
    ''' Dipole element. '''
    type: str = Field(alias='mag_type', default='DIPOLE', frozen=True)
    magnetic: Dipole_Magnet

class Quadrupole(Magnet):
    ''' Quadrupole element. '''
    type: str = Field(alias='mag_type', default='QUADRUPOLE', frozen=True)
    magnetic: Quadrupole_Magnet

class Sextupole(Magnet):
    ''' Sextupole element. '''
    type: str = Field(alias='mag_type', default='SEXTUPOLE', frozen=True)
    magnetic: Sextupole_Magnet

class Corrector(Dipole):
    type: str = Field(alias='mag_type', default='CORRECTOR', frozen=True)

class Horizontal_Corrector(Dipole):
    type: str = Field(alias='mag_type', default='HORIZONTAL_CORRECTOR', frozen=True)

class Vertical_Corrector(Dipole):
    type: str = Field(alias='mag_type', default='VERTICAL_CORRECTOR', frozen=True)

class Solenoid(Magnet):
    type: str = Field(alias='mag_type', default='SOLENOID', frozen=True)
    magnetic: Solenoid_Magnet

class BPM(Element):
    diagnostic: BPM_Diagnostic
    controls: BPMPV

    def to_CATAP(self):
        catap_dict = super().to_CATAP()
        catap_dict.update({
            'bpm_type': self.diagnostic.type,
            'bpm_set_max_wait_time': self.diagnostic.settle_time,
            'att1cal': self.diagnostic.attenuation1_calibration,
            'att2cal': self.diagnostic.attenuation2_calibration,
            'v1cal': self.diagnostic.voltage1_calibration,
            'v2cal': self.diagnostic.voltage2_calibration,
            'qcal': self.diagnostic.charge_calibration,
            'mn': self.diagnostic.mn,
            'xn': self.diagnostic.xn,
            'yn': self.diagnostic.yn,
        })
        return catap_dict

class Camera(PhysicalElement):
    diagnostic: Camera_Diagnostic
    controls: CameraPV

class Screen(PhysicalElement):
    diagnostic: Screen_Diagnostic
    controls: ScreenPV

    def to_CATAP(self):
        catap_dict = super().to_CATAP()
        catap_dict.update({
            'screen_type': self.diagnostic.type,
            'has_camera': self.diagnostic.has_camera,
            'camera_name': self.diagnostic.camera_name,
            'devices': self.escape_string_list(self.diagnostic.devices),
        })
        return catap_dict

class ChargeDiagnostic(PhysicalElement):
    diagnostic: Charge_Diagnostic
    controls: ChargeDiagnosticPV

class VacuumGuage(PhysicalElement):
    manufacturer: ManufacturerElement
    controls: VacuumGuagePV

class LaserEnergyMeter(PhysicalElement):
    laser: LaserEnergyMeterElement
    controls: LaserEnergyMeterPV

class LaserHalfWavePlate(LaserEnergyMeter):
    laser: LaserElement
    controls: LaserHWPPV

class LaserMirror(LaserEnergyMeter):
    laser: LaserMirrorElement
    controls: LaserMirrorPV

class Lighting(_baseElement):
    lights: LightingElement
    controls: LightingPV

class PID(_baseElement):
    PID: PIDElement
    controls: PIDPV

class LLRF(_baseElement):
    LLRF: LLRFElement
    controls: LLRFPV

class RFModulator(_baseElement):
    modulator: RFModulatorElement
    controls: RFModulatorPV

class RFProtection(_baseElement):
    modulator: RFProtectionElement
    controls: RFProtectionPV

class RFHeartbeat(_baseElement):
    heartbeat: RFHeartbeatElement
    controls: RFHeartbeatPV

class Shutter(PhysicalElement):
    shutter: ShutterElement
    controls: ShutterPV

class Valve(PhysicalElement):
    valve: ValveElement
    controls: ValvePV
