import os
from typing import Type, List, Union
from pydantic import field_validator, Field

from .baseModels import T, Aliases, IgnoreExtra
from .PV import (
    PV,
    MagnetPV,
    BPMPV,
    BAMPV,
    BLMPV,
    CameraPV,
    ScreenPV,
    ChargeDiagnosticPV,
    VacuumGuagePV,
    LaserEnergyMeterPV,
    LaserHWPPV,
    LaserMirrorPV,
    LightingPV,
    PIDPV,
    LLRFPV,
    RFModulatorPV,
    ShutterPV,
    ValvePV,
    RFProtectionPV,
    RFHeartbeatPV,
)
from .manufacturer import ManufacturerElement
from .electrical import ElectricalElement
from .degauss import DegaussablElement
from .physical import PhysicalElement, Rotation
from .magnetic import (
    Dipole_Magnet,
    Quadrupole_Magnet,
    Sextupole_Magnet,
    Solenoid_Magnet,
)
from .diagnostic import (
    BPM_Diagnostic,
    BAM_Diagnostic,
    BLM_Diagnostic,
    Camera_Diagnostic,
    Screen_Diagnostic,
    Charge_Diagnostic,
)
from .laser import LaserElement, LaserEnergyMeterElement, LaserMirrorElement
from .lighting import LightingElement
from .RF import (
    PIDElement,
    LLRFElement,
    RFModulatorElement,
    RFProtectionElement,
    RFHeartbeatElement,
    RFCavityElement,
    RFDeflectingCavityElement,
    WakefieldElement,
)
from .shutter import ShutterElement, ValveElement
from .simulation import (
    ApertureElement,
    RFCavitySimulationElement,
    WakefieldSimulationElement,
)
import yaml
from collections.abc import MutableMapping


def flatten(dictionary, parent_key="", separator="_"):
    items = []
    for key, value in dictionary.items():
        new_key = parent_key + separator + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(flatten(value, new_key, separator=separator).items())
        else:
            items.append((new_key, value))
    return dict(items)


class string_with_quotes(str):
    pass


class flow_list(list):
    pass


def flow_list_rep(dumper, data):
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)


def quoted_presenter(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


yaml.add_representer(string_with_quotes, quoted_presenter)
yaml.add_representer(flow_list, flow_list_rep)


class _baseElement(IgnoreExtra):
    name: str
    hardware_class: str
    hardware_type: str
    hardware_model: str = Field(default="Generic", frozen=True)
    machine_area: str
    virtual_name: str = ""
    alias: Union[str, list, Aliases, None] = Field(alias="name_alias", default=None)
    subelement: bool | str = False

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: str) -> str:
        assert isinstance(v, str)
        try:
            PV(pv_string=str(v) + ":")
        except Exception:
            raise ValueError("name is not a valid element name")
        return v

    @field_validator("alias", mode="before")
    @classmethod
    def validate_alias(cls, v: Union[str, List, None]) -> Aliases:
        # print(list(map(str.strip, v.split(','))))
        if isinstance(v, str):
            return Aliases(aliases=list(map(str.strip, v.split(","))))
        elif isinstance(v, (list, tuple)):
            return Aliases(aliases=list(v))
        elif isinstance(v, (dict)):
            return Aliases(aliases=v["aliases"])
        elif v is None:
            return Aliases(aliases=[])
        else:
            raise ValueError("alias should be a string or a list of strings")

    def escape_string_list(self, escapes) -> str:
        if len(list(escapes)) > 0:
            return string_with_quotes(",".join(map(str, list(escapes))))
        return string_with_quotes("")

    @classmethod
    def from_CATAP(cls: Type[T], fields: dict) -> T:
        return cls(**fields)

    def generate_aliases(self) -> list:
        magnetPV = PV.fromString(str(self.name) + ":")  # ('CLA', 'S07', 'QUAD', 1)
        return [
            magnetPV.area + "-" + magnetPV.typename + str(magnetPV.index).zfill(2),
            magnetPV.area + "-" + magnetPV.typename + str(magnetPV._indexString),
            magnetPV.area + "-" + magnetPV.typename + str(magnetPV.index),
        ]

    def to_CATAP(self) -> dict:
        aliases = (
            ",".join(self.alias.aliases)
            if self.alias is not None
            else self.generate_aliases()
        )
        return {
            "machine_area": self.machine_area,
            "hardware_type": self.hardware_type,
            "name": self.name,
            # 'virtual_name': self.virtual_name,
            "name_alias": ",".join(map(str, list(aliases))),
        }

    @property
    def no_controls(self) -> str:
        return (
            self.__class__.__name__
            + "("
            + " ".join(
                [
                    k + "=" + getattr(self, k).__repr__()
                    for k in self.model_fields.keys()
                    if k != "controls"
                ]
            )
            + ")"
        )

    @property
    def subdirectory(self) -> str:
        if self.__class__.__name__ == self.hardware_type:
            return os.path.join(self.hardware_class, self.hardware_type)
        return os.path.join(
            self.hardware_class, self.__class__.__name__, self.hardware_type
        )

    @property
    def YAML_filename(self) -> str:
        return os.path.join(self.subdirectory, self.name + ".yaml")

    @property
    def hardware_info(self) -> dict:
        return {"class": self.hardware_class, "type": self.hardware_type}

    def flat(self):
        return flatten(self.model_dump(), parent_key="", separator="_")

    def is_subelement(self) -> bool:
        if str(self.subelement).lower() == "false":
            return False
        elif str(self.subelement).lower() == "true":
            return True
        if isinstance(self.subelement, bool):
            return self.subelement
        else:
            return isinstance(self.subelement, str)


class PhysicalElement(_baseElement):
    """Element with physical, degaussable, electrical, manufacturer, and controls items."""

    physical: PhysicalElement

    def to_CATAP(self):
        catap_dict = super().to_CATAP()
        catap_dict.update(
            {
                "position": list(self.physical.middle)[2],
            }
        )
        return catap_dict

    @property
    def bend_angle(self):
        return Rotation.from_list([0, 0, 0])

    @property
    def start_angle(self):
        return self.physical.rotation + self.physical.global_rotation

    @property
    def end_angle(self):
        return self.start_angle


class Element(PhysicalElement):
    """Element with physical, electrical and manufacturer items."""

    electrical: ElectricalElement
    manufacturer: ManufacturerElement

    def to_CATAP(self):
        catap_dict = super().to_CATAP()
        catap_dict.update(
            {
                "manufacturer": self.manufacturer.manufacturer,
                "serial_number": self.manufacturer.serial_number,
            }
        )
        return catap_dict


class Magnet(Element):
    """Element with physical, electrical, manufacturer, controls and degauss items."""

    hardware_class: str = Field(default="Magnet", frozen=True)
    controls: MagnetPV
    degauss: DegaussablElement
    magnetic: None = None

    @property
    def bend_angle(self):
        return Rotation.from_list([0, 0, self.magnetic.angle])

    @property
    def end_angle(self):
        return self.start_angle + self.bend_angle

    # @field_validator('type', mode='before')
    # @classmethod
    # def validate_type(cls, v: str) -> str:
    #     # print(list(map(str.strip, v.split(','))))
    #     if isinstance(v, str):
    #         return v.upper()
    #     else:
    #         raise ValueError('alias should be a string or a list of strings')

    def to_CATAP(self):
        catap_dict = super().to_CATAP()
        catap_dict.update(
            {
                "mag_type": self.type,
                "degauss_tolerance": self.degauss.tolerance,
                "degauss_values": self.escape_string_list(self.degauss.values),
                "num_degauss_steps": self.degauss.steps,
                "field_integral_coefficients": self.escape_string_list(
                    self.magnetic.field_integral_coefficients
                ),
                "linear_saturation_coefficients": self.escape_string_list(
                    self.magnetic.linear_saturation_coefficients
                ),
                "mag_set_max_wait_time": self.magnetic.settle_time,
                "magnetic_length": 1000 * self.magnetic.length,
                "ri_tolerance": self.electrical.read_tolerance,
                "min_i": self.electrical.minI,
                "max_i": self.electrical.maxI,
            }
        )
        return catap_dict

    # @property
    # def subdirectory(self):
    #     return os.path.join(self.hardware_type,self.type)


class Dipole(Magnet):
    """Dipole element."""

    hardware_type: str = Field(default="Dipole", frozen=True)
    magnetic: Dipole_Magnet


class Quadrupole(Magnet):
    """Quadrupole element."""

    hardware_type: str = Field(default="Quadrupole", frozen=True)
    magnetic: Quadrupole_Magnet


class Sextupole(Magnet):
    """Sextupole element."""

    hardware_type: str = Field(default="Sextupole", frozen=True)
    magnetic: Sextupole_Magnet


class Horizontal_Corrector(Dipole):
    """Horizontal Corrector element."""

    hardware_type: str = Field(default="Horizontal_Corrector", frozen=True)


class Vertical_Corrector(Dipole):
    """Vertical Corrector element."""

    hardware_type: str = Field(default="Vertical_Corrector", frozen=True)


class Combined_Corrector(Dipole):
    """H&V Corrector element."""

    hardware_type: str = Field(default="Combined_Corrector", frozen=True)
    Horizontal_Corrector: str | None = Field(default=None, frozen=True)
    Vertical_Corrector: str | None = Field(default=None, frozen=True)


class Solenoid(Magnet):
    """Solenoid element."""

    hardware_type: str = Field(default="Solenoid", frozen=True)
    magnetic: Solenoid_Magnet


class Diagnostic(PhysicalElement):
    hardware_class: str = Field(default="Diagnostic", frozen=True)


class BPM(Diagnostic):
    """BPM element."""

    hardware_type: str = Field(default="BPM", frozen=True)
    hardware_model: str = Field(default="Stripline", frozen=True)
    diagnostic: BPM_Diagnostic
    controls: BPMPV

    def to_CATAP(self):
        catap_dict = super().to_CATAP()
        catap_dict.update(
            {
                "bpm_type": self.diagnostic.type,
                "bpm_set_max_wait_time": self.diagnostic.settle_time,
                "att1cal": self.diagnostic.attenuation1_calibration,
                "att2cal": self.diagnostic.attenuation2_calibration,
                "v1cal": self.diagnostic.voltage1_calibration,
                "v2cal": self.diagnostic.voltage2_calibration,
                "qcal": self.diagnostic.charge_calibration,
                "mn": self.diagnostic.mn,
                "xn": self.diagnostic.xn,
                "yn": self.diagnostic.yn,
            }
        )
        return catap_dict


class BAM(Diagnostic):
    """BAM element."""

    hardware_type: str = Field(default="BAM", frozen=True)
    hardware_model: str = Field(default="DESY", frozen=True)
    diagnostic: BAM_Diagnostic
    controls: BAMPV


class BLM(Diagnostic):
    """BLM element."""

    hardware_type: str = Field(default="BLM", frozen=True)
    hardware_model: str = Field(default="CDR", frozen=True)
    diagnostic: BLM_Diagnostic
    controls: BLMPV


class Camera(Diagnostic):
    """Camera element."""

    hardware_type: str = Field(default="Camera", frozen=True)
    hardware_model: str = Field(default="PCO", frozen=True)
    diagnostic: Camera_Diagnostic
    controls: CameraPV


class Screen(Diagnostic):
    """Screen element."""

    hardware_type: str = Field(default="Screen", frozen=True)
    hardware_model: str = Field(default="YAG", frozen=True)
    diagnostic: Screen_Diagnostic
    controls: ScreenPV

    def to_CATAP(self):
        catap_dict = super().to_CATAP()
        catap_dict.update(
            {
                "screen_type": self.diagnostic.type,
                "has_camera": self.diagnostic.has_camera,
                "camera_name": self.diagnostic.camera_name,
                "devices": self.escape_string_list(self.diagnostic.devices),
            }
        )
        return catap_dict


class ChargeDiagnostic(Diagnostic):
    """Charge Diagnostic element."""

    hardware_type: str = Field(default="ChargeDiagnostic", frozen=True)
    diagnostic: Charge_Diagnostic
    controls: ChargeDiagnosticPV


class WCM(ChargeDiagnostic):
    """WCM Charge Diagnostic element."""

    hardware_type: str = Field(default="WCM", frozen=True)


class FCM(ChargeDiagnostic):
    """FCM Charge Diagnostic element."""

    hardware_type: str = Field(default="FCM", frozen=True)


class ICT(ChargeDiagnostic):
    """FCM Charge Diagnostic element."""

    hardware_type: str = Field(default="ICT", frozen=True)


class VacuumGuage(PhysicalElement):
    """Vacuum Guage element."""

    hardware_type: str = Field(default="VacuumGuage", frozen=True)
    hardware_model: str = Field(default="IMG", frozen=True)
    manufacturer: ManufacturerElement
    controls: VacuumGuagePV


class LaserEnergyMeter(PhysicalElement):
    """Laser Energy Meter element."""

    hardware_type: str = Field(default="LaserEnergyMeter", frozen=True)
    hardware_model: str = Field(default="Gentec Photodiode", frozen=True)
    laser: LaserEnergyMeterElement
    controls: LaserEnergyMeterPV


class LaserHalfWavePlate(LaserEnergyMeter):
    """Laser Half Wave Plate element."""

    hardware_type: str = Field(default="LaserHalfWavePlate", frozen=True)
    hardware_model: str = Field(default="Newport", frozen=True)
    laser: LaserElement
    controls: LaserHWPPV


class LaserMirror(LaserEnergyMeter):
    """Laser Mirror element."""

    hardware_type: str = Field(default="LaserMirror", frozen=True)
    hardware_model: str = Field(default="Planar", frozen=True)
    laser: LaserMirrorElement
    controls: LaserMirrorPV


class Lighting(_baseElement):
    """Lighting element."""

    hardware_type: str = Field(default="Lighting", frozen=True)
    hardware_model: str = Field(default="LED", frozen=True)
    lights: LightingElement
    controls: LightingPV


class PID(_baseElement):
    """PID element."""

    hardware_type: str = Field(default="PID", frozen=True)
    hardware_model: str = Field(default="RF", frozen=True)
    PID: PIDElement
    controls: PIDPV


class LLRF(_baseElement):
    """LLRF element."""

    hardware_type: str = Field(default="LLRF", frozen=True)
    hardware_model: str = Field(default="Libera", frozen=True)
    LLRF: LLRFElement
    controls: LLRFPV


class RFCavity(PhysicalElement):
    """RFCavity element."""

    hardware_type: str = Field(default="RFCavity", frozen=True)
    hardware_model: str = Field(default="SBand", frozen=True)
    cavity: RFCavityElement
    simulation: RFCavitySimulationElement


class Wakefield(PhysicalElement):
    """Collimator element."""

    hardware_type: str = Field(default="Wakefield", frozen=True)
    hardware_model: str = Field(default="Dielectric", frozen=True)
    cavity: WakefieldElement
    simulation: WakefieldSimulationElement


class RFDeflectingCavity(PhysicalElement):
    """RFCavity element."""

    hardware_type: str = Field(default="RFDeflectingCavity", frozen=True)
    hardware_model: str = Field(default="SBand", frozen=True)
    cavity: RFDeflectingCavityElement
    simulation: RFCavitySimulationElement


class RFModulator(_baseElement):
    """RFModulator element."""

    hardware_type: str = Field(default="RFModulator", frozen=True)
    hardware_model: str = Field(default="Thales", frozen=True)
    modulator: RFModulatorElement
    controls: RFModulatorPV


class RFProtection(_baseElement):
    """RFProtection element."""

    hardware_type: str = Field(default="RFProtection", frozen=True)
    hardware_model: str = Field(default="PROT", frozen=True)
    modulator: RFProtectionElement
    controls: RFProtectionPV


class RFHeartbeat(_baseElement):
    """RFHeartbeat element."""

    hardware_type: str = Field(default="RFHeartbeat", frozen=True)
    heartbeat: RFHeartbeatElement
    controls: RFHeartbeatPV


class Shutter(PhysicalElement):
    """Shutter element."""

    hardware_type: str = Field(default="Shutter", frozen=True)
    shutter: ShutterElement
    controls: ShutterPV


class Valve(PhysicalElement):
    """Valve element."""

    hardware_type: str = Field(default="Valve", frozen=True)
    valve: ValveElement
    controls: ValvePV


class Marker(PhysicalElement):
    """Marker element."""

    hardware_type: str = Field(default="Marker", frozen=True)
    hardware_model: str = Field(default="Simulation", frozen=True)


class Aperture(PhysicalElement):
    """Aperture element."""

    hardware_type: str = Field(default="Aperture", frozen=True)
    hardware_model: str = Field(default="Simulation", frozen=True)
    aperture: ApertureElement


class Collimator(Aperture):
    """Collimator element."""

    hardware_type: str = Field(default="Collimator", frozen=True)
    hardware_model: str = Field(default="Simulation", frozen=True)
