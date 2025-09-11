import sys
from pprint import pprint

sys.path.append("../")
from PAdantic.PAdantic import PAdantic  # noqa E402

machine = PAdantic(
    layout_file="../../padantic-clara/CLARA/layouts.yaml",
    section_file="../../padantic-clara/CLARA/sections.yaml",
    yaml_dir="../../padantic-clara/CLARA/YAML/",
)
machine.default_layout = "CLARA"
pprint(machine.get_screens_and_cameras(end="CLA-S05-MAG-QUAD-01"))
