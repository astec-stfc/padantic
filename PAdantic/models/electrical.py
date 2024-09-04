from pydantic import Field

from .baseModels import IgnoreExtra


class ElectricalElement(IgnoreExtra):
    """Electrical info model."""

    minI: float = Field(alias="min_i", default=0)
    maxI: float = Field(alias="max_i", default=0)
    read_tolerance: float = Field(alias="ri_tolerance", default=0.1)
