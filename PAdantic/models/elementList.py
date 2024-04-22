import os
from copy import copy
from typing import Type, List, Dict, Any
from pydantic import field_validator, Field, BaseModel, ValidationInfo, PrivateAttr
from models._functions import read_yaml

from models.element import _baseElement
from models.baseModels import YAMLBaseModel

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

    def __sub__ (self, other):
        copy = getattr(self, self._basename).copy()
        if other in copy:
            del copy[other]
        return copy

    def append(self, other: Any) -> None:
        if not isinstance(other, list):
            other = [other]
        super().__init__(name=self.name, elements = self + other)
        setattr(self, self._basename, self + other)

    def remove(self, other: Any) -> None:
        if other in getattr(self, self._basename):
            copy = getattr(self, self._basename).copy()
            copy.remove(other)
            super().__init__(name=self.name, elements=copy)
            getattr(self, self._basename).remove(other)

    def __str__(self):
        return str({k: v.names() for k,v in getattr(self, self._basename).items()})

    def __repr__(self):
        return self.__str__()

class ElementList(YAMLBaseModel):
    elements: Dict[str, BaseModel|None]

    def names(self):
        return [e.name for e in self.elements.values()]

    def index(self, element: str|BaseModel):
        if isinstance(element, str):
            return list(self.elements.keys()).index(element)
        return list(self.elements.values()).index(element)

    def _get_attributes_or_none(self, a):
        data = {}
        for k,v in self.elements.items():
            if v is not None and hasattr(v, a):
                data.update({k: getattr(v,a)})
            else:
                data.update({k: None})
        return data

    def __getattr__(self, a):
        try:
            return super().__getattr__(a)
        except Exception as e:
            print(e)
            data = self._get_attributes_or_none(a)
            if all([isinstance(d, (BaseModel|None)) for d in data.values()]):
                return ElementList(elements=data)
            return data

    def list(self):
        return list(self.elements.values())

class SectionLattice(BaseLatticeModel):
    elements: ElementList
    _basename: str = 'elements'

    @field_validator('elements', mode='before')
    @classmethod
    def validate_elements(cls, elements: List[_baseElement]|ElementList, info: ValidationInfo) -> ElementList:
        if isinstance(elements, list):
            return ElementList(elements={e.name:e for e in elements})
        return elements

    def names(self):
        return getattr(self, self._basename).names()

    def __str__(self):
        return str(getattr(self, self._basename))

    def __getattr__(self, a):
        try:
            return super().__getattr__(a)
        except:
            return getattr(self.elements,a)

    def _get_all_elements(self) -> ElementList:
        return self.elements.list()

class MachineLayout(BaseLatticeModel):
    sections: Dict[str, SectionLattice]
    _basename: str = 'sections'

    def names(self):
        return [e.name for e in getattr(self, self._basename).values()]

    def __str__(self):
        return str({k: v.names() for k,v in getattr(self, self._basename).items()})

    def _get_all_elements(self) -> list:
        matrix = [v._get_all_elements() for v in self.sections.values()]
        return [item for row in matrix for item in row]

    def _get_all_element_names(self) -> list:
        return [e.name for e in self._get_all_elements()]

    def get_element(self, name: str) -> _baseElement:
        '''
        Return the LatticeElement object corresponding to a given machine element

        :param str name: Name of the element to look up
        :returns: LatticeElement instance for that element, or *None* if that element does not exist
        '''
        if name in self._get_all_element_names():
            index = self._get_all_element_names().index(name)
            return self._get_all_elements()[index]
        else:
            raise LatticeError('Element %s does not exist in the accelerator lattice' % name)

    def _get_element_names(self, lattice: list) -> list:
        '''
        Return the name for each LatticeElement object in a list defining a lattice

        :param str lattice: List of LatticeElement objects representing machine hardware
        :returns: List of strings defining the names of the machine elements
        '''
        return [ele.name for ele in lattice]

    def _lookup_index(self, name: str) -> int:
        '''
        Look up the index of an element in a given lattice

        :param str name: Name of the element to search for
        :returns: List index of the item within that beam path, or *None* if that element does not exist
        '''
        # fetch the index of the element
        ele_obj = self.get_element(name)
        try:
            return self._get_all_element_names().index(ele_obj.name)
        except ValueError:
            raise LatticeError('Element %s does not exist anywhere in beam path "%s"' % (name))

    def elements_between(
            self, end: str=None, start: str=None,
            element_type: str|list=None) -> List[str]:
        '''
        Returns a list of all lattice elements (of a specified type) between
        any two points along the accelerator. Elements are ordered according
        to their longitudinal position along the beam path.

        :param str end: Name of the element defining the end of the search region
        :param str start: Name of the element defining the start of the search region
        :param str | list type: Type(s) of elements to include in the list
        :returns: List containing the names of all elements between (and including) *start* and *end*
        '''
        # replace blank start and/or end point
        element_names = self._get_all_element_names()
        if start is None:
            start = element_names[0]
        if end is None:
            end = element_names[-1]

        # check the start and end elements are valid
        start_obj = self.get_element(start)
        end_obj = self.get_element(end)

        # truncate the list between the start and end elements
        first = self._lookup_index(start)
        last = self._lookup_index(end) + 1
        result = self._get_all_elements()[first:last]

        # filter the results to include only certain element types
        if isinstance(element_type, (str, list)):
            _types = [element_type] if isinstance(element_type, str) else element_type
            result = [ele for ele in result if ele.hardware_type in _types]

        return self._get_element_names(result)

class MachineModel(YAMLBaseModel):
    elements: Dict[str, _baseElement] = {}
    layout_file: str = 'layouts.yaml'

    @field_validator('elements', mode='before')
    @classmethod
    def validate_elements(cls, elements: dict, info: ValidationInfo) -> str:
        cls._build_layouts(cls, elements)
        return elements

    @field_validator('layout_file', mode='before')
    @classmethod
    def validate_layout_file(cls, v: str) -> str:
        assert os.path.isfile(v)
        config = read_yaml(v)
        cls._layouts = config.layouts
        return v

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
        super().__init__(layout_file=self.layout_file, elements=self + values)

    def update(self, values: dict) -> None:
        super().__init__(layout_file=self.layout_file, elements=self + values)

    def __getattr__(self, item: str):
        return getattr(self.elements, item)

    def __getitem__(self, item: str) -> int:
            return self.elements[item]

    def __setitem__(self, item: str, value: Any) -> None:
        super().__init__(elements=self + {item: value})

    def _build_layouts(self, elements: dict) -> None:
        '''build lists defining the lattice elements along each possible beam path'''
        # build dictionary with a lattice for each beam path
        self.sections = {}
        self.lattices = {}
        for path, areas in self._layouts.items():

            for _area in areas:
                # collect list of elements from this machine area
                new_elements = [x for x in elements.values() if (x.machine_area == _area)]
                self.sections[_area] = SectionLattice(name=_area, elements=new_elements)
                # add the new elements to the lattice
            self.lattices[path] = MachineLayout(name=path, sections={_area: self.sections[_area] for _area in areas})

    def get_element(self, name: str) -> _baseElement:
        '''
        Return the LatticeElement object corresponding to a given machine element

        :param str name: Name of the element to look up
        :returns: LatticeElement instance for that element, or *None* if that element does not exist
        '''
        if name in self.elements:
            return self.elements[name]
        else:
            raise LatticeError('Element %s does not exist in the accelerator lattice' % name)

    def elements_between(
            self, end: str=None, start: str=None,
            element_type: str|list=None) -> List[str]:
        '''
        Returns a list of all lattice elements (of a specified type) between
        any two points along the accelerator. Elements are ordered according
        to their longitudinal position along the beam path.

        :param str end: Name of the element defining the end of the search region
        :param str start: Name of the element defining the start of the search region
        :param str | list type: Type(s) of elements to include in the list
        :returns: List containing the names of all elements between (and including) *start* and *end*
        '''
        # replace blank start and/or end point
        element_names = self.elements.keys()
        if start is None:
            start = element_names[0]
        if end is None:
            end = element_names[-1]

        # check the start and end elements are valid
        start_obj = self.get_element(start)
        end_obj = self.get_element(end)

         # determine machine area at the end of the path
        path_to_end = end_obj.machine_area if (end_obj.machine_area in self.lattices) else 'CLARA'
        full_path = self.lattices[path_to_end]

        return full_path.elements_between(end=end, start=start,
                element_type=element_type)
