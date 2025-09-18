import sys
from pprint import pprint

sys.path.append("..")
from PAdantic.PAdantic import PAdantic  # noqa E402

machine = PAdantic(
    layout="../../padantic-lattices/CLARA/layouts.yaml",
    section="../../padantic-lattices/CLARA/sections.yaml",
    element_list="../../padantic-lattices/NEW/CLARA/YAML/",
)


def flatten(xss):
    return [x for xs in xss for x in xs]


def unique_list(a_list):
    seen = list()
    for x in flatten(a_list):
        if x not in seen:
            seen.append(x)
    return seen


machine.default_path = "SP3"
print(machine.get_elements_s_pos())
pprint({d: machine.get_element(d).base_model_dump() for d in machine.get_dipoles()})
# exit()
for magnet_name in machine.get_quadrupoles():
    linsat = machine.get_element(magnet_name).magnetic.linear_saturation_coefficients
    kvals = magnet_name, linsat.currentToK(48, 30)
    print(magnet_name, kvals[1]["K"], linsat.KToCurrent(kvals[1], 30))
    print(magnet_name, kvals[1]["KL"], linsat.KLToCurrent(kvals[1], 30))
exit()
