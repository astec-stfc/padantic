import os
import glob
from more_itertools import flatten
from pydantic import field_validator
from yaml.constructor import Constructor
from .models.elementList import MachineModel
from .Importers.YAML_Loader import read_YAML_Element_File, read_YAML_Combined_File


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

    def get_rf_cavities(self, end: str = None, start: str = None, path: str = None):
        return self.elements_between(
            start=start, end=end, element_class="rf", path=path
        )

    def get_diagnostics(self, end: str = None, start: str = None, path: str = None):
        return self.elements_between(
            start=start, end=end, element_class="diagnostic", path=path
        )

    def get_charge_diagnostics(
        self, end: str = None, start: str = None, path: str = None
    ):
        return self.elements_between(
            start=start,
            end=end,
            element_class="diagnostic",
            element_type=["FCM", "WCM", "ICT"],
            path=path,
        )

    def get_beam_position_monitors(
        self, end: str = None, start: str = None, path: str = None
    ):
        return self.elements_between(
            start=start,
            end=end,
            element_class="diagnostic",
            element_type="BPM",
            path=path,
        )

    def get_position_diagnostics(
        self, end: str = None, start: str = None, path: str = None
    ):
        return self.elements_between(
            start=start,
            end=end,
            element_class="diagnostic",
            element_type=["Screen", "BPM"],
            path=path,
        )

    def get_cameras(self, end: str = None, start: str = None, path: str = None):
        return [
            self[scr].diagnostic.camera_name
            for scr in self.elements_between(
                start=start,
                end=end,
                element_class="diagnostic",
                element_type="Screen",
                path=path,
            )
        ]

    def get_screens_and_cameras(
        self, end: str = None, start: str = None, path: str = None
    ):
        return {
            scr: self[scr].diagnostic.camera_name
            for scr in self.elements_between(
                start=start,
                end=end,
                element_class="diagnostic",
                element_type="Screen",
                path=path,
            )
        }

    def get_magnets(self, end: str = None, start: str = None, path: str = None):
        return self.elements_between(
            start=start, end=end, element_class="magnet", path=path
        )

    def get_quadrupoles(self, end: str = None, start: str = None, path: str = None):
        return self.elements_between(
            start=start,
            end=end,
            element_class="magnet",
            element_type="quadrupole",
            path=path,
        )

    def get_dipoles(self, end: str = None, start: str = None, path: str = None):
        return self.elements_between(
            start=start,
            end=end,
            element_class="magnet",
            element_type="dipole",
            path=path,
        )

    def __get_combined_corrector_sub_correctors(self, elem: str):
        if hasattr(self[elem], "Horizontal_Corrector") and self[elem].Horizontal_Corrector is not None:
            if hasattr(self[elem], "Vertical_Corrector") and self[elem].Vertical_Corrector is not None:
                return [self[elem].Horizontal_Corrector, self[elem].Vertical_Corrector]
            else:
                return [self[elem].Horizontal_Corrector]
        elif hasattr(self[elem], "Vertical_Corrector") and self[elem].Vertical_Corrector is not None:
            return [self[elem].Vertical_Corrector]
        else:
            return [elem]

    def get_correctors(self, end: str = None, start: str = None, path: str = None):
        correctors = self.elements_between(
            start=start,
            end=end,
            element_class="magnet",
            element_type=["combined_corrector", "horizontal_corrector", "vertical_corrector"],
            path=path,
        )
        return list(flatten([
            (
                self.__get_combined_corrector_sub_correctors(c)
            )
            for c in correctors
        ]))

    def get_horizontal_correctors(
        self, end: str = None, start: str = None, path: str = None
    ):
        horizontal_correctors = self.elements_between(
            start=start,
            end=end,
            element_class="magnet",
            element_type=["combined_corrector", "horizontal_corrector"],
            path=path,
        )
        return [
            (
                self[c].Horizontal_Corrector
                if hasattr(self[c], "Horizontal_Corrector")
                and self[c].Horizontal_Corrector is not None
                else c
            )
            for c in horizontal_correctors
        ]

    def get_vertical_correctors(
        self, end: str = None, start: str = None, path: str = None
    ):
        vertical_correctors = self.elements_between(
            start=start,
            end=end,
            element_class="magnet",
            element_type=["combined_corrector", "Vertical_Corrector"],
            path=path,
        )
        return [
            (
                self[c].Vertical_Corrector
                if hasattr(self[c], "Vertical_Corrector")
                and self[c].Vertical_Corrector is not None
                else c
            )
            for c in vertical_correctors
        ]

    def get_lattice_correctors(
        self, end: str = None, start: str = None, path: str = None
    ):
        return self.elements_between(
            start=start,
            end=end,
            element_class="magnet",
            element_type=["combined_corrector", "horizontal_corrector", "vertical_corrector"],
            path=path,
        )

    def get_sextupoles(self, end: str = None, start: str = None, path: str = None):
        return self.elements_between(
            start=start,
            end=end,
            element_class="magnet",
            element_type="sextupole",
            path=path,
        )

    def get_solenoids(self, end: str = None, start: str = None, path: str = None):
        return self.elements_between(
            start=start,
            end=end,
            element_class="magnet",
            element_type="solenoid",
            path=path,
        )

    def get_vacuum_components(
        self, end: str = None, start: str = None, path: str = None
    ):
        return self.elements_between(
            start=start, end=end, element_class="vacuum", path=path
        )

    def get_shutters(self, end: str = None, start: str = None, path: str = None):
        return self.elements_between(
            start=start,
            end=end,
            element_class="vacuum",
            element_type="shutter",
            path=path,
        )

    def __all_elements(
        self, element_class: str | None = None, element_type: str | None = None
    ) -> set:
        return set(
            [
                elem
                for pathelems in [
                    self.elements_between(
                        start=None,
                        end=None,
                        element_class=element_class,
                        element_type=element_type,
                        path=path,
                    )
                    for path in self.lattices.keys()
                ]
                for elem in pathelems
            ]
        )

    @property
    def all_elements(self):
        return self.__all_elements()

    @property
    def all_rf_cavities(self):
        return self.__all_elements(element_class="rf")

    @property
    def all_diagnostics(self):
        return self.__all_elements(element_class="diagnostic")

    @property
    def all_charge_diagnostics(self) -> set:
        return self.__all_elements(
            element_class="diagnostic",
            element_type=["FCM", "WCM", "ICT"],
        )

    @property
    def all_beam_position_monitors(self) -> set:
        return self.__all_elements(
            element_class="diagnostic",
            element_type="BPM",
        )

    @property
    def all_position_diagnostics(self) -> set:
        return self.__all_elements(
            element_class="diagnostic",
            element_type=["Screen", "BPM"],
        )

    @property
    def all_cameras(self) -> set:
        return [
            self[scr].diagnostic.camera_name
            for scr in self.__all_elements(
                element_class="diagnostic",
                element_type="Screen",
            )
        ]

    @property
    def all_screens_and_cameras(self) -> set:
        return {
            scr: self[scr].diagnostic.camera_name
            for scr in self.__all_elements(
                element_class="diagnostic",
                element_type="Screen",
            )
        }

    @property
    def all_magnets(self) -> set:
        return self.__all_elements(element_class="magnet")

    @property
    def all_quadrupoles(self) -> set:
        return self.__all_elements(
            element_class="magnet",
            element_type="quadrupole",
        )

    @property
    def all_dipoles(self) -> set:
        return self.__all_elements(
            element_class="magnet",
            element_type="dipole",
        )

    @property
    def all_correctors(self) -> set:
        return set(
            [
                elem
                for pathelems in [
                    self.get_correctors(
                        start=None,
                        end=None,
                        path=path,
                    )
                    for path in self.lattices.keys()
                ]
                for elem in pathelems
            ]
        )

    @property
    def all_horizontal_correctors(self) -> set:
        return set(
            [
                elem
                for pathelems in [
                    self.get_horizontal_correctors(
                        start=None,
                        end=None,
                        path=path,
                    )
                    for path in self.lattices.keys()
                ]
                for elem in pathelems
            ]
        )

    @property
    def all_vertical_correctors(self) -> set:
        return set(
            [
                elem
                for pathelems in [
                    self.get_vertical_correctors(
                        start=None,
                        end=None,
                        path=path,
                    )
                    for path in self.lattices.keys()
                ]
                for elem in pathelems
            ]
        )

    @property
    def all_sextupoles(self) -> set:
        return self.__all_elements(
            element_class="magnet",
            element_type="sextupole",
        )

    @property
    def all_solenoids(self) -> set:
        return self.__all_elements(
            element_class="magnet",
            element_type="solenoid",
        )

    @property
    def all_vacuum_components(self) -> set:
        return self.__all_elements(element_class="vacuum")

    @property
    def all_shutters(self) -> set:
        return self.__all_elements(
            element_class="vacuum",
            element_type="shutter",
        )
