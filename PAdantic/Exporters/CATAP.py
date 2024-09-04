import os
import yaml


def element_to_CATAP(elem):
    catap_dict = {}
    catap_dict["controls_information"] = {}
    catap_dict["controls_information"]["PV"] = True
    catap_dict["controls_information"]["pv_record_map"] = {}
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
