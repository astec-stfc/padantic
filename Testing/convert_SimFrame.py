import sys
import os
sys.path.append('..')
from PAdantic.PAdantic import PAdantic
from PAdantic.Importers.SimFrame_Loader import SF_files, read_SimFrame_YAML, get_SimFrame_PV
from PAdantic.models.elementList import MachineModel
from PAdantic.Exporters.YAML import export_as_yaml, export_machine

machine = MachineModel(layout_file='../PAdantic/Machines/CLARA/layouts.yaml', section_file='../PAdantic/Machines/CLARA/sections.yaml')

for f in SF_files:
    elem = read_SimFrame_YAML(f)
    machine.update({n: e for n,e in elem.items()})

export_machine('../PAdantic/Machines/CLARA/YAML', machine)

exit()
