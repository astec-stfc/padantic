import os
from pydantic import (
    model_serializer,
    ConfigDict,
    field_validator,
    Field,
    create_model,
    computed_field,
)
from typing import Dict, Any, List, Union
import yaml

from .baseModels import T, YAMLBaseModel

# Load PV definitions from yaml file
# This creates some flake8 F821 warnings that are ignored manually
with open(
    os.path.abspath(os.path.dirname(__file__)) + "/../PV_Values.yaml", "r"
) as stream:
    data = yaml.load(stream, Loader=yaml.Loader)
    for k, v in data.items():
        globals()[k] = v
    machineNames = globals()["machineNames"]
    areaNames = globals()["areaNames"]
    classTypes = globals()["classTypes"]
    classPVRecords = globals()["classPVRecords"]
    classPVNames = globals()["classPVNames"]


class PVSet(YAMLBaseModel):
    """Base PV model."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=True,
    )
    ...


class PV(PVSet):
    pv_string: str
    _pv_dict: dict
    _PV_index: List[int]

    @field_validator("pv_string", mode="before")
    def fromString(cls, pv: str) -> T:
        assert ":" in pv
        prefix, postfix = pv.split(":", 1)
        substr = prefix.split("-")
        if len(substr) == 5:
            cls._pv_dict = {
                "machine": substr[0],
                "area": substr[1],
                "classname": substr[2],
                "typename": substr[3],
                "index": substr[4],
                "record": postfix,
            }
            cls._PV_index = list(range(5))
        elif len(substr) == 4:
            cls._pv_dict = {
                "machine": substr[0],
                "area": None,
                "classname": substr[1],
                "typename": substr[2],
                "index": substr[3],
                "record": postfix,
            }
            cls._PV_index = [0, 2, 3, 4]
        elif len(substr) == 3:
            cls._pv_dict = {
                "machine": substr[0],
                "area": substr[1],
                "classname": substr[2],
                "typename": None,
                "index": None,
                "record": postfix,
            }
            cls._PV_index = [0, 1, 2]
        elif len(substr) == 7:
            cls._pv_dict = {
                "machine": substr[0],
                "area": substr[1],
                "classname": substr[2],
                "typename": "-".join(substr[4:-1]),
                "index": substr[-1],
                "record": postfix,
            }
            cls._PV_index = list(range(5))
        cls.validate_machine(cls)
        cls.validate_area(cls)
        cls.validate_class(cls)
        cls.validate_type(cls)
        cls.validate_index(cls)
        cls.validate_record(cls)
        return pv

    @computed_field
    def machine(self) -> str:
        return self._pv_dict["machine"]

    def validate_machine(cls) -> str:
        v = cls._pv_dict["machine"]
        if v.upper() not in map(str.upper, machineNames):  # noqa F821
            print("PV - Validate Machine Error:", machineNames, v)  # noqa F821
            raise ValueError("Invalid Machine", v.upper())
        return v.upper()

    @computed_field
    @property
    def area(self) -> str:
        return self._pv_dict["area"]

    def validate_area(cls) -> str:
        v = cls._pv_dict["area"]
        if v is None:
            return v
        else:
            if v.upper() not in map(str.upper, areaNames) and not v == "":  # noqa F821
                print("PV - Validate Area Error:", areaNames, v)  # noqa F821
                raise ValueError("Invalid Area")
            return v.upper()

    @computed_field
    @property
    def classname(self) -> str:
        return self._pv_dict["classname"]

    def validate_class(cls) -> str:
        v = cls._pv_dict["classname"]
        if v is None:
            return v
        else:
            if v.upper() not in map(str.upper, classTypes.keys()):  # noqa F821
                print("PV - Validate Class Error:", classTypes.keys(), v)  # noqa F821
                raise ValueError("Invalid Class Name")
            return v.upper()

    @computed_field
    @property
    def typename(self) -> str:
        return self._pv_dict["typename"]

    def validate_type(cls) -> str:
        """Confirm that `typename` is in the valid types for class `classname`"""
        v = cls._pv_dict["typename"]
        if v is None:
            return v
        else:
            classname = cls._pv_dict["classname"]
            if v.upper() not in map(str.upper, classTypes[classname]):  # noqa F821
                print(
                    "PV - Validate Type Error:", classTypes[classname], v  # noqa F821
                )
                raise ValueError("Invalid Type Name")
            return v.upper()

    @computed_field
    @property
    def index(self) -> str:
        return self._pv_dict["index"]

    def validate_index(cls) -> int:
        v = cls._pv_dict["index"]
        if v is None:
            return v
        elif v.isdigit():
            return int(v)
        elif not isinstance(v, str):
            raise ValueError(f"Invalid index {v}")
        return v

    @computed_field
    @property
    def record(self) -> str:
        return self._pv_dict["record"]

    def validate_record(cls) -> str:
        """Confirm that `record` is in the valid PV record names for class `classname` and type `typename`"""
        v = cls._pv_dict["record"]
        if v is None or v == "":
            return v
        if "typename" in cls._pv_dict:
            typename = cls._pv_dict["typename"]
        else:
            raise ValueError("typename missing")
        if typename in classPVRecords:  # noqa F821
            records = classPVRecords[typename]  # noqa F821
        else:
            raise ValueError(f"Invalid Record typename {typename} [{cls._pv_dict}]")
        if isinstance(classPVRecords[typename], str):  # noqa F821
            # If we are referencing another record class!
            records = classPVRecords[classPVRecords[typename]]  # noqa F821
        # print(f'validate_record {typename}', records)
        if v.upper() not in map(str.upper, records):
            # print(f'validate_record {v}','    -',v)
            raise ValueError(f"Invalid Record Name {v.upper()} [{records}]")
        return v

    @property
    def _indexString(self) -> str:
        if 4 in self._PV_index:
            if isinstance(self.index, int):
                return "-" + str(self.index).zfill(2)
            else:
                return "-" + str(self.index)

    @property
    def basename(self) -> str:
        name = (
            "-".join(
                [
                    getattr(self, a)
                    for a in [
                        ["machine", "area", "classname", "typename"][i]
                        for i in self._PV_index
                        if i < 4
                    ]
                ]
            )
            + self._indexString
        )
        return name

    @property
    def name(self) -> str:
        return self.pv_string

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

    @field_validator("*", mode="before")
    @classmethod
    def validate_pv(cls, v: Union[PV, str]) -> PV:
        if isinstance(v, str):
            return PV(pv_string=v)
        return v

    def __str__(self) -> str:
        return ", ".join(
            [
                k + "=PV('" + getattr(self, k).__str__() + "')"
                for k in self.model_fields.keys()
                if getattr(self, k) is not None
            ]
        )

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        return {
            k: getattr(self, k)
            for k in self.model_fields.keys()
            if getattr(self, k) is not None
        }

    @classmethod
    def with_defaults(cls, *args):
        d = {}
        for k, v in cls.model_fields.items():
            for name in args:
                try:
                    pv = PV.fromString(
                        name + ":" + v.json_schema_extra["postfixdefault"]
                    )
                    d[k] = pv
                    break
                except Exception as e:
                    # print('Exception', e)
                    print(name, k, v.json_schema_extra["postfixdefault"])
                    raise e
        return cls(**d)

    def update(self, **new_data):
        for field, value in new_data.items():
            setattr(self, field, value)


PVMappings = {
    "MAG": "Magnet",
    "BPM": "BPM",
    "BAM": "BAM",
    "BLM": "BLM",
    "CAM": "Camera",
    "SCR": "Screen",
    "WCM": "ChargeDiagnostic",
    "ICT": "ChargeDiagnostic",
    "FCUP": "ChargeDiagnostic",
    "IMG": "VacuumGuage",
    "EM": "LaserEnergyMeter",
    "HWP": "LaserHWP",
    "PICO": "LaserMirror",
    "Lighting": "Lighting",
    "PID": "PID",
    "LLRF": "LLRF",
    "RFModulator": "RFModulator",
    "Shutter": "Shutter",
    "Valve": "Valve",
    "RFProtection": "RFProtection",
    "RFHeartbeat": "RFHeartbeat",
}

for k, v in PVMappings.items():
    pvs = {}
    for p in classPVNames[k]:  # noqa F821
        if isinstance(p, str):
            pvs[p] = (PV, Field(postfixdefault=p))
        if isinstance(p, dict):
            for pd, vd in p.items():
                pvs[pd] = (PV, Field(postfixdefault=vd))
    PVData = create_model(v + "PV", **pvs, __base__=ElementPV)
    globals()[v + "PV"] = type(v + "PV", (PVData,), {})
