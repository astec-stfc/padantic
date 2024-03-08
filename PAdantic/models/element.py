from pydantic import BaseModel

from models.PV import MagnetPV, BPMPV, CameraPV
from models.manufacturer import ManufacturerElement
from models.electrical import ElectricalElement
from models.degauss import DegaussablElement
from models.physical import PhysicalElement
from models.magnetic import Dipole_Magnet, Quadrupole_Magnet, Sextupole_Magnet
from models.diagnostic import BPM_Diagnostic, Camera_Diagnostic

class Element(BaseModel):
    ''' Element with physical, degaussable, electrical, manufacturer, and controls items. '''
    physical:   PhysicalElement
    electrical: ElectricalElement
    manufacturer: ManufacturerElement

class Dipole(Element):
    ''' Dipole element. '''
    magnetic: Dipole_Magnet
    controls: MagnetPV
    degauss :   DegaussablElement

class Quadrupole(Element):
    ''' Quadrupole element. '''
    magnetic: Quadrupole_Magnet
    controls: MagnetPV
    degauss :   DegaussablElement

class Sextupole(Element):
    ''' Sextupole element. '''
    magnetic: Sextupole_Magnet
    controls: MagnetPV
    degauss :   DegaussablElement

class BPM(Element):
    diagnostic: BPM_Diagnostic
    controls: BPMPV

class Camera(BaseModel):
    diagnostic: Camera_Diagnostic
    controls: CameraPV
