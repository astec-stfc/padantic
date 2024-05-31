from pydantic import model_serializer, ConfigDict, field_validator, ValidationInfo, Field, create_model, model_validator
from typing import Dict, Any, List
import yaml

from .baseModels import T, YAMLBaseModel

# Load PV definitions
with open('PV_Values.yaml','r') as stream:
    data = yaml.load(stream, Loader=yaml.Loader)
    for k,v in data.items():
        globals()[k] = v

class PVSet(YAMLBaseModel):
    ''' Base PV model. '''
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=True,
    )
    ...

class PV(PVSet):
    ''' PV model. '''
    machine: str | None
    area: str | None
    classname: str | None
    typename: str | None
    index: int | str | None
    record: str
    _PV_index: List[int]

    @field_validator('machine', mode='before')
    @classmethod
    def validate_machine(cls, v: str) -> str:
        if v.upper() not in map(str.upper, machineNames):
            raise ValueError('Invalid Machine', v.upper())
        return v.upper()

    @field_validator('area', mode='before')
    @classmethod
    def validate_area(cls, v: str) -> str:
        if v == None:
            return v
        else:
            if v.upper() not in map(str.upper, areaNames) and not v == '':
                raise ValueError('Invalid Area')
            return v.upper()

    @field_validator('classname', mode='before')
    @classmethod
    def validate_class(cls, v: str) -> str:
        if v == None:
            return v
        else:
            if v.upper() not in map(str.upper, classtypeNames.keys()):
                raise ValueError('Invalid Class Name')
            return v.upper()

    @field_validator('typename', mode='before')
    @classmethod
    def validate_type(cls, v: str, info: ValidationInfo) -> str:
        if v == None:
            return v
        else:
            classname = info.data['classname']
            if v.upper() not in map(str.upper, classtypeNames[classname]):
                print('validate_type',classtypeNames[classname], v)
                raise ValueError('Invalid Type Name')
            return v.upper()

    @field_validator('index', mode='before')
    @classmethod
    def validate_index(cls, v: str) -> int:
        if v == None:
            return v
        elif v.isdigit():
            return int(v)
        elif not isinstance(v, str):
            raise ValueError(f'Invalid index {v}')
        return v

    @field_validator('record', mode='before')
    @classmethod
    def validate_record(cls, v: str, info: ValidationInfo) -> str:
        if v == None or v == '':
            return v
        if 'typename' in info.data:
            typename = info.data['typename']
        else:
            raise ValueError('typename missing')
        if typename in classrecordNames:
            records = classrecordNames[typename]
        else:
            raise ValueError(f"Invalid Record typename {typename}")
        if isinstance(classrecordNames[typename], str):
            records = classrecordNames[classrecordNames[typename]]
        # print(f'validate_record {typename}', records)
        if v.upper() not in map(str.upper, records):
            # print(f'validate_record {v}','    -',v)
            raise ValueError('Invalid Record Name')
        return v

    def split_string(self, pv):
        assert ':' in pv
        prefix, postfix = pv.split(':', 1)
        substr = prefix.split('-')
        if len(substr) == 5:
            return {'machine': substr[0], 'area': substr[1], 'classname': substr[2],
                             'typename': substr[3], 'index': substr[4], 'record': postfix}, list(range(5))
        elif len(substr) == 4:
            return {'machine': substr[0], 'area': None, 'classname': substr[1],
                             'typename': substr[2], 'index': substr[3], 'record': postfix}, [0,2,3,4]
        elif len(substr) == 3:
            return {'machine': substr[0], 'area': substr[1], 'classname': substr[2],
                             'typename': None, 'index': None, 'record': postfix}, [0,1,2]
        elif len(substr) == 7:
            return {'machine': substr[0], 'area': substr[1], 'classname': substr[2],
                             'typename': '-'.join(substr[4:-1]), 'index': substr[-1], 'record': postfix}, list(range(5))

    @classmethod
    def fromString(cls, pv: str) -> T:
        d, i = self.split_string(pv)
        model = cls.model_validate(d)
        model._PV_index = i
        return model

    @property
    def _indexString(self) -> str:
        if 4 in self._PV_index:
            if isinstance(self.index, int):
                return '-' + str(self.index).zfill(2)
            else:
                return '-' + str(self.index)

    @property
    def basename(self) -> str:
        name = '-'.join([getattr(self, a) for a in [['machine', 'area', 'classname', 'typename'][i] for i in self._PV_index if i < 4]]) + self._indexString
        return name

    @property
    def name(self) -> str:
        name = self.basename + ':' + self.record
        return name

    def __str__(self) -> str:
        return self.name

    def __int__(self) -> int:
        return self.index

    def __repr__(self):
        return self.__str__()

    @model_serializer
    def ser_model(self) -> str:
        return self.__str__()

class ElementPV(YAMLBaseModel):
    model_config = ConfigDict(validate_assignment=True)

    def __str__(self) -> str:
        return ', '.join([k + '=PV(\''+getattr(self, k).__str__()+'\')' for k in self.model_fields.keys() if getattr(self, k) is not None])

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        return {k: getattr(self,k) for k in self.model_fields.keys() if getattr(self,k) is not None}

    @classmethod
    def with_defaults(cls, *args):
        d = {}
        for k, v in cls.model_fields.items():
            for name in args:
                try:
                    pv = PV.fromString(name + ':' + v.json_schema_extra['postfixdefault'])
                    d[k] = pv
                    break
                except Exception as e:
                    # print('Exception', e)
                    # print(name, k, v.json_schema_extra['postfixdefault'])
                    pass
        return cls(**d)

    def update(self, **new_data):
        for field, value in new_data.items():
           setattr(self, field, value)

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
    'Lighting': 'Lighting',
    'PID': 'PID',
    'LLRF': 'LLRF',
    'RFModulator': 'RFModulator',
    'Shutter': 'Shutter',
    'Valve': 'Valve',
    'RFProtection': 'RFProtection',
    'RFHeartbeat': 'RFHeartbeat',
}

for k, v in PVMappings.items():
    pvs = {}
    for p in classPVNames[k]:
        if isinstance(p, str):
            pvs[p] = (PV, Field(postfixdefault=p))
        if isinstance(p, dict):
            for pd,vd in p.items():
                pvs[pd] = (PV, Field(postfixdefault=vd))
    PVData = create_model(v+'PV', **pvs, __base__=ElementPV)
    globals()[v+'PV'] = type(v+'PV', (PVData, ), {})
