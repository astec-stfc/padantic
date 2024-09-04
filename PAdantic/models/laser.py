from pydantic import Field, field_validator
from typing import List, Type, Union

from .baseModels import IgnoreExtra, T


class LaserElement(IgnoreExtra):
    """Laser info model."""

    pv_type: str = Field(alias="laser_pv_type")


class LaserEnergyMeterElement(IgnoreExtra):
    """Laser info model."""

    calibration_factor: float = Field()
    pv_type: str = Field(alias="laser_pv_type")


class LaserMirrorSense(IgnoreExtra):
    left: float = Field(alias="left_sense")
    right: float = Field(alias="right_sense")
    up: float = Field(alias="up_sense")
    down: float = Field(alias="down_sense")


class LaserMirrorElement(IgnoreExtra):
    """Laser info model."""

    step_max: float = Field()
    sense: LaserMirrorSense
    vertical_channel: Union[int, None] = None
    horizontal_channel: Union[int, None] = None

    @classmethod
    def from_CATAP(cls: Type[T], fields: dict) -> T:
        cls._create_field_class(cls, fields, "sense", LaserMirrorSense)
        return super().from_CATAP(fields)
