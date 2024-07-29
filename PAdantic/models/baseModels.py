from pydantic import BaseModel, model_serializer, ConfigDict
from typing import TypeVar, Dict, Any, Type, List
import yaml
import numpy as np

# Create a generic variable that can be 'Parent', or any subclass.
T = TypeVar('T', bound='BaseModel')

class string_with_quotes(str):
    pass

class flow_list(list):
    pass

def flow_list_rep(dumper, data):
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)

def quoted_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

yaml.add_representer(string_with_quotes, quoted_presenter)
yaml.add_representer(flow_list, flow_list_rep)

def convert_numpy_types(v):
    if isinstance(v, dict):
        return {k:convert_numpy_types(l) for k,l in v.items()}
    if isinstance(v, (np.ndarray, list, tuple)):
        return flow_list([convert_numpy_types(l) for l in v])
    elif isinstance(v, (np.float64, np.float32, np.float16, np.float_ )):
        return float(v)
    elif isinstance(v, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
        return int(v)
    else:
        return v

class YAMLBaseModel(BaseModel):
    ''' Base Model that ignores extra fields. '''

    def yaml_dump(self) -> dict:
        return convert_numpy_types(self.model_dump())

class IgnoreExtra(YAMLBaseModel):
    ''' Base Model that ignores extra fields. '''
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="ignore",
        populate_by_name=True,
    )

    # @model_serializer
    # def ser_model(self) -> Dict[str, Any]:
    #     # print(self.__class__.__name__, [getattr(self,k) for k in self.model_fields.keys()])
    #     return {k: getattr(self,k) for k in self.model_fields.keys() if getattr(self,k) != 0 and getattr(self,k) is not None and getattr(self,k) != {}}

    def _create_field_class(self, fields: dict, fieldname: str, fieldclass: List[str]) -> None:
        fields[fieldname] = fieldclass.from_CATAP(fields)

    def _create_field(self, fields: dict, fieldname: str, fieldinputs: List[str]) -> None:
        fields[fieldname] = [fields[x] for x in fieldinputs]

    @classmethod
    def from_CATAP(cls: Type[T], fields: dict) -> T:
        return cls(**fields)

    def update(self, **kwargs):
        [v.annotation.update(k) for k,v in self.model_fields.items() if hasattr(v.annotation, 'update')]
        self.__dict__.update(kwargs)

class NumpyModel(YAMLBaseModel):
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

    def update(self, **kwargs):
        [v.annotation.update(v) for k,v in self.model_fields.items() if hasattr(v.annotation, 'update')]
        self.__dict__.update(kwargs)

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
        if other == 0 or other == 0. or other == None:
            if all([getattr(self, k) == 0 for k in self.model_fields.keys()]):
                return False
            return True
        return list(self) != list(other)

class objectList(IgnoreExtra):

    def __iter__(self) -> iter:
        return iter(getattr(self, list(self.model_fields.keys())[0]))

    def __str__(self) -> str:
        return str(list(getattr(self, list(self.model_fields.keys())[0])))

    def __repr__(self) -> repr:
        return repr(list(getattr(self, list(self.model_fields.keys())[0])))

class DeviceList(objectList):
    devices: list = []

class Aliases(objectList):
    aliases: list = []
