import os

from PAdantic.models.elementList import MachineModel
from Importers.SimFrame_Loader import SF_files, read_SimFrame_YAML
from Importers.CATAP_Loader import catap_files, read_CATAP_YAML
from Exporters.CATAP import element_to_CATAP, save_CATAP_file

if __name__ == "__main__":

    # SFmachine = MachineModel(layout_file=os.path.abspath('./layouts.yaml'))
    #
    # for f in SF_files:
    #     elem = read_SimFrame_YAML(f)
    #     SFmachine.update({n: e for n,e in elem.items()})

    CATAPmachine = MachineModel(layout_file=os.path.abspath("./layouts.yaml"))

    for f in catap_files:
        elem = read_CATAP_YAML(f)
        CATAPmachine.update({n: e for n, e in elem.items()})

    # for n,e in {n:e for n,e in machine.elements.items() if not 'FMS' in n}.items():
    #     save_CATAP_file(n, e)
