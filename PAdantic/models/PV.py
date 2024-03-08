from pydantic import BaseModel, model_serializer, ConfigDict, field_validator, ValidationInfo
from typing import Dict, Any
import yaml

from .baseModels import T

# Load PV definitions
with open('PV_Values.yaml','r') as stream:
    data = yaml.load(stream, Loader=yaml.Loader)
    for k,v in data.items():
        globals()[k] = v

class PVSet(BaseModel):
    ''' Base PV model. '''
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=True,
    )
    ...

class PV(PVSet):
    ''' PV model. '''
    machine: str
    area: str
    classname: str
    typename: str
    index: int | str
    record: str

    @field_validator('machine', mode='before')
    @classmethod
    def validate_machine(cls, v: str) -> str:
        if v.upper() not in map(str.upper, machineNames):
            raise ValueError('Invalid Machine', v.upper())
        return v.upper()

    @field_validator('area', mode='before')
    @classmethod
    def validate_area(cls, v: str) -> str:
        if v.upper() not in map(str.upper, areaNames):
            raise ValueError('Invalid Area')
        return v.upper()

    @field_validator('classname', mode='before')
    @classmethod
    def validate_class(cls, v: str) -> str:
        if v.upper() not in map(str.upper, classtypeNames.keys()):
            raise ValueError('Invalid Class Name')
        return v.upper()

    @field_validator('typename', mode='before')
    @classmethod
    def validate_type(cls, v: str, info: ValidationInfo) -> str:
        classname = info.data['classname']
        if v.upper() not in map(str.upper, classtypeNames[classname]):
            raise ValueError('Invalid Type Name')
        return v.upper()

    @field_validator('index', mode='before')
    @classmethod
    def validate_index(cls, v: str) -> int:
        if not v.isdigit():
            raise ValueError('Invalid Type Name')
        return int(v)

    @field_validator('record', mode='before')
    @classmethod
    def validate_record(cls, v: str, info: ValidationInfo) -> str:
        classname = info.data['classname']
        if v.upper() not in map(str.upper, classrecordNames[classname]):
            raise ValueError('Invalid Record Name')
        return v

    @classmethod
    def fromString(cls, pv: str) -> T:
        assert ':' in pv
        prefix, postfix = pv.split(':')
        substr = prefix.split('-')
        assert len(substr) == 5
        return cls.model_validate({'machine': substr[0], 'area': substr[1], 'classname': substr[2],
                             'typename': substr[3], 'index': substr[4], 'record': postfix})

    @property
    def _indexString(self) -> str:
        return str(self.index).zfill(2)

    @property
    def basename(self) -> str:
        name = '-'.join([getattr(self, a) for a in ['machine', 'area', 'classname', 'typename']]) + '-' + self._indexString
        return name

    @property
    def name(self) -> str:
        name = self.basename + ':' + self.record
        return name

    def __str__(self) -> str:
        return self.name

    def __int__(self) -> int:
        return self.index

    @model_serializer
    def ser_model(self) -> str:
        return self.__str__()

class MagnetPV(BaseModel):
    ''' Magnet PV model. '''
    GETSETI:    PV | None = None
    READI:      PV | None = None
    RILK:       PV | None = None
    RPOWER:     PV | None = None
    SETI:       PV | None = None
    SPOWER:     PV | None = None
    ILK_RESET:  PV | None = None
    K_DIP_P:    PV | None = None
    INT_STR_MM: PV | None = None
    INT_STR:    PV | None = None
    K_SET_P:    PV | None = None
    K_ANG:      PV | None = None
    K_MRAD:     PV | None = None
    K_VAL:      PV | None = None

    def __str__(self) -> str:
        return 'MagnetPV(' + ', '.join([k + '=PV(\''+getattr(self, k).__str__()+'\')' for k in self.model_fields.keys() if getattr(self, k) is not None])

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        return {k: getattr(self,k) for k in self.model_fields.keys() if getattr(self,k) is not None}
