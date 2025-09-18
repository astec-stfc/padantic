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
from PAdantic.models.control import ControlsInformation  # noqa E402
from PAdantic.models.element import Element  # noqa E402

machine = MachineModel(
    layout_file="../../padantic-lattices/CLARA/layouts.yaml",
    section_file="../../padantic-lattices/CLARA/sections.yaml",
)

for f in SF_files:
    elem = read_SimFrame_YAML(f)
    for name, element in elem.items():
        example_controls = {
            "variables": {
                "state": {
                    "identifier": f"{element.name}:STATE",
                    "dtype": "int",
                    "protocol": "CA",
                    "units": "N/A",
                    "description": f"State of {element.name}",
                    "read_only": False,
                },
                "setpoint": {
                    "identifier": f"{element.name}:SP",
                    "dtype": "float",
                    "protocol": "CA",
                    "units": "N/A",
                    "description": f"Setpoint of {element.name}",
                },
                "readback": {
                    "identifier": f"{element.name}:RBV",
                    "dtype": "float",
                    "protocol": "CA",
                    "units": "N/A",
                    "description": f"Readback of {element.name}",
                },
            }
        }
        controls = ControlsInformation(**example_controls)
        if isinstance(element, Element):
            element.controls = controls
        machine.update({n: e for n, e in elem.items()})
    machine.update({n: e for n, e in elem.items()})

export_machine("../../padantic-lattices/CLARA_export/YAML", machine)
export_machine_combined_file("../../padantic-lattices/CLARA_export/", machine)
