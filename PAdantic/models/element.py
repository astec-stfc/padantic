from typing import Type, List
from pydantic import BaseModel, field_validator, Field

from models.baseModels import T, Aliases
from models.PV import (MagnetPV, BPMPV, CameraPV, ScreenPV, ChargeDiagnosticPV, VacuumGuagePV, LaserEnergyMeterPV, LaserHWPPV,
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

class _baseElement(BaseModel):
    name: str
    hardware_type: str
    machine_area: str
    virtual_name: str = ''
    alias: str|list|Aliases = Field(alias='name_alias', default=None)

    @classmethod
    def from_CATAP(cls: Type[T], fields: dict) -> T:
        return cls(**fields)

    @property
    def no_controls(self):
        return self.__class__.__name__+'('+' '.join([k+'='+getattr(self, k).__repr__() for k in self.model_fields.keys() if k != 'controls'])+')'

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

class Element(_baseElement):
    ''' Element with physical, degaussable, electrical, manufacturer, and controls items. '''
    physical:   PhysicalElement
    electrical: ElectricalElement
    manufacturer: ManufacturerElement

class Magnet(Element):
    controls: MagnetPV
    degauss : DegaussablElement

class Dipole(Magnet):
    ''' Dipole element. '''
    magnetic: Dipole_Magnet

class Quadrupole(Magnet):
    ''' Quadrupole element. '''
    magnetic: Quadrupole_Magnet

class Sextupole(Magnet):
    ''' Sextupole element. '''
    magnetic: Sextupole_Magnet

class Horizontal_Corrector(Dipole): ...
class Vertical_Corrector(Dipole): ...
class Solenoid(Magnet):
    magnetic: Solenoid_Magnet


class BPM(Element):
    diagnostic: BPM_Diagnostic
    controls: BPMPV

class Camera(_baseElement):
    diagnostic: Camera_Diagnostic
    controls: CameraPV

class Screen(_baseElement):
    physical:   PhysicalElement
    diagnostic: Screen_Diagnostic
    controls: ScreenPV

class ChargeDiagnostic(_baseElement):
    physical:   PhysicalElement
    diagnostic: Charge_Diagnostic
    controls: ChargeDiagnosticPV

class VacuumGuage(_baseElement):
    physical:   PhysicalElement
    manufacturer: ManufacturerElement
    controls: VacuumGuagePV

class LaserEnergyMeter(_baseElement):
    physical:   PhysicalElement
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

class Shutter(_baseElement):
    shutter: ShutterElement
    controls: ShutterPV

class Valve(_baseElement):
    valve: ValveElement
    controls: ValvePV
