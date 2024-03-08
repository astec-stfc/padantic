from pydantic import BaseModel, model_serializer, ConfigDict, Field, field_validator, ValidationInfo
from typing import List

from .baseModels import IgnoreExtra

class DegaussablElement(IgnoreExtra):
    ''' Degauss info model. '''
    degauss_tolerance: float = Field(default=0.5)
    degauss_values: List[float] = Field(default=[])
    degauss_steps: int = Field(alias='num_degauss_steps', default=11)

    @field_validator('degauss_values', mode='before')
    @classmethod
    def validate_degauss_values(cls, v: str|List) -> list:
        if isinstance(v, str):
            return list(map(float, v.split(',')))
        elif isinstance(v, (list, tuple)):
            return list(v)
        else:
            raise ValueError('degauss_values should be a string or a list of floats')
