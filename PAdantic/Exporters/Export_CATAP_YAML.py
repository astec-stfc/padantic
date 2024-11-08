import os

from PAdantic.models.elementList import MachineModel
from Importers.CATAP_Loader import catap_files, read_CATAP_YAML

if __name__ == "__main__":
    CATAPmachine = MachineModel(layout_file=os.path.abspath("./layouts.yaml"))

    for f in catap_files:
        elem = read_CATAP_YAML(f)
        CATAPmachine.update({n: e for n, e in elem.items()})
