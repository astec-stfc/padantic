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
    layout_file="Machines/CLARA/layouts.yaml",
    section_file="Machines/CLARA/sections.yaml",
)

for f in SF_files:
    elem = read_SimFrame_YAML(f)
    machine.update({n: e for n, e in elem.items()})

print(export_machine("../PAdantic/Machines/CLARA/YAML", machine))
export_machine_combined_file("../PAdantic/Machines/CLARA/", machine)
