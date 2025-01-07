import sys

sys.path.append("..")
from PAdantic.PAdantic import PAdantic  # noqa E402

machine = PAdantic(
    layout_file="Machines/CLARA/layouts.yaml",
    section_file="Machines/CLARA/sections.yaml",
    yaml_dir="Machines/CLARA/YAML/",
)

machine.default_layout = "CLARA"
print(machine.get_all_position_diagnostics(path='C2V'))
