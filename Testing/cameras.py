import sys
sys.path.append('../')
from PAdantic.PAdantic import PAdantic

# cam = Camera(name="CLA-S01-DIA-CAM-01", machine_area="S01", physical=PhysicalElement(), diagnostic=Camera_Diagnostic(type="PCO"), controls=CameraPV.with_defaults("CLA-S01-DIA-CAM-01"))
# print(cam.yaml_dump())
# export_elements("../PAdantic/Machines/CLARA/YAML", [cam])

machine = PAdantic(
    layout_file="Machines/CLARA/layouts.yaml",
    section_file="Machines/CLARA/sections.yaml",
    yaml_dir="Machines/CLARA/YAML/",
)
machine.default_layout = "CLARA"
print(machine.get_all_screens_and_cameras(end='CLA-S05-MAG-QUAD-01'))
print(machine.get_all_shutters(end='CLA-FED-MAG-QUAD-03'))
