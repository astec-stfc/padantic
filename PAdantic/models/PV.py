from pydantic import BaseModel, model_serializer, ConfigDict, field_validator, ValidationInfo, Field, create_model
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
        if v.upper() not in map(str.upper, areaNames) and not v == '':
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
        if 'typename' in info.data:
            typename = info.data['typename']
        else:
            raise ValueError('typename missing')
        if classname in classrecordNames:
            records = classrecordNames[classname]
        elif typename in classrecordNames:
            records = classrecordNames[typename]
        else:
            raise ValueError('Invalid Record classname/typename')
        if v.upper() not in map(str.upper, records):
            # raise ValueError('Invalid Record Name')
            print('    -',v)
        return v

    @classmethod
    def fromString(cls, pv: str) -> T:
        assert ':' in pv
        prefix, postfix = pv.split(':', 1)
        substr = prefix.split('-')
        if len(substr) == 5:
            return cls.model_validate({'machine': substr[0], 'area': substr[1], 'classname': substr[2],
                             'typename': substr[3], 'index': substr[4], 'record': postfix})
        elif len(substr) == 4:
            return cls.model_validate({'machine': substr[0], 'area': '', 'classname': substr[1],
                             'typename': substr[2], 'index': substr[3], 'record': postfix})

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

class ElementPV(BaseModel):

    def __str__(self) -> str:
        return ', '.join([k + '=PV(\''+getattr(self, k).__str__()+'\')' for k in self.model_fields.keys() if getattr(self, k) is not None])

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        return {k: getattr(self,k) for k in self.model_fields.keys() if getattr(self,k) is not None}

PVMappings = {
    'MAG': 'Magnet',
    'BPM': 'BPM',
    'CAM': 'Camera',
    'SCR': 'Screen',
    'WCM': 'ChargeDiagnostic',
    'FCUP': 'ChargeDiagnostic',
    'IMG': 'VacuumGuage',
    'EM': 'LaserEnergyMeter',
    'HWP': 'LaserHWP',
    'PICO': 'LaserMirror',
    'Lighting': 'Lighting'
}

for k, v in PVMappings.items():
    pvs = {p: (PV, Field(default=None)) for p in classPVNames[k]}
    PVData = create_model(v+'PV', **pvs, __base__=ElementPV)
    globals()[v+'PV'] = type(v+'PV', (PVData, ), {})
