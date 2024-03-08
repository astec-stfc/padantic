from pydantic import BaseModel, model_serializer, Field, field_validator, NonNegativeInt, create_model, NonNegativeFloat
from typing import Dict, Any, List

from .baseModels import IgnoreExtra

class Multipole(BaseModel):
    ''' Single order magnetic multipole model. '''
    order: NonNegativeInt = 0
    normal: float = 0.
    skew: float = 0.
    radius: float = 0.

multipoles = {'K'+str(l)+'L': (Multipole, Field(default=Multipole(order=l), repr=False)) for l in range(0,13)}
MultipolesData = create_model('Multipoles', **multipoles)

class Multipoles(MultipolesData):
    ''' Magnetic multipoles model. '''

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
    ''' Field integral coefficients model. '''
    coefficients: List[float] = [0]

    def currentToK(self, current: float, energy: float) -> float:
        sign = numpy.copysign(1, current)
        ficmod = [i * int(sign) for i in field_integral_coefficients[:-1]]
        coeffs = np.append(ficmod, self.coefficients[-1])
        int_strength = numpy.polyval(coeffs, abs(current))
        effect = (constants.speed_of_light / 1e6) * int_strength / energy
        return effect

    def __iter__(self) -> iter:
        return iter(self.coefficients)

class MagneticElement(IgnoreExtra):
    ''' Magnetic info model. '''
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

class Dipole_Magnet(MagneticElement):
    ''' Sextupole magnet with magnetic order 0. '''
    order: int = Field(repr=False, default=0, frozen=True)

class Quadrupole_Magnet(MagneticElement):
    ''' Sextupole magnet with magnetic order 1. '''
    order: int = Field(repr=False, default=1, frozen=True)

class Sextupole_Magnet(MagneticElement):
    ''' Sextupole magnet with magnetic order 2. '''
    order: int = Field(repr=False, default=2, frozen=True)
