from pydantic import BaseModel, NonNegativeFloat, model_serializer, ConfigDict, NonNegativeInt, Field, create_model, field_validator, confloat, ValidationInfo
from typing import List, Optional, Any
from annotated_types import Ge
import numpy as np
from _functions import _rotation_matrix
from typing import TypeVar, Type


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

class Position(NumpyModel):
    x: confloat(ge=-1,le=1) = 0.
    y: confloat(ge=-1,le=1) = 0.
    z: confloat(ge=0,le=100) = 0.

class Rotation(NumpyModel):
    phi:    confloat(ge=0,le=6.29)   = 0.
    psi:    confloat(ge=0,le=6.29)  = 0.
    theta:  confloat(ge=0,le=6.29)   = 0.

class ElementError(BaseModel):
    position_error: Position = Position(x=0,y=0,z=0)
    rotation_error: Rotation = Rotation(theta=0, phi=0, psi=0)
    survey_position: Position = Position(x=0,y=0,z=0)
    survey_rotation: Rotation = Rotation(theta=0, phi=0, psi=0)

class PhysicalElement(BaseModel):
    middle: Position
    rotation: Rotation = Rotation(theta=0, phi=0, psi=0)
    global_rotation: Rotation = Rotation(theta=0, phi=0, psi=0)
    position_error: ElementError = ElementError()
    length: NonNegativeFloat = 0.

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

    # @debug
    def normal(self, order: int) -> int|float:
        return getattr(self, 'K'+str(order)+'L').normal

    def skew(self, order: int) -> int|float:
        return getattr(self, 'K'+str(order)+'L').skew

class FieldIntegral(BaseModel):
    coefficients: List[float] = [0]

    def currentToK(self, current: float, energy: float) -> float:
        sign = numpy.copysign(1, current)
        ficmod = [i * int(sign) for i in field_integral_coefficients[:-1]]
        coeffs = np.append(ficmod, self.coefficients[-1])
        int_strength = numpy.polyval(coeffs, abs(current))
        effect = (constants.speed_of_light / 1e6) * int_strength / energy
        return effect

class MagneticElement(PhysicalElement):
    order: int = Field(repr=False, default=-1, frozen=True)
    skew: bool = False
    magnetic_length: NonNegativeFloat = 0.
    multipoles: Multipoles = Multipoles()
    systematic_multipoles: Multipoles = Multipoles()
    random_multipoles: Multipoles = Multipoles()
    field_integral_coefficients: FieldIntegral = FieldIntegral()

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        self.kl = data['kl'] if 'kl' in data else None
        if self.skew:
            setattr(self.multipoles, 'K'+str(self.order)+'L', Multipole(skew=self.kl, order=self.order))
        else:
            setattr(self.multipoles, 'K'+str(self.order)+'L', Multipole(normal=self.kl, order=self.order))

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

class DegaussablElement(MagneticElement):
    degauss_tolerance: float = 0.5
    degauss_values: List[float] = []
    num_degauss_steps: int = 11

class Dipole_Magnet(DegaussablElement):
    order: int = Field(repr=False, default=0, frozen=True)

class Quadrupole_Magnet(DegaussablElement):
    order: int = Field(repr=False, default=1, frozen=True)

class Sextupole_Magnet(DegaussablElement):
    order: int = Field(repr=False, default=2, frozen=True)

class ElectricalElement(BaseModel):
    settle_time: float = 45.0
    minI: float = -0
    maxI: float = 0
    read_tolerance: float = 0.1

machineOptions = map(str.upper, ['CLA'])
areaOptions = map(str.upper, ['S01','S02','S03','S04','S05','S06','S07','L01','L02','L03','L04','L4H','SP2','SP3','FEA','FEH','FED'])
classtypeOptions = {
'MAG': ['QUAD', 'DIP', 'HVCOR', 'SEXT'],
'DIA': ['SCR', 'BPM', 'ICT', 'BAM'],
'PS': ['SHTR'],
'VAC': ['APER'],
'SIM': ['MARK']
}
classrecordOptions = {
'MAG': ['RILK', 'SETI', 'GETSETI', 'READI', 'SPOWER', 'RPOWER', 'K_DIP_P', 'INT_STR_MM', 'INT_STR', 'K_SET_P', 'K_ANG', 'K_MRAD', 'K_VAL']
}

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
    record: str = ''

    @field_validator('machine', mode='before')
    @classmethod
    def validate_machine(cls, v: str) -> str:
        if v.upper() not in machineOptions:
            raise ValueError('Invalid Machine')
        return v.upper()

    @field_validator('area', mode='before')
    @classmethod
    def validate_area(cls, v: str) -> str:
        if v.upper() not in areaOptions:
            raise ValueError('Invalid Area')
        return v.upper()

    @field_validator('classname', mode='before')
    @classmethod
    def validate_class(cls, v: str) -> str:
        if v.upper() not in classtypeOptions.keys():
            raise ValueError('Invalid Class Name')
        return v.upper()

    @field_validator('typename', mode='before')
    @classmethod
    def validate_type(cls, v: str, info: ValidationInfo) -> str:
        classname = info.data['classname']
        if v.upper() not in classtypeOptions[classname]:
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
        if v.upper() not in classrecordOptions[classname]:
            raise ValueError('Invalid Record Name')
        return v.upper()

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

class MagnetPV(BaseModel):
    GETSETI:    PV()
    READI:      PV()
    RILK:       PV()
    RPOWER:     PV()
    SETI:       PV()
    SPOWER:     PV()
    ILK_RESET:  PV()
    K_DIP_P:    PV()
    INT_STR_MM: PV()
    INT_STR:    PV()
    K_SET_P:    PV()
    K_ANG:      PV()
    K_MRAD:     PV()
    K_VAL:      PV()

if __name__ == "__main__":
    pos = Dipole_Magnet(middle=Position(z=1.2), kl=np.pi/6, length=0.3, global_rotation=Rotation(theta=0*np.pi/6))
    # print(pos.multipoles)
    print(pos.angle)
    print(pos.middle)
    print(pos.start)
    print(pos.end)
    print(PV.fromString('CLA-S02-MAG-QUAD-01:GETSETI').basename)
    # print(pos.KnL(1))
    # pos.kl = 5
    # pos.multipoles.K2L.skew = 2.
    # print(pos.multipoles)
