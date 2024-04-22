import os
import pandas
from copy import copy

from yaml.constructor import Constructor

def add_bool(self, node):
    return self.construct_scalar(node)

Constructor.add_constructor(u'tag:yaml.org,2002:bool', add_bool)

from typing import get_origin, Any, Dict
from pydantic import BaseModel, RootModel
from models.elementList import MachineModel
from Importers.SimFrame_Loader import SF_files, read_SimFrame_YAML, get_SimFrame_PV
from Importers.CATAP_Loader import element_to_CATAP
from Exporters.YAML import export_as_yaml

if __name__ == "__main__":


    machine = MachineModel(layout_file=os.path.abspath('./layouts.yaml'))

    for f in SF_files:
        elem = read_SimFrame_YAML(f)
        machine.update({n: e for n,e in elem.items()})
    # print(machine.lattices['SP3'])
    # print(machine.elements_between(
    #         start='CLA-S07-MAG-QUAD-01', end='CLA-SP3-DIA-SCR-02',
    #         element_type='Screen'))
    print(machine.get_element('CLA-S07-MAG-QUAD-01').manufacturer.model_dump(exclude_defaults=False))
    # export_as_yaml('test.yaml', machine.get_element('CLA-S07-MAG-QUAD-01'))
