from pydantic import BaseModel, NonNegativeFloat, model_serializer, ConfigDict, NonNegativeInt, Field, create_model, field_validator, confloat, ValidationInfo
from typing import List, Optional, Any, Dict
from annotated_types import Ge
import numpy as np
from _functions import _rotation_matrix
from typing import TypeVar, Type
import yaml

import logging
import importlib
importlib.reload(logging)

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG, datefmt='%I:%M:%S')

def debug(fn):
    def wrapper(*args, **kwargs):
        logging.debug(f"Invoking {fn.__name__}")
        logging.debug(f"  args: {args}")
        logging.debug(f"  kwargs: {kwargs}")
        result = fn(*args, **kwargs)
        logging.debug(f"  returned {result}")
        return result
    return wrapper

# Create a generic variable that can be 'Parent', or any subclass.
T = TypeVar('T', bound='BaseModel')

# Load PV definitions
with open('PV_Values.yaml','r') as stream:
    data = yaml.load(stream, Loader=yaml.Loader)
    for k,v in data.items():
        globals()[k] = v

class IgnoreExtra(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="ignore",
    )

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        # print(self.__class__.__name__, [getattr(self,k) for k in self.model_fields.keys()])
        return {k: getattr(self,k) for k in self.model_fields.keys() if getattr(self,k) != 0 and getattr(self,k) is not None and getattr(self,k) != {}}

class NumpyModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_serializer
    def ser_model(self) -> np.ndarray:
        return self.array

    @property
    def array(self) -> np.ndarray:
        return np.array([getattr(self, a) for a in self.model_fields.keys()])

    @classmethod
    def from_list(cls: Type[T], vec: List[float | int]) -> T:
        assert len(vec) == len(cls.model_fields)
        return cls(**dict(zip(list(cls.model_fields.keys()), vec)))

    @classmethod
    def from_values(cls: Type[T], *values: float | int) -> T:
        assert len(values) == len(cls.model_fields)
        return cls(**dict(zip(list(cls.model_fields.keys()), values)))

class NumpyVectorModel(NumpyModel):

    def __iter__(self):
        return iter([getattr(self, k) for k in self.model_fields.keys()])

    def __eq__(self, other: Any) -> bool:
        if other == 0 or other == 0. or other == None:
            if all([getattr(self, k) == 0 for k in self.model_fields.keys()]):
                return True
            return False
        return list(self) == list(other)

    def __neq__(self, other: Any) -> bool:
        # print('__neq__ called', other)
        if other == 0 or other == 0. or other == None:
            if all([getattr(self, k) == 0 for k in self.model_fields.keys()]):
                return False
            return True
        return list(self) != list(other)

class Position(NumpyVectorModel):
    x: confloat(ge=-1,le=1)  = 0.
    y: confloat(ge=-1,le=1)  = 0.
    z: confloat(ge=0,le=100) = 0.

class Rotation(NumpyVectorModel):
    phi:    confloat(ge=0,le=6.29)   = 0.
    psi:    confloat(ge=0,le=6.29)   = 0.
    theta:  confloat(ge=0,le=6.29)   = 0.

class ElementError(IgnoreExtra):
    position_error: Position = Position(x=0,y=0,z=0)
    rotation_error: Rotation = Rotation(theta=0, phi=0, psi=0)
    survey_position: Position = Position(x=0,y=0,z=0)
    survey_rotation: Rotation = Rotation(theta=0, phi=0, psi=0)

class PhysicalElement(IgnoreExtra):
    middle: Position = Field(alias='position')
    rotation: Rotation = Rotation(theta=0, phi=0, psi=0)
    global_rotation: Rotation = Rotation(theta=0, phi=0, psi=0)
    error: ElementError = ElementError()
    length: NonNegativeFloat = 0.

    @field_validator('middle', mode='before')
    @classmethod
    def validate_middle(cls, v: float|int|List) -> Position:
        if isinstance(v, (float, int)):
            return Position(z=v)
        elif isinstance(v, (list, tuple)):
            if len(v) == 3:
                return Position(x=v[0], y=v[1], z=v[2])
            elif len(v) == 2:
                return Position(x=v[0], y=0, z=v[1])
        else:
            raise ValueError('middle should be a number or a list of floats')

    @field_validator('rotation', 'global_rotation', mode='before')
    @classmethod
    def validate_rotation(cls, v: float|int|List) -> Position:
        if isinstance(v, (float, int)):
            return Rotation(theta=v)
        elif isinstance(v, (list, tuple)):
            if len(v) == 3:
                return Rotation(phi=v[0], psi=v[1], theta=v[2])
        else:
            raise ValueError('middle should be a number or a list of floats')


    @property
    def rotation_matrix(self) -> List[int|float]:
        return _rotation_matrix(self.rotation.theta + self.global_rotation.theta)

    def rotated_position(self, vec: List[int|float] = [0,0,0]) -> List[int|float]:
        return np.dot(np.array(vec), self.rotation_matrix)

    @property
    def start(self) -> List[int|float]:
        middle = np.array(self.middle.array)
        sx = 0
        sy = 0
        sz = 1.0*self.length * np.tan(0.5 * self.angle) / self.angle if hasattr(self, 'angle') and abs(self.angle) > 1e-9 else 1.0*self.length / 2.0
        vec = [sx, sy, sz]
        start = middle - self.rotated_position(vec)
        return Position.from_list(start)

    @property
    def end(self) -> List[int|float]:
        ex = (self.length * (1 - np.cos(self.angle))) / self.angle if hasattr(self, 'angle') and abs(self.angle) > 1e-9 else 0
        ey = 0
        ez = (self.length * (np.sin(self.angle))) / self.angle if hasattr(self, 'angle') and abs(self.angle) > 1e-9 else self.length
        vec = [ex, ey, ez]
        end = self.start.array + self.rotated_position(vec)
        return Position.from_list(end)

class Multipole(BaseModel):
    order: NonNegativeInt = 0
    normal: float = 0.
    skew: float = 0.
    radius: float = 0.

multipoles = {'K'+str(l)+'L': (Multipole, Field(default=Multipole(order=l), repr=False)) for l in range(0,13)}
MultipolesData = create_model('Multipoles', **multipoles)

class Multipoles(MultipolesData):

    def __str__(self):
        return ' '.join(['K'+str(i)+'L=Multipole('+getattr(self, 'K'+str(i)+'L').__str__()+')' for i in range(13) if abs(getattr(self, 'K'+str(i)+'L').normal) > 0 or abs(getattr(self, 'K'+str(i)+'L').skew) > 0])

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        return {k: getattr(self,k) for k in self.model_fields.keys() if abs(getattr(self, k).normal) > 0 or abs(getattr(self, k).skew) > 0}

    def normal(self, order: int) -> int|float:
        return getattr(self, 'K'+str(order)+'L').normal

    def skew(self, order: int) -> int|float:
        return getattr(self, 'K'+str(order)+'L').skew

    def __eq__(self, other) -> bool:
        return self.ser_model() == other

    def __neq__(self) -> bool:
        return not self.__eq__(other)

class FieldIntegral(BaseModel):
    coefficients: List[float] = [0]

    def currentToK(self, current: float, energy: float) -> float:
        sign = numpy.copysign(1, current)
        ficmod = [i * int(sign) for i in field_integral_coefficients[:-1]]
        coeffs = np.append(ficmod, self.coefficients[-1])
        int_strength = numpy.polyval(coeffs, abs(current))
        effect = (constants.speed_of_light / 1e6) * int_strength / energy
        return effect

    def __iter__(self):
        return iter(self.coefficients)

class MagneticElement(IgnoreExtra):
    order: int = Field(repr=False, default=-1, frozen=True)
    skew: bool = False
    length: NonNegativeFloat = 0.
    multipoles: Multipoles = Multipoles()
    systematic_multipoles: Multipoles = Multipoles()
    random_multipoles: Multipoles = Multipoles()
    field_integral_coefficients: FieldIntegral = FieldIntegral()

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        self.kl = data['kl'] if 'kl' in data else 0
        if self.skew:
            setattr(self.multipoles, 'K'+str(self.order)+'L', Multipole(skew=self.kl, order=self.order))
        else:
            setattr(self.multipoles, 'K'+str(self.order)+'L', Multipole(normal=self.kl, order=self.order))

    @field_validator('field_integral_coefficients', mode='before')
    @classmethod
    def validate_field_integral_coefficients(cls, v: str|List) -> FieldIntegral:
        if isinstance(v, str):
            return FieldIntegral(coefficients=list(map(float, v.split(','))))
        elif isinstance(v, (list, tuple)):
            return FieldIntegral(coefficients=list(v))
        else:
            raise ValueError('field_integral_coefficients should be a string or a list of floats')


    # @debug
    def KnL(self, order: int = None) -> int|float:
        f = self.multipoles.skew if self.skew else self.multipoles.normal
        order = self.order if order is None else order
        return f(order) if order >= 0 else 0

    def Kn(self, order: int = None) -> int|float:
        return self.knl(order) / self.length

    @property
    def kl(self) -> int|float:
        return self.KnL(self.order)
    @kl.setter
    def kl(self, kl: float = 0) -> None:
        setattr(self.multipoles, 'K'+str(self.order)+'L', Multipole(normal=kl, order=self.order))

    @property
    def angle(self) -> float:
        return self.KnL(order=0)

class DegaussablElement(IgnoreExtra):
    degauss_tolerance: float = Field(default=0.5)
    degauss_values: List[float] = Field(default=[])
    degauss_steps: int = Field(alias='num_degauss_steps', default=11)

    @field_validator('degauss_values', mode='before')
    @classmethod
    def validate_degauss_values(cls, v: str|List) -> str:
        if isinstance(v, str):
            return list(map(float, v.split(',')))
        elif isinstance(v, (list, tuple)):
            return list(v)
        else:
            raise ValueError('degauss_values should be a string or a list of floats')

class ElectricalElement(IgnoreExtra):
    settle_time:    float = Field(alias='mag_set_max_wait_time', default=45.0)
    minI:           float = Field(alias='min_i', default=0)
    maxI:           float = Field(alias='max_i', default=0)
    read_tolerance: float = Field(alias='ri_tolerance', default=0.1)

class ManufacturerElement(IgnoreExtra):
    manufacturer: str
    serial_number: str
    hardware_type: str

class PVSet(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=True,
    )
    ...

class PV(PVSet):
    machine: str
    area: str
    classname: str
    typename: str
    index: int | str
    record: str

    @field_validator('machine', mode='before')
    @classmethod
    def validate_machine(cls, v: str) -> str:
        if v.upper() not in map(str.upper, machineNames):
            raise ValueError('Invalid Machine', v.upper())
        return v.upper()

    @field_validator('area', mode='before')
    @classmethod
    def validate_area(cls, v: str) -> str:
        if v.upper() not in map(str.upper, areaNames):
            raise ValueError('Invalid Area')
        return v.upper()

    @field_validator('classname', mode='before')
    @classmethod
    def validate_class(cls, v: str) -> str:
        if v.upper() not in map(str.upper, classtypeNames.keys()):
            raise ValueError('Invalid Class Name')
        return v.upper()

    @field_validator('typename', mode='before')
    @classmethod
    def validate_type(cls, v: str, info: ValidationInfo) -> str:
        classname = info.data['classname']
        if v.upper() not in map(str.upper, classtypeNames[classname]):
            raise ValueError('Invalid Type Name')
        return v.upper()

    @field_validator('index', mode='before')
    @classmethod
    def validate_index(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError('Invalid Type Name')
        return int(v)

    @field_validator('record', mode='before')
    @classmethod
    def validate_record(cls, v: str, info: ValidationInfo) -> str:
        classname = info.data['classname']
        if v.upper() not in map(str.upper, classrecordNames[classname]):
            raise ValueError('Invalid Record Name')
        return v

    @classmethod
    def fromString(cls, pv: str) -> T:
        assert ':' in pv
        prefix, postfix = pv.split(':')
        substr = prefix.split('-')
        assert len(substr) == 5
        return cls.model_validate({'machine': substr[0], 'area': substr[1], 'classname': substr[2],
                             'typename': substr[3], 'index': substr[4], 'record': postfix})

    @property
    def _indexString(self):
        return str(self.index).zfill(2)

    @property
    def basename(self):
        name = '-'.join([getattr(self, a) for a in ['machine', 'area', 'classname', 'typename']]) + '-' + self._indexString
        return name

    @property
    def name(self):
        name = self.basename + ':' + self.record
        return name

    def __str__(self):
        return self.name

    def __int__(self):
        return self.index

    @model_serializer
    def ser_model(self) -> str:
        return self.__str__()

class MagnetPV(BaseModel):
    GETSETI:    PV | None = None
    READI:      PV | None = None
    RILK:       PV | None = None
    RPOWER:     PV | None = None
    SETI:       PV | None = None
    SPOWER:     PV | None = None
    ILK_RESET:  PV | None = None
    K_DIP_P:    PV | None = None
    INT_STR_MM: PV | None = None
    INT_STR:    PV | None = None
    K_SET_P:    PV | None = None
    K_ANG:      PV | None = None
    K_MRAD:     PV | None = None
    K_VAL:      PV | None = None

    def __str__(self):
        return 'MagnetPV(' + ', '.join([k + '=PV(\''+getattr(self, k).__str__()+'\')' for k in self.model_fields.keys() if getattr(self, k) is not None])

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        return {k: getattr(self,k) for k in self.model_fields.keys() if getattr(self,k) is not None}

class Dipole_Magnet(MagneticElement):
    order: int = Field(repr=False, default=0, frozen=True)

class Quadrupole_Magnet(MagneticElement):
    order: int = Field(repr=False, default=1, frozen=True)

class Sextupole_Magnet(MagneticElement):
    order: int = Field(repr=False, default=2, frozen=True)

class Element(BaseModel):
    physical:   PhysicalElement
    degauss :   DegaussablElement
    electrical: ElectricalElement
    manufacturer: ManufacturerElement
    controls: MagnetPV

class Dipole(Element):
    magnetic: Dipole_Magnet

class Quadrupole(Element):
    magnetic: Quadrupole_Magnet

class Sextupole(Element):
    magnetic: Sextupole_Magnet

def readYAML(filename):
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
