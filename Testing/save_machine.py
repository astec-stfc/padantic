import sys

sys.path.append("..")
from PAdantic.Importers.SimFrame_Loader import (  # noqa E402
    SF_files,
    read_SimFrame_YAML,
)
from PAdantic.Exporters.YAML import (  # noqa E402
    export_machine,
    export_machine_combined_file,
)
from PAdantic.models.elementList import MachineModel  # noqa E402

machine = MachineModel(
    layout_file="../../padantic-clara/CLARA/layouts.yaml",
    section_file="../../padantic-clara/CLARA/sections.yaml",
)

for f in SF_files:
    elem = read_SimFrame_YAML(f)
    machine.update({n: e for n, e in elem.items()})

print(export_machine("../../padantic-clara/CLARA_export/YAML", machine))
export_machine_combined_file("../../padantic-clara/CLARA_export/", machine)
