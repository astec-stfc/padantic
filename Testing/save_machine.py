import sys

sys.path.append("..")
from PAdantic.PAdantic import PAdantic

# machine = PAdantic(layout_file='Machines/CLARA/layouts.yaml', section_file='Machines/CLARA/sections.yaml', yaml_dir='Machines/CLARA/YAML')
# print(machine['CLA-S07-DIA-CDR-01'])
# print(machine.elements_between(
#         start='CLA-S05-MAG-QUAD-01', end='CLA-SP2-DIA-SCR-02',
#         element_type=None))

from PAdantic.Importers.SimFrame_Loader import (
    SF_files,
    read_SimFrame_YAML,
    get_SimFrame_PV,
)
from PAdantic.Exporters.YAML import export_as_yaml, export_machine

# machine = MachineModel(layout_file='Machines/CLARA/layouts.yaml', section_file='Machines/CLARA/sections.yaml')
# for f in SF_files:
#     elem = read_SimFrame_YAML(f)
#     machine.update({n: e for n,e in elem.items()})
machine = PAdantic(
    layout_file="../PAdantic/Machines/CLARA/layouts.yaml",
    section_file="../PAdantic/Machines/CLARA/sections.yaml",
    yaml_dir="../PAdantic/Machines/CLARA/YAML",
)
print(machine.elements["CLA-FEA-MAG-QUAD-01"].flat())
print(export_machine("../PAdantic/Machines/CLARA/YAML", machine))

# machine = PAdantic(layout_file='Machines/CLARA/layouts.yaml', section_file='Machines/CLARA/sections.yaml', yaml_dir='Machines/CLARA/YAML')

exit()
