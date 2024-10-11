import numpy as np
from pydantic import field_validator, confloat, Field, NonNegativeFloat, AliasChoices
from typing import List, Type, Union

from ._functions import _rotation_matrix

from .baseModels import IgnoreExtra, NumpyVectorModel, T


class Position(NumpyVectorModel):
    """Position model."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, other: Type[T]) -> T:
        return Position(
            x=(self.x + other.x), y=(self.y + other.y), z=(self.z + other.z)
        )

    def __radd__(self, other: Type[T]) -> T:
        return self.__add__(other)

    def __sub__(self, other: Type[T]) -> T:
        return Position(
            x=(self.x - other.x), y=(self.y - other.y), z=(self.z - other.z)
        )

    def __rsub__(self, other: Type[T]) -> T:
        return Position(
            x=(other.x - self.x), y=(other.y - self.y), z=(other.z - self.z)
        )

    def dot(self, other: Union[List, Type[T]]) -> float:
        if isinstance(other, (set, tuple, list)):
            other = Position.from_list(other)
        return self.x * other.x + self.y * other.y + self.z * other.z

    def vector_angle(self, other: Union[List, Type[T]], direction: List) -> float:
        if isinstance(other, (set, tuple, list)):
            other = Position.from_list(other)
        return (self - other).dot(direction)

    def length(self) -> float:
        return np.sqrt([self.x * self.x + self.y * self.y + self.z * self.z])


class Rotation(NumpyVectorModel):
    """Rotation model."""

    phi: confloat(ge=-3.14, le=3.14) = 0.0    # type: ignore
    psi: confloat(ge=-3.14, le=3.14) = 0.0    # type: ignore
    theta: confloat(ge=-3.14, le=3.14) = 0.0  # type: ignore

    def __add__(self, other: Type[T]) -> T:
        return Rotation(
            phi=(self.phi + other.phi),
            psi=(self.psi + other.psi),
            theta=(self.theta + other.theta),
        )

    def __radd__(self, other: Type[T]) -> T:
        return self.__add__(other)

    def __sub__(self, other: Type[T]) -> T:
        return Rotation(
            phi=(self.phi - other.phi),
            psi=(self.psi - other.psi),
            theta=(self.theta - other.theta),
        )

    def __rsub__(self, other: Type[T]) -> T:
        return Rotation(
            phi=(other.phi - self.phi),
            psi=(other.psi - self.psi),
            theta=(other.theta - self.theta),
        )

    def __abs__(self):
        return Rotation(phi=abs(self.phi), psi=abs(self.psi), theta=abs(self.theta))

    def __gt__(self, value: Union[int, float, List, Type[T]]):
        if isinstance(value, (int, float)):
            return any([self.phi > value, self.psi > value, self.theta > value])
        elif isinstance(value, (Union[list, set, tuple])):
            return [self.phi, self.psi, self.theta] > value
        elif isinstance(value, Rotation):
            return any(
                [self.phi > value.phi, self.psi > value.psi, self.theta > value.theta]
            )


class ElementError(IgnoreExtra):
    """Position/Rotation error model."""

    position: Union[Position, List[Union[float, int]]] = Position(x=0, y=0, z=0)
    rotation: Union[Rotation, List[Union[float, int]]] = Rotation(theta=0, phi=0, psi=0)

    @field_validator("position", mode="before")
    @classmethod
    def validate_position(cls, v: Union[Position, List]) -> Position:
        if isinstance(v, (list, tuple)) and len(v) == 3:
            return Position(x=v[0], y=v[1], z=v[2])
        else:
            raise ValueError("position should be a number or a list of floats")

    @field_validator("rotation", mode="before")
    @classmethod
    def validate_rotation(cls, v: Union[Rotation, List]) -> Position:
        if isinstance(v, (list, tuple)) and len(v) == 3:
            return Rotation(theta=v[0], phi=v[1], psi=v[2])
        else:
            raise ValueError("rotation should be a number or a list of floats")

    def __str__(self):
        if any([getattr(self, k) != 0 for k in self.model_fields.keys()]):
            return " ".join(
                [
                    getattr(self, k).__repr__()
                    for k in self.model_fields.keys()
                    if getattr(self, k) != 0
                ]
            )
        else:
            return str(None)

    def __repr__(self):
        return self.__class__.__name__ + "(" + self.__str__() + ")"

    def __eq__(self, other):
        if other == 0:
            return all([getattr(self, k) == 0 for k in self.model_fields.keys()])
        else:
            return super().__eq__(other)


class ElementSurvey(ElementError):
    ...


class PhysicalElement(IgnoreExtra):
    """Physical info model."""

    middle: Position = Field(
        alias=AliasChoices("position", "centre"), default=Position()
    )
    datum: Position = Field(default=0)
    rotation: Rotation = Rotation(theta=0, phi=0, psi=0)
    global_rotation: Rotation = Rotation(theta=0, phi=0, psi=0)
    error: ElementError = ElementError()
    survey: ElementSurvey = ElementSurvey()
    length: NonNegativeFloat = 0.0

    def __str__(self):
        # print({k: getattr(self, k) != 0 for k in self.model_fields.keys()})
        if any([getattr(self, k) != 0 for k in self.model_fields.keys()]):
            return " ".join(
                [
                    str(k) + "=" + getattr(self, k).__repr__()
                    for k in self.model_fields.keys()
                    if getattr(self, k) != 0
                ]
            )
        else:
            return str()

    def __repr__(self):
        return self.__class__.__name__ + "(" + self.__str__() + ")"

    # def __add__(self, other: PhysicalElement) -> [Position, Rotation]:
    #     pass
    #
    # def __radd__(self, other: PhysicalElement) ->  -> [Position, Rotation]:
    #     pass
    #
    # def __sub__ (self, other: PhysicalElement) ->  -> [Position, Rotation]:
    #     pass

    @field_validator("middle", "datum", mode="before")
    @classmethod
    def validate_middle(cls, v: Union[float, int, List]) -> Position:
        if isinstance(v, (float, int)):
            return Position(z=v)
        elif isinstance(v, (list, tuple)):
            if len(v) == 3:
                return Position(x=v[0], y=v[1], z=v[2])
            elif len(v) == 2:
                return Position(x=v[0], y=0, z=v[1])
        elif isinstance(v, (Position)):
            return v
        else:
            raise ValueError("middle should be a number or a list of floats")

    @field_validator("rotation", "global_rotation", mode="before")
    @classmethod
    def validate_rotation(cls, v: Union[float, int, List]) -> Rotation:
        if isinstance(v, (float, int)):
            return Rotation(theta=v)
        elif isinstance(v, (list, tuple)):
            if len(v) == 3:
                return Rotation(phi=v[0], psi=v[1], theta=v[2])
        elif isinstance(v, (Rotation)):
            return v
        else:
            raise ValueError("middle should be a number or a list of floats")

    @property
    def rotation_matrix(self) -> List[Union[int, float]]:
        return _rotation_matrix(self.rotation.theta + self.global_rotation.theta)

    def rotated_position(
        self, vec: List[Union[int, float]] = [0, 0, 0]
    ) -> List[Union[int, float]]:
        return np.dot(np.array(vec), self.rotation_matrix)

    @property
    def start(self) -> Position:
        middle = np.array(self.middle.array)
        sx = 0
        sy = 0
        sz = (
            1.0 * self.length * np.tan(0.5 * self.angle) / self.angle
            if hasattr(self, "angle") and abs(self.angle) > 1e-9
            else 1.0 * self.length / 2.0
        )
        vec = [sx, sy, sz]
        start = middle - self.rotated_position(vec)
        return Position.from_list(start)

    @property
    def end(self) -> Position:
        ex = (
            (self.length * (1 - np.cos(self.angle))) / self.angle
            if hasattr(self, "angle") and abs(self.angle) > 1e-9
            else 0
        )
        ey = 0
        ez = (
            (self.length * (np.sin(self.angle))) / self.angle
            if hasattr(self, "angle") and abs(self.angle) > 1e-9
            else self.length
        )
        vec = [ex, ey, ez]
        end = self.start.array + self.rotated_position(vec)
        return Position.from_list(end)
