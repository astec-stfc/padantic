import os
from typing import Type, List, Union
from pydantic import field_validator, Field

from PAdantic.models.control import ControlsInformation

from .baseModels import T, Aliases, IgnoreExtra
from .manufacturer import ManufacturerElement
from .electrical import ElectricalElement
from .degauss import DegaussableElement
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
        # try:
        #     PV(pv=str(v) + ":")
        # except Exception:
        #     raise ValueError("name is not a valid element name")
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

    # def generate_aliases(self) -> list:
    #     magnetPV = PV.fromString(str(self.name) + ":")  # ('CLA', 'S07', 'QUAD', 1)
    #     return [
    #         magnetPV.area + "-" + magnetPV.typename + str(magnetPV.index).zfill(2),
    #         magnetPV.area + "-" + magnetPV.typename + str(magnetPV._indexString),
    #         magnetPV.area + "-" + magnetPV.typename + str(magnetPV.index),
    #     ]

    def to_CATAP(self) -> dict:
        return {
            "machine_area": self.machine_area,
            "hardware_type": self.hardware_type,
            "name": self.name,
            # 'virtual_name': self.virtual_name,
            "name_alias": (
                self.alias.aliases if isinstance(self.alias, Aliases) else self.alias
            ),
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


class PhysicalBaseElement(_baseElement):
    """Element with physical, degaussable, electrical, manufacturer, and controls items."""

    physical: PhysicalElement = PhysicalElement()

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


class Element(PhysicalBaseElement):
    """Element with physical, electrical and manufacturer items."""

    electrical: ElectricalElement = ElectricalElement()
    manufacturer: ManufacturerElement = ManufacturerElement()
    controls: ControlsInformation | None = None

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
    degauss: DegaussableElement = DegaussableElement()
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
                "mag_type": self.hardware_type,
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
    magnetic: Dipole_Magnet = Dipole_Magnet()


class Quadrupole(Magnet):
    """Quadrupole element."""

    hardware_type: str = Field(default="Quadrupole", frozen=True)
    magnetic: Quadrupole_Magnet = Quadrupole_Magnet()


class Sextupole(Magnet):
    """Sextupole element."""

    hardware_type: str = Field(default="Sextupole", frozen=True)
    magnetic: Sextupole_Magnet = Sextupole_Magnet()


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


class Diagnostic(Element):
    hardware_class: str = Field(default="Diagnostic", frozen=True)


class BPM(Diagnostic):
    """BPM element."""

    hardware_type: str = Field(default="BPM", frozen=True)
    hardware_model: str = Field(default="Stripline", frozen=True)
    diagnostic: BPM_Diagnostic

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


class BLM(Diagnostic):
    """BLM element."""

    hardware_type: str = Field(default="BLM", frozen=True)
    hardware_model: str = Field(default="CDR", frozen=True)
    diagnostic: BLM_Diagnostic


class Camera(Diagnostic):
    """Camera element."""

    hardware_type: str = Field(default="Camera", frozen=True)
    hardware_model: str = Field(default="PCO", frozen=True)
    diagnostic: Camera_Diagnostic


class Screen(Diagnostic):
    """Screen element."""

    hardware_type: str = Field(default="Screen", frozen=True)
    hardware_model: str = Field(default="YAG", frozen=True)
    diagnostic: Screen_Diagnostic

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


class WCM(ChargeDiagnostic):
    """WCM Charge Diagnostic element."""

    hardware_type: str = Field(default="WCM", frozen=True)


class FCM(ChargeDiagnostic):
    """FCM Charge Diagnostic element."""

    hardware_type: str = Field(default="FCM", frozen=True)


class ICT(ChargeDiagnostic):
    """FCM Charge Diagnostic element."""

    hardware_type: str = Field(default="ICT", frozen=True)


class VacuumGauge(Element):
    """Vacuum Gauge element."""

    hardware_type: str = Field(default="VacuumGauge", frozen=True)
    hardware_model: str = Field(default="IMG", frozen=True)
    manufacturer: ManufacturerElement


class LaserEnergyMeter(Element):
    """Laser Energy Meter element."""

    hardware_type: str = Field(default="LaserEnergyMeter", frozen=True)
    hardware_model: str = Field(default="Gentec Photodiode", frozen=True)
    laser: LaserEnergyMeterElement


class LaserHalfWavePlate(Element):
    """Laser Half Wave Plate element."""

    hardware_type: str = Field(default="LaserHalfWavePlate", frozen=True)
    hardware_model: str = Field(default="Newport", frozen=True)
    laser: LaserElement


class LaserMirror(Element):
    """Laser Mirror element."""

    hardware_type: str = Field(default="LaserMirror", frozen=True)
    hardware_model: str = Field(default="Planar", frozen=True)
    laser: LaserMirrorElement


class Lighting(_baseElement):
    """Lighting element."""

    hardware_type: str = Field(default="Lighting", frozen=True)
    hardware_model: str = Field(default="LED", frozen=True)
    lights: LightingElement


class PID(_baseElement):
    """PID element."""

    hardware_type: str = Field(default="PID", frozen=True)
    hardware_model: str = Field(default="RF", frozen=True)
    PID: PIDElement


class LLRF(_baseElement):
    """LLRF element."""

    hardware_type: str = Field(default="LLRF", frozen=True)
    hardware_model: str = Field(default="Libera", frozen=True)
    LLRF: LLRFElement


class RFCavity(Element):
    """RFCavity element."""

    hardware_type: str = Field(default="RFCavity", frozen=True)
    hardware_model: str = Field(default="SBand", frozen=True)
    cavity: RFCavityElement
    simulation: RFCavitySimulationElement


class Wakefield(PhysicalBaseElement):
    """Collimator element."""

    hardware_type: str = Field(default="Wakefield", frozen=True)
    hardware_model: str = Field(default="Dielectric", frozen=True)
    cavity: WakefieldElement
    simulation: WakefieldSimulationElement


class RFDeflectingCavity(RFCavity):
    """RFCavity element."""

    hardware_type: str = Field(default="RFDeflectingCavity", frozen=True)
    hardware_model: str = Field(default="SBand", frozen=True)
    cavity: RFDeflectingCavityElement


class RFModulator(_baseElement):
    """RFModulator element."""

    hardware_type: str = Field(default="RFModulator", frozen=True)
    hardware_model: str = Field(default="Thales", frozen=True)
    modulator: RFModulatorElement


class RFProtection(_baseElement):
    """RFProtection element."""

    hardware_type: str = Field(default="RFProtection", frozen=True)
    hardware_model: str = Field(default="PROT", frozen=True)
    modulator: RFProtectionElement


class RFHeartbeat(_baseElement):
    """RFHeartbeat element."""

    hardware_type: str = Field(default="RFHeartbeat", frozen=True)
    heartbeat: RFHeartbeatElement


class Shutter(Element):
    """Shutter element."""

    hardware_type: str = Field(default="Shutter", frozen=True)
    shutter: ShutterElement


class Valve(Element):
    """Valve element."""

    hardware_type: str = Field(default="Valve", frozen=True)
    valve: ValveElement


class Marker(PhysicalBaseElement):
    """Marker element."""

    hardware_type: str = Field(default="Marker", frozen=True)
    hardware_model: str = Field(default="Simulation", frozen=True)


class Aperture(PhysicalBaseElement):
    """Aperture element."""

    hardware_type: str = Field(default="Aperture", frozen=True)
    hardware_model: str = Field(default="Simulation", frozen=True)
    aperture: ApertureElement


class Collimator(Aperture):
    """Collimator element."""

    hardware_type: str = Field(default="Collimator", frozen=True)
    hardware_model: str = Field(default="Simulation", frozen=True)


class Drift(PhysicalBaseElement):
    hardware_type: str = Field(default="Drift", frozen=True)
