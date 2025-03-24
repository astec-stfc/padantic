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
print(machine.get_all_elements())
exit()
for magnet_name in machine.get_quadrupoles():
    linsat = machine.get_element(magnet_name).magnetic.linear_saturation_coefficients
    print(magnet_name, linsat.currentToK(10, 240))
    print(magnet_name, linsat.KToCurrent(linsat.currentToK(1, 240)[0], 240))
