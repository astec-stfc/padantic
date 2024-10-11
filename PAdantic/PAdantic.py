import os
from pydantic import field_validator
from .models.elementList import MachineModel
from .Importers.YAML_Loader import read_YAML_Element_File, read_YAML_Combined_File
import glob

from yaml.constructor import Constructor


def add_bool(self, node):
    return self.construct_scalar(node)


Constructor.add_constructor("tag:yaml.org,2002:bool", add_bool)


class PAdantic(MachineModel):
    yaml_dir: str

    @field_validator("yaml_dir", mode="before")
    @classmethod
    def validate_yaml_dir(cls, v: str) -> str:
        if os.path.isfile(v):
            return v
        elif os.path.isfile(os.path.abspath(os.path.dirname(__file__) + "/" + v)):
            return os.path.abspath(os.path.dirname(__file__) + "/" + v)
        elif os.path.isdir(v):
            return v
        elif os.path.isdir(os.path.abspath(os.path.dirname(__file__) + "/" + v)):
            return os.path.abspath(os.path.dirname(__file__) + "/" + v)
        else:
            raise ValueError(f"Directory {v} does not exist")

    def model_post_init(self, __context):
        super().model_post_init(__context)
        if os.path.isfile(self.yaml_dir):
            yaml_elems = read_YAML_Combined_File(self.yaml_dir)
        elif os.path.isdir(self.yaml_dir):
            YAML_files = glob.glob(
                os.path.abspath(self.yaml_dir + "/**/*.yaml"), recursive=True
            )
            yaml_elems = [read_YAML_Element_File(y) for y in YAML_files]
        self.update({y.name: y for y in yaml_elems})

    def get_all_diagnostics(self, end: str = None, start: str = None):
        return self.elements_between(start=start, end=end, element_class="diagnostic")

    def get_all_charge_diagnostics(self, end: str = None, start: str = None):
        return self.elements_between(start=start, end=end, element_class="diagnostic", element_type=["FCM", "WCM", "ICT"])

    def get_all_position_diagnostics(self, end: str = None, start: str = None):
        return self.elements_between(start=start, end=end, element_class="diagnostic", element_type=["Screen", "BPM"])

    def get_all_cameras(self, end: str = None, start: str = None):
        return [self[scr].diagnostic.camera_name for scr in self.elements_between(start=start, end=end, element_class="diagnostic", element_type="Screen")]

    def get_all_screens_and_cameras(self, end: str = None, start: str = None):
        return {scr: self[scr].diagnostic.camera_name for scr in self.elements_between(start=start, end=end, element_class="diagnostic", element_type="Screen")}

    def get_all_magnets(self, end: str = None, start: str = None):
        return self.elements_between(start=start, end=end, element_class="magnet")

    def get_all_quadrupoles(self, end: str = None, start: str = None):
        return self.elements_between(start=start, end=end, element_class="magnet", element_type="quadrupole")

    def get_all_dipoles(self, end: str = None, start: str = None):
        return self.elements_between(start=start, end=end, element_class="magnet", element_type="dipole")

    def get_all_correctors(self, end: str = None, start: str = None):
        return self.elements_between(start=start, end=end, element_class="magnet", element_type=["corrector", "horizontal_corrector", "vertical_corrector"])

    def get_all_sextupoles(self, end: str = None, start: str = None):
        return self.elements_between(start=start, end=end, element_class="magnet", element_type="sextupole")

    def get_all_solenoids(self, end: str = None, start: str = None):
        return self.elements_between(start=start, end=end, element_class="magnet", element_type="solenoid")

    def get_all_vacuum_components(self, end: str = None, start: str = None):
        return self.elements_between(start=start, end=end, element_class="vacuum")

    def get_all_shutters(self, end: str = None, start: str = None):
        return self.elements_between(start=start, end=end, element_class="vacuum", element_type="shutter")
