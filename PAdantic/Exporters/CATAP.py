import os
import yaml
from PAdantic.PAdantic import MachineModel


def element_to_CATAP(elem):
    catap_dict = {}
    catap_dict["controls_information"] = {}
    catap_dict["controls_information"]["PV"] = True
    catap_dict["controls_information"]["pv_record_map"] = {}
    print(elem.controls)
    exit()
    for k, v in dict(elem.controls).items():
        catap_dict["controls_information"]["pv_record_map"][k] = str(v)
    catap_dict["controls_information"]["records"] = ",".join(dict(elem.controls).keys())
    catap_dict["properties"] = elem.to_CATAP()
    return catap_dict


def save_CATAP_file(n, e):
    subdir = e.hardware_type
    if not os.path.isdir("to_CATAP/MasterLattice/" + subdir):
        os.mkdir("to_CATAP/MasterLattice/" + subdir)
    with open("to_CATAP/MasterLattice/" + subdir + "/" + n + ".yml", "w") as outfile:
        yaml.dump(element_to_CATAP(e), outfile, default_flow_style=False)

    # print(element_to_CATAP(e))


def export_machine(path: str, machine: MachineModel, overwrite: bool = False) -> None:
    for name, elem in machine.elements.items():
        directory = os.path.join(path, elem.subdirectory)
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, elem.name + ".yaml")
        if overwrite or not os.path.isfile(filename):
            print("Exporting Element", name, "to file", filename)
            save_CATAP_file(filename, elem)


def export_machine_dict(machine: MachineModel) -> list:
    for name, elem in machine.elements.items():
        if hasattr(elem, "controls"):
            print("Exporting Element", name)
            yield element_to_CATAP(elem)
