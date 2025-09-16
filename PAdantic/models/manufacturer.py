from pydantic import Field, field_validator
from typing import Any
from .baseModels import IgnoreExtra


class ManufacturerElement(IgnoreExtra):
    """Manufacturer info model."""

    manufacturer: str = ""
    serial_number: str = ""
    hardware_class: str = Field(alias="hardware_type", default="")

    @field_validator("manufacturer", "serial_number", mode="before")
    @classmethod
    def validate_field_integral_coefficients(cls, v: Any) -> str:
        return str(v)
