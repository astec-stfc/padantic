from pydantic import Field, field_validator, create_model
from typing import List, Type, Any, Union

from .baseModels import IgnoreExtra, T, YAMLBaseModel


class RFCavityElement(IgnoreExtra):
    structure_Type: str = "TravellingWave"
    attenuation_constant: float = 0
    cell_length: float = 0.0333333333333333
    coupling_cell_length: Union[float, None] = None
    design_gamma: Union[float, None] = None
    design_power: float = 25000000
    frequency: float = 2998500000.0
    n_cells: Union[int, float]
    crest: float = 0
    phase: float
    shunt_impedance: Union[float, None] = None


class WakefieldElement(IgnoreExtra):
    cell_length: float = 0.0333333333333333
    n_cells: Union[int, float] = 1


class RFDeflectingCavityElement(IgnoreExtra):
    coupling_cell_length: Union[float, None] = None
    design_gamma: Union[float, None] = None
    design_power: float = 25000000
    frequency: float = 2998500000.0
    crest: float = 0
    phase: float = 90


class PIDPhaseRange(IgnoreExtra):
    min: Union[float, int]
    max: Union[float, int]

    def __str__(self) -> str:
        return str([self.min, self.max])

    def __repr__(self) -> repr:
        return self.__str__()

    def __iter__(self) -> iter:
        return iter([getattr(self, k) for k in self.model_fields.keys()])


class PIDWeightRange(PIDPhaseRange): ...


class PIDElement(IgnoreExtra):
    """LLRF info model."""

    forward_channel: int
    probe_channel: int
    enable: str
    disable: str
    phase_range: Union[str, list, PIDPhaseRange]
    phase_weight_range: Union[str, list, PIDWeightRange]

    @field_validator("phase_range", mode="before")
    @classmethod
    def validate_phase_range(cls, v: Union[str, List]) -> PIDPhaseRange:
        if isinstance(v, str):
            # print('str')
            splitlist = list(map(str.strip, v.split(",")))
            assert len(splitlist) == 2
            min, max = splitlist
            return PIDPhaseRange(min=min, max=max)
        elif isinstance(v, (list, tuple)):
            # print('list')
            assert len(v) == 2
            return PIDPhaseRange(min=v[0], max=v[1])
        elif isinstance(v, (PIDPhaseRange)):
            # print('isinstance')
            return v
        else:
            raise ValueError("phase_range should be a string or a list of numbers")

    @field_validator("phase_weight_range", mode="before")
    @classmethod
    def validate_phase_weight_range(cls, v: Union[str, List]) -> PIDWeightRange:
        if isinstance(v, str):
            splitlist = list(map(str.strip, v.split(",")))
            assert len(splitlist) == 2
            min, max = splitlist
            return PIDWeightRange(min=min, max=max)
        elif isinstance(v, (list, tuple)):
            assert len(v) == 2
            return PIDWeightRange(min=v[0], max=v[1])
        elif isinstance(v, (PIDWeightRange)):
            return v
        else:
            raise ValueError(
                "phase_weight_range should be a string or a list of numbers"
            )


class Trace(IgnoreExtra):
    data_size: int = Field(alias="trace_data_size")
    data_count: int = Field(alias="one_trace_data_count")
    data_chunk_size: int = Field(alias="one_trace_data_chunk_size")
    number_of_start_zeros: int = Field(alias="trace_num_of_start_zeros")


fields = {str(i): (str, Field(alias="CH" + str(i), default="")) for i in range(1, 9)}
ChannelNamesBase = create_model("ChannelNamesBase", **fields, __base__=IgnoreExtra)


class ChannelNames(ChannelNamesBase): ...


llrffieldnames = [
    "klystron_forward",
    "klystron_reverse",
    "cavity_forward",
    "cavity_reverse",
    "cavity_probe",
]
llrftimingsCATAPnames = ["kf", "kr", "cf", "cr", "cp"]
cavitynames = ["LRRG", "HRRG", "L01", "CALIBRATION"]


class LLRFChannelIndex(YAMLBaseModel):
    power: int
    phase: int


class LLRFChannelsBase(YAMLBaseModel):
    labels: List[str] = []

    @classmethod
    def from_CATAP(cls: Type[T], fields: dict) -> T:
        inputs = {}
        for name in llrffieldnames:
            if "ONE_RECORD_" + str.upper(name) + "_POWER" in fields:
                substr = "ONE_RECORD_" + str.upper(name)
                inputs[str.upper(name)] = LLRFChannelIndex(
                    power=fields[substr + "_POWER"], phase=fields[substr + "_PHASE"]
                )
            for cav in cavitynames:
                if (
                    "ONE_RECORD_" + str.upper(cav) + "_" + str.upper(name) + "_POWER"
                    in fields
                ):
                    subname = str.upper(cav) + "_" + str.upper(name)
                    substr = "ONE_RECORD_" + subname
                    inputs[subname] = LLRFChannelIndex(
                        power=fields[substr + "_POWER"], phase=fields[substr + "_PHASE"]
                    )
        inputs["labels"] = list(inputs.keys())
        return cls(**inputs)

    @property
    def phases(self):
        pass


class LLRFTiming(YAMLBaseModel):
    start: Union[float, int]
    end: Union[float, int]


fields = {i: (LLRFTiming, Field()) for i in llrffieldnames}
LLRFTimingsBase = create_model("LLRFTimingsBase", **fields, __base__=IgnoreExtra)


class LLRFTimings(LLRFTimingsBase):

    @classmethod
    def from_CATAP(cls: Type[T], fields: dict) -> T:
        for name, prefix in zip(*[llrffieldnames, llrftimingsCATAPnames]):
            fields[name] = LLRFTiming(
                start=fields[prefix + "pow_mean_start_time"],
                end=fields[prefix + "pow_mean_end_time"],
            )
        return super().from_CATAP(fields)


class LLRFElement(IgnoreExtra):
    trace: Trace
    max_amplitude: float = Field(alias="MAX_AMPLITUDE")
    channel_names: ChannelNames
    one_record: LLRFChannelsBase
    crest_phase: float
    timings: LLRFTimings

    def _create_LLRFChannels_Model(self, fields: dict):
        inputs = {}
        for name in llrffieldnames:
            if "ONE_RECORD_" + str.upper(name) + "_POWER" in fields:
                substr = "ONE_RECORD_" + str.upper(name)
                inputs[str.upper(name)] = LLRFChannelIndex(
                    power=fields[substr + "_POWER"], phase=fields[substr + "_PHASE"]
                )
            for cav in cavitynames:
                if (
                    "ONE_RECORD_" + str.upper(cav) + "_" + str.upper(name) + "_POWER"
                    in fields
                ):
                    subname = str.upper(cav) + "_" + str.upper(name)
                    substr = "ONE_RECORD_" + subname
                    inputs[subname] = LLRFChannelIndex(
                        power=fields[substr + "_POWER"], phase=fields[substr + "_PHASE"]
                    )
        model_fields = {i: (LLRFChannelIndex, Field()) for i in inputs.keys()}
        LLRFChannels = create_model(
            "LLRFChannels", **model_fields, __base__=LLRFChannelsBase
        )
        fields["labels"] = list(model_fields.keys())
        return LLRFChannels

    @classmethod
    def from_CATAP(cls: Type[T], fields: dict) -> T:
        cls._create_field_class(cls, fields, "trace", Trace)
        cls._create_field_class(cls, fields, "channel_names", ChannelNames)
        onerclass = cls._create_LLRFChannels_Model(cls, fields)
        cls._create_field_class(cls, fields, "one_record", onerclass)
        cls._create_field_class(cls, fields, "timings", LLRFTimings)
        return super().from_CATAP(fields)


class RFModulatorElement(IgnoreExtra): ...


class RFProtectionElement(IgnoreExtra):
    prot_type: str


class RFHeartbeatElement(IgnoreExtra): ...
