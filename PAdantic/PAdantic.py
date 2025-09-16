import os
import glob
from math import copysign
from itertools import chain
from typing import List
from pydantic import field_validator
from yaml.constructor import Constructor

from PAdantic.models.physical import PhysicalElement, Position
from .models.elementList import MachineModel, _baseElement
from .models.element import Drift
from .Importers.YAML_Loader import (
    read_YAML_Combined_File,
    read_YAML_Element_Files,
    interpret_YAML_Element,
)
import numpy as np


def flatten(xss):
    """Flatten a list of lists."""
    return list(chain.from_iterable(xss))


def add_bool(self, node):
    return self.construct_scalar(node)


Constructor.add_constructor("tag:yaml.org,2002:bool", add_bool)


def dot(a, b) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def chunks(li, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(li), n):
        yield li[i: i + n]


class PAdantic(MachineModel):
    element_list: str | List[_baseElement]

    @field_validator("element_list", mode="before")
    @classmethod
    def validate_element_list(cls, v: str | list) -> str | list:
        if isinstance(v, str):
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
        else:
            return v

    def model_post_init(self, __context):
        super().model_post_init(__context)
        if isinstance(self.element_list, str):
            if os.path.isfile(self.element_list):
                elems = read_YAML_Combined_File(self.element_list)
            elif os.path.isdir(self.element_list):
                files = glob.glob(
                    os.path.abspath(self.element_list + "/**/*.yaml"), recursive=True
                )
                data = read_YAML_Element_Files(files)
                elems = [interpret_YAML_Element(data) for data in data]
        else:
            elems = self.element_list
        self.update({y.name: y for y in elems})

    def createDrifts(self, end: str = None, start: str = None, path: str = None):
        """Insert drifts into a sequence of 'elements'"""
        positions = []
        originalelements = dict()
        elementno = 0
        newelements = dict()

        elements = self.elements_between(
            start=start, end=end, element_class=None, path=path
        )

        for name in elements:
            elem = self.elements[name]
            originalelements[name] = elem
            pos = elem.physical.start.array
            positions.append(pos)
            positions.append(elem.physical.end.array)
        positions = positions[1:]
        positions.append(positions[-1])
        driftdata = list(
            zip(iter(list(originalelements.items())), list(chunks(positions, 2)))
        )

        for e, d in driftdata:
            newelements[e[0]] = e[1]
            if len(d) > 1:
                x1, y1, z1 = d[0]
                x2, y2, z2 = d[1]
                try:
                    length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
                    vector = dot((d[1] - d[0]), [0, 0, 1])
                except Exception as exc:
                    print("Element with error = ", e[0])
                    print(d)
                    raise exc
                if round(length, 6) > 0:
                    elementno += 1
                    name = "drift" + str(elementno)
                    x, y, z = [(a + b) / 2.0 for a, b in zip(d[0], d[1])]
                    newdrift = Drift(
                        name=name,
                        machine_area=newelements[e[0]].machine_area,
                        hardware_class="drift",
                        physical=PhysicalElement(
                            length=round(copysign(length, vector), 6),
                            middle=Position(x=x, y=y, z=z),
                            datum=Position(x=x, y=y, z=z),
                        ),
                    )
                    newelements[name] = newdrift
        return newelements

    def get_elements(self, end: str = None, start: str = None, path: str = None):
        return self.elements_between(
            start=start, end=end, element_class=None, path=path
        )

    def _drift_length(self, start: list[float], end: list[float]):
        return np.linalg.norm(end - start)

    def get_elements_s_pos(self, end: str = None, start: str = None, path: str = None):
        elements = self.createDrifts(start=start, end=end, path=path)
        start_and_end = [
            [name, elem.physical.length, elem.hardware_type == "Drift"]
            for name, elem in elements.items()
        ]
        elem_s = {}
        s_pos = 0
        for elem, l, drift in start_and_end:
            s_pos += l
            if not drift:
                elem_s[elem] = round(s_pos, 6)
        return elem_s

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
            scr: self[scr].diagnostic
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

    def get_separate_magnets(
        self, end: str = None, start: str = None, path: str = None
    ):
        magnets = self.get_magnets(end=end, start=start, path=path)
        return list(
            flatten(
                [(self.__get_combined_corrector_sub_correctors(c)) for c in magnets]
            )
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
        if (
            hasattr(self[elem], "Horizontal_Corrector")
            and self[elem].Horizontal_Corrector is not None
        ):
            if (
                hasattr(self[elem], "Vertical_Corrector")
                and self[elem].Vertical_Corrector is not None
            ):
                return [self[elem].Horizontal_Corrector, self[elem].Vertical_Corrector]
            else:
                return [self[elem].Horizontal_Corrector]
        elif (
            hasattr(self[elem], "Vertical_Corrector")
            and self[elem].Vertical_Corrector is not None
        ):
            return [self[elem].Vertical_Corrector]
        else:
            return [elem]

    def get_correctors(self, end: str = None, start: str = None, path: str = None):
        correctors = self.elements_between(
            start=start,
            end=end,
            element_class="magnet",
            element_type=[
                "combined_corrector",
                "horizontal_corrector",
                "vertical_corrector",
            ],
            path=path,
        )
        return list(
            flatten(
                [(self.__get_combined_corrector_sub_correctors(c)) for c in correctors]
            )
        )

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
            element_type=[
                "combined_corrector",
                "horizontal_corrector",
                "vertical_corrector",
            ],
            path=path,
        )

    def get_combined_correctors(
        self, end: str = None, start: str = None, path: str = None
    ):
        return self.elements_between(
            start=start,
            end=end,
            element_class="magnet",
            element_type=["combined_corrector"],
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
    def all_combined_correctors(self) -> set:
        return self.__all_elements(
            element_class="magnet",
            element_type="combined_corrector",
        )

    @property
    def all_separate_magnets(self) -> set:
        return set(
            [
                elem
                for pathelems in [
                    self.get_separate_magnets(start=None, end=None, path=path)
                    for path in self.lattices.keys()
                ]
                for elem in pathelems
            ]
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
