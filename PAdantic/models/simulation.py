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
    wakefield_definition: Union[str, None] = None
    t_column: Union[str, None] = "t"
    wx_column: Union[str, None] = "Wx"
    wy_column: Union[str, None] = "Wy"
    wz_column: Union[str, None] = "Wz"


class WakefieldSimulationElement(IgnoreExtra):
    allow_long_beam: bool = True
    bunched_beam: bool = False
    change_momentum: bool = True
    factor: float = 1
    field_amplitude: float = 0
    field_definition: str = "TWS_S-DL.dat"
    interpolate: bool = True
    scale_kick: float = 1
    t_column: str = Field(alias="tcolumn", default="t")
    w_column: str = Field(alias="wcolumn", default="Ez")
