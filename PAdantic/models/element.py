from pydantic import BaseModel, NonNegativeFloat, model_serializer, ConfigDict, NonNegativeInt, Field, create_model, field_validator, confloat, ValidationInfo
from typing import List, Optional, Any, Dict
from annotated_types import Ge
from _functions import _rotation_matrix
from typing import TypeVar, Type
import yaml

from models.PV import magnetTypes, PV, MagnetPV
from models.manufacturer import ManufacturerElement
from models.electrical import ElectricalElement
from models.magnetic import Dipole_Magnet, Quadrupole_Magnet, Sextupole_Magnet
from models.degauss import DegaussablElement
from models.physical import PhysicalElement

class Element(BaseModel):
    ''' Element with physical, degaussable, electrical, manufacturer, and controls items. '''
    physical:   PhysicalElement
    degauss :   DegaussablElement
    electrical: ElectricalElement
    manufacturer: ManufacturerElement
    controls: MagnetPV

class Dipole(Element):
    ''' Dipole element. '''
    magnetic: Dipole_Magnet

class Quadrupole(Element):
    ''' Quadrupole element. '''
    magnetic: Quadrupole_Magnet

class Sextupole(Element):
    ''' Sextupole element. '''
    magnetic: Sextupole_Magnet
