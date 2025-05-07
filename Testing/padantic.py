import sys

sys.path.append("..")
from PAdantic.PAdantic import PAdantic  # noqa E402

machine = PAdantic(
    layout_file="Machines/CLARA/layouts.yaml",
    section_file="Machines/CLARA/sections.yaml",
    yaml_dir="Machines/CLARA/YAML/",
)


def flatten(xss):
    return [x for xs in xss for x in xs]


def unique_list(a_list):
    seen = list()
    for x in flatten(a_list):
        if x not in seen:
            seen.append(x)
    return seen


machine.default_layout = "SP3"
# pprint({d: machine.get_element(d).yaml_dump() for d in machine.get_dipoles()})
# exit()
for magnet_name in machine.get_quadrupoles():
    linsat = machine.get_element(magnet_name).magnetic.linear_saturation_coefficients
    kvals = magnet_name, linsat.currentToK(48, 30)
    print(magnet_name, kvals[1]["K"], linsat.KToCurrent(kvals[1], 30))
    print(magnet_name, kvals[1]["KL"], linsat.KLToCurrent(kvals[1], 30))
