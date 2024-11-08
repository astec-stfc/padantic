from pydantic import Field
from typing import Union

from .baseModels import IgnoreExtra


class ApertureElement(IgnoreExtra):
    """Physical info model."""

    horizontal_size: float = 1
    vertical_size: float = 1
    shape: str = "rectangular"


class RFCavitySimulationElement(IgnoreExtra):
    field_amplitude: float = 0
    field_definition: Union[str, None] = None
    field_definition_gdf: Union[str, None] = None
    longitudinal_wakefield_sdds: Union[str, None] = None
    transverse_wakefield_sdds: Union[str, None] = None
    wakefield_gdf: Union[str, None] = None
    t_column: Union[str, None] = "t"
    wx_column: Union[str, None] = "W"
    wy_column: Union[str, None] = "W"
    wz_column: Union[str, None] = "W"


class WakefieldSimulationElement(IgnoreExtra):
    allow_long_beam: bool = True
    bunched_beam: bool = False
    change_momentum: bool = True
    factor: float = 1
    field_amplitude: float = 0
    field_definition: str = "TWS_S-DL.dat"
    field_definition_sdds: Union[str, None] = None
    field_definition_gdf: Union[str, None] = None
    interpolate: bool = True
    scale_kick: float = 1
    t_column: str = Field(alias="tcolumn", default="t")
    w_column: str = Field(alias="wcolumn", default="Ez")
