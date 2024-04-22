from pydantic import Field, field_validator
from typing import List

from .baseModels import IgnoreExtra

class DegaussablElement(IgnoreExtra):
    ''' Degauss info model. '''
    tolerance: float = Field(default=0.5, alias='degauss_tolerance')
    values: List[float] = Field(default=[], alias='degauss_values')
    steps: int = Field(default=11, alias='num_degauss_steps')

    @field_validator('values', mode='before')
    @classmethod
    def validate_degauss_values(cls, v: str|List) -> list:
        if isinstance(v, str):
            return list(map(float, v.split(',')))
        elif isinstance(v, (list, tuple)):
            return list(v)
        else:
            raise ValueError('degauss_values should be a string or a list of floats')
