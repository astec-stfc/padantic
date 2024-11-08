import numpy as np
from scipy.constants import speed_of_light
from pydantic import (
    BaseModel,
    model_serializer,
    Field,
    field_validator,
    NonNegativeInt,
    create_model,
    NonNegativeFloat,
)
from typing import Dict, Any, List, Union
import numpy as np
from scipy import constants
from .baseModels import IgnoreExtra, T


class Multipole(BaseModel):
    """Single order magnetic multipole model."""

    order: NonNegativeInt = 0
    normal: float = 0.0
    skew: float = 0.0
    radius: float = 0.0


multipoles = {
    "K" + str(no) + "L": (Multipole, Field(default=Multipole(order=no), repr=False))
    for no in range(0, 13)
}
MultipolesData = create_model("Multipoles", **multipoles)


class Multipoles(MultipolesData):
    """Magnetic multipoles model."""

    @field_validator("*", mode="before")
    def validate_Multipole(cls, v: Union[List, dict]) -> Multipole:
        if isinstance(v, (list, tuple)):
            if len(v) == 2:
                return Multipole(order=v[0], normal=v[1])
            elif len(v) == 4:
                return Multipole(order=v[0], normal=v[1], skew=v[2], radius=v[3])
        elif isinstance(v, (dict)):
            return Multipole(**v)
        elif isinstance(v, (Multipole)):
            return v
        else:
            raise ValueError("Multipole should be a dict or a list of floats")

    def __str__(self):
        return " ".join(
            [
                "K"
                + str(i)
                + "L=Multipole("
                + getattr(self, "K" + str(i) + "L").__str__()
                + ")"
                for i in range(0, 13)
                if abs(getattr(self, "K" + str(i) + "L").normal) > 0
                or abs(getattr(self, "K" + str(i) + "L").skew) > 0
            ]
        )

    def __repr__(self):
        return "Multipoles(" + self.__str__() + ")"

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        return {
            k: getattr(self, k)
            for k in self.model_fields.keys()
            if abs(getattr(self, k).normal) > 0 or abs(getattr(self, k).skew) > 0
        }

    def normal(self, order: int) -> Union[int, float]:
        return getattr(self, "K" + str(order) + "L").normal

    def skew(self, order: int) -> Union[int, float]:
        return getattr(self, "K" + str(order) + "L").skew

    def __eq__(self, other) -> bool:
        return self.ser_model() == other

    def __neq__(self, other) -> bool:
        return not self.__eq__(other)


class FieldIntegral(BaseModel):
    """Field integral coefficients model."""

    coefficients: List[Union[int, float]] = [0]

    def currentToK(self, current: float, energy: float) -> float:
        sign = np.copysign(1, current)
        ficmod = [i * int(sign) for i in self.coefficients[:-1]]
        coeffs = np.append(ficmod, self.coefficients[-1])
        int_strength = np.polyval(coeffs, abs(current))
        effect = (speed_of_light / 1e6) * int_strength / energy
        return effect

    def __iter__(self) -> iter:
        return iter(self.coefficients)


class LinearSaturationFit(BaseModel):
    """Linear + saturation fit coefficients model."""

    m: float = 0
    I_max: NonNegativeFloat = 0
    f: float = 0
    a: float = 0
    I0: float = 0
    d: float = 0
    L: NonNegativeFloat = 0

    @classmethod
    def from_string(cls, v: Union[str, List]) -> T:
        if isinstance(v, str):
            coeff_list = list(map(float, v.strip().split(",")))
            assert len(coeff_list) == len(cls.model_fields.keys())
            return cls(**{k: v for k, v in zip(cls.model_fields.keys(), coeff_list)})
        elif isinstance(v, (list, tuple)):
            assert len(v) == len(cls.model_fields.keys())
            return cls(**{k: v for k, v in zip(cls.model_fields.keys(), coeff_list)})
        else:
            raise ValueError(
                "LinearSaturationFit should be a string or a list of floats"
            )

    def update_from_string(self, v: Union[str, List]) -> None:
        if isinstance(v, str):
            coeff_list = list(map(float, v.strip().split(",")))
            assert len(coeff_list) == len(self.model_fields.keys())
            [setattr(self, k, v) for k, v in zip(self.model_fields.keys(), coeff_list)]
        elif isinstance(v, (list, tuple)):
            assert len(v) == len(self.model_fields.keys())
            [setattr(self, k, v) for k, v in zip(self.model_fields.keys(), v)]

    def currentToK(self, current: float, energy: float) -> float:
        abs_I = abs(current)
        m, I_max, f, a, I0, d, L = list(self.coefficients)
        int_strength = (
            m * current
            if abs_I < I_max
            else np.copysign((f * abs_I**3 + a * (abs_I - I0) ** 2 + d), current)
        )
        gradient = int_strength / L
        return gradient

    def __iter__(self) -> iter:
        return iter(
            [getattr(self, k) for k in ["m", "I_max", "f", "a", "I0", "d", "L"]]
        )


class MagneticElement(IgnoreExtra):
    """Magnetic info model."""

    order: int = Field(repr=False, default=-1, frozen=True)
    skew: bool = False
    length: NonNegativeFloat = Field(default=0.0, alias="magnetic_length")
    multipoles: Multipoles = Multipoles()
    systematic_multipoles: Multipoles = Multipoles()
    random_multipoles: Multipoles = Multipoles()
    field_integral_coefficients: FieldIntegral = FieldIntegral()
    linear_saturation_coefficients: LinearSaturationFit = LinearSaturationFit()
    settle_time: float = Field(alias="mag_set_max_wait_time", default=45.0)

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        if "kl" in data:
            self.kl = data["kl"]
        if "angle" in data and self.order == 0:
            self.kl = data["angle"]
        if self.skew:
            setattr(
                self.multipoles,
                "K" + str(self.order) + "L",
                Multipole(skew=self.kl, order=self.order),
            )
        else:
            setattr(
                self.multipoles,
                "K" + str(self.order) + "L",
                Multipole(normal=self.kl, order=self.order),
            )
        if "k1l" in data:
            # print('k1l', data['k1l'])
            setattr(
                self.multipoles,
                "K" + str(1) + "L",
                Multipole(normal=data["k1l"], order=1),
            )
        # print(self.multipoles)

    @field_validator("field_integral_coefficients", mode="before")
    @classmethod
    def validate_field_integral_coefficients(
        cls, v: Union[str, List, dict]
    ) -> FieldIntegral:
        if isinstance(v, str):
            return FieldIntegral(coefficients=list(map(float, v.split(","))))
        elif isinstance(v, (list, tuple)):
            return FieldIntegral(coefficients=list(v))
        elif isinstance(v, (dict)):
            return FieldIntegral(**v)
        elif isinstance(v, (FieldIntegral)):
            return v
        else:
            raise ValueError(
                "field_integral_coefficients should be a string or a list of floats"
            )

    # @debug
    def KnL(self, order: int = None) -> Union[int, float]:
        f = self.multipoles.skew if self.skew else self.multipoles.normal
        order = self.order if order is None else order
        return f(order) if order >= 0 else 0

    def Kn(self, order: int = None) -> Union[int, float]:
        return self.knl(order) / self.length

    @property
    def kl(self) -> Union[int, float]:
        return self.KnL(self.order)

    @kl.setter
    def kl(self, kl: float = 0) -> None:
        # print('kl called!', getattr(self.multipoles, 'K'+str(self.order)+'L'))
        setattr(getattr(self.multipoles, "K" + str(self.order) + "L"), "normal", kl)
        setattr(
            getattr(self.multipoles, "K" + str(self.order) + "L"), "order", self.order
        )

    @property
    def angle(self) -> float:
        return self.KnL(order=0)


class Dipole_Magnet(MagneticElement):
    """Dipole magnet with magnetic order 0."""

    order: int = Field(repr=False, default=0, frozen=True)


class Quadrupole_Magnet(MagneticElement):
    """Quadrupole with magnetic order 1."""

    order: int = Field(repr=False, default=1, frozen=True)


class Sextupole_Magnet(MagneticElement):
    """Sextupole magnet with magnetic order 2."""

    order: int = Field(repr=False, default=2, frozen=True)


solenoidFields = {
    "S" + str(no) + "L": (float, Field(default=0, repr=False)) for no in range(0, 13)
}
solenoidFieldsData = create_model("solenoidFieldsData", **solenoidFields)


class SolenoidFields(solenoidFieldsData):
    """Magnetic multipoles model."""

    def __str__(self):
        return " ".join(
            [
                "S" + str(i) + "L=" + getattr(self, "S" + str(i) + "L").__str__() + ""
                for i in range(13)
                if abs(getattr(self, "S" + str(i) + "L")) > 0
            ]
        )

    def __repr__(self):
        return "SolenoidFields(" + self.__str__() + ")"

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        return {
            k: getattr(self, k)
            for k in self.model_fields.keys()
            if abs(getattr(self, k)) > 0
        }

    def normal(self, order: int) -> Union[int, float]:
        return getattr(self, "S" + str(order) + "L")

    def __eq__(self, other: Any) -> bool:
        return self.ser_model() == other

    def __neq__(self, other: Any) -> bool:
        return not self.__eq__(other)


class Solenoid_Magnet(IgnoreExtra):
    """Solenoid magnet higher order fields."""

    length: NonNegativeFloat = Field(default=0.0, alias="magnetic_length")
    order: int = Field(repr=False, default=0, frozen=True)
    fields: SolenoidFields = SolenoidFields()
    systematic_fields: SolenoidFields = SolenoidFields()
    random_fields: SolenoidFields = SolenoidFields()
    field_integral_coefficients: FieldIntegral = FieldIntegral()
    linear_saturation_coefficients: LinearSaturationFit = LinearSaturationFit()
    settle_time: float = Field(alias="mag_set_max_wait_time", default=45.0)

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        if "ks" in data:
            self.ks = data["ks"]
        elif "field_amplitude" in data:
            self.ks = data["field_amplitude"] * self.length
        else:
            self.ks = 0
        # setattr(self.fields, 'S'+str(self.order)+'L', self.ks)

    @field_validator("field_integral_coefficients", mode="before")
    @classmethod
    def validate_field_integral_coefficients(cls, v: Union[str, List]) -> FieldIntegral:
        if isinstance(v, str):
            return FieldIntegral(coefficients=list(map(float, v.split(","))))
        elif isinstance(v, (list, tuple)):
            return FieldIntegral(coefficients=list(v))
        elif isinstance(v, (dict)):
            return FieldIntegral(**v)
        elif isinstance(v, (FieldIntegral)):
            return v
        else:
            raise ValueError(
                "field_integral_coefficients should be a string or a list of floats"
            )

    @property
    def ks(self) -> Union[int, float]:
        return getattr(self.fields, "S" + str(self.order) + "L")

    @ks.setter
    def ks(self, ks: float = 0) -> None:
        setattr(self.fields, "S" + str(self.order) + "L", ks)
