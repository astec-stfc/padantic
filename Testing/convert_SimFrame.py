import sys

sys.path.append("..")
from PAdantic.Importers.SimFrame_Loader import read_SimFrame_YAML
from PAdantic.models.elementList import MachineModel  # noqa E402
from PAdantic.Exporters.YAML import export_machine  # noqa E402

master_lattice_location = "../../masterlattice/MasterLattice/YAML"

SF_files = [
    f"{master_lattice_location}/CLA_Gun400.yaml",
    f"{master_lattice_location}/CLA_SP2.yaml",
    f"{master_lattice_location}/CLA_SP3.yaml",
    f"{master_lattice_location}/CLA_FEBE.yaml",
    f"{master_lattice_location}/CLA_SP1.yaml",
]


machine = MachineModel(
    layout_file="../../padantic-clara/CLARA/layouts.yaml",
    section_file="../../padantic-clara/CLARA/sections.yaml",
)

for f in SF_files:
    elem = read_SimFrame_YAML(f)
    machine.update({n: e for n, e in elem.items()})

export_machine("../../padantic-clara/NEW/CLARA/YAML", machine, overwrite=True)

exit()
