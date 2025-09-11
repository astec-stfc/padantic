import sys
from pprint import pprint

sys.path.append("..")
from PAdantic.PAdantic import PAdantic  # noqa E402
from PAdantic.Exporters.CATAP import export_machine_dict

machine = PAdantic(
    layout_file="../../padantic-clara/CLARA/layouts.yaml",
    section_file="../../padantic-clara/CLARA/sections.yaml",
    yaml_dir="../../padantic-clara/CLARA/YAML/",
)

catap_machine = export_machine_dict(machine=machine)
pprint(list(catap_machine)[0])
