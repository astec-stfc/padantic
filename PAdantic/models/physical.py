from pydantic import field_validator, confloat, Field, NonNegativeFloat
from typing import List

from ._functions import _rotation_matrix

from .baseModels import IgnoreExtra, NumpyVectorModel

class Position(NumpyVectorModel):
    ''' Position model. '''
    x: confloat(ge=-1,le=1)  = 0.
    y: confloat(ge=-1,le=1)  = 0.
    z: confloat(ge=0,le=100) = 0.

class Rotation(NumpyVectorModel):
    ''' Rotation model. '''
    phi:    confloat(ge=0,le=6.29)   = 0.
    psi:    confloat(ge=0,le=6.29)   = 0.
    theta:  confloat(ge=0,le=6.29)   = 0.

class ElementError(IgnoreExtra):
    ''' Position/Rotation error model. '''
    position: Position = Position(x=0,y=0,z=0)
    rotation: Rotation = Rotation(theta=0, phi=0, psi=0)

    def __str__(self):
        if any([getattr(self, k) != 0 for k in self.model_fields.keys()]):
            return ' '.join([getattr(self, k).__repr__() for k in self.model_fields.keys() if getattr(self, k) != 0])
        else:
            return str(None)

    def __repr__(self):
        return self.__class__.__name__+'('+self.__str__()+')'

    def __eq__(self, other):
        if other == 0:
            return all([getattr(self, k) == 0 for k in self.model_fields.keys()])
        else:
            return super().__eq__(other)

class ElementSurvey(ElementError): ...

class PhysicalElement(IgnoreExtra):
    ''' Physical info model. '''
    middle: Position = Field(alias='position', default=0)
    rotation: Rotation = Rotation(theta=0, phi=0, psi=0)
    global_rotation: Rotation = Rotation(theta=0, phi=0, psi=0)
    error: ElementError = ElementError()
    survey: ElementSurvey = ElementSurvey()
    length: NonNegativeFloat = 0.

    def __str__(self):
        # print({k: getattr(self, k) != 0 for k in self.model_fields.keys()})
        if any([getattr(self, k) != 0 for k in self.model_fields.keys()]):
            return ' '.join([str(k)+'='+getattr(self, k).__repr__() for k in self.model_fields.keys() if getattr(self, k) != 0])
        else:
            return str()

    def __repr__(self):
        return self.__class__.__name__+'('+self.__str__()+')'

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
    def validate_rotation(cls, v: float|int|List) -> Rotation:
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
