from pydantic import Field, field_validator
from typing import List, Union

from .baseModels import IgnoreExtra


class ShutterElement(IgnoreExtra):
    """Laser info model."""

    interlocks: List[str] = Field(alias="shutter_interlock_names", default=[])

    @field_validator("interlocks", mode="before")
    @classmethod
    def validate_interlocks(cls, v: Union[str, List]) -> List[str]:
        if isinstance(v, str):
            return list(map(str.strip, v.split(",")))
        elif isinstance(v, (list, tuple)):
            return v
        else:
            raise ValueError("interlocks should be a string or a list of strings")


class ValveElement(IgnoreExtra):
    """Laser info model."""
