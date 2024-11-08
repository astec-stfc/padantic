import sys

sys.path.append("..")
from PAdantic.Importers.SimFrame_Loader import (  # noqa E402
    SF_files,
    read_SimFrame_YAML,
)
from PAdantic.models.elementList import MachineModel  # noqa E402
from PAdantic.Exporters.YAML import export_machine  # noqa E402

machine = MachineModel(
    layout_file="../PAdantic/Machines/CLARA/layouts.yaml",
    section_file="../PAdantic/Machines/CLARA/sections.yaml",
)

for f in SF_files:
    elem = read_SimFrame_YAML(f)
    machine.update({n: e for n, e in elem.items()})

export_machine("../PAdantic/Machines/CLARA/YAML", machine)

exit()
