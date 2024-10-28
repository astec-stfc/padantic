import sys

sys.path.append("..")
from PAdantic.PAdantic import PAdantic  # noqa E402

machine = PAdantic(
    layout_file="Machines/CLARA/layouts.yaml",
    section_file="Machines/CLARA/sections.yaml",
    yaml_dir="Machines/CLARA/YAML/",
)
# print(list(machine.lattices['CLARA'].elements))
# print(machine['CLA-S07-DIA-CDR-01'])
machine.default_layout = "CLARA"
print(machine.get_all_elements(element_class="diagnostic", element_type="Screen"))
