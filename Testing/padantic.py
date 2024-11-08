import sys

sys.path.append("..")
from PAdantic.PAdantic import PAdantic
from PAdantic.Exporters.YAML import export_machine_combined_file


# machine = PAdantic(layout_file='Machines/CLARA/layouts.yaml', section_file='Machines/CLARA/sections.yaml', yaml_dir='Machines/CLARA/YAML/')
# print(export_machine_combined_file('../PAdantic/Machines/CLARA', machine))

machine = PAdantic(
    layout_file="Machines/CLARA/layouts.yaml",
    section_file="Machines/CLARA/sections.yaml",
    yaml_dir="Machines/CLARA/YAML/",
)
# print(machine.lattices['CLARA'].elements_between(element_class="magnet"))
# print(machine['CLA-S07-DIA-CDR-01'])
machine.default_layout = "CLARA"
print(machine.get_all_solenoids())

# from PAdantic.Importers.SimFrame_Loader import SF_files, read_SimFrame_YAML, get_SimFrame_PV
# from PAdantic.Exporters.YAML import export_as_yaml, export_machine
# machine = MachineModel(layout_file='Machines/CLARA/layouts.yaml', section_file='Machines/CLARA/sections.yaml')
# for f in SF_files:
#     elem = read_SimFrame_YAML(f)
#     machine.update({n: e for n,e in elem.items()})
# machine = PAdantic(layout_file='Machines/CLARA/layouts.yaml', section_file='Machines/CLARA/sections.yaml', yaml_dir='Machines/CLARA/YAML')
# print(machine.elements['CLA-FEA-MAG-QUAD-01'].flat())
# print(export_machine('Machines/CLARA/YAML', machine))
exit()
