from pydantic import BaseModel, model_serializer, ConfigDict
from typing import TypeVar, Dict, Any, Type, List
import yaml
import numpy as np

# Create a generic variable that can be 'Parent', or any subclass.
T = TypeVar('T', bound='BaseModel')

class IgnoreExtra(BaseModel):
    ''' Base Model that ignores extra fields. '''
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="ignore",
    )

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        # print(self.__class__.__name__, [getattr(self,k) for k in self.model_fields.keys()])
        return {k: getattr(self,k) for k in self.model_fields.keys() if getattr(self,k) != 0 and getattr(self,k) is not None and getattr(self,k) != {}}

class NumpyModel(BaseModel):
    ''' Model using numpy arrays. '''

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_serializer
    def ser_model(self) -> np.ndarray:
        return self.array

    @property
    def array(self) -> np.ndarray:
        return np.array([getattr(self, a) for a in self.model_fields.keys()])

    @classmethod
    def from_list(cls: Type[T], vec: List[float | int]) -> T:
        assert len(vec) == len(cls.model_fields)
        return cls(**dict(zip(list(cls.model_fields.keys()), vec)))

    @classmethod
    def from_values(cls: Type[T], *values: float | int) -> T:
        assert len(values) == len(cls.model_fields)
        return cls(**dict(zip(list(cls.model_fields.keys()), values)))

class NumpyVectorModel(NumpyModel):
    ''' vector model using numpy arrays. '''

    def __iter__(self) -> iter:
        return iter([getattr(self, k) for k in self.model_fields.keys()])

    def __eq__(self, other: Any) -> bool:
        if other == 0 or other == 0. or other == None:
            if all([getattr(self, k) == 0 for k in self.model_fields.keys()]):
                return True
            return False
        return list(self) == list(other)

    def __neq__(self, other: Any) -> bool:
        # print('__neq__ called', other)
        if other == 0 or other == 0. or other == None:
            if all([getattr(self, k) == 0 for k in self.model_fields.keys()]):
                return False
            return True
        return list(self) != list(other)
