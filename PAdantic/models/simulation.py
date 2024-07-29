from pydantic import field_validator, confloat, Field, NonNegativeFloat, AliasChoices
from typing import List

from ._functions import _rotation_matrix

from .baseModels import IgnoreExtra, NumpyVectorModel

class ApertureElement(IgnoreExtra):
    ''' Physical info model. '''
    horizontal_size: float = 1
    vertical_size: float = 1
    shape: str = 'rectangular'

class RFCavitySimulationElement(IgnoreExtra):
    field_amplitude: float = 0
    field_definition: str|None = None
    field_definition_gdf: str|None = None
    longitudinal_wakefield_sdds: str|None = None
    transverse_wakefield_sdds: str|None = None
    wakefield_gdf: str|None = None
    t_column: str|None = "t"
    wx_column: str|None = "W"
    wy_column: str|None = "W"
    wz_column: str|None = "W"

class WakefieldSimulationElement(IgnoreExtra):
    allow_long_beam: bool = True
    bunched_beam: bool = False
    change_momentum: bool = True
    factor: float = 1
    field_amplitude: float = 0
    field_definition: str = 'TWS_S-DL.dat'
    field_definition_sdds: str|None = None
    field_definition_gdf: str|None = None
    interpolate: bool = True
    scale_kick: float = 1
    t_column: str = Field(alias='tcolumn', default='t')
    w_column: str = Field(alias='wcolumn', default='Ez')
