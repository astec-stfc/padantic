import os
import yaml
from typing import Union
from ..models.elementList import MachineModel
from ..models.element import PhysicalElement


def export_as_yaml(
    filename: Union[str, None], ele: PhysicalElement = PhysicalElement
) -> None:
    if filename is not None:
        with open(filename, "w") as yaml_file:
            yaml.default_flow_style = True
            dump = ele.yaml_dump()
            # dump["hardware_subclass"] = ele.__class__.__name__
            yaml.dump(dump, yaml_file)
    else:
        dump = ele.yaml_dump()
        # dump["hardware_subclass"] = ele.__class__.__name__
        return dump


def export_machine_combined_file(path: str, machine: MachineModel) -> None:
    filename = os.path.join(path, "summary.yaml")
    os.makedirs(path, exist_ok=True)
    combined_yaml = {}
    for name, elem in machine.elements.items():
        combined_yaml[name] = export_as_yaml(None, elem)
    with open(filename, "w") as yaml_file:
        yaml.default_flow_style = True
        yaml.dump(combined_yaml, yaml_file)


def export_machine(path: str, machine: MachineModel, overwrite: bool = False) -> None:
    for name, elem in machine.elements.items():
        directory = os.path.join(path, elem.subdirectory)
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, elem.name + ".yaml")
        if overwrite or not os.path.isfile(filename):
            print("Exporting Element", name, "to file", filename)
            export_as_yaml(filename, elem)


def export_elements(path: str, elements: list[PhysicalElement]) -> None:
    for elem in elements:
        directory = os.path.join(path, elem.subdirectory)
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, elem.name + ".yaml")
        export_as_yaml(filename, elem)
