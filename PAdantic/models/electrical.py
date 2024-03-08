from pydantic import Field

from .baseModels import IgnoreExtra

class ElectricalElement(IgnoreExtra):
    ''' Electrical info model. '''
    settle_time:    float = Field(alias='mag_set_max_wait_time', default=45.0)
    minI:           float = Field(alias='min_i', default=0)
    maxI:           float = Field(alias='max_i', default=0)
    read_tolerance: float = Field(alias='ri_tolerance', default=0.1)
