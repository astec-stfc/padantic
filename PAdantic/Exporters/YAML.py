import os
import yaml
from pydantic import BaseModel
from ..models.elementList import MachineModel
import numpy as np

def export_as_yaml(filename: str | None, ele: BaseModel = BaseModel) -> None:
    if filename is not None:
        with open(filename,"w") as yaml_file:
            yaml.default_flow_style=True
            dump = ele.yaml_dump()
            dump['class_name'] = ele.__class__.__name__
            # print(dump)
            # exit()
            yaml.dump(dump, yaml_file)
    else:
        return ele.yaml_dump()

def export_machine(path, machine: MachineModel) -> None:
    for name, elem in machine.elements.items():
        directory = os.path.join(path, elem.subdirectory)
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, elem.name + '.yaml')
        export_as_yaml(filename, elem)
