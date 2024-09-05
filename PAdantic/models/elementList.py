import os
from typing import List, Dict, Any, Union
from pydantic import field_validator, BaseModel, ValidationInfo

from ._functions import read_yaml, merge_two_dicts
from .element import _baseElement
from .baseModels import YAMLBaseModel
from .exceptions import LatticeError


class BaseLatticeModel(YAMLBaseModel):
    name: str
    _basename: str

    def __add__(self, other: dict) -> dict:
        copy = getattr(self, self._basename).copy()
        copy.extend(other)
        return copy

    def __radd__(self, other: dict) -> dict:
        copy = other.copy()
        copy.extend(getattr(self, self._basename))
        return copy

    def __sub__(self, other):
        copy = getattr(self, self._basename).copy()
        if other in copy:
            del copy[other]
        return copy

    def append(self, other: Any) -> None:
        if not isinstance(other, list):
            other = [other]
        super().__init__(name=self.name, elements=self + other)
        setattr(self, self._basename, self + other)

    def remove(self, other: Any) -> None:
        if other in getattr(self, self._basename):
            copy = getattr(self, self._basename).copy()
            copy.remove(other)
            super().__init__(name=self.name, elements=copy)
            getattr(self, self._basename).remove(other)

    def __str__(self):
        return str({k: v.names() for k, v in getattr(self, self._basename).items()})

    def __repr__(self):
        return self.__str__()


class ElementList(YAMLBaseModel):
    elements: Dict[str, Union[BaseModel, None]]

    def __str__(self):
        return str([e.name for e in self.elements.values()])

    def __getitem__(self, item: str) -> int:
        return self.elements[item]

    def names(self):
        return [e.name for e in self.elements.values()]

    def index(self, element: Union[str, BaseModel]):
        if isinstance(element, str):
            return list(self.elements.keys()).index(element)
        return list(self.elements.values()).index(element)

    def _get_attributes_or_none(self, a):
        data = {}
        for k, v in self.elements.items():
            if v is not None and hasattr(v, a):
                data.update({k: getattr(v, a)})
            else:
                data.update({k: None})
        return data

    def __getattr__(self, a):
        try:
            return super().__getattr__(a)
        except Exception:
            data = self._get_attributes_or_none(a)
            if all([isinstance(d, (Union[BaseModel, None])) for d in data.values()]):
                return ElementList(elements=data)
            return data

    def list(self):
        return list(self.elements.values())


class SectionLattice(BaseLatticeModel):
    order: List[str]
    elements: ElementList
    # other_elements: ElementList = ElementList(elements={})
    _basename: str = "elements"

    @field_validator("elements", mode="before")
    @classmethod
    def validate_elements(
        cls, elements: Union[List[_baseElement], ElementList], info: ValidationInfo
    ) -> ElementList:
        if isinstance(elements, list):
            elemdict = {e.name: e for e in elements}
            # print([e for e in info.data['order'] if e not in elemdict.keys()])
            return ElementList(
                elements={
                    e: elemdict[e] for e in info.data["order"] if e in elemdict.keys()
                }
            )
        assert isinstance(elements, ElementList)
        return elements

    @property
    def names(self):
        return self.elements.names()

    def __str__(self):
        # return str(getattr(self, self._basename).__str__())
        return str(self.names)

    def __getitem__(self, item: Union[str, int]) -> BaseModel:
        if isinstance(item, int):
            return self.elements[self.names[item]]
        return self.elements[item]

    def __getattr__(self, a):
        try:
            return super().__getattr__(a)
        except Exception:
            return getattr(self.elements, a)

    def _get_all_elements(self) -> ElementList:
        return [self.elements[e] for e in self.order if e in self.elements.names()]


class MachineLayout(BaseLatticeModel):
    sections: Dict[str, SectionLattice]  # = Field(frozen=True)
    _basename: str = "sections"

    def model_post_init(self, __context):
        matrix = [v._get_all_elements() for v in self.sections.values()]
        all_elems = [item for row in matrix for item in row]
        if len(all_elems) > 0:
            all_elems_reversed = reversed(all_elems)
            start_pos = all_elems[-1].physical.start
            all_elem_corrected = []
            for elem in all_elems_reversed:
                vector = not elem.physical.end.vector_angle(start_pos, [0, 0, -1]) < 0
                if vector:
                    all_elem_corrected += [elem]
                    start_pos = elem.physical.start
            self._all_elements = list(reversed(all_elem_corrected))
        else:
            self._all_elements = {}

    def names(self):
        return [e.name for e in getattr(self, self._basename).values()]

    def __str__(self):
        return str([k for k, v in self.sections.items()])

    def __getattr__(self, item: str):
        return getattr(self.sections, item)

    def __getitem__(self, item: str) -> int:
        return self.sections[item]

    def _get_all_elements(self) -> list:
        return self._all_elements

    def _get_all_element_names(self) -> list:
        return [e.name for e in self._get_all_elements()]

    def get_element(self, name: str) -> _baseElement:
        """
        Return the LatticeElement object corresponding to a given machine element

        :param str name: Name of the element to look up
        :returns: LatticeElement instance for that element, or *None* if that element does not exist
        """
        if name in self._get_all_element_names():
            index = self._get_all_element_names().index(name)
            return self._get_all_elements()[index]
        else:
            return None

    def _get_element_names(self, lattice: list) -> list:
        """
        Return the name for each LatticeElement object in a list defining a lattice

        :param str lattice: List of LatticeElement objects representing machine hardware
        :returns: List of strings defining the names of the machine elements
        """
        return [ele.name for ele in lattice]

    def _lookup_index(self, name: str) -> int:
        """
        Look up the index of an element in a given lattice

        :param str name: Name of the element to search for
        :returns: List index of the item within that beam path, or *None* if that element does not exist
        """
        try:
            # fetch the index of the element
            return self._get_all_element_names().index(name)
        except ValueError:
            return None

    @property
    def elements(self):
        return self._get_all_element_names()

    def elements_between(
        self,
        end: str = None,
        start: str = None,
        element_type: Union[str, list, None] = None,
    ) -> List[str]:
        """
        Returns a list of all lattice elements (of a specified type) between
        any two points along the accelerator. Elements are ordered according
        to their longitudinal position along the beam path.

        :param str end: Name of the element defining the end of the search region
        :param str start: Name of the element defining the start of the search region
        :param str | list type: Type(s) of elements to include in the list
        :returns: List containing the names of all elements between (and including) *start* and *end*
        """
        # replace blank start and/or end point
        element_names = self._get_all_element_names()
        if start is None:
            start = element_names[0]
        if end is None:
            end = element_names[-1]

        # truncate the list between the start and end elements
        first = self._lookup_index(start)
        last = self._lookup_index(end) + 1
        result = self._get_all_elements()[first:last]

        if isinstance(element_type, (str, list)):
            # make list of valid types
            if isinstance(element_type, str):
                type_list = [element_type.lower()]
            elif isinstance(element_type, list):
                type_list = [_type.lower() for _type in element_type]

            # apply search criteria
            result = [
                ele for ele in result if (ele.hardware_class.lower() in type_list)
            ]

        return self._get_element_names(result)


class MachineModel(YAMLBaseModel):
    layout_file: str
    section_file: str
    elements: Dict[str, _baseElement] = {}
    sections: Dict[str, SectionLattice] = {}
    lattices: Dict[str, MachineLayout] = {}

    @field_validator("layout_file", mode="before")
    @classmethod
    def validate_layout_file(cls, v: str) -> str:
        if os.path.isfile(v):
            return v
        elif os.path.isfile(os.path.abspath(os.path.dirname(__file__) + "/../" + v)):
            return os.path.abspath(os.path.dirname(__file__) + "/../" + v)
        else:
            raise ValueError(f"Directory {v} does not exist")

    @field_validator("section_file", mode="before")
    @classmethod
    def validate_section_file(cls, v: str) -> str:
        if os.path.isfile(v):
            return v
        elif os.path.isfile(os.path.abspath(os.path.dirname(__file__) + "/../" + v)):
            return os.path.abspath(os.path.dirname(__file__) + "/../" + v)
        else:
            raise ValueError(f"Directory {v} does not exist")

    def model_post_init(self, __context):
        config = read_yaml(self.layout_file)
        self._layouts = config.layouts
        config = read_yaml(self.section_file)
        self._section_definitions = config.sections
        if len(self.elements) > 0:
            self._build_layouts(self.elements)

    def __add__(self, other) -> dict:
        copy = self.elements.copy()
        copy.update(other)
        return copy

    def __radd__(self, other) -> dict:
        copy = other.copy()
        copy.update(self.elements)
        return copy

    def __iter__(self) -> iter:
        return iter(self.elements)

    def __str__(self):
        return str(list(self.elements.keys()))

    def append(self, values: dict) -> None:
        self.elements = merge_two_dicts(values, self.elements)
        self._build_layouts(self.elements)

    def update(self, values: dict) -> None:
        return self.append(values)

    def __getitem__(self, item: str) -> int:
        return self.elements[item]

    def __setitem__(self, item: str, value: Any) -> None:
        super().__init__(elements=self + {item: value})

    def _build_layouts(self, elements: dict) -> None:
        """build lists defining the lattice elements along each possible beam path"""
        # build dictionary with a lattice for each beam path
        for path, areas in self._layouts.items():

            for _area in areas:
                # collect list of elements from this machine area
                new_elements = [
                    x for x in elements.values() if (x.machine_area == _area)
                ]
                if _area in self._section_definitions:
                    self.sections[_area] = SectionLattice(
                        name=_area,
                        elements=new_elements,
                        order=self._section_definitions[_area],
                    )
                else:
                    print("MachineModel", "_build_layouts", _area, "missing")

            self.lattices[path] = MachineLayout(
                name=path,
                sections={
                    _area: self.sections[_area]
                    for _area in areas
                    if _area in self.sections
                },
            )

    def get_element(self, name: str) -> _baseElement:
        """
        Return the LatticeElement object corresponding to a given machine element

        :param str name: Name of the element to look up
        :returns: LatticeElement instance for that element, or *None* if that element does not exist
        """
        if name in self.elements:
            return self.elements[name]
        else:
            return None

    def elements_between(
        self,
        end: str = None,
        start: str = None,
        element_type: Union[str, list, None] = None,
    ) -> List[str]:
        """
        Returns an ordered list of all lattice elements (of a specific type) between
        any two points along the accelerator.

        :param str end: Name of the last element. This element is used to determine the beam path.
        :param str start: Name of the first element.
        :param str | list type: Type(s) of elements to include in the list
        :returns: List of all element names between *start* and *end* (inclusive)
        """
        # determine the beam path
        default_path = "CLARA" if not (hasattr(self,'_default_path') and self._default_path in self.lattices) else self._default_path
        if end is None:
            path_obj = self.lattices[default_path]
            end = path_obj.elements[-1]
        else:
            end_obj = self.get_element(end)
            beam_path = (
                end_obj.machine_area
                if (end_obj.machine_area in self.lattices)
                else default_path
            )
            path_obj = self.lattices[beam_path]

        # find the start of the search area
        if start is None:
            start = path_obj.elements[0]

        # return a list of elements along this beam path
        elements = path_obj.elements_between(
            start=start, end=end, element_type=element_type
        )
        return elements
